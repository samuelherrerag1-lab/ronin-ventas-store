"""Contrato de la API de publicación (`/api/publish/*`).

El router se monta en una app de prueba para no depender de que main.py ya lo
haya integrado; este contrato es el que consume el frontend.
"""

import json
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import backend.routers.api_publish as api_publish
import backend.services.publish_state as publish_state
from backend.routers.api_publish import router

app = FastAPI()
app.include_router(router)
client = TestClient(app)

CONTRACT_FIELDS = {"id", "platform", "text", "image_url", "target_route", "target_sku_id", "status"}


def test_readiness_contract_with_real_counts():
    res = client.get("/api/publish/readiness")
    assert res.status_code == 200
    data = res.json()
    assert {"ready", "checks", "blockers", "counts", "next_actions"} <= set(data)
    check_ids = {check["id"] for check in data["checks"]}
    assert {
        "deliverables",
        "checkout",
        "vertex",
        "art",
        "routes",
        "content",
        "site",
    } <= check_ids
    for check in data["checks"]:
        assert set(check) == {"id", "label", "ok", "detail"}
        assert isinstance(check["ok"], bool)
        assert check["detail"].strip()
    assert data["ready"] == (data["blockers"] == [])
    assert data["blockers"] == [check["id"] for check in data["checks"] if not check["ok"]]

    counts = data["counts"]
    for key in (
        "skus",
        "paid",
        "leads",
        "checkouts",
        "checkouts_gumroad",
        "checkouts_hotmart",
        "skus_missing_checkout",
        "threads",
        "pins",
        "art_covers",
        "deliverables",
    ):
        assert isinstance(counts[key], int), key
    assert counts["skus"] == 55
    assert counts["paid"] == 52
    assert counts["leads"] == 3
    assert counts["deliverables"] == 55
    assert counts["art_covers"] == 55
    assert counts["skus_missing_checkout"] == counts["paid"] - counts["checkouts"]
    assert counts["checkouts"] <= counts["checkouts_gumroad"] + counts["checkouts_hotmart"]
    assert len(counts["skus_missing_checkout_ids"]) == counts["skus_missing_checkout"]
    assert counts["threads"] >= 4
    assert counts["pins"] >= 7

    assert data["next_actions"], "siempre debe haber una acción siguiente"
    if "checkout" in data["blockers"]:
        assert any("Gumroad" in action and "Hotmart" in action for action in data["next_actions"])
    # El sitio no está exportado en el entorno de tests: debe ser un blocker honesto.
    assert "site" in data["blockers"]


def test_kit_threads_items_and_absolute_routes():
    res = client.get("/api/publish/kit", params={"platform": "threads", "limit": 50})
    assert res.status_code == 200
    data = res.json()
    assert data["published_to_network"] is False
    assert data["items"], "la cola de Threads no puede venir vacía"
    for item in data["items"]:
        assert set(item) == CONTRACT_FIELDS
        assert item["platform"] == "threads"
        assert item["text"].strip()
        assert item["image_url"] is None  # no hay captura renderizada: no se finge
        assert item["target_route"].startswith("http://testserver/")
        assert item["status"] in ("queued", "published")

    limited = client.get("/api/publish/kit", params={"platform": "threads", "limit": 2}).json()
    assert len(limited["items"]) == 2


def test_kit_pinterest_excludes_benchmarks_and_resolves_images():
    res = client.get("/api/publish/kit", params={"platform": "pinterest", "limit": 100})
    assert res.status_code == 200
    items = res.json()["items"]
    own_pins = [pin for pin in items if not pin["id"].startswith("pin_bench_")]
    assert len(own_pins) == len(items), "los pines de benchmark no se publican"
    assert items
    for item in items:
        assert set(item) == CONTRACT_FIELDS
        assert item["target_route"].startswith("http://testserver/")
        assert item["image_url"] is None or item["image_url"].startswith("http://testserver/")


def test_kit_rejects_invalid_platform():
    assert client.get("/api/publish/kit", params={"platform": "instagram"}).status_code == 422


def test_mark_persists_local_only_state():
    res = client.post(
        "/api/publish/mark",
        json={"platform": "threads", "item_id": "th_001", "status": "published"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["tracked_locally"] is True
    assert data["published_to_network"] is False
    assert data["publication_url"] is None
    assert "no publica" in data["note"].lower()

    kit = client.get("/api/publish/kit", params={"platform": "threads"}).json()
    statuses = {item["id"]: item["status"] for item in kit["items"]}
    assert statuses["th_001"] == "published"

    state_file = Path(publish_state.PUBLISH_STATE_PATH)
    assert state_file.is_file()
    stored = json.loads(state_file.read_text(encoding="utf-8"))
    assert stored["platforms"]["threads"]["th_001"]["status"] == "published"


def test_mark_validates_payload_and_item():
    assert (
        client.post(
            "/api/publish/mark",
            json={"platform": "threads", "item_id": "th_001", "status": "published_to_threads"},
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/api/publish/mark",
            json={"platform": "threads", "item_id": "no_existe", "status": "queued"},
        ).status_code
        == 404
    )
    assert (
        client.post(
            "/api/publish/mark",
            json={"platform": "pinterest", "item_id": "pin_bench_01", "status": "queued"},
        ).status_code
        == 404
    )


def test_export_site_uses_publish_pack_contract(monkeypatch):
    captured = {}

    class FakePack:
        @staticmethod
        def build_site(base_url=""):
            captured["base_url"] = base_url
            return {"generated_at": "2026-11-04T00:00:00Z", "routes": 55, "files": 120}

    monkeypatch.setattr(api_publish, "_load_publish_pack", lambda: FakePack)
    res = client.post("/api/publish/export-site")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["manifest"]["routes"] == 55
    assert captured["base_url"] == "http://testserver"

    def missing_module():
        raise ModuleNotFoundError("No module named 'backend.services.publish_pack'")

    monkeypatch.setattr(api_publish, "_load_publish_pack", missing_module)
    res_missing = client.post("/api/publish/export-site")
    assert res_missing.status_code == 503
    assert "publish_pack" in res_missing.json()["detail"]

    class BrokenPack:
        @staticmethod
        def build_site(base_url=""):
            raise RuntimeError("sin permisos de escritura")

    monkeypatch.setattr(api_publish, "_load_publish_pack", lambda: BrokenPack)
    res_broken = client.post("/api/publish/export-site")
    assert res_broken.status_code == 500
    assert "sin permisos" in res_broken.json()["detail"]


def test_site_manifest_honest_404_and_read(tmp_path, monkeypatch):
    manifest_file = tmp_path / "manifest.json"
    monkeypatch.setattr(publish_state, "MANIFEST_PATH", manifest_file)
    res = client.get("/api/publish/site-manifest")
    assert res.status_code == 404
    assert "export-site" in res.json()["detail"]

    manifest_file.write_text(json.dumps({"skus": 55, "routes": 55}), encoding="utf-8")
    ok = client.get("/api/publish/site-manifest")
    assert ok.status_code == 200
    assert ok.json()["manifest"]["skus"] == 55


def test_publish_state_rejects_bad_values():
    with pytest.raises(ValueError):
        publish_state.mark_item("tiktok", "x", "published")
    with pytest.raises(ValueError):
        publish_state.mark_item("threads", "x", "done")
