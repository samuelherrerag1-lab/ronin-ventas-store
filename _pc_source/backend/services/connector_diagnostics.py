import concurrent.futures
from typing import Any, Dict
from backend.config import CUSTOMIZATIONS_JSON_PATH, ensure_dirs
from backend.models.diagnostic_models import ConnectorTestResult, TestAllResponse
from backend.services.json_store import lock_for, quarantine_corrupt, read_json, write_json_atomic
from backend.services.probe_runners import (
    DOMAIN_TARGETS,
    now_iso,
    test_chrome_vault,
    test_lan_server,
    test_opencode_v2,
    test_social_domain,
    test_vertex_ai,
)
from backend.services.probe_store import test_github_auth, test_gumroad_api

CORE_CONNECTOR_IDS = [
    "google_master",
    "threads",
    "pinterest",
    "gumroad",
    "hotmart",
    "vertex_ai",
    "opencode_v2",
    "github_pages",
]


def run_connector_test(connector_id: str) -> ConnectorTestResult:
    cid = connector_id.lower()
    if cid == "vertex_ai":
        res = test_vertex_ai()
    elif cid in ("opencode_v2", "opencode", "deepseek"):
        res = test_opencode_v2()
    elif cid == "gumroad":
        res = test_gumroad_api()
    elif cid in ("github_pages", "github"):
        res = test_github_auth()
    elif cid in ("google_master", "chrome_persistent", "chrome"):
        res = test_chrome_vault()
    elif cid == "lan_server":
        res = test_lan_server()
    elif cid in DOMAIN_TARGETS:
        name, url = DOMAIN_TARGETS[cid]
        res = test_social_domain(cid, name, url)
    else:
        res = ConnectorTestResult(
            connector_id=connector_id,
            name=connector_id,
            status="FALLA",
            latency_ms=0.0,
            detail=f"Conector no registrado en el sistema: {connector_id}",
            checked_at=now_iso(),
            error_literal=f"Conector desconocido: {connector_id}",
        )
    _save_single_test_result(res)
    return res


def run_all_connector_tests() -> TestAllResponse:
    results: Dict[str, ConnectorTestResult] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        future_map = {executor.submit(run_connector_test, cid): cid for cid in CORE_CONNECTOR_IDS}
        for future in concurrent.futures.as_completed(future_map):
            cid = future_map[future]
            try:
                results[cid] = future.result()
            except Exception as exc:
                results[cid] = ConnectorTestResult(
                    connector_id=cid,
                    name=cid,
                    status="FALLA",
                    detail=f"Excepción en test worker: {str(exc)}",
                    checked_at=now_iso(),
                    error_literal=str(exc),
                )
    connected = sum(1 for r in results.values() if r.status == "CONECTADO")
    falla = sum(1 for r in results.values() if r.status == "FALLA")
    sin_ver = sum(1 for r in results.values() if r.status == "SIN_VERIFICAR")
    tested_at = now_iso()
    _save_all_results(results, tested_at)
    return TestAllResponse(
        total=len(results),
        connected_count=connected,
        falla_count=falla,
        sin_verificar_count=sin_ver,
        results=results,
        tested_at=tested_at,
    )


def _load_diagnostic_state() -> Dict[str, Any]:
    ensure_dirs()
    data, error = read_json(CUSTOMIZATIONS_JSON_PATH)
    if error is not None:
        quarantine_corrupt(CUSTOMIZATIONS_JSON_PATH)
        return {}
    return data if isinstance(data, dict) else {}


def _save_single_test_result(result: ConnectorTestResult) -> None:
    # Los tests corren en threads: sin lock dos resultados simultáneos se
    # pisaban y se perdían conectores del panel.
    with lock_for(CUSTOMIZATIONS_JSON_PATH):
        state = _load_diagnostic_state()
        diag = state.get("last_diagnostic_results", {})
        diag[result.connector_id] = result.model_dump()
        state["last_diagnostic_results"] = diag
        state["last_diagnostic_at"] = result.checked_at
        write_json_atomic(CUSTOMIZATIONS_JSON_PATH, state)


def _save_all_results(results: Dict[str, ConnectorTestResult], tested_at: str) -> None:
    with lock_for(CUSTOMIZATIONS_JSON_PATH):
        state = _load_diagnostic_state()
        state["last_diagnostic_results"] = {key: value.model_dump() for key, value in results.items()}
        state["last_diagnostic_at"] = tested_at
        write_json_atomic(CUSTOMIZATIONS_JSON_PATH, state)


def _is_trustworthy(connector_id: str, entry: Dict[str, Any]) -> bool:
    """Descarta resultados sembrados o incompletos.

    Un resultado solo vale si fue producido por una sonda real: su id coincide
    con la clave, no es el marcador `mock_id` y trae un detalle verificable.
    """
    if not isinstance(entry, dict):
        return False
    if entry.get("connector_id") != connector_id:
        return False
    if entry.get("connector_id") in ("mock_id", "mock", "test"):
        return False
    if str(entry.get("name", "")).strip().lower() == "mock connector":
        return False
    detail = str(entry.get("detail") or "").strip()
    if detail in ("", "OK"):
        return False
    return entry.get("status") in ("CONECTADO", "FALLA", "SIN_VERIFICAR")


def get_last_diagnostic_results() -> Dict[str, Dict[str, Any]]:
    state = _load_diagnostic_state()
    raw = state.get("last_diagnostic_results", {}) or {}
    return {cid: entry for cid, entry in raw.items() if _is_trustworthy(cid, entry)}
