"""Cola programada: N piezas/día por plataforma y auto-respuestas vencidas.

El tick es idempotente por (fecha, franja). Modo seco por defecto: publicar de
verdad exige ``dry_run=false`` explícito. El hilo daemon arranca una sola vez.
"""

import datetime
import math
import os
import sys
import threading
from typing import Any, Callable, Dict, List, Optional

from backend.services import publish_state
from backend.services import social_config as cfg, social_jobs, social_pieces, social_replies
from backend.services import social_schedule_store as store
from backend.services.social_feed_seed import load_or_init_feeds

_SCHED_LOCK = threading.Lock()
_THREAD: Optional[threading.Thread] = None
_STOP = threading.Event()


def get_schedule() -> Dict[str, Any]:
    return store.get_schedule()


def update_schedule(payload: Dict[str, Any]) -> Dict[str, Any]:
    return store.update_schedule(payload)


def _interval_s() -> float:
    try:
        return max(30.0, float(os.environ.get("RONIN_SOCIAL_TICK_S", "120")))
    except ValueError:
        return 120.0


def _active_job_ids() -> set:
    active = set()
    for job in social_jobs.list_jobs(limit=30):
        if job.get("status") in ("queued", "running"):
            for entry in job.get("pieces", []):
                active.add(str(entry.get("id")))
    return active


def _next_ids(platform: str, count: int) -> List[str]:
    feeds = load_or_init_feeds()
    published = social_pieces.published_index().get(platform, {})
    active = _active_job_ids()
    if platform == "threads":
        candidates = [post.post_id for post in feeds["threads"] if post.status != "published"]
    else:
        candidates = [
            pin.pin_id for pin in feeds["pinterest"]
            if not pin.is_competitor_benchmark and pin.status != "published"
        ]
    selected: List[str] = []
    for item_id in candidates:
        if len(selected) >= count:
            break
        if item_id in published or item_id in active:
            continue
        if publish_state.local_status(platform, item_id) != "published":
            selected.append(item_id)
    return selected


def _process_replies(
    reply_runner: Optional[Callable[[Dict[str, Any]], Any]], limit: int = 4
) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    runner = reply_runner
    for entry in social_replies.due_replies()[:limit]:
        try:
            if runner is None:
                from backend.services import social_publisher

                runner = social_publisher.publish_reply
            runner(entry)
            social_replies.mark_result(entry, True)
            results.append({"reply_id": entry.get("reply_id"), "status": "published"})
        except Exception as exc:  # noqa: BLE001 - se guarda el error literal
            detail = f"{type(exc).__name__}: {exc}"
            social_replies.mark_result(entry, False, detail)
            results.append({"reply_id": entry.get("reply_id"), "status": "failed", "error": detail})
    return results


def _count_for(config: Dict[str, Any], platform: str, today: str) -> int:
    runs = store.runs_today(config, today)
    return sum(1 for run in runs if run.get("platform") == platform and run.get("status") == "started")


def tick(
    now: Optional[datetime.datetime] = None,
    runner: Optional[Callable[..., Dict[str, Any]]] = None,
    reply_runner: Optional[Callable[[Dict[str, Any]], Any]] = None,
) -> Dict[str, Any]:
    """Ejecuta un tick del scheduler. Sin efectos si está desactivado."""
    config = store._load()
    reference = now or datetime.datetime.now()
    today = reference.date().isoformat()
    replies = _process_replies(reply_runner)
    summary: Dict[str, Any] = {
        "date": today,
        "slot": None,
        "enabled": bool(config.get("enabled")),
        "jobs": [],
        "replies": replies,
        "reason": None,
    }
    if not config.get("enabled"):
        summary["reason"] = "programación desactivada (enabled=false); no se lanzó nada."
        config["last_tick"] = cfg.now_iso()
        store._save(config)
        return summary
    slot = store.slot_now(reference, config)
    if slot is None:
        summary["reason"] = "ninguna franja de hoy ha vencido todavía."
        config["last_tick"] = cfg.now_iso()
        store._save(config)
        return summary
    summary["slot"] = slot
    already = [
        run
        for run in store.runs_today(config, today)
        if run.get("slot") == slot and run.get("status") in ("started", "no_pieces")
    ]
    if already:
        summary["reason"] = f"la franja {slot} de {today} ya se ejecutó; no se duplica."
        config["last_tick"] = cfg.now_iso()
        store._save(config)
        return summary

    if runner is None:
        from backend.services import social_publisher

        runner = social_publisher.create_and_start
    slots = max(1, len(config.get("times_local", [])))
    for platform, key in (("threads", "threads_per_day"), ("pinterest", "pinterest_per_day")):
        per_day = int(config.get(key, 0))
        done = _count_for(config, platform, today)
        if done >= per_day:
            continue
        want = min(per_day - done, max(1, math.ceil(per_day / slots)), 20)
        ids = _next_ids(platform, want)
        if not ids:
            config["runs"].append(
                {
                    "date": today,
                    "slot": slot,
                    "platform": platform,
                    "status": "no_pieces",
                    "job_id": None,
                    "at": cfg.now_iso(),
                }
            )
            continue
        try:
            job = runner(platform, ids, len(ids), bool(config.get("dry_run", True)))
            config["runs"].append(
                {
                    "date": today,
                    "slot": slot,
                    "platform": platform,
                    "status": "started",
                    "job_id": job.get("job_id"),
                    "dry_run": bool(config.get("dry_run", True)),
                    "at": cfg.now_iso(),
                }
            )
            summary["jobs"].append(
                {"platform": platform, "job_id": job.get("job_id"), "pieces": len(ids)}
            )
        except Exception as exc:  # noqa: BLE001 - el error queda en el estado
            detail = f"{type(exc).__name__}: {exc}"
            config["last_error"] = detail
            config["runs"].append(
                {
                    "date": today,
                    "slot": slot,
                    "platform": platform,
                    "status": "error",
                    "job_id": None,
                    "error": detail,
                    "at": cfg.now_iso(),
                }
            )
            summary.setdefault("errors", []).append(detail)
    config["last_tick"] = cfg.now_iso()
    store._save(config)
    return summary


def _loop() -> None:
    while not _STOP.is_set():
        try:
            tick()
        except Exception as exc:  # noqa: BLE001 - el hilo nunca debe morir en silencio
            try:
                config = store._load()
                config["last_error"] = f"tick falló: {type(exc).__name__}: {exc}"
                config["last_tick"] = cfg.now_iso()
                store._save(config)
            except Exception:
                pass
        _STOP.wait(_interval_s())


def start_scheduler() -> Dict[str, Any]:
    global _THREAD
    with _SCHED_LOCK:
        if _THREAD is not None and _THREAD.is_alive():
            return {"running": True, "started": False, "interval_s": _interval_s()}
        _STOP.clear()
        _THREAD = threading.Thread(target=_loop, daemon=True, name="ronin-social-scheduler")
        _THREAD.start()
    return {"running": True, "started": True, "interval_s": _interval_s()}


def stop_scheduler() -> None:
    _STOP.set()


def scheduler_status() -> Dict[str, Any]:
    config = get_schedule()
    return {
        "running": bool(_THREAD is not None and _THREAD.is_alive()),
        "interval_s": _interval_s(),
        "enabled": bool(config.get("enabled")),
        "dry_run": bool(config.get("dry_run", True)),
        "times_local": config.get("times_local", []),
        "next_slot": config.get("next_slot"),
        "last_tick": config.get("last_tick"),
        "last_error": config.get("last_error"),
        "pending_replies": config.get("pending_replies", 0),
    }


def ensure_scheduler() -> bool:
    """Arranca el hilo una vez, salvo en pytest o si el operador lo desactiva."""
    if os.environ.get("RONIN_SOCIAL_SCHEDULER", "1") == "0":
        return False
    if "pytest" in sys.modules:
        return False
    result = start_scheduler()
    return bool(result.get("running"))
