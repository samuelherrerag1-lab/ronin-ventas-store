"""API del publicador social real: sesión, login, jobs, cola y programación.

El router NO se monta aquí: el Lead lo incluye en ``backend/main.py`` con
``from backend.routers.api_social_publish import router as social_publish_router``
y ``app.include_router(social_publish_router)``.

Regla de honestidad: ningún endpoint devuelve ``published`` sin URL medida por
la plataforma. ``dry_run`` es True por defecto en todos los jobs.
"""

import datetime
from typing import Any, Dict, List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from backend.services import publish_scheduler, social_browser, social_config as cfg
from backend.services import social_jobs, social_login_flow, social_login_keeper, social_pieces, social_publisher

router = APIRouter(prefix="/api/social", tags=["social-publish"])

Platform = Literal["threads", "pinterest"]


class PublishRequest(BaseModel):
    platform: Platform
    ids: Optional[List[str]] = Field(default=None, max_length=20)
    limit: int = Field(default=3, ge=1, le=20)
    dry_run: bool = True


class ScheduleRequest(BaseModel):
    enabled: Optional[bool] = None
    dry_run: Optional[bool] = None
    threads_per_day: Optional[int] = Field(default=None, ge=0, le=20)
    pinterest_per_day: Optional[int] = Field(default=None, ge=0, le=20)
    times_local: Optional[List[str]] = Field(default=None, max_length=6)


class LoginAllRequest(BaseModel):
    timeout_s: float = Field(default=3600.0, ge=60, le=7200)


def _ensure_scheduler() -> None:
    publish_scheduler.ensure_scheduler()


def _guard_profile() -> None:
    try:
        cfg.assert_profile_available()
    except cfg.SocialError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


def _session_with_age(platform: str) -> Dict[str, Any]:
    state = social_browser.get_session(platform)
    checked_at = state.get("checked_at")
    age: Optional[float] = None
    if checked_at:
        try:
            moment = datetime.datetime.fromisoformat(str(checked_at))
            age = round((datetime.datetime.now(datetime.timezone.utc) - moment).total_seconds())
        except ValueError:
            age = None
    state["age_seconds"] = age
    state["stale"] = age is None or age > 6 * 3600
    return state


@router.get("/status")
def social_status() -> Dict[str, Any]:
    jobs = social_jobs.list_jobs(limit=20)
    running = [social_jobs.summary(job) for job in jobs if job.get("status") in ("queued", "running")]
    last = social_jobs.summary(jobs[0]) if jobs else None
    return {
        "profile": {
            "path": str(cfg.profile_dir()),
            "channel": cfg.chrome_channel(),
            "is_vault": cfg.using_vault(),
            "in_use_by": cfg.vault_lock_owner() if cfg.using_vault() else None,
            "browser_busy": social_browser.browser_busy(),
        },
        "sessions": {platform: _session_with_age(platform) for platform in cfg.PLATFORMS},
        "login": social_login_keeper.login_keeper.status(),
        "login_flow": social_login_flow.multi_login_flow.status(),
        "scheduler": publish_scheduler.scheduler_status(),
        "jobs": {"total": len(jobs), "running": running, "last": last},
        "notes": [
            "El estado de sesión solo cambia con una medición real (login o verificar).",
            "Los jobs en modo seco rellenan y capturan, nunca pulsan Publicar.",
        ],
    }


@router.post("/login/all")
def social_login_all(payload: Optional[LoginAllRequest] = None) -> Dict[str, Any]:
    """Una sola ventana con una pestaña por plataforma y login humano."""
    _guard_profile()
    timeout_s = payload.timeout_s if payload else 3600.0
    try:
        result = social_login_flow.multi_login_flow.start(timeout_s=timeout_s)
    except cfg.SocialError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return {
        **result,
        "note": (
            "Ventana persistente con una pestaña de Threads y otra de Pinterest. "
            "El login se detecta solo y se guarda medido; no cierres la ventana."
        ),
    }


@router.post("/login/{platform}")
def social_login(platform: Platform) -> Dict[str, Any]:
    _guard_profile()
    try:
        result = social_login_keeper.login_keeper.start(platform)
    except cfg.SocialError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return {
        **result,
        "note": (
            "Se abrió una ventana de Chrome persistente. Inicia sesión ahí: el sistema "
            "detecta el login solo y lo guarda como estado medido."
        ),
    }


@router.get("/session/{platform}")
def social_session(platform: Platform, verify: bool = Query(False)) -> Dict[str, Any]:
    if verify:
        _guard_profile()
        return {"platform": platform, "state": social_browser.verify_session(platform), "measured": True}
    return {"platform": platform, "state": _session_with_age(platform), "measured": False}


@router.post("/session/{platform}/verify")
def social_session_verify(platform: Platform) -> Dict[str, Any]:
    _guard_profile()
    state = social_browser.verify_session(platform)
    return {"platform": platform, "state": state, "measured": True}


@router.get("/queue")
def social_queue(
    platform: Platform = Query(...),
    limit: int = Query(50, ge=1, le=200),
) -> Dict[str, Any]:
    pieces = social_pieces.list_pieces(platform, limit=limit)
    published = social_pieces.published_index().get(platform, {})
    items = [
        {
            "id": piece["id"],
            "sku_id": piece["sku_id"],
            "status": piece["status"],
            "text": piece["text"],
            "title": piece.get("title"),
            "description": piece.get("description"),
            "board": piece.get("board"),
            "target_route": piece.get("target_route"),
            "image_url": piece.get("image_url"),
            "has_image": bool(piece.get("image_path")),
            "published_url": (published.get(piece["id"]) or {}).get("post_url"),
            "notes": piece.get("notes", []),
        }
        for piece in pieces
    ]
    return {"platform": platform, "count": len(items), "items": items}


@router.post("/publish")
def social_publish(payload: PublishRequest) -> Dict[str, Any]:
    _guard_profile()
    try:
        job = social_publisher.create_and_start(
            payload.platform,
            ids=payload.ids,
            limit=payload.limit,
            dry_run=payload.dry_run,
        )
    except cfg.SocialError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {
        "job_id": job["job_id"],
        "platform": job["platform"],
        "dry_run": job["dry_run"],
        "status": job["status"],
        "pieces": [entry["id"] for entry in job["pieces"]],
        "note": (
            "Modo seco: se navega, rellena y captura sin publicar."
            if job["dry_run"]
            else "Publicación real: el job pulsará Publicar y solo marcará 'published' si mide la URL."
        ),
        "job": social_jobs.summary(job),
    }


@router.get("/jobs")
def social_jobs_list(limit: int = Query(20, ge=1, le=100)) -> Dict[str, Any]:
    jobs = social_jobs.list_jobs(limit=limit)
    return {"count": len(jobs), "jobs": [social_jobs.summary(job) for job in jobs]}


@router.get("/jobs/{job_id}")
def social_job_detail(job_id: str) -> Dict[str, Any]:
    job = social_jobs.load_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"No existe el job {job_id}")
    return {"job": job}


@router.get("/jobs/{job_id}/evidence/{filename}")
def social_evidence(job_id: str, filename: str) -> FileResponse:
    if social_jobs.load_job(job_id) is None:
        raise HTTPException(status_code=404, detail=f"No existe el job {job_id}")
    root = cfg.EVIDENCE_DIR.resolve()
    candidate = (cfg.EVIDENCE_DIR / filename).resolve()
    if root not in candidate.parents or not candidate.is_file():
        raise HTTPException(status_code=404, detail="Evidencia no encontrada")
    return FileResponse(str(candidate))


@router.get("/schedule")
def social_get_schedule() -> Dict[str, Any]:
    return {"schedule": publish_scheduler.get_schedule()}


@router.post("/schedule")
def social_set_schedule(payload: ScheduleRequest) -> Dict[str, Any]:
    try:
        config = publish_scheduler.update_schedule(payload.model_dump(exclude_none=True))
    except cfg.SocialError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if config.get("enabled"):
        publish_scheduler.ensure_scheduler()
    return {"schedule": config}


@router.post("/schedule/tick")
def social_schedule_tick() -> Dict[str, Any]:
    return {"result": publish_scheduler.tick()}


@router.post("/scheduler/start")
def social_scheduler_start() -> Dict[str, Any]:
    return {"result": publish_scheduler.start_scheduler(), "status": publish_scheduler.scheduler_status()}


router.dependencies.append(Depends(_ensure_scheduler))
