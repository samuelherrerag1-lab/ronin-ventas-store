"""Orquestador del publicador real: sesión, piezas, evidencia y honestidad.

Modo seco por defecto: navega, rellena y captura SIN pulsar Publicar. Con
``dry_run=False`` publica de verdad, espera confirmación, extrae la URL del
post/pin y guarda screenshot. Si no hay login el job falla con
``login_required`` y el paso exacto para resolverlo; nunca simula éxito.
"""

import threading
import time
from typing import Any, Callable, Dict, List, Optional

from backend.services import social_browser, social_config as cfg, social_detect, social_jobs
from backend.services import social_pieces, social_publishers, social_replies

LOGIN_INSTRUCTIONS = (
    "login_required: no hay sesión activa de {label}. Abre la ventana de login una vez "
    "con POST /api/social/login/{platform} (o el botón 'Abrir login' del panel), inicia "
    "sesión en Chrome y vuelve a lanzar el job. Evidencia medida: {evidence}"
)


def _save(job: Dict[str, Any]) -> None:
    social_jobs.save_job(job)


def _measure(page: Any, platform: str, job_id: str = "") -> Dict[str, Any]:
    state = dict(social_detect.detect_login(page, platform))
    block = social_detect.detect_block(page)
    state.update(
        {
            "checked_at": cfg.now_iso(),
            "screenshot": social_browser.capture(page, f"session_{platform}", job_id),
            "blocked": bool(block["blocked"]),
            "stale": False,
        }
    )
    if block["blocked"]:
        state.update({"logged_in": False, "status": "blocked", "evidence": block["evidence"]})
    social_browser.save_session(platform, state)
    return state


def _instructions(platform: str, state: Dict[str, Any]) -> str:
    return LOGIN_INSTRUCTIONS.format(
        label=cfg.PLATFORM_LABEL[platform],
        platform=platform,
        evidence=state.get("evidence") or "sin evidencia",
    )


def create_job(platform: str, ids: Optional[List[str]] = None, limit: int = 3, dry_run: bool = True) -> Dict[str, Any]:
    pieces = social_pieces.list_pieces(platform, limit=limit, ids=ids)
    if not pieces:
        raise cfg.SocialError(
            f"No hay piezas disponibles en {cfg.PLATFORM_LABEL[platform]} para los ids {ids or 'automáticos'}."
        )
    if platform == "pinterest":
        missing = [piece["id"] for piece in pieces if not piece.get("image_path")]
        if len(missing) == len(pieces):
            raise cfg.SocialError(
                "Pinterest exige imagen real y ninguna de las piezas seleccionadas tiene una en disco: "
                + ", ".join(missing)
            )
    job = social_jobs.create_job(
        platform,
        pieces,
        dry_run,
        {"ids": ids, "limit": limit, "dry_run": dry_run},
    )
    social_jobs.add_step(job, "job_creado", "ok", f"{len(pieces)} pieza(s) · dry_run={dry_run}")
    _save(job)
    return job


def start_job(job_id: str) -> None:
    thread = threading.Thread(target=_background, args=(job_id,), daemon=True, name=f"ronin-publish-{job_id}")
    thread.start()


def _background(job_id: str) -> None:
    try:
        execute_job(job_id)
    except Exception as exc:  # noqa: BLE001 - ninguna excepción deja el job colgado
        job = social_jobs.load_job(job_id)
        if job is not None:
            social_jobs.add_step(job, "error_no_controlado", "failed", f"{type(exc).__name__}: {exc}")
            social_jobs.finalize(job, error=f"Error no controlado: {type(exc).__name__}: {exc}")


def create_and_start(platform: str, ids: Optional[List[str]] = None, limit: int = 3, dry_run: bool = True) -> Dict[str, Any]:
    job = create_job(platform, ids=ids, limit=limit, dry_run=dry_run)
    start_job(job["job_id"])
    return job


def _pieces_for_job(job: Dict[str, Any]) -> List[Dict[str, Any]]:
    platform = job["platform"]
    ordered: List[Dict[str, Any]] = []
    for entry in job.get("pieces", []):
        piece = social_pieces.get_piece(platform, str(entry.get("id")))
        if piece is not None:
            ordered.append(piece)
    return ordered


def execute_job(
    job_id: str,
    session_factory: Optional[Callable[[str], Any]] = None,
    publisher_factory: Optional[Callable[[str, Any, str], Any]] = None,
    sleep_func: Callable[[float], None] = time.sleep,
) -> Dict[str, Any]:
    job = social_jobs.load_job(job_id)
    if job is None:
        raise cfg.SocialError(f"No existe el job {job_id}")
    if job.get("status") not in ("queued", "running"):
        return job

    platform = job["platform"]
    dry_run = bool(job.get("dry_run", True))
    job["status"] = "running"
    job["started_at"] = cfg.now_iso()
    social_jobs.add_step(
        job, "job_iniciado", "ok", f"modo={'seco (no publica)' if dry_run else 'PUBLICACION REAL'}"
    )
    _save(job)

    session_factory = session_factory or social_browser.platform_session
    publisher_factory = publisher_factory or social_publishers.build_publisher
    pieces = _pieces_for_job(job)

    try:
        with session_factory(platform) as page:
            state = _measure(page, platform, job_id)
            job["session"] = state
            social_jobs.add_step(job, "sesion_medida", state.get("status", "unknown"), state.get("evidence", ""))
            _save(job)
            if not state.get("logged_in"):
                social_jobs.finalize(job, error=_instructions(platform, state))
                return job
            if state.get("blocked"):
                social_jobs.finalize(job, error=f"bloqueado: {state.get('evidence')}")
                return job

            publisher = publisher_factory(platform, page, job_id)
            for index, piece in enumerate(pieces):
                if not dry_run and index > 0:
                    delay = cfg.piece_delay_s()
                    social_jobs.add_step(
                        job, "pausa_humana", "ok", f"{delay:.1f} s de espera entre publicaciones"
                    )
                    _save(job)
                    sleep_func(delay)
                social_jobs.update_piece(job, piece["id"], status="running")
                social_jobs.add_step(job, f"pieza_{piece['id']}", "running", f"preparando {platform}")
                _save(job)
                try:
                    fill_info = publisher.fill(piece)
                    fill_shot = social_browser.capture(page, f"{piece['id']}_relleno", job_id)
                    social_jobs.add_screenshot(job, fill_shot)
                    piece_notes = list(piece.get("notes", [])) + list(fill_info.get("notes") or [])
                    if dry_run:
                        social_jobs.update_piece(
                            job,
                            piece["id"],
                            status="dry_run_ok",
                            screenshot=fill_shot,
                            notes=piece_notes + ["Modo seco: se rellenó y capturó sin pulsar Publicar."],
                        )
                        social_jobs.add_step(
                            job, f"pieza_{piece['id']}", "dry_run_ok", "rellenado y capturado; NO publicado"
                        )
                    else:
                        result = publisher.publish()
                        post_shot = social_browser.capture(page, f"{piece['id']}_publicado", job_id)
                        social_jobs.add_screenshot(job, post_shot)
                        post_url = result.get("post_url")
                        status = "published" if post_url else "published_unverified"
                        social_jobs.update_piece(
                            job,
                            piece["id"],
                            status=status,
                            post_url=post_url,
                            screenshot=post_shot,
                            notes=piece_notes,
                        )
                        social_jobs.add_step(
                            job,
                            f"pieza_{piece['id']}",
                            status,
                            f"URL={post_url or 'no medida'} · confirmación={result.get('confirmation') or 'no medida'}",
                        )
                        if post_url:
                            social_pieces.mark_published(platform, piece["id"], post_url, job_id)
                        if platform == "threads" and post_url and piece.get("self_replies"):
                            replies = social_replies.enqueue_replies(post_url, piece["self_replies"])
                            social_jobs.update_piece(
                                job, piece["id"], self_replies_scheduled=len(replies)
                            )
                except cfg.SocialError as exc:
                    social_jobs.update_piece(job, piece["id"], status="failed", error=str(exc))
                    social_jobs.add_step(job, f"pieza_{piece['id']}", "failed", str(exc))
                except Exception as exc:  # noqa: BLE001 - error literal por pieza
                    reason = f"{type(exc).__name__}: {exc}"
                    social_jobs.update_piece(job, piece["id"], status="failed", error=reason)
                    social_jobs.add_step(job, f"pieza_{piece['id']}", "failed", reason)
                social_jobs.recompute_progress(job)
                _save(job)
    except cfg.SocialError as exc:
        social_jobs.add_step(job, "error_sesion", "failed", str(exc))
        social_jobs.finalize(job, error=str(exc))
        return job
    except Exception as exc:  # noqa: BLE001 - razón literal para el operador
        reason = f"Fallo del navegador persistente: {type(exc).__name__}: {exc}"
        social_jobs.add_step(job, "error_navegador", "failed", reason)
        social_jobs.finalize(job, error=reason)
        return job

    social_jobs.add_step(job, "job_finalizado", "ok", "se recalculó el estado final")
    social_jobs.finalize(job)
    return job


def publish_reply(entry: Dict[str, Any]) -> Dict[str, Any]:
    """Publica una auto-respuesta vencida en Threads (usada por el scheduler)."""
    with social_browser.platform_session("threads") as page:
        state = _measure(page, "threads", "replies")
        if not state.get("logged_in"):
            raise cfg.SocialError(_instructions("threads", state))
        publisher = social_publishers.build_publisher("threads", page, "replies")
        return publisher.reply(str(entry.get("post_url")), str(entry.get("text")))
