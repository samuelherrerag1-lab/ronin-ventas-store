"""Captura real de leads para los lead magnets.

Antes, el formulario de L01 validaba el correo y llamaba a `window.print()`:
no guardaba nada. Ahora se persiste con lock y escritura atómica, se exige
consentimiento explícito y se rechaza un SKU que no exista en el catálogo (la
respuesta anterior devolvía un PDF que no correspondía).
"""

import datetime
import re
import uuid
from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.config import LEADS_JSON_PATH, ensure_dirs
from backend.services.catalog_seed import load_or_init_catalog
from backend.services.json_store import lock_for, read_json, write_json_atomic

router = APIRouter(prefix="/api/leads", tags=["leads"])

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]{2,}$")
MAX_LEADS = 50_000
FALLBACK_DELIVERABLE = "/deliverables/l01_anatomia-post-418-usd.html"


class LeadPayload(BaseModel):
    email: str = Field(min_length=5, max_length=254)
    source: str = Field(default="l01", max_length=40)
    sku_id: str = Field(default="L01", max_length=10)
    consent: bool = False


def _load() -> Dict[str, Any]:
    ensure_dirs()
    data, error = read_json(LEADS_JSON_PATH)
    if error is None and isinstance(data, dict) and isinstance(data.get("leads"), list):
        return data
    return {"leads": [], "updated_at": None}


def _save(data: Dict[str, Any]) -> None:
    ensure_dirs()
    data["updated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    write_json_atomic(LEADS_JSON_PATH, data)


def _sku_index() -> Dict[str, str]:
    try:
        return {
            item.sku_id: f"/deliverables/{item.sku_id.lower()}_{item.slug}.html"
            for item in load_or_init_catalog()
        }
    except Exception:
        return {}


@router.post("")
def create_lead(payload: LeadPayload):
    email = payload.email.strip().lower()
    if not EMAIL_RE.match(email):
        raise HTTPException(status_code=422, detail="Correo inválido")
    if not payload.consent:
        raise HTTPException(
            status_code=422,
            detail="Se requiere consentimiento explícito para guardar el correo.",
        )
    deliverable_url = _sku_index().get(payload.sku_id)
    if deliverable_url is None:
        raise HTTPException(status_code=422, detail=f"SKU no existe en el catálogo: {payload.sku_id}")

    with lock_for(LEADS_JSON_PATH):
        data = _load()
        if len(data["leads"]) >= MAX_LEADS:
            raise HTTPException(status_code=507, detail="Almacén de leads lleno")

        already = any(
            lead.get("email") == email and lead.get("source") == payload.source
            for lead in data["leads"]
        )
        if not already:
            data["leads"].append(
                {
                    "id": f"ld_{uuid.uuid4().hex[:10]}",
                    "email": email,
                    "source": payload.source,
                    "sku_id": payload.sku_id,
                    "consent": payload.consent,
                    "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                }
            )
            _save(data)
        total = len(data["leads"])

    return {
        "status": "stored" if not already else "already_registered",
        "deliverable_url": deliverable_url or FALLBACK_DELIVERABLE,
        "total_leads": total,
    }


@router.get("/count")
def leads_count():
    data = _load()
    by_source: Dict[str, int] = {}
    for lead in data["leads"]:
        source = lead.get("source", "?")
        by_source[source] = by_source.get(source, 0) + 1
    return {"total": len(data["leads"]), "by_source": by_source}
