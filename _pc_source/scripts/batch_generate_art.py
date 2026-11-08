"""Motor por lotes de generación y compresión de arte para Ronin Ventas OS."""
import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from google import genai
from google.genai import types
from PIL import Image

from backend.config import DATA_DIR, NANO_BANANA_MODEL, VERTEX_LOCATION, VERTEX_PROJECT_ID
from backend.services.vertex_image_service import CANONICAL_SEED_PATH, CINEMATIC_2D_STYLE, DARK_INSIDER_MODIFIER

PROMPTS_PATH = DATA_DIR / "product_art_prompts.json"
ART_DIR = DATA_DIR / "product_art"
ORIGINAL_DIR = ART_DIR / "original"
WEB_DIR = ART_DIR / "web"
MANIFEST_PATH = ART_DIR / "manifest.json"


def ensure_dirs():
    for d in [ORIGINAL_DIR, WEB_DIR]:
        d.mkdir(parents=True, exist_ok=True)


def compress_image(orig_path: Path, web_path: Path, aspect: str) -> int:
    web_path.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(orig_path) as img:
        img = img.convert("RGB")
        w, h = img.size
        if aspect == "3:4":
            target = (600, 800)
        elif aspect == "16:9":
            target = (960, 540)
        elif aspect == "1:1":
            target = (512, 512)
        else:
            target = (w // 2, h // 2)
        img.thumbnail(target, Image.Resampling.LANCZOS)
        img.save(web_path, "WEBP", quality=82, method=6)
    return web_path.stat().st_size


def generate_single_item(client: genai.Client, cat: str, key: str, spec: Dict[str, Any], force: bool = False) -> Dict[str, Any]:
    orig_cat_dir = ORIGINAL_DIR / cat
    web_cat_dir = WEB_DIR / cat
    orig_path = orig_cat_dir / f"{key}.png"
    web_path = web_cat_dir / f"{key}.webp"

    if orig_path.exists() and web_path.exists() and not force:
        return {"key": key, "status": "cached", "orig": str(orig_path), "web": str(web_path)}

    orig_cat_dir.mkdir(parents=True, exist_ok=True)
    use_ron = spec.get("ron", False)
    prompt = spec["prompt"]
    aspect = spec.get("aspect", "3:4")

    contents = []
    if use_ron and CANONICAL_SEED_PATH.is_file():
        try:
            contents.append(Image.open(CANONICAL_SEED_PATH))
        except Exception:
            pass
        contents.append(f"{CINEMATIC_2D_STYLE}{prompt}")
    else:
        contents.append(f"{prompt} Style: {DARK_INSIDER_MODIFIER}")

    last_err = None
    for attempt in range(3):
        try:
            resp = client.models.generate_content(
                model=NANO_BANANA_MODEL,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE"],
                    image_config=types.ImageConfig(aspect_ratio=aspect),
                ),
            )
            img_bytes = None
            for p in resp.candidates[0].content.parts:
                if p.inline_data:
                    img_bytes = p.inline_data.data
                    break
            if img_bytes:
                orig_path.write_bytes(img_bytes)
                web_size = compress_image(orig_path, web_path, aspect)
                if cat == "covers" and key.endswith("_v1"):
                    sku = spec.get("sku")
                    if sku:
                        top_web = WEB_DIR / f"{sku}.webp"
                        top_web.write_bytes(web_path.read_bytes())
                return {"key": key, "status": "generated", "bytes": len(img_bytes), "web_bytes": web_size}
        except Exception as e:
            last_err = e
            time.sleep(2 * (attempt + 1))
    return {"key": key, "status": "failed", "error": str(last_err)}


def update_manifest():
    manifest: Dict[str, Any] = {"version": "2.0.0", "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"), "categories": {}}
    if PROMPTS_PATH.exists():
        prompts = json.loads(PROMPTS_PATH.read_text(encoding="utf-8"))
        for cat, items in prompts.items():
            manifest["categories"][cat] = {}
            for key, spec in items.items():
                orig_path = ORIGINAL_DIR / cat / f"{key}.png"
                web_path = WEB_DIR / cat / f"{key}.webp"
                if web_path.exists():
                    manifest["categories"][cat][key] = {
                        "sku": spec.get("sku"),
                        "aspect": spec.get("aspect"),
                        "ron": spec.get("ron"),
                        "web_url": f"/product_art/web/{cat}/{key}.webp",
                        "web_file": f"{cat}/{key}.webp",
                        "web_size_kb": round(web_path.stat().st_size / 1024, 1),
                    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")


def run_batch(category: str = "all", concurrency: int = 4, limit: int = 0, force: bool = False):
    ensure_dirs()
    if not PROMPTS_PATH.exists():
        print(f"Error: {PROMPTS_PATH} no existe.")
        return
    prompts_data = json.loads(PROMPTS_PATH.read_text(encoding="utf-8"))

    queue = []
    for cat, items in prompts_data.items():
        if category != "all" and cat != category:
            continue
        for key, spec in items.items():
            queue.append((cat, key, spec))

    if limit > 0:
        queue = queue[:limit]

    print(f"Iniciando lote de {len(queue)} tareas (Categoría: {category}, Hilos: {concurrency})...")
    client = genai.Client(vertexai=True, project=VERTEX_PROJECT_ID, location=VERTEX_LOCATION)

    done, errs, cached = 0, 0, 0
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futs = {pool.submit(generate_single_item, client, c, k, s, force): (c, k) for c, k, s in queue}
        for f in as_completed(futs):
            res = f.result()
            st = res.get("status")
            if st == "generated":
                done += 1
                print(f"[{done+cached}/{len(queue)}] OK: {res['key']} ({res.get('web_bytes',0)//1024} KB)")
            elif st == "cached":
                cached += 1
            else:
                errs += 1
                print(f"ERR: {res['key']} -> {res.get('error')}")

    update_manifest()
    elapsed = round(time.time() - t0, 1)
    cost = round(done * 0.03, 2)
    print(f"Lote finalizado en {elapsed}s. Generados: {done}, Cacheados: {cached}, Errores: {errs}. Gasto: ~${cost} USD")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--category", default="all")
    parser.add_argument("--concurrency", type=int, default=4)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    run_batch(args.category, args.concurrency, args.limit, args.force)
