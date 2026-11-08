"""Persistencia atómica de los jobs de publicación y su evidencia.

Cada job es autocontenido en ``data/publish_jobs/<job_id>.json``: petición,
pasos, piezas, URLs reales, errores literales y screenshots. El estado se
escribe con ``json_store.write_json_atomic`` para que una interrupción no deje
un JSON a medias.
"""

import datetime
import re
import secrets
from typing import Any, Dict, List, Optional

from backend.services import social_config as cfg
from backend.services.json_store import read_json, write_json_atomic

TERMINAL_STATUSES = ("completed", "partial", "failed")
OK_PIECE_STATUSES = ("published", "dry_run_ok")


def new_job_id() -> str:
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"job_{stamp}_{secrets.token_hex(3)}"


def job_path(job_id: str) -> Any:
    if not re.match(cfg.JOB_ID_RE, job_id or ""):
        raise cfg.SocialError(f"job_id inválido: {job_id!r}")
    return cfg.SOCIAL_DIR / f"{job_id}.json"


def save_job(job: Dict[str, Any]) -> Dict[str, Any]:
    cfg.ensure_dirs()
    write_json_atomic(job_path(job["job_id"]), job)
    return job


def load_job(job_id: str) -> Optional[Dict[str, Any]]:
    try:
        path = job_path(job_id)
    except cfg.SocialError:
        return None
    data, error = read_json(path)
    if error or not isinstance(data, dict):
        return None
    return data


def list_jobs(limit: int = 20) -> List[Dict[str, Any]]:
    cfg.ensure_dirs()
    files = sorted(cfg.SOCIAL_DIR.glob("job_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    jobs: List[Dict[str, Any]] = []
    for path in files[: max(1, limit)]:
        data, error = read_json(path)
        if not error and isinstance(data, dict):
            jobs.append(data)
    return jobs


def create_job(platform: str, pieces: List[Dict[str, Any]], dry_run: bool, request_info: Dict[str, Any]) -> Dict[str, Any]:
    now = cfg.now_iso()
    job: Dict[str, Any] = {
        "job_id": new_job_id(),
        "platform": platform,
        "dry_run": bool(dry_run),
        "status": "queued",
        "created_at": now,
        "started_at": None,
        "finished_at": None,
        "request": request_info,
        "session": None,
        "error": None,
        "steps": [],
        "screenshots": [],
        "progress": {"total": len(pieces), "done": 0, "ok": 0, "failed": 0},
        "pieces": [],
    }
    for piece in pieces:
        job["pieces"].append(
            {
                "id": piece["id"],
                "sku_id": piece.get("sku_id"),
                "target_route": piece.get("target_route"),
                "text_preview": (piece.get("text") or "")[:160],
                "status": "queued",
                "post_url": None,
                "screenshot": None,
                "error": None,
                "notes": piece.get("notes", []),
                "self_replies_scheduled": 0,
                "timestamp": None,
            }
        )
    save_job(job)
    return job


def add_step(job: Dict[str, Any], name: str, status: str, detail: str = "") -> None:
    job.setdefault("steps", []).append(
        {
            "at": cfg.now_iso(),
            "name": name,
            "status": status,
            "detail": detail[:2000],
        }
    )


def piece(job: Dict[str, Any], item_id: str) -> Optional[Dict[str, Any]]:
    for entry in job.get("pieces", []):
        if entry.get("id") == item_id:
            return entry
    return None


def update_piece(job: Dict[str, Any], item_id: str, **fields: Any) -> Optional[Dict[str, Any]]:
    entry = piece(job, item_id)
    if entry is None:
        return None
    entry.update(fields)
    entry["timestamp"] = fields.get("timestamp") or cfg.now_iso()
    return entry


def add_screenshot(job: Dict[str, Any], relative: Optional[str]) -> None:
    if relative and relative not in job.setdefault("screenshots", []):
        job["screenshots"].append(relative)


def recompute_progress(job: Dict[str, Any]) -> Dict[str, Any]:
    pieces = job.get("pieces", [])
    done = sum(1 for entry in pieces if entry.get("status") not in ("queued", "running"))
    ok = sum(1 for entry in pieces if entry.get("status") in OK_PIECE_STATUSES)
    failed = sum(1 for entry in pieces if entry.get("status") == "failed")
    job["progress"] = {"total": len(pieces), "done": done, "ok": ok, "failed": failed}
    return job["progress"]


def finalize(job: Dict[str, Any], error: Optional[str] = None) -> Dict[str, Any]:
    recompute_progress(job)
    progress = job["progress"]
    if error:
        job["status"] = "failed"
        job["error"] = error
    elif progress["total"] > 0 and progress["ok"] == progress["total"]:
        job["status"] = "completed"
    elif progress["ok"] > 0:
        job["status"] = "partial"
        job["error"] = f"{progress['failed']} pieza(s) fallaron; {progress['ok']} correctas."
    else:
        job["status"] = "failed"
        job["error"] = job.get("error") or "Ninguna pieza se pudo procesar."
    job["finished_at"] = cfg.now_iso()
    save_job(job)
    return job


def summary(job: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "job_id": job.get("job_id"),
        "platform": job.get("platform"),
        "dry_run": job.get("dry_run"),
        "status": job.get("status"),
        "created_at": job.get("created_at"),
        "finished_at": job.get("finished_at"),
        "progress": job.get("progress"),
        "error": job.get("error"),
        "published_urls": [entry.get("post_url") for entry in job.get("pieces", []) if entry.get("post_url")],
    }
