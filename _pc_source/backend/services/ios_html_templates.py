"""Lockscreen iOS 17.5 renderizado desde HTML.

Proporciones medidas sobre capturas reales de iPhone 15 Pro a 738x1600
(equivalente 393x852 pt). No usa estimaciones.
"""

import base64
import html
import io
import re
from functools import lru_cache
from pathlib import Path
from typing import List

from backend.services.ios_lockscreen_css import build_lockscreen_css
from backend.services.vertex_image_service import GENERATED_IMG_DIR

WALLPAPER_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,80}\.(png|jpg|jpeg|webp)$")

CSP_META = '<meta http-equiv="Content-Security-Policy" content="script-src \'none\'; object-src \'none\'">'

FONTS_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "fonts"

SIGNAL_SVG = """<svg class="sig" viewBox="0 0 18 12" fill="white"><rect x="0" y="8" width="3" height="4" rx="1"/><rect x="5" y="5.6" width="3" height="6.4" rx="1"/><rect x="10" y="3.2" width="3" height="8.8" rx="1"/><rect x="15" y="0" width="3" height="12" rx="1"/></svg>"""
WIFI_SVG = """<svg class="wifi" viewBox="0 0 17 12" fill="white"><path d="M8.5 11.2 6.2 8.6a3.4 3.4 0 0 1 4.6 0L8.5 11.2Z"/><path d="M4.6 7a5.9 5.9 0 0 1 7.8 0l-1.3 1.5a3.9 3.9 0 0 0-5.2 0L4.6 7Z"/><path d="M1.7 3.9a10.2 10.2 0 0 1 13.6 0l-1.4 1.6a8.1 8.1 0 0 0-10.8 0L1.7 3.9Z"/></svg>"""
PLAY_SVG = """<svg viewBox="0 0 24 24"><path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20Zm-1.2 5.6 6 4.4-6 4.4V7.6Z"/></svg>"""
FLASHLIGHT_SVG = """<svg viewBox="0 0 24 24"><path d="M7 3h10a1 1 0 0 1 1 1v2.4a2 2 0 0 1-.6 1.4L15.6 9.7V20a2 2 0 0 1-2 2h-3.2a2 2 0 0 1-2-2V9.7L6.6 7.8A2 2 0 0 1 6 6.4V4a1 1 0 0 1 1-1Zm5 7.2a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3Z"/></svg>"""
CAMERA_SVG = """<svg viewBox="0 0 24 24"><path d="M8.5 3.5a1.5 1.5 0 0 1 1.2-.6h4.6a1.5 1.5 0 0 1 1.2.6L16.6 5H19a3 3 0 0 1 3 3v10a3 3 0 0 1-3 3H5a3 3 0 0 1-3-3V8a3 3 0 0 1 3-3h2.4l1.1-1.5ZM12 9a4.5 4.5 0 1 0 0 9 4.5 4.5 0 0 0 0-9Zm0 2a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5Z"/></svg>"""
CLOSE_SVG = """<svg viewBox="0 0 24 24"><path d="M5 5l14 14M19 5L5 19" stroke-linecap="round"/></svg>"""
HOTMART_FLAME = """<svg width="22" height="22" viewBox="0 0 24 24" fill="white"><path d="M12 2C9.5 6 7 9 7 13a5 5 0 0 0 10 0c0-1.5-.5-3-1.5-4.5C14.5 10 13 11.5 13 13a1 1 0 1 1-2 0c0-2.5 2-4.5 3-6-1 0-2.5 1-3.5 2.5C10 8 11 5 12 2Z"/></svg>"""


STATUS_BAR_APP = """
<div class="status-bar">
  <span class="carrier-text font-clock">03:14</span>
  <div class="status-cluster">
    <svg class="cell-icon" viewBox="0 0 17 11" fill="white">
      <rect x="0" y="7.5" width="3" height="3.5" rx="0.8" />
      <rect x="4.5" y="5" width="3" height="6" rx="0.8" />
      <rect x="9" y="2.5" width="3" height="8.5" rx="0.8" />
      <rect x="13.5" y="0" width="3" height="11" rx="0.8" />
    </svg>
    <span class="net-text">5G</span>
    <div class="battery-wrap">
      <div class="battery-shell"><div class="battery-fill"></div></div>
      <div class="battery-cap"></div>
    </div>
  </div>
</div>
"""


def get_font_css() -> str:
    """Compatibilidad con ios_app_templates (Apple Notes y Stripe)."""
    return _font_face()


def _font_face() -> str:
    faces = []
    for weight, filename, fallback in (
        (400, "SFPRODISPLAYREGULAR.woff", "SF Pro Display"),
        (600, "SFPRODISPLAYMEDIUM.woff", "SF Pro Display Semibold"),
        (700, "SFPRODISPLAYBOLD.woff", "SF Pro Display Bold"),
    ):
        path = FONTS_DIR / filename
        if path.exists():
            b64 = base64.b64encode(path.read_bytes()).decode("ascii")
            src = f"url('data:font/woff;base64,{b64}') format('woff')"
        else:
            src = f"local('{fallback}')"
        faces.append(
            f"@font-face{{font-family:'SF Pro Display';font-style:normal;font-weight:{weight};src:{src};}}"
        )
    return "".join(faces)


def _safe_wallpaper_path(wallpaper_filename: str) -> "Path | None":
    """Solo permite un nombre de archivo simple dentro de GENERATED_IMG_DIR."""
    if not WALLPAPER_RE.fullmatch(wallpaper_filename or ""):
        return None
    root = GENERATED_IMG_DIR.resolve()
    candidate = (GENERATED_IMG_DIR / wallpaper_filename).resolve()
    if root not in candidate.parents or not candidate.is_file():
        return None
    return candidate


@lru_cache(maxsize=8)
def _wallpaper_data_uri(wallpaper_filename: str) -> str:
    """Incrusta el fondo para que funcione en cualquier motor de render."""
    wp = _safe_wallpaper_path(wallpaper_filename)
    if wp is None:
        wp = _safe_wallpaper_path("ios17_titanium_wallpaper.png")
    if wp is None:
        return ""
    try:
        from PIL import Image

        with Image.open(wp) as img:
            img = img.convert("RGB").resize((1179, 2556), Image.LANCZOS)
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=90, optimize=True)
        b64 = base64.b64encode(buffer.getvalue()).decode("ascii")
        return f"data:image/jpeg;base64,{b64}"
    except Exception:
        return ""


def _background(wallpaper_filename: str) -> str:
    uri = _wallpaper_data_uri(wallpaper_filename)
    if uri:
        return (
            "background:linear-gradient(180deg,rgba(0,0,0,.18) 0%,rgba(0,0,0,.04) 38%,"
            f"rgba(0,0,0,.62) 100%),url('{uri}') center/cover no-repeat;"
        )
    return "background:radial-gradient(circle at 50% 18%,#16203a 0%,#070b18 58%,#02040a 100%);"


def _split_notification(raw: str, idx: int) -> dict:
    text = raw.strip()
    app = "Gumroad"
    is_hotmart = bool(re.search(r"hotmart|nequi|pse|efecty|cop", text, re.I))
    if is_hotmart:
        app = "Hotmart"
    body = re.sub(r"^(gumroad|hotmart|stripe)\s*[•:\-]?\s*", "", text, flags=re.I)
    return {
        "app": app,
        "is_hotmart": is_hotmart,
        "title": app,
        "body": body,
        "time": "ahora" if idx == 0 else f"Hace {idx * 9 + 2} min",
    }


def _notification_html(raw: str, idx: int) -> str:
    n = _split_notification(raw, idx)
    if n["is_hotmart"]:
        icon = f'<div class="icon-squircle hotmart-bg">{HOTMART_FLAME}</div>'
    else:
        icon = '<div class="icon-squircle gumroad-bg"><div class="glyph">G</div></div>'
    return f"""
      <div class="notif-card">
        {icon}
        <div class="notif-body">
          <div class="notif-title-row"><span class="notif-title">{html.escape(n['app'])}</span><span class="notif-time">{html.escape(n['time'])}</span></div>
          <div class="notif-text">{html.escape(n['body'])}</div>
        </div>
      </div>"""


def build_ios17_lockscreen_html(
    headline_metric: str,
    sub_metric: str,
    notifications: List[str],
    timestamp_label: str = "07:12",
    date_label: str = "domingo, 2 de noviembre",
    wallpaper_filename: str = "ios17_editorial_dark_wallpaper.png",
    now_playing: str = "",
    battery_level: int = 78,
    with_widgets: bool = False,
) -> str:
    css = build_lockscreen_css(_background(wallpaper_filename), _font_face())
    cards = "".join(_notification_html(n, i) for i, n in enumerate(notifications[:2]))

    safe_headline = html.escape(headline_metric or "")
    safe_sub = html.escape(sub_metric or "")
    safe_time = html.escape(timestamp_label or "")
    safe_date = html.escape(date_label or "")
    safe_playing = html.escape(now_playing or "")
    safe_battery = max(0, min(100, int(battery_level)))

    now_line = f'<span class="track">{safe_playing}</span>' if safe_playing else ""
    play = PLAY_SVG if safe_playing else ""

    widgets = ""
    if with_widgets:
        widgets = f"""
        <div class="widgets-row">
          <div class="widget-rect">
            <div class="w-badge"><span class="w-dot"></span>STRIPE • HOY</div>
            <div class="w-main">{safe_headline}</div>
            <div class="w-sub">{safe_sub}</div>
          </div>
          <div class="widget-circ">
            <svg viewBox="0 0 36 36"><circle cx="18" cy="18" r="14" fill="none" stroke="rgba(255,255,255,.18)" stroke-width="3.4"/><circle cx="18" cy="18" r="14" fill="none" stroke="#10B981" stroke-width="3.4" stroke-dasharray="88" stroke-dashoffset="8" stroke-linecap="round"/></svg>
            <span>94%</span>
          </div>
        </div>"""

    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8">{CSP_META}<style>{css}</style></head><body>
  <div class="status-bar">
    <span class="carrier">TIGO</span>
    <div class="status-icons">{SIGNAL_SVG}{WIFI_SVG}<div class="battery"><span>{safe_battery}</span></div></div>
  </div>
  <div class="lock-block">
    <div class="now-line">{safe_date}{play}{now_line}</div>
    <div class="clock">{safe_time}</div>
    {widgets}
  </div>
  <div class="notif-section">
    <div class="notif-hdr"><span>Centro de notificaciones</span><div class="close-btn">{CLOSE_SVG}</div></div>
    {cards}
    <div class="tail-1"></div>
  </div>
  <div class="bottom-actions">
    <div class="action-circle">{FLASHLIGHT_SVG}</div>
    <div class="action-circle">{CAMERA_SVG}</div>
  </div>
  <div class="home-indicator"></div>
</body></html>"""
