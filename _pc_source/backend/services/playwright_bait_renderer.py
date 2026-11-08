import os
import shutil
import subprocess
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List
from PIL import Image, ImageDraw, ImageFont
from backend.services.ios_app_templates import build_ios17_notes_html, build_ios17_stripe_html
from backend.services.ios_html_templates import _safe_wallpaper_path, build_ios17_lockscreen_html
from backend.services.vertex_image_service import GENERATED_IMG_DIR, ensure_img_dir

WATERMARK_TEXT = "SIMULACIÓN · MOCKUP — NO ES UNA VENTA REAL"
DEFAULT_WALLPAPER = "ios17_editorial_dark_wallpaper.png"


def _watermark_enabled() -> bool:
    return os.environ.get("BAIT_WATERMARK", "1").strip() != "0"


def _apply_simulation_watermark(path: Path) -> None:
    """Marca visible la captura como simulación: es un mockup, no una venta real."""
    if not _watermark_enabled() or not path.is_file():
        return
    try:
        with Image.open(path) as raw:
            img = raw.convert("RGBA")
        draw = ImageDraw.Draw(img, "RGBA")
        font = None
        for candidate in (r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\arial.ttf"):
            if Path(candidate).is_file():
                font = ImageFont.truetype(candidate, 30)
                break
        if font is None:
            font = ImageFont.load_default()
        box = draw.textbbox((0, 0), WATERMARK_TEXT, font=font)
        text_w = box[2] - box[0]
        x = (img.width - text_w) // 2
        y = 2450
        draw.rounded_rectangle([x - 22, y - 10, x + text_w + 22, y + 42], radius=13, fill=(0, 0, 0, 165))
        draw.text((x, y), WATERMARK_TEXT, fill=(255, 214, 10, 240), font=font)
        img.convert("RGB").save(path, format="PNG", optimize=True)
    except Exception:
        # El watermark nunca debe tumbar la generación de arte.
        pass


def _render_retina_fallback(
    out_path: Path,
    headline: str,
    sub: str,
    notifs: List[str],
    time_str: str,
    date_str: str = "domingo, 2 de noviembre",
    wallpaper_filename: str = "ios17_editorial_dark_wallpaper.png",
) -> None:
    wp_path = GENERATED_IMG_DIR / wallpaper_filename
    if not wp_path.exists():
        wp_path = GENERATED_IMG_DIR / "ios17_titanium_wallpaper.png"
    if wp_path.exists():
        base = Image.open(wp_path).convert("RGBA").resize((1179, 2556))
    else:
        base = Image.new("RGBA", (1179, 2556), (10, 12, 18, 255))
    overlay = Image.new("RGBA", (1179, 2556), (0, 0, 0, 75))
    base = Image.alpha_composite(base, overlay)
    draw = ImageDraw.Draw(base)

    draw.text((90, 68), "Claro", fill=(255, 255, 255, 240))
    draw.text((960, 68), "5G  100%", fill=(255, 255, 255, 240))
    draw.text((589, 260), date_str, fill=(255, 255, 255, 230), anchor="mm")
    draw.text((589, 430), time_str, fill=(255, 255, 255, 235), anchor="mm")

    draw.rounded_rectangle([250, 560, 740, 740], radius=45, fill=(20, 24, 34, 180), outline=(255, 255, 255, 55), width=3)
    draw.text((280, 580), "STRIPE • HOY", fill=(255, 255, 255, 180))
    draw.text((280, 620), headline, fill=(255, 255, 255, 255))
    draw.text((280, 680), sub, fill=(110, 231, 183, 255))
    draw.ellipse([790, 560, 970, 740], fill=(20, 24, 34, 180), outline=(16, 185, 129, 255), width=6)
    draw.text((880, 650), "94%", fill=(255, 255, 255, 255), anchor="mm")

    draw.text((60, 1400), "Centro de notificaciones", fill=(255, 255, 255, 230))
    y_card = 1460
    for idx, raw in enumerate(notifs[:2]):
        is_h = "hotmart" in raw.lower() or "cop" in raw.lower()
        color = (255, 106, 61, 255) if is_h else (255, 144, 232, 255)
        draw.rounded_rectangle([48, y_card, 1131, y_card + 225], radius=60, fill=(36, 38, 46, 215), outline=(255, 255, 255, 35), width=3)
        draw.rounded_rectangle([80, y_card + 35, 220, y_card + 175], radius=32, fill=color)
        draw.text((150, y_card + 105), "H" if is_h else "G", fill=(255, 255, 255) if is_h else (0, 0, 0), anchor="mm")
        draw.text((250, y_card + 45), "Hotmart" if is_h else "Gumroad", fill=(255, 255, 255, 255))
        draw.text((250, y_card + 105), "¡Venta realizada!" if is_h else "You made a sale!", fill=(255, 255, 255, 255))
        draw.text((250, y_card + 155), raw[:55], fill=(255, 255, 255, 210))
        y_card += 250

    draw.rounded_rectangle([520, 2510, 659, 2525], radius=10, fill=(255, 255, 255, 230))
    base.convert("RGB").save(out_path, format="PNG", optimize=True)


def render_ios_bait_screenshot_png(
    headline_metric: str,
    sub_metric: str,
    notifications: List[str],
    timestamp_label: str = "07:12",
    date_label: str = "domingo, 2 de noviembre",
    wallpaper_filename: str = "ios17_editorial_dark_wallpaper.png",
    widget_type: str = "ios_lockscreen",
) -> Dict[str, Any]:
    ensure_img_dir()
    if not _safe_wallpaper_path(wallpaper_filename):
        wallpaper_filename = DEFAULT_WALLPAPER
    if widget_type == "iphone_note_3am":
        html_str = build_ios17_notes_html(headline_metric, sub_metric, notifications, timestamp_label, date_label)
    elif widget_type == "stripe_gumroad_dashboard":
        html_str = build_ios17_stripe_html(headline_metric, sub_metric, notifications, timestamp_label)
    else:
        html_str = build_ios17_lockscreen_html(
            headline_metric, sub_metric, notifications, timestamp_label, date_label, wallpaper_filename
        )

    filename = f"ios17_bait_{time.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}.png"
    out_path: Path = GENERATED_IMG_DIR / filename

    rendered = False
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            b = p.chromium.launch(headless=True)
            # Sin JavaScript: el HTML solo maqueta; nunca debe ejecutar scripts.
            context = b.new_context(
                viewport={"width": 393, "height": 852},
                device_scale_factor=3,
                java_script_enabled=False,
            )
            page = context.new_page()
            page.set_content(html_str, wait_until="load")
            page.screenshot(path=str(out_path), full_page=False)
            b.close()
            rendered = True
    except Exception:
        pass

    if not rendered:
        chrome_cands = [r"C:\Program Files\Google\Chrome\Application\chrome.exe", shutil.which("chrome") or ""]
        c_bin = next((c for c in chrome_cands if c and Path(c).exists()), None)
        if c_bin:
            tmp_html = Path(tempfile.gettempdir()) / f"ronin_ios_{uuid.uuid4().hex[:8]}.html"
            tmp_profile = Path(tempfile.mkdtemp(prefix="ronin_headless_profile_"))
            tmp_html.write_text(html_str, encoding="utf-8")
            try:
                subprocess.run(
                    [
                        c_bin,
                        "--headless=new",
                        f"--user-data-dir={tmp_profile}",
                        "--no-first-run",
                        "--no-default-browser-check",
                        "--disable-gpu",
                        "--hide-scrollbars",
                        "--force-device-scale-factor=3",
                        "--window-size=393,852",
                        f"--screenshot={out_path}",
                        tmp_html.as_uri(),
                    ],
                    check=True,
                    timeout=25,
                )
                rendered = True
            except Exception:
                pass
            finally:
                tmp_html.unlink(missing_ok=True)
                shutil.rmtree(tmp_profile, ignore_errors=True)

    if not rendered:
        _render_retina_fallback(out_path, headline_metric, sub_metric, notifications, timestamp_label, date_label, wallpaper_filename)

    _apply_simulation_watermark(out_path)

    return {
        "status": "ok",
        "filename": filename,
        "image_url": f"/generated_images/{filename}",
        "resolution": "1179x2556 (iPhone 15 Pro 3x Retina)",
        "bytes": out_path.stat().st_size,
        "simulation_watermark": _watermark_enabled(),
    }
