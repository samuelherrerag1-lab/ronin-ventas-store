import json
import subprocess
from typing import Any, Dict, List

from backend.config import (
    CHROME_VAULT_DIR,
    CUSTOMIZATIONS_JSON_PATH,
    SIBLING_FINOPS_PATH,
    VERTEX_PROJECT_ID,
    ensure_dirs,
    find_chrome_executable,
)
from backend.models.catalog_models import ConnectorCard, SkillCustomizationItem
from backend.services.connector_diagnostics import get_last_diagnostic_results
from backend.services.connectors_catalog import DEFAULT_CONNECTORS
from backend.services.json_store import lock_for, quarantine_corrupt, read_json, write_json_atomic
from backend.services.skills_catalog import DEFAULT_SKILLS
from backend.services.skills_loader import load_all_skills


def _load_saved_state() -> Dict[str, Any]:
    ensure_dirs()
    data, error = read_json(CUSTOMIZATIONS_JSON_PATH)
    if error is not None:
        quarantine_corrupt(CUSTOMIZATIONS_JSON_PATH)
        return {"connected_ids": [], "skill_toggles": {}}
    return data if isinstance(data, dict) else {"connected_ids": [], "skill_toggles": {}}


def _save_state(state: Dict[str, Any]) -> None:
    ensure_dirs()
    write_json_atomic(CUSTOMIZATIONS_JSON_PATH, state)


def get_finops_summary() -> Dict[str, Any]:
    local_ledger = CUSTOMIZATIONS_JSON_PATH.parent / "finops-ledger.json"
    for source, path in (("local", local_ledger), ("sibling", SIBLING_FINOPS_PATH)):
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return {
                "project_id": data.get("project_id", VERTEX_PROJECT_ID),
                "total_spent_usd": data.get("total_spent_usd", 0.0),
                "circuit_breaker_limit_usd": data.get("circuit_breaker_limit_usd", 50.0),
                "remaining_trial_balance_usd": data.get("remaining_trial_balance_usd"),
                "ledger_found": True,
                "ledger_source": source,
                "ledger_path": str(path),
            }
        except Exception:
            continue
    return {
        "project_id": VERTEX_PROJECT_ID,
        "total_spent_usd": 0.0,
        "circuit_breaker_limit_usd": 50.0,
        "remaining_trial_balance_usd": None,
        "ledger_found": False,
        "ledger_source": "defaults",
        "ledger_path": None,
    }


def list_connectors() -> List[ConnectorCard]:
    diag_results = get_last_diagnostic_results()
    cards: List[ConnectorCard] = []

    for item in DEFAULT_CONNECTORS:
        cid = item["connector_id"]
        res = diag_results.get(cid)
        if res:
            status = res.get("status", "SIN_VERIFICAR")
            latency_ms = res.get("latency_ms")
            detail = res.get("detail")
            checked_at = res.get("checked_at")
        else:
            status = "SIN_VERIFICAR"
            latency_ms = None
            detail = "Sin verificar (ejecuta diagnóstico para prueba real)"
            checked_at = None

        cards.append(
            ConnectorCard(
                **item,
                status=status,
                latency_ms=latency_ms,
                detail=detail,
                checked_at=checked_at,
            )
        )
    return cards


def launch_connector_login(connector_id: str, launch_browser: bool = True) -> Dict[str, Any]:
    """Abre la ventana de login. NUNCA declara la cuenta como conectada.

    El único camino a `CONECTADO` es `run_connector_test`, que exige evidencia.
    """
    target = next((c for c in DEFAULT_CONNECTORS if c["connector_id"] == connector_id), None)
    if not target:
        raise ValueError(f"Conector desconocido: {connector_id}")

    ensure_dirs()
    chrome_exe = find_chrome_executable()
    base = {
        "connector_id": connector_id,
        "login_url": target["login_url"],
        "chrome_vault_path": str(CHROME_VAULT_DIR),
        "browser_launched": False,
        "verification": "pending",
        "instruction": "Inicia sesión en la ventana de Chrome y luego pulsa 'Test Conexión'.",
    }

    if not launch_browser:
        return {**base, "status": "not_requested", "detail": "No se solicitó abrir el navegador."}

    if chrome_exe is None:
        return {
            **base,
            "status": "chrome_not_found",
            "detail": "No se encontró chrome.exe en las rutas del sistema.",
        }

    cmd = [
        str(chrome_exe),
        f"--user-data-dir={CHROME_VAULT_DIR}",
        "--no-first-run",
        "--no-default-browser-check",
        target["login_url"],
    ]
    try:
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as exc:  # noqa: BLE001 - devolvemos la razón literal
        return {
            **base,
            "status": "launch_failed",
            "detail": f"{type(exc).__name__}: {exc}",
        }

    return {
        **base,
        "status": "browser_opened",
        "browser_launched": True,
        "detail": "Chrome abierto con el perfil persistente. La sesión aún no está verificada.",
    }


def list_skills_customizations() -> List[SkillCustomizationItem]:
    state = _load_saved_state()
    toggles = state.get("skill_toggles", {})
    return load_all_skills(DEFAULT_SKILLS, toggles)


def toggle_skill_customization(skill_id: str, enabled: bool) -> SkillCustomizationItem:
    with lock_for(CUSTOMIZATIONS_JSON_PATH):
        state = _load_saved_state()
        toggles = state.get("skill_toggles", {})
        toggles[skill_id] = enabled
        state["skill_toggles"] = toggles
        _save_state(state)
    updated = [s for s in list_skills_customizations() if s.skill_id == skill_id]
    if not updated:
        raise ValueError(f"Skill no encontrada: {skill_id}")
    return updated[0]