"""Compara dos capturas iOS: side-by-side + mapa de diferencias + metricas.

Uso:
    .\\.venv\\Scripts\\python.exe scripts\\compare_ios_capture.py A.png B.png
    .\\.venv\\Scripts\\python.exe scripts\\compare_ios_capture.py --all
    .\\.venv\\Scripts\\python.exe scripts\\compare_ios_capture.py A.png B.png --out comparacion.png

--all compara las capturas "antes" con las variantes nuevas del manifest.
Salida por defecto: data/captures/ios/compare_*.png
Solo Pillow (el venv oficial no trae numpy).
"""

import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent.parent
CAPTURES = ROOT / "data" / "captures" / "ios"

PAIRS = [
    ("before/lockscreen_dark.png", "01_lockscreen_dark_wallpaper.png"),
    ("before/notes_3am.png", "06_notes_3am_dark.png"),
    ("before/stripe_dashboard.png", "08_stripe_dashboard.png"),
]


def _font(size: int):
    for candidate in (r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\arial.ttf"):
        if Path(candidate).is_file():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def pixel_delta(a: Image.Image, b: Image.Image) -> Image.Image:
    """Diferencia por canal maximo (L) entre dos imagenes del mismo tamano."""
    r, g, bl = ImageChops.difference(a, b).split()
    return ImageChops.lighter(ImageChops.lighter(r, g), bl)


def image_metrics(a: Image.Image, b: Image.Image, delta: Image.Image, threshold: int = 10) -> dict:
    hist = delta.histogram()
    total = a.size[0] * a.size[1]
    mean = sum(i * count for i, count in enumerate(hist)) / total
    changed = sum(hist[threshold + 1:])
    strong = sum(hist[33:])
    mask = delta.point(lambda v: 255 if v > threshold else 0)
    bbox = mask.getbbox()
    return {
        "size": list(a.size),
        "mean_abs_diff": round(mean, 2),
        "pct_changed": round(changed * 100 / total, 2),
        "pct_strong_diff": round(strong * 100 / total, 2),
        "diff_bbox": list(bbox) if bbox else None,
    }


def _heatmap(delta: Image.Image) -> Image.Image:
    boosted = delta.point(lambda v: min(255, v * 3))
    return ImageOps.colorize(boosted, black="#08080C", mid="#7A1D14", white="#FF5A3C")


def compare(a_path: Path, b_path: Path, out_path: Path, threshold: int = 10) -> dict:
    a = Image.open(a_path).convert("RGB")
    b = Image.open(b_path).convert("RGB")
    if a.size != b.size:
        b = b.resize(a.size, Image.LANCZOS)
    delta = pixel_delta(a, b)
    metrics = image_metrics(a, b, delta, threshold)
    metrics.update({
        "a": str(a_path),
        "b": str(b_path),
        "a_bytes": a_path.stat().st_size,
        "b_bytes": b_path.stat().st_size,
    })

    panel_w, gap, header, footer = 356, 16, 96, 30
    panel_h = round(panel_w * a.size[1] / a.size[0])
    canvas = Image.new("RGB", (3 * panel_w + 4 * gap, header + panel_h + footer + gap), (10, 11, 15))
    draw = ImageDraw.Draw(canvas)
    title_font, label_font = _font(20), _font(15)

    draw.text((gap, 18), "COMPARACION DE CAPTURAS iOS", fill=(240, 241, 246), font=title_font)
    draw.text(
        (gap, 48),
        f"MAE {metrics['mean_abs_diff']} / pixeles distintos {metrics['pct_changed']}% (umbral {threshold})",
        fill=(150, 154, 168), font=label_font,
    )

    labels = ("A · ANTES", "B · AHORA", "DIFERENCIA x3")
    for i, panel in enumerate((a, b, _heatmap(delta))):
        x, y = gap + i * (panel_w + gap), header
        canvas.paste(panel.resize((panel_w, panel_h), Image.LANCZOS), (x, y))
        draw.rectangle([x, y, x + panel_w - 1, y + panel_h], outline=(44, 46, 58))
        draw.text((x + 2, y + panel_h + 7), labels[i], fill=(200, 203, 214), font=label_font)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path, format="PNG", optimize=True)
    try:
        metrics["comparison"] = str(out_path.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        metrics["comparison"] = str(out_path)
    return metrics


def main() -> int:
    parser = argparse.ArgumentParser(description="Compara capturas iOS y mide diferencias")
    parser.add_argument("a", nargs="?", help="imagen A (antes)")
    parser.add_argument("b", nargs="?", help="imagen B (despues)")
    parser.add_argument("--all", action="store_true", help="compara los pares before/* del proyecto")
    parser.add_argument("--threshold", type=int, default=10, help="umbral de diferencia por canal (0-255)")
    parser.add_argument("--out", default="", help="PNG de salida para el modo de dos imagenes")
    args = parser.parse_args()

    results = []
    if args.all or not (args.a and args.b):
        for before, after in PAIRS:
            a_path, b_path = CAPTURES / before, CAPTURES / after
            if not a_path.is_file() or not b_path.is_file():
                print(f"[skip] falta {before if not a_path.is_file() else after}")
                continue
            out = CAPTURES / f"compare_{a_path.stem}_vs_{b_path.stem}.png"
            results.append(compare(a_path, b_path, out, args.threshold))
    else:
        a_path, b_path = Path(args.a), Path(args.b)
        out = Path(args.out) if args.out else CAPTURES / f"compare_{a_path.stem}_vs_{b_path.stem}.png"
        results.append(compare(a_path, b_path, out, args.threshold))

    if not results:
        print("Nada que comparar. Pasa dos PNG o ejecuta --all.")
        return 1
    for item in results:
        print(json.dumps(item, ensure_ascii=False, indent=2))
    print(f"\n{len(results)} comparacion(es) escritas en data/captures/ios/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
