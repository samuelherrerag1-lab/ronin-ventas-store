"""Aislamiento de estado en tests.

Ningún test debe escribir en `data/`. Antes, correr `pytest` sembraba
`customizations_state.json` con conectores falsos, `metrics_real.json` con
ventas de prueba y, sobre todo, agregaba un post basura a
`data/social_feeds.json` en cada corrida. Aquí se aíslan catálogo, feeds,
leads, métricas, estado de conectores y el de publicación.

Además se toma un snapshot de los JSON reales al inicio de la sesión: si la
suite los modifica, `test_data_dir_not_mutated_by_suite` falla.
"""

import hashlib
import json
import shutil
from pathlib import Path

import pytest

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
REAL_STATE_FILES = (
    "catalog.json",
    "social_feeds.json",
    "leads.json",
    "metrics_real.json",
    "customizations_state.json",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture(scope="session", autouse=True)
def data_dir_snapshot():
    """Hashes de los JSON reales al arrancar la suite (antes de cualquier test)."""
    snapshot = {
        name: _sha256(DATA_DIR / name)
        for name in REAL_STATE_FILES
        if (DATA_DIR / name).is_file()
    }
    head = _sha256(DATA_DIR / "catalog.json") if (DATA_DIR / "catalog.json").is_file() else None
    yield {"files": snapshot, "catalog": head}


@pytest.fixture(autouse=True)
def isolate_state_files(tmp_path, monkeypatch, data_dir_snapshot):
    state_file = tmp_path / "customizations_state.json"
    state_file.write_text(
        json.dumps({"connected_ids": [], "skill_toggles": {}}), encoding="utf-8"
    )

    metrics_file = tmp_path / "metrics_real.json"
    metrics_file.write_text(
        json.dumps({"sales": [], "manual_piece_metrics": [], "last_updated": None}),
        encoding="utf-8",
    )

    leads_file = tmp_path / "leads.json"
    leads_file.write_text(json.dumps({"leads": [], "updated_at": None}), encoding="utf-8")

    # Copia del catálogo real: los tests pueden escribir sin tocar data/.
    catalog_file = tmp_path / "catalog.json"
    real_catalog = DATA_DIR / "catalog.json"
    if real_catalog.is_file():
        shutil.copy2(real_catalog, catalog_file)
    else:
        catalog_file.write_text("[]", encoding="utf-8")

    # Feeds: no se copia el archivo real (tiene 55 posts de producción); se deja
    # que el store siembre la cola por defecto en tmp.
    feeds_file = tmp_path / "social_feeds.json"
    publish_state_file = tmp_path / "publish_state.json"
    publish_site_dir = tmp_path / "publish_site"

    import backend.routers.api_metrics as api_metrics
    import backend.services.catalog_seed as catalog_seed
    import backend.services.connector_diagnostics as connector_diagnostics
    import backend.services.connectors_hub as connectors_hub
    import backend.services.metrics_service as metrics_service
    import backend.services.publish_state as publish_state
    import backend.services.social_feed_seed as social_feed_seed
    import backend.routers.api_leads as api_leads

    monkeypatch.setattr(connectors_hub, "CUSTOMIZATIONS_JSON_PATH", state_file)
    monkeypatch.setattr(connector_diagnostics, "CUSTOMIZATIONS_JSON_PATH", state_file)
    monkeypatch.setattr(metrics_service, "METRICS_REAL_PATH", metrics_file)
    monkeypatch.setattr(api_metrics, "METRICS_REAL_PATH", metrics_file, raising=False)
    monkeypatch.setattr(api_leads, "LEADS_JSON_PATH", leads_file)
    monkeypatch.setattr(social_feed_seed, "FEEDS_JSON_PATH", feeds_file)
    monkeypatch.setattr(catalog_seed, "CATALOG_JSON_PATH", catalog_file)
    monkeypatch.setattr(publish_state, "PUBLISH_STATE_PATH", publish_state_file)
    monkeypatch.setattr(publish_state, "MANIFEST_PATH", publish_site_dir / "manifest.json")

    yield

    # Cinturón y tirantes: si un módulo importó el path antes del patch, se
    # restaura aquí para no filtrar estado entre tests.
    for module, attr, real in (
        (catalog_seed, "CATALOG_JSON_PATH", DATA_DIR / "catalog.json"),
        (social_feed_seed, "FEEDS_JSON_PATH", DATA_DIR / "social_feeds.json"),
    ):
        if getattr(module, attr) != real:
            setattr(module, attr, real)
