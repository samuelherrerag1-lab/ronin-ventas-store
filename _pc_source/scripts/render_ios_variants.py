"""Genera las variantes de capturas iOS y una hoja de contactos.

Uso:
    .\\.venv\\Scripts\\python.exe scripts\\render_ios_variants.py
    .\\.venv\\Scripts\\python.exe scripts\\render_ios_variants.py --only notes
    .\\.venv\\Scripts\\python.exe scripts\\render_ios_variants.py --no-sheet

Salida: data/captures/ios/*.png + contact_sheet.png + manifest.json
"""

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

from backend.services.ios_app_templates import build_ios17_notes_html, build_ios17_stripe_html  # noqa: E402
from backend.services.ios_html_templates import build_ios17_lockscreen_html  # noqa: E402
from backend.services.playwright_bait_renderer import DEFAULT_WALLPAPER, render_html_to_png  # noqa: E402

OUT_DIR = ROOT / "data" / "captures" / "ios"
TITANIUM = "ios17_titanium_wallpaper.png"

LOCK_NOTIFS = [
    "Gumroad: You made a sale! $27.00 — Bóveda 500 Hooks",
    "Hotmart: Pago aprobado COP 89.900 — Kit Sistema Completo",
]
LOCK_ONE = ["Gumroad: You made a sale! $27.00 — Bóveda 500 Hooks"]
NOTE_LINES = [
    "Micro-asset de una página listo antes de las 8 AM",
    "Order bump +$9 USD activo en el checkout",
    "Publicar solo cuando el dolor sea obvio",
]
TXS = ["Bóveda 500 Hooks: $27.00 USD", "Kit Sistema Completo: $47.00 USD", "Order Bump Maquina: $19.00 USD"]
DATE = "domingo, 2 de noviembre"
NOTE_DATE = "2 de noviembre de 2026"
NOTE_TITLE = "3 cosas que descubrí a las 3 AM"

VARIANTS = [
    {"name": "01_lockscreen_dark_wallpaper", "kind": "lockscreen", "theme": "dark",
     "wallpaper": DEFAULT_WALLPAPER, "clock": "07:12", "notifs": LOCK_NOTIFS, "widgets": False},
    {"name": "02_lockscreen_dark_no_wallpaper", "kind": "lockscreen", "theme": "dark",
     "wallpaper": "", "clock": "07:12", "notifs": LOCK_NOTIFS, "widgets": False},
    {"name": "03_lockscreen_light_no_wallpaper", "kind": "lockscreen", "theme": "light",
     "wallpaper": "", "clock": "07:12", "notifs": LOCK_NOTIFS, "widgets": False},
    {"name": "04_lockscreen_dark_widgets", "kind": "lockscreen", "theme": "dark",
     "wallpaper": DEFAULT_WALLPAPER, "clock": "07:12", "notifs": LOCK_NOTIFS, "widgets": True},
    {"name": "05_lockscreen_titanium_one_notif", "kind": "lockscreen", "theme": "dark",
     "wallpaper": TITANIUM, "clock": "07:12", "notifs": LOCK_ONE, "widgets": False},
    {"name": "06_notes_3am_dark", "kind": "notes", "theme": "dark", "wallpaper": ""},
    {"name": "07_notes_3am_light", "kind": "notes", "theme": "light", "wallpaper": ""},
    {"name": "08_stripe_dashboard", "kind": "stripe", "theme": "dark", "wallpaper": ""},
]


def _html_for(variant: dict) -> str:
    kind = variant["kind"]
    if kind == "lockscreen":
        return build_ios17_lockscreen_html(
            "$418.50 USD", "7 ventas hoy", variant["notifs"], variant["clock"], DATE,
            wallpaper_filename=variant["wallpaper"], with_widgets=variant["widgets"], theme=variant["theme"],
        )
    if kind == "notes":
        return build_ios17_notes_html(NOTE_TITLE, "apuntes", NOTE_LINES, "03:14", NOTE_DATE, theme=variant["theme"])
    return build_ios17_stripe_html("$418.50", "9 pagos · ticket medio $46.50", TXS, "03:14")


def _label_font(size: int):
    for candidate in (r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\arial.ttf"):
        if Path(candidate).is_file():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def contact_sheet(entries: list, out_path: Path, cols: int = 4, thumb_w: int = 258) -> Path:
    thumb_h = round(thumb_w * 2556 / 1179)
    gap, label_h = 18, 30
    rows = (len(entries) + cols - 1) // cols
    width = cols * thumb_w + (cols + 1) * gap
    height = rows * (thumb_h + label_h) + (rows + 1) * gap
    canvas = Image.new("RGB", (width, height), (10, 11, 15))
    draw = ImageDraw.Draw(canvas)
    font = _label_font(15)
    for i, entry in enumerate(entries):
        row, col = divmod(i, cols)
        x = gap + col * (thumb_w + gap)
        y = gap + row * (thumb_h + label_h + gap)
        with Image.open(entry["path"]) as raw:
            thumb = raw.convert("RGB").resize((thumb_w, thumb_h), Image.LANCZOS)
        canvas.paste(thumb, (x, y))
        draw.rectangle([x, y, x + thumb_w - 1, y + thumb_h], outline=(40, 42, 52))
        draw.text((x + 2, y + thumb_h + 7), entry["name"], fill=(168, 172, 188), font=font)
    canvas.save(out_path, format="PNG", optimize=True)
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Genera variantes de capturas iOS retinas")
    parser.add_argument("--only", default="", help="filtra variantes por substring del nombre")
    parser.add_argument("--no-sheet", action="store_true", help="no genera la hoja de contactos")
    parser.add_argument("--out", default=str(OUT_DIR), help="directorio de salida")
    args = parser.parse_args()

    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    selected = [v for v in VARIANTS if args.only.lower() in v["name"].lower()]
    if not selected:
        print(f"Sin variantes que coincidan con '{args.only}'")
        return 1

    entries = []
    started = time.time()
    for variant in selected:
        target = out_dir / f"{variant['name']}.png"
        ok = render_html_to_png(_html_for(variant), target)
        size = target.stat().st_size if target.is_file() else 0
        entries.append({
            "name": variant["name"],
            "kind": variant["kind"],
            "theme": variant["theme"],
            "wallpaper": variant["wallpaper"] or "gradiente",
            "path": _rel(target),
            "bytes": size,
            "rendered": bool(ok and size > 5000),
        })
        print(f"[{'ok' if ok and size > 5000 else 'FALLO'}] {variant['name']:<36} {size:>9} bytes")

    if not args.no_sheet:
        sheet = contact_sheet(entries, out_dir / "contact_sheet.png")
        print(f"[ok] hoja de contactos: {_rel(sheet)}  ({sheet.stat().st_size} bytes)")

    manifest = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "viewport_pt": "393x852",
        "pixels": "1179x2556",
        "sheet": "data/captures/ios/contact_sheet.png",
        "variants": entries,
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    failed = [e["name"] for e in entries if not e["rendered"]]
    print(f"Listo en {time.time() - started:.1f}s · {len(entries) - len(failed)}/{len(entries)} renderizadas")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
