"""Customizations & Connectors Hub.

Los teardowns de competencia ya no están hardcodeados aquí: viven en
`data/competitor_notes.json` con fecha de revisión, fuente y estado de
verificación. Si el archivo no existe se devuelve una lista vacía honesta.
"""

import re
from typing import Any, Dict, List, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator

from backend.config import DATA_DIR
from backend.services.connect_jobs import get_job, masked_secrets, start_job, stop_job
from backend.services.connector_diagnostics import run_all_connector_tests, run_connector_test
from backend.services.connectors_hub import (
    get_finops_summary,
    list_connectors,
    list_skills_customizations,
    toggle_skill_customization,
)
from backend.services.json_store import read_json
from backend.services.playwright_bait_renderer import render_ios_bait_screenshot_png
from backend.services.vault_inspector import inspect_chrome_vault
from backend.services.vertex_image_service import generate_nano_banana_image
from backend.security_middleware import image_job_guard

router = APIRouter(prefix="/api/customizations", tags=["customizations"])

COMPETITOR_NOTES_PATH = DATA_DIR / "competitor_notes.json"
VALID_CONNECTOR_ID = re.compile(r"[a-z0-9_]{1,32}")

BROWSER_PROVIDERS = {
    "google_master": ("google", "https://accounts.google.com/"),
    "threads": ("threads", "https://www.threads.net/login"),
    "pinterest": ("pinterest", "https://www.pinterest.com/login/"),
    "gumroad": ("gumroad", "https://gumroad.com/login"),
    "hotmart": ("hotmart", "https://app-vlc.hotmart.com/login"),
}


class ConnectRequest(BaseModel):
    launch_browser: bool = True


class ToggleSkillRequest(BaseModel):
    enabled: bool


class VertexGenerateRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=2000)
    aspect_ratio: Literal["1:1", "2:3", "3:2", "3:4", "4:3", "9:16", "16:9"] = "3:4"


class RenderIosPngRequest(BaseModel):
    headline_metric: str = Field(default="$418.50 USD", max_length=80)
    sub_metric: str = Field(default="9 notificaciones durante la noche", max_length=140)
    notifications: List[str] = Field(min_length=1, max_length=6)
    timestamp_label: str = Field(default="07:12", max_length=20)
    date_label: str = Field(default="domingo, 2 de noviembre", max_length=40)
    wallpaper_filename: str = Field(default="ios17_editorial_dark_wallpaper.png", max_length=120)
    widget_type: str = Field(default="ios_lockscreen", max_length=40)

    @field_validator("notifications")
    @classmethod
    def _limit_notifications(cls, value: List[str]) -> List[str]:
        for note in value:
            if len(note) > 160:
                raise ValueError("Cada notificación debe tener 160 caracteres o menos")
        return value

    @field_validator("wallpaper_filename")
    @classmethod
    def _plain_filename(cls, value: str) -> str:
        if "/" in value or "\\" in value or ".." in value:
            raise ValueError("wallpaper_filename debe ser un nombre de archivo simple (sin rutas)")
        return value


def _load_competitor_notes() -> Dict[str, Any]:
    data, error = read_json(COMPETITOR_NOTES_PATH)
    if error is not None or not isinstance(data, dict):
        return {
            "notes": [],
            "reviewed_at": None,
            "source": f"sin archivo legible en {COMPETITOR_NOTES_PATH.name}",
        }
    return data


@router.get("")
def get_customizations_overview():
    connectors = [card.model_dump() for card in list_connectors()]
    skills = [skill.model_dump() for skill in list_skills_customizations()]
    notes = _load_competitor_notes()
    return {
        "connectors": connectors,
        "skills": skills,
        "finops": get_finops_summary(),
        "stealth_Diagnostic": inspect_chrome_vault(),
        "competitor_teardowns": notes.get("notes", []),
        "competitor_teardowns_reviewed_at": notes.get("reviewed_at"),
        "competitor_teardowns_source": notes.get("source"),
    }


@router.post("/connect/{connector_id}")
def connect_provider(connector_id: str, req: ConnectRequest):
    if not req.launch_browser:
        return {
            "connector_id": connector_id,
            "status": "not_requested",
            "verification": "pending",
            "browser_launched": False,
            "detail": "No se solicitó abrir el navegador.",
        }

    mapping = BROWSER_PROVIDERS.get(connector_id)
    if mapping is None:
        return {
            "connector_id": connector_id,
            "status": "manual_required",
            "verification": "pending",
            "browser_launched": False,
            "detail": "Este conector no se abre con navegador. Usa el comando indicado en Capacidades.",
        }

    provider, login_url = mapping
    job = start_job(connector_id, login_url, provider)
    return {**job, "verification": "pending", "login_url": login_url}


@router.get("/connect/{connector_id}/status")
def connect_status(connector_id: str):
    if not VALID_CONNECTOR_ID.fullmatch(connector_id):
        raise HTTPException(
            status_code=422,
            detail=f"Identificador de conector inválido: {connector_id}",
        )
    job = get_job(connector_id)
    if job is None:
        job = {
            "connector_id": connector_id,
            "status": "idle",
            "step": "Sin intentos de conexión",
            "detail": None,
        }
    return {"job": job, "secrets": masked_secrets()}


@router.post("/connect/{connector_id}/stop")
def connect_stop(connector_id: str):
    try:
        return stop_job(connector_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/secrets")
def secrets_summary():
    return masked_secrets()


@router.post("/test/{connector_id}")
def test_connector_endpoint(connector_id: str):
    return run_connector_test(connector_id).model_dump()


@router.post("/test-all")
def test_all_connectors_endpoint():
    return run_all_connector_tests().model_dump()


@router.post("/skills/{skill_id}/toggle")
def toggle_skill(skill_id: str, req: ToggleSkillRequest):
    try:
        updated = toggle_skill_customization(skill_id, req.enabled)
        return updated.model_dump()
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/vertex-generate")
def api_generate_vertex_image(req: VertexGenerateRequest):
    try:
        with image_job_guard():
            return generate_nano_banana_image(req.prompt, req.aspect_ratio)
    except Exception as exc:  # noqa: BLE001 - se devuelve la razón literal
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/render-ios-png")
def api_render_ios_png(req: RenderIosPngRequest):
    try:
        return render_ios_bait_screenshot_png(
            req.headline_metric,
            req.sub_metric,
            req.notifications,
            req.timestamp_label,
            req.date_label,
            req.wallpaper_filename,
            req.widget_type,
        )
    except Exception as exc:  # noqa: BLE001 - se devuelve la razón literal
        raise HTTPException(status_code=500, detail=str(exc)) from exc
