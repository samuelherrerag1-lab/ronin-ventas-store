"""Feeds de Threads/Pinterest.

El estado `published` de estos feeds es SOLO seguimiento local del operador: no
hay llamada a las plataformas, ni URL, ni timestamp devuelto por la red. El
toggle se conserva por compatibilidad, pero delega en `publish_state` y añade
`publication_note` + `published_to_network: false` en cada respuesta.
"""

from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.models.catalog_models import BaitWidgetConfig, ThreadsPostItem
from backend.services.publish_state import LOCAL_ONLY_NOTE, local_status, mark_item, status_map
from backend.services.social_feed_seed import (
    MUTATION_NOTE,
    get_last_load_error,
    load_or_init_feeds,
    mutate_thread_hook,
    next_thread_id,
    save_feeds,
)

router = APIRouter(prefix="/api/feeds", tags=["feeds"])


class CreateBaitPostRequest(BaseModel):
    headline_metric: str = Field(min_length=1, max_length=80)
    sub_metric: str = Field(default="", max_length=140)
    notifications: list[str] = Field(default_factory=list, max_length=8)
    widget_type: str = "ios_lockscreen"
    post_text: str = Field(min_length=1, max_length=4000)
    target_sku_id: str = Field(default="E01", max_length=10)


def _tracked(platform: str, raw: Dict[str, Any], statuses: Dict[str, str]) -> Dict[str, Any]:
    item_id = raw.get("post_id") if platform == "threads" else raw.get("pin_id")
    payload = dict(raw)
    payload["status"] = statuses.get(str(item_id), "queued")
    payload["status_source"] = "local_tracking"
    payload["published_to_network"] = False
    payload["publication_note"] = LOCAL_ONLY_NOTE
    return payload


def _toggle(platform: str, feeds: Dict[str, list], item_id: str) -> Dict[str, Any]:
    current = local_status(platform, item_id)
    target = "queued" if current == "published" else "published"
    result = mark_item(platform, item_id, target)
    source = feeds["threads"] if platform == "threads" else feeds["pinterest"]
    raw = next(
        (
            item.model_dump()
            for item in source
            if (item.post_id if platform == "threads" else item.pin_id) == item_id
        ),
        None,
    )
    if raw is None:
        raise HTTPException(status_code=404, detail=f"Ítem {item_id} no encontrado")
    return {**_tracked(platform, raw, status_map(platform)), "detail": result["note"]}


@router.get("")
def get_all_feeds(include_benchmarks: bool = True):
    feeds = load_or_init_feeds()
    pins = feeds["pinterest"]
    if not include_benchmarks:
        pins = [pin for pin in pins if not pin.is_competitor_benchmark]
    return {
        "threads": [_tracked("threads", post.model_dump(), status_map("threads")) for post in feeds["threads"]],
        "pinterest": [_tracked("pinterest", pin.model_dump(), status_map("pinterest")) for pin in pins],
        "status_source": "local_tracking",
        "published_to_network": False,
        "publication_note": LOCAL_ONLY_NOTE,
        "load_warning": get_last_load_error(),
    }


@router.post("/threads/{post_id}/mutate-hook")
def api_mutate_thread_hook(post_id: str):
    feeds = load_or_init_feeds()
    for idx, post in enumerate(feeds["threads"]):
        if post.post_id == post_id:
            mutated = mutate_thread_hook(post)
            feeds["threads"][idx] = mutated
            save_feeds(feeds["threads"], feeds["pinterest"])
            payload = _tracked("threads", mutated.model_dump(), status_map("threads"))
            payload.update(
                {
                    "engine": "template_variant",
                    "ai_used": False,
                    "mutation_note": MUTATION_NOTE,
                }
            )
            return payload
    raise HTTPException(status_code=404, detail=f"Post {post_id} no encontrado")


@router.post("/threads/{post_id}/toggle-status")
def api_toggle_thread_status(post_id: str):
    return _toggle("threads", load_or_init_feeds(), post_id)


@router.post("/pinterest/{pin_id}/toggle-status")
def api_toggle_pin_status(pin_id: str):
    feeds = load_or_init_feeds()
    pin = next((item for item in feeds["pinterest"] if item.pin_id == pin_id), None)
    if pin is None or pin.is_competitor_benchmark:
        raise HTTPException(status_code=404, detail=f"Pin propio {pin_id} no encontrado")
    return _toggle("pinterest", feeds, pin_id)


@router.post("/threads/from-bait")
def api_create_thread_from_bait(req: CreateBaitPostRequest):
    feeds = load_or_init_feeds()
    new_post = ThreadsPostItem(
        post_id=next_thread_id(feeds["threads"]),
        strategy_lane="via_a_captura_anzuelo",
        format="image_bait",
        hook_pattern="Custom Bait Studio Injection",
        body_slides=[req.post_text],
        suggested_self_replies=[
            "El enlace al sistema exacto está en mi perfil antes de que lo cierre.",
            "¿Cuántos siguen creyendo que esto requiere mostrar la cara?",
        ],
        target_sku_id=req.target_sku_id,
        topic_tag="Negocios Digitales",
        bait_widget=BaitWidgetConfig(
            widget_type=req.widget_type,  # type: ignore[arg-type]
            headline_metric=req.headline_metric,
            sub_metric=req.sub_metric,
            notifications=req.notifications,
            timestamp_label="03:18 AM",
        ),
    )
    feeds["threads"].insert(0, new_post)
    save_feeds(feeds["threads"], feeds["pinterest"])
    return _tracked("threads", new_post.model_dump(), status_map("threads"))
