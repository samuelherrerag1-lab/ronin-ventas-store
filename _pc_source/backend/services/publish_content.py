"""Contenido del sitio estático publicable: tienda, legales, 404 y colas.

Separado de `publish_pack.py` (orquestación) para respetar el límite de 250
líneas. Todo es HTML/CSS propio, sin CDNs, sin emojis y sin promesas de ingresos.
"""

import html
import json
from datetime import datetime
from pathlib import Path

from backend.config import DATA_DIR
from backend.models.catalog_models import ProductSKU

FORMAT_GROUPS = (
    ("ebook_blueprint", "Blueprints editoriales"),
    ("boveda_arsenal", "Bóvedas y arsenales"),
    ("micro_app_html", "Micro-apps HTML"),
    ("kit_sistema", "Sistemas completos"),
    ("mega_bundle", "Mega-bundles"),
    ("lead_magnet", "Recursos gratuitos"),
)
LEGAL_PAGES = (("terminos", "Términos"), ("privacidad", "Privacidad"),
               ("reembolso", "Reembolsos"), ("licencia", "Licencia"))
SITE_CSS = "\n".join([
    "*{box-sizing:border-box;margin:0;padding:0}",
    ":root{--bg:#08080c;--panel:#0e0e15;--line:rgba(255,255,255,.09);--text:#f4f4f5;--muted:#9d9dab;--accent:#10b981;--gold:#f59e0b;--mono:ui-monospace,SFMono-Regular,Consolas,monospace}",
    "body{background:var(--bg);color:var(--text);font:16px/1.65 -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background-image:radial-gradient(900px 500px at 80% -10%,rgba(224,122,95,.10),transparent 60%),radial-gradient(700px 420px at -10% 110%,rgba(16,185,129,.07),transparent 60%);min-height:100vh}",
    ".wrap{max-width:1080px;margin:0 auto;padding:40px 20px 72px}",
    ".top{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:30px}",
    ".brand{display:flex;align-items:center;gap:10px}.mark{width:34px;height:34px;border-radius:9px;display:grid;place-items:center;background:var(--accent);color:#08080c;font-weight:900}",
    ".brand b{letter-spacing:.14em;font-size:12px;text-transform:uppercase}",
    "h1{font-size:clamp(28px,4.6vw,46px);line-height:1.06;letter-spacing:-.035em;margin-bottom:12px}",
    "h2{font-size:20px;letter-spacing:-.02em;margin:34px 0 14px;padding-bottom:8px;border-bottom:1px solid var(--line)}",
    "p{color:var(--muted);font-size:15px;line-height:1.65}.lead{font-size:17px;max-width:720px}",
    ".hero{display:grid;grid-template-columns:1.4fr .6fr;gap:24px;align-items:center;margin-bottom:22px}",
    ".hero img{width:100%;border-radius:16px;border:1px solid var(--line);display:block}",
    ".stats{display:flex;gap:10px;flex-wrap:wrap;margin:18px 0}.chip{border:1px solid var(--line);background:var(--panel);border-radius:99px;padding:6px 12px;font:11px var(--mono);color:var(--muted)}",
    ".chip.ok{color:var(--accent);border-color:rgba(16,185,129,.35)}.chip.warn{color:var(--gold);border-color:rgba(245,158,11,.35)}",
    ".grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:16px}",
    ".card{background:var(--panel);border:1px solid var(--line);border-radius:14px;overflow:hidden;display:flex;flex-direction:column;text-decoration:none;color:inherit;transition:border-color .15s}",
    ".card:hover{border-color:rgba(16,185,129,.45)}.card img{width:100%;aspect-ratio:2/3;object-fit:cover;display:block;background:#0a0a10}",
    ".card .body{padding:12px 13px 14px;display:flex;flex-direction:column;gap:6px;flex:1}",
    ".card .fmt{font:10px var(--mono);letter-spacing:.1em;text-transform:uppercase;color:var(--accent)}",
    ".card h3{font-size:14px;line-height:1.3}.card p{font-size:12px;line-height:1.5}",
    ".card .row{display:flex;justify-content:space-between;align-items:center;margin-top:auto;padding-top:8px;font:12px var(--mono)}",
    ".price{color:var(--text);font-weight:700}.state{color:var(--muted)}.state.pending{color:var(--gold)}.state.free{color:var(--accent)}",
    "footer{margin-top:44px;padding-top:18px;border-top:1px solid var(--line);font:12px var(--mono);color:#71717f;line-height:1.8}",
    "footer nav{display:flex;flex-wrap:wrap;gap:6px 16px;margin-top:10px}footer a{color:#a1a1ad;text-decoration:none;border-bottom:1px solid rgba(255,255,255,.16)}",
    ".note{border:1px solid rgba(245,158,11,.35);background:rgba(245,158,11,.07);border-radius:12px;padding:13px 15px;font-size:13px;color:#fbd38d;margin:16px 0}",
    "article{max-width:780px}article h2{margin-top:28px}article ul{margin:10px 0 0 20px;display:grid;gap:8px}article li{color:var(--muted);font-size:14px}",
    "a.back{color:var(--accent);text-decoration:none;font:12px var(--mono)}",
    "@media(max-width:760px){.hero{grid-template-columns:1fr}.hero img{max-width:260px}}",
])


def esc(value: object) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def price_label(sku: ProductSKU) -> str:
    return "Gratis" if sku.price_usd <= 0 else f"${sku.price_usd:.0f} USD"


def cover_rel(sku: ProductSKU) -> str:
    return f"assets/covers/{sku.sku_id}_v1.webp"


def route_prefix(sku: ProductSKU) -> str:
    return sku.bridge_route.strip("/").split("/")[0]


def _shell(title: str, body: str, footer: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="es"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(title)} — Ronin Ventas OS, productos digitales con licencia personal.">
<style>{SITE_CSS}</style>
</head><body><div class="wrap">
{body}
<footer>{footer}</footer>
</div></body></html>"""


def _legal_links(prefix: str, home: str = "") -> str:
    links = "".join(f'<a href="{prefix}{slug}/">{esc(label)}</a>' for slug, label in LEGAL_PAGES)
    home_link = f'<a href="{home}">Inicio del sitio</a>' if home else ""
    return f'<nav aria-label="Páginas legales">{links}{home_link}</nav>'


def build_store_html(catalog: list[ProductSKU], generated_at: str) -> str:
    paid = [sku for sku in catalog if sku.price_usd > 0]
    leads = [sku for sku in catalog if sku.price_usd <= 0]
    ready = [sku for sku in paid if sku.gumroad_url or sku.hotmart_url]
    sections = []
    for fmt, label in FORMAT_GROUPS:
        items = [sku for sku in catalog if sku.format == fmt]
        if not items:
            continue
        cards = []
        for sku in items:
            configured = bool(sku.gumroad_url or sku.hotmart_url) or sku.price_usd <= 0
            state = "Gratis" if sku.price_usd <= 0 else ("Checkout listo" if configured else "Checkout pendiente")
            state_class = "free" if sku.price_usd <= 0 else ("" if configured else " pending")
            cards.append(
                f'<a class="card" href="{route_prefix(sku)}/{esc(sku.slug)}/">'
                f'<img src="{cover_rel(sku)}" alt="Portada de {esc(sku.title)}" loading="lazy" width="230" height="345">'
                f'<div class="body"><span class="fmt">{esc(sku.sku_id)} · {esc(sku.format)}</span>'
                f'<h3>{esc(sku.title)}</h3><p>{esc(sku.subtitle[:120])}{"..." if len(sku.subtitle) > 120 else ""}</p>'
                f'<div class="row"><span class="price">{esc(price_label(sku))}</span>'
                f'<span class="state{state_class}">{esc(state)}</span></div></div></a>'
            )
        sections.append(f'<h2 id="{fmt}">{esc(label)} ({len(items)})</h2><div class="grid">{"".join(cards)}</div>')
    hero = (
        '<div class="hero"><div><h1>Los 55 activos del catálogo Ronin</h1>'
        '<p class="lead">Blueprints, bóvedas, micro-apps HTML, sistemas y mega-bundles. '
        "Cada SKU tiene su propia ruta puente semántica, su precio y su estado real de checkout.</p></div>"
        '<img src="assets/ron/stan_hero_ai.webp" alt="Ron, identidad visual de Ronin Ventas OS" '
        'loading="lazy" width="420" height="520"></div>'
    )
    stats = (
        f'<div class="stats"><span class="chip">{len(catalog)} SKUs</span>'
        f'<span class="chip">{len(paid)} de pago</span><span class="chip">{len(leads)} gratis</span>'
        f'<span class="chip{" ok" if ready else " warn"}">Checkout configurado: {len(ready)}/{len(paid)}</span></div>'
    )
    note = ""
    if len(ready) < len(paid):
        note = (
            f'<div class="note">Hay {len(paid) - len(ready)} SKUs de pago sin pasarela asignada. '
            "Sus páginas no muestran un botón de compra que no funcione: se configura desde el "
            "panel de Publicación del sistema.</div>"
        )
    body = (
        f'<header class="top"><div class="brand"><span class="mark">R</span><b>Ronin Ventas OS</b></div>'
        f'<span class="chip">Sitio estático · {esc(generated_at)}</span></header>'
        f"{hero}{stats}{note}{''.join(sections)}"
    )
    footer = (
        "Producto digital. Sin promesas de ingresos. Sin resultados garantizados. "
        "Licencia personal no transferible. "
        f"Generado automáticamente el {esc(generated_at)}.{_legal_links('legal/')}"
    )
    return _shell("Tienda — Ronin Ventas OS", body, footer)


def build_404_html() -> str:
    body = (
        '<div class="brand" style="margin-bottom:20px"><span class="mark">R</span>'
        '<b>Ronin Ventas OS</b></div><h1>Ruta no encontrada</h1>'
        '<p class="lead">La página que buscas no existe en este sitio estático. '
        'Las 55 rutas del catálogo están en la tienda.</p>'
        '<p style="margin-top:18px"><a class="back" href="index.html">Volver a la tienda</a></p>'
    )
    return _shell("404 — Ronin Ventas OS", body,
                  "Sitio estático generado por Ronin Ventas OS." + _legal_links(""))


def build_threads_content(feeds: dict, route_by_sku: dict[str, str]) -> list[dict]:
    items = []
    for post in feeds.get("threads", []):
        sku_id = post.get("target_sku_id", "")
        slides = post.get("body_slides") or []
        items.append({
            "id": post.get("post_id"),
            "platform": "threads",
            "text": "\n\n".join(slides),
            "self_replies": post.get("suggested_self_replies", []),
            "image": f"assets/covers/{sku_id}_v1.webp" if sku_id else None,
            "target_route": route_by_sku.get(sku_id, ""),
            "target_sku_id": sku_id,
            "status": post.get("status", "queued"),
            "note": "Seguimiento local. El sitio no publica en Threads.",
        })
    return items


def build_pinterest_content(feeds: dict, route_by_sku: dict[str, str]) -> list[dict]:
    items, pins_dir = [], DATA_DIR / "generated_images"
    for pin in feeds.get("pinterest", []):
        # Los pines de benchmark (competencia) no se publican: igual que /api/publish/kit.
        if pin.get("is_competitor_benchmark"):
            continue
        image_url = (pin.get("image_url") or "").strip()
        image = None
        if image_url and image_url.startswith("/generated_images/"):
            name = Path(image_url).name
            if (pins_dir / name).is_file():
                image = f"assets/pins/{name}"
        sku_id = pin.get("target_sku_id", "")
        items.append({
            "id": pin.get("pin_id"),
            "platform": "pinterest",
            "title": pin.get("seo_title", ""),
            "description": pin.get("seo_description", ""),
            "text": f'{pin.get("overlay_headline", "")} | {pin.get("overlay_badge", "")}',
            "board": pin.get("board_name", ""),
            "image": image,
            "image_source": image_url or None,
            "target_route": route_by_sku.get(sku_id, pin.get("bridge_route", "")),
            "target_sku_id": sku_id,
            "status": pin.get("status", "queued"),
            "note": "Seguimiento local. El sitio no publica en Pinterest.",
        })
    return items


def content_readme(threads: int, pins: int, base_url: str) -> str:
    return "\n".join([
        "# Cola de contenido del sitio",
        "",
        f"Contenido exportado de `data/social_feeds.json`: {threads} piezas de Threads y {pins} pines.",
        "Las imágenes están en `assets/pins/` y `assets/covers/`. El texto está listo para copiar.",
        "",
        "## Importante",
        "",
        "- Este sitio NO publica en ninguna red social: solo deja la cola lista y enlazada a su ruta puente.",
        "- Marca el seguimiento en el panel de Publicación (estado local `published`/`queued`).",
        "- No repitas la misma URL del catálogo en menos de 72 horas.",
        "- Verifica el texto y la imagen antes de publicar; nada se envía automáticamente.",
        "",
        f"Base del sitio: {base_url or '(sin base_url configurada)'}",
        "",
    ])


def write_json(path: Path, payload: object) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    path.write_text(text, encoding="utf-8")
    return len(text.encode("utf-8"))


def generated_stamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")
