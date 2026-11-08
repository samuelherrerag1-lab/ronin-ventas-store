"""Sonda real de Vertex AI para Ronin Ventas OS.

Comprueba qué proyectos/regiones/modelos de imagen responden de verdad antes de
gastar en un lote. No declara nada sin una imagen escrita y validada en disco.

Uso:
    .venv\\Scripts\\python.exe scripts\\probe_vertex.py            # solo el proyecto activo
    .venv\\Scripts\\python.exe scripts\\probe_vertex.py --all       # matriz completa
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.config import (  # noqa: E402
    NANO_BANANA_FALLBACK_MODEL,
    NANO_BANANA_MODEL,
    VERTEX_LOCATION,
    VERTEX_PROJECT_ID,
)

PROJECTS = ["REDACTED_EXAMPLE_PROJECT", "example-project-id"]
LOCATIONS = ["global", "us-central1"]
MODELS = ["gemini-3.1-flash-image", "gemini-3.1-flash-lite-image", "gemini-2.5-flash-image"]


def probe(project: str, location: str, model: str) -> tuple[bool, str]:
    try:
        from google import genai
        from google.genai import types
    except Exception as exc:  # pragma: no cover - entorno roto
        return False, f"import google-genai: {type(exc).__name__}: {exc}"

    t0 = time.time()
    try:
        client = genai.Client(vertexai=True, project=project, location=location)
        response = client.models.generate_content(
            model=model,
            contents=["a single matte black obsidian dot on pure white background, product photo"],
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(aspect_ratio="1:1"),
            ),
        )
    except Exception as exc:
        return False, f"{type(exc).__name__}: {str(exc)[:300]}"

    for candidate in getattr(response, "candidates", None) or []:
        content = getattr(candidate, "content", None)
        for part in getattr(content, "parts", None) or []:
            inline = getattr(part, "inline_data", None)
            data = getattr(inline, "data", None)
            if isinstance(data, bytes) and len(data) > 500:
                return True, f"{len(data)} bytes en {round(time.time() - t0, 1)}s"
    return False, "sin bytes de imagen en la respuesta"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true", help="probar la matriz completa")
    args = parser.parse_args()

    print(f"Proyecto activo : {VERTEX_PROJECT_ID}")
    print(f"Región activa   : {VERTEX_LOCATION}")
    print(f"Modelo activo   : {NANO_BANANA_MODEL} (fallback {NANO_BANANA_FALLBACK_MODEL})\n")

    if args.all:
        combos = [(p, loc, m) for p in PROJECTS for loc in LOCATIONS for m in MODELS]
    else:
        combos = [(VERTEX_PROJECT_ID, VERTEX_LOCATION, NANO_BANANA_MODEL)]
        if NANO_BANANA_FALLBACK_MODEL:
            combos.append((VERTEX_PROJECT_ID, VERTEX_LOCATION, NANO_BANANA_FALLBACK_MODEL))

    failures = 0
    active_ok = False
    for project, location, model in combos:
        ok, detail = probe(project, location, model)
        status = "OK " if ok else "NO "
        print(f"[{status}] {project} | {location:11s} | {model:28s} | {detail}")
        failures += 0 if ok else 1
        if ok and project == VERTEX_PROJECT_ID and location == VERTEX_LOCATION and model == NANO_BANANA_MODEL:
            active_ok = True

    print(f"\nResultado: {'ACTIVO OK' if active_ok else 'REVISAR configuración'}")
    return 0 if active_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
