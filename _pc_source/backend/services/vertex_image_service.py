"""Generación de arte con Nano Banana 2 sobre Vertex AI (proyecto nuevo).

Reglas del sistema:
- Proyecto/región/modelo salen de `backend.config`, no hardcodeados aquí.
- Se reintenta lo transitorio (429/503/deadline) y se cae al modelo lite.
- Una imagen solo cuenta como generada si hay bytes > 500 escritos en disco.
- Cada generación se registra en el ledger FinOps (coste real, no estimado a ojo).
"""

import datetime
import json
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from google import genai
from google.genai import types

from backend.config import (
    DATA_DIR,
    DEFAULT_IMAGE_COST_USD,
    FIN_OPS_JSON_PATH,
    FINOPS_CIRCUIT_BREAKER_USD,
    IMAGE_COST_USD,
    NANO_BANANA_FALLBACK_MODEL,
    NANO_BANANA_MODEL,
    VERTEX_LOCATION,
    VERTEX_PROJECT_ID,
    ensure_dirs,
)

GENERATED_IMG_DIR = DATA_DIR / "generated_images"
CANONICAL_SEED_PATH = GENERATED_IMG_DIR / "ron_canonical_seed.png"
MIN_VALID_IMAGE_BYTES = 500
TRANSIENT_MARKERS = (
    "429",
    "resource_exhausted",
    "503",
    "unavailable",
    "deadline",
    "500",
    "504",
    "timeout",
    "connection reset",
)

RON_CHARACTER = (
    "Ron has a large egg-shaped white head, big cartoon eyes with white sclera and "
    "black pupils, sad angled eyebrows, prominent pink-brown under-eye bags (ojeras), "
    "a small frown, a messy dark-brown hair tuft swept to one side, an oversized "
    "terracotta hoodie #E07A5F with a front pocket and drawstrings, thin black stick "
    "legs and mitten hands, and a slightly hunched posture."
)

CINEMATIC_2D_STYLE = (
    "Premium cinematic 2D animated frame. Dark moody atmosphere, dramatic volumetric "
    "lighting, rich ink textures, halftone shading, subtle paper grain, deep shadows, "
    "high contrast, hand-drawn comic illustration with thick black outlines and flat "
    f"colors. {RON_CHARACTER} Cinematic depth, atmospheric dust and embers. "
    "No text, no captions, no logos, no watermark, no photorealism, no 3D render. Scene: "
)

DARK_INSIDER_MODIFIER = (
    "Ultra-sharp editorial dark luxury aesthetic, deep obsidian shadows, subtle gold and emerald rim lighting, "
    "high-contrast cinematic composition, shot on 35mm f/1.4 lens, authentic film grain, zero plastic sheen."
)

_CLIENTS: Dict[Tuple[str, str], Any] = {}


def ensure_img_dir() -> Path:
    ensure_dirs()
    GENERATED_IMG_DIR.mkdir(parents=True, exist_ok=True)
    return GENERATED_IMG_DIR


def _load_ledger() -> Dict[str, Any]:
    if FIN_OPS_JSON_PATH.exists():
        try:
            return json.loads(FIN_OPS_JSON_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "project_id": VERTEX_PROJECT_ID,
        "total_spent_usd": 0.0,
        "circuit_breaker_limit_usd": FINOPS_CIRCUIT_BREAKER_USD,
        "images": 0,
        "entries": [],
    }


def _record_spend(model: str, cost: float, filename: str) -> Dict[str, Any]:
    ensure_dirs()
    ledger = _load_ledger()
    ledger["project_id"] = VERTEX_PROJECT_ID
    ledger["total_spent_usd"] = round(float(ledger.get("total_spent_usd", 0.0)) + cost, 4)
    ledger["images"] = int(ledger.get("images", 0)) + 1
    ledger.setdefault("entries", []).append(
        {
            "at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "filename": filename,
            "model": model,
            "cost_usd": cost,
        }
    )
    FIN_OPS_JSON_PATH.write_text(json.dumps(ledger, indent=2, ensure_ascii=False), encoding="utf-8")
    return ledger


def _client() -> Any:
    key = (VERTEX_PROJECT_ID, VERTEX_LOCATION)
    if key not in _CLIENTS:
        _CLIENTS[key] = genai.Client(vertexai=True, project=VERTEX_PROJECT_ID, location=VERTEX_LOCATION)
    return _CLIENTS[key]


def _is_transient(exc: Exception) -> bool:
    text = f"{type(exc).__name__} {exc}".lower()
    return any(marker in text for marker in TRANSIENT_MARKERS)


def _extract_image(response: Any) -> Tuple[Optional[bytes], Optional[str]]:
    for candidate in getattr(response, "candidates", None) or []:
        content = getattr(candidate, "content", None)
        for part in getattr(content, "parts", None) or []:
            inline = getattr(part, "inline_data", None)
            data = getattr(inline, "data", None)
            if isinstance(data, bytes) and data:
                mime = getattr(inline, "mime_type", None)
                return data, str(mime) if mime else None
    return None, None


def _build_contents(prompt: str) -> Tuple[List[Any], bool]:
    use_ron_style = any(k in prompt.lower() for k in ("ron", "terracotta", "ojeras", "2d", "comic", "ink"))
    contents: List[Any] = []
    if use_ron_style:
        if CANONICAL_SEED_PATH.is_file():
            try:
                from PIL import Image

                contents.append(Image.open(CANONICAL_SEED_PATH))
            except Exception:
                pass
        contents.append(f"{CINEMATIC_2D_STYLE}{prompt.strip()}")
    else:
        contents.append(f"{prompt.strip()}. Style: {DARK_INSIDER_MODIFIER}")
    return contents, use_ron_style


def vertex_status() -> Dict[str, Any]:
    """Estado honesto de configuración (no prueba la red)."""
    from backend.config import GCLOUD_ADC_PATH

    ledger = _load_ledger()
    return {
        "project_id": VERTEX_PROJECT_ID,
        "location": VERTEX_LOCATION,
        "primary_model": NANO_BANANA_MODEL,
        "fallback_model": NANO_BANANA_FALLBACK_MODEL,
        "adc_present": GCLOUD_ADC_PATH.is_file(),
        "seed_present": CANONICAL_SEED_PATH.is_file(),
        "total_spent_usd": ledger.get("total_spent_usd", 0.0),
        "circuit_breaker_limit_usd": ledger.get("circuit_breaker_limit_usd", FINOPS_CIRCUIT_BREAKER_USD),
    }


def generate_nano_banana_image(prompt: str, aspect_ratio: str = "3:4") -> Dict[str, Any]:
    if not prompt or not prompt.strip():
        raise ValueError("El prompt de imagen no puede estar vacío.")

    ensure_img_dir()
    ledger = _load_ledger()
    cost = IMAGE_COST_USD.get(NANO_BANANA_MODEL, DEFAULT_IMAGE_COST_USD)
    limit = float(ledger.get("circuit_breaker_limit_usd", FINOPS_CIRCUIT_BREAKER_USD))
    spent = float(ledger.get("total_spent_usd", 0.0))
    if spent + cost > limit:
        raise RuntimeError(
            f"Circuit Breaker FinOps alcanzado (${spent:.2f} gastados de ${limit:.2f}). "
            "Incrementa FINOPS_CIRCUIT_BREAKER_USD o reinicia el ledger."
        )

    contents, use_ron_style = _build_contents(prompt)
    errors: List[str] = []
    used_model = NANO_BANANA_MODEL
    image_bytes: Optional[bytes] = None
    mime: Optional[str] = None

    for model in (NANO_BANANA_MODEL, NANO_BANANA_FALLBACK_MODEL):
        for attempt in (1, 2, 3):
            t0 = time.time()
            try:
                response = _client().models.generate_content(
                    model=model,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        response_modalities=["IMAGE"],
                        image_config=types.ImageConfig(aspect_ratio=aspect_ratio),
                    ),
                )
                image_bytes, mime = _extract_image(response)
                if image_bytes:
                    used_model = model
                    break
                errors.append(f"{model} intento {attempt}: respuesta sin imagen")
            except Exception as exc:
                errors.append(f"{model} intento {attempt}: {type(exc).__name__} — {str(exc)[:240]}")
                if not _is_transient(exc):
                    break
                time.sleep(4 * attempt)
            finally:
                elapsed_attempt = round(time.time() - t0, 2)
        if image_bytes:
            break

    if not image_bytes or len(image_bytes) <= MIN_VALID_IMAGE_BYTES:
        raise RuntimeError(
            "Nano Banana no devolvió una imagen válida. "
            f"Proyecto {VERTEX_PROJECT_ID} · región {VERTEX_LOCATION}. Detalle: {' | '.join(errors[-3:])}"
        )

    ext = ".jpg" if mime and "jpeg" in mime else ".png"
    filename = f"nb2_{time.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}{ext}"
    out_path = GENERATED_IMG_DIR / filename
    out_path.write_bytes(image_bytes)
    if not out_path.is_file() or out_path.stat().st_size <= MIN_VALID_IMAGE_BYTES:
        raise RuntimeError(f"La imagen se escribió vacía o corrupta: {out_path}")

    real_cost = IMAGE_COST_USD.get(used_model, DEFAULT_IMAGE_COST_USD)
    ledger = _record_spend(used_model, real_cost, filename)

    return {
        "status": "ok",
        "project_id": VERTEX_PROJECT_ID,
        "location": VERTEX_LOCATION,
        "model": used_model,
        "fallback_used": used_model != NANO_BANANA_MODEL,
        "style_mode": "cinematic-2d-v2 (Ron Seed)" if use_ron_style else "dark-insider-oled",
        "filename": filename,
        "image_url": f"/generated_images/{filename}",
        "bytes": len(image_bytes),
        "elapsed_attempt_sec": elapsed_attempt,
        "estimated_cost_usd": real_cost,
        "spent_total_usd": ledger.get("total_spent_usd", 0.0),
    }
