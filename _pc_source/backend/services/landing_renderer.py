"""Landing server-rendered para cada ruta puente.

Sin JavaScript, sin dependencias externas y sin promesas de ingresos.
Si el checkout no está configurado, lo dice en vez de fingir un botón o una
pasarela. `base_url` es opcional: sirve para canonical/OG absolutos y para que
el sitio estático generado por `publish_pack` tenga URLs canónicas reales.
"""

import html
import json
from typing import Optional

from backend.models.catalog_models import ProductSKU

FORMAT_LABEL = {
    "ebook_blueprint": "Blueprint editorial",
    "boveda_arsenal": "Bóveda de consulta",
    "micro_app_html": "Micro-app interactiva",
    "kit_sistema": "Sistema completo",
    "mega_bundle": "Mega-bundle",
    "lead_magnet": "Recurso gratuito",
}

LEGAL_PAGES = (
    ("terminos", "Términos"),
    ("privacidad", "Privacidad"),
    ("reembolso", "Reembolsos"),
    ("licencia", "Licencia"),
)

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{background:#08080c;color:#f4f4f5;font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
background-image:radial-gradient(900px 500px at 80% -10%,rgba(224,122,95,.10),transparent 60%),
radial-gradient(700px 420px at -10% 110%,rgba(16,185,129,.07),transparent 60%);min-height:100vh}
.wrap{max-width:760px;margin:0 auto;padding:48px 22px 64px}
.brand{display:flex;align-items:center;gap:10px;margin-bottom:44px}
.mark{width:34px;height:34px;border-radius:9px;display:grid;place-items:center;background:#10b981;color:#08080c;font-weight:900}
.brand b{letter-spacing:.14em;font-size:12px;text-transform:uppercase}
.eyebrow{display:inline-flex;gap:8px;align-items:center;font:11px ui-monospace,monospace;letter-spacing:.12em;
text-transform:uppercase;color:#f59e0b;border:1px solid rgba(245,158,11,.35);background:rgba(245,158,11,.08);
border-radius:99px;padding:5px 12px;margin-bottom:18px}
h1{font-size:clamp(30px,5vw,44px);line-height:1.06;letter-spacing:-.035em;margin-bottom:14px}
.sub{color:#b9b9c6;font-size:17px;margin-bottom:26px}
.cover{width:100%;max-width:340px;border-radius:16px;border:1px solid rgba(255,255,255,.10);
display:block;margin:0 0 26px;aspect-ratio:2/3;object-fit:cover;background:#0e0e15}
.price{display:flex;align-items:baseline;gap:12px;margin-bottom:28px;flex-wrap:wrap}
.price strong{font-size:40px;letter-spacing:-.03em}
.price span{color:#8b8b99;font:13px ui-monospace,monospace}
.card{background:#0e0e15;border:1px solid rgba(255,255,255,.08);border-radius:16px;padding:22px;margin-bottom:18px}
.card h2{font-size:13px;text-transform:uppercase;letter-spacing:.12em;color:#10b981;margin-bottom:12px}
ul{list-style:none;display:grid;gap:9px}
li{display:flex;gap:10px;color:#d6d6e0;font-size:15px}
li::before{content:"";width:6px;height:6px;border-radius:50%;background:#10b981;margin-top:9px;flex-shrink:0}
.cta{display:flex;flex-direction:column;gap:10px;margin:26px 0 10px}
.btn{display:block;text-align:center;text-decoration:none;padding:16px;border-radius:13px;font-weight:800;font-size:15px}
.btn-primary{background:#10b981;color:#04120c}
.btn-secondary{background:rgba(255,255,255,.06);color:#f4f4f5;border:1px solid rgba(255,255,255,.14)}
.disabled{background:rgba(255,255,255,.04);color:#8b8b99;border:1px dashed rgba(255,255,255,.18);cursor:not-allowed}
.note{font:12px ui-monospace,monospace;color:#7c7c8a;line-height:1.6}
.bump{border:1px dashed rgba(245,158,11,.45);background:rgba(245,158,11,.07);border-radius:14px;padding:16px;margin-bottom:18px}
.bump b{color:#f59e0b}
footer{margin-top:36px;padding-top:18px;border-top:1px solid rgba(255,255,255,.08);font:12px ui-monospace,monospace;color:#6e6e7a}
footer a{color:#9a9aa8;text-decoration:none;border-bottom:1px solid rgba(255,255,255,.16)}
footer nav{display:flex;flex-wrap:wrap;gap:6px 14px;margin-top:10px}
"""


def _esc(value: str) -> str:
    return html.escape(value or "", quote=True)


def _checkout_bullet(checkout_url: str) -> str:
    if "gumroad.com" in checkout_url:
        return "Pago procesado por Gumroad (tarjeta, Apple Pay o PayPal según tu país)."
    if "hotmart.com" in checkout_url:
        return "Pago procesado por Hotmart (Nequi, PSE, Efecty o tarjeta según tu país)."
    return "Pago procesado por la pasarela oficial de este producto."


def _bullets(sku: ProductSKU, checkout_url: str) -> list[str]:
    bullets = [
        f"Formato: {FORMAT_LABEL.get(sku.format, sku.format)}.",
        f"{sku.deliverable_spec}." if sku.deliverable_spec else "Entrega digital inmediata.",
        "Funciona sin conexión: un solo archivo, sin dependencias externas.",
        "Acceso de por vida y actualizaciones de la versión que compraste.",
    ]
    if checkout_url:
        bullets.append(_checkout_bullet(checkout_url))
    else:
        bullets.append("Aún sin pasarela asignada: no se muestra un botón de pago que no funcione.")
    if sku.price_cop:
        bullets.append(f"Precio local aproximado: {sku.price_cop:,} COP.".replace(",", "."))
    return bullets


def _canonical(sku: ProductSKU, base_url: str) -> str:
    if not base_url:
        return sku.bridge_route
    return f"{base_url.rstrip('/')}{sku.bridge_route}/"


def _cover_url(sku: ProductSKU, assets_href: str) -> str:
    return f"{assets_href.rstrip('/')}/covers/{sku.sku_id}_v1.webp"


def _legal_footer(legal_root: str, store_href: str) -> str:
    links = "".join(
        f'<a href="{_esc(legal_root)}{slug}/">{_esc(label)}</a>' for slug, label in LEGAL_PAGES
    )
    store_link = (
        f'<a href="{_esc(store_href)}">Tienda completa</a>' if store_href else ""
    )
    if not links and not store_link:
        return ""
    return f'<nav aria-label="Páginas legales">{links}{store_link}</nav>'


def render_landing(
    sku: ProductSKU,
    checkout_url: str = "",
    currency_note: str = "",
    base_url: str = "",
    assets_href: str = "/product_art",
    legal_root: str = "",
    store_href: str = "",
    download_href: str = "",
) -> str:
    price = "Gratis" if sku.price_usd == 0 else f"${sku.price_usd:.0f} USD"
    label = FORMAT_LABEL.get(sku.format, sku.format)
    bullets = "".join(f"<li>{_esc(b)}</li>" for b in _bullets(sku, checkout_url))
    cover = _cover_url(sku, assets_href)
    canonical = _canonical(sku, base_url)
    # OG debe ser URL absoluta y apuntar al asset del sitio, nunca concatenar una ruta relativa.
    og_image = (
        f"{base_url.rstrip('/')}/assets/covers/{sku.sku_id}_v1.webp"
        if base_url
        else cover
    )

    if checkout_url:
        cta = (
            f'<a class="btn btn-primary" href="{_esc(checkout_url)}" rel="noopener" '
            f'referrerpolicy="no-referrer-when-downgrade">Comprar ahora — {_esc(price)}</a>'
        )
    else:
        cta = (
            '<span class="btn disabled">Checkout aún no configurado</span>'
            '<p class="note">Este producto todavía no tiene pasarela asignada. '
            "No se muestra un botón de pago que no funcione.</p>"
        )

    if sku.price_usd <= 0:
        target = download_href or (
            f"/deliverables/{sku.sku_id.lower()}_{sku.slug}.html"
        )
        cta = (
            f'<a class="btn btn-primary" href="{_esc(target)}" '
            'rel="noopener">Descargar gratis</a>'
        )

    structured = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": sku.title,
            "description": sku.subtitle,
            "sku": sku.sku_id,
            "offers": {
                "@type": "Offer",
                "price": f"{sku.price_usd:.2f}",
                "priceCurrency": "USD",
                "availability": "https://schema.org/InStock",
                "url": canonical,
            },
        },
        ensure_ascii=False,
    )

    return f"""<!DOCTYPE html>
<html lang="es"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_esc(sku.title)}</title>
<meta name="description" content="{_esc(sku.subtitle)}">
<meta property="og:type" content="product">
<meta property="og:title" content="{_esc(sku.title)}">
<meta property="og:description" content="{_esc(sku.subtitle)}">
<meta property="og:image" content="{_esc(og_image)}">
<link rel="canonical" href="{_esc(canonical)}">
<script type="application/ld+json">{structured}</script>
<style>{CSS}</style>
</head><body><div class="wrap">
  <div class="brand"><span class="mark">R</span><b>Ronin Ventas OS</b></div>
  <span class="eyebrow">{_esc(label)} · {_esc(sku.sku_id)}</span>
  <h1>{_esc(sku.title)}</h1>
  <p class="sub">{_esc(sku.subtitle)}</p>
  <img class="cover" src="{_esc(cover)}" alt="Portada de {_esc(sku.title)}" loading="lazy" width="340" height="510">
  <div class="price"><strong>{_esc(price)}</strong>{f'<span>{_esc(currency_note)}</span>' if currency_note else ''}</div>

  <div class="card"><h2>Qué recibes</h2><ul>{bullets}</ul></div>
  <div class="card"><h2>El ángulo</h2><p class="note">{_esc(sku.hook_angle)}</p></div>

  <div class="bump"><b>Order bump opcional (+$9 USD)</b>
    <p class="note">Se ofrece dentro del checkout, no aquí. Si no lo quieres, no lo pagas.</p></div>

  <div class="cta">{cta}</div>

  <footer>
    Sin promesas de ingresos. Sin resultados garantizados. Producto digital de formación y herramientas.<br>
    Ruta: {_esc(sku.bridge_route)} · SKU {_esc(sku.sku_id)}
    {_legal_footer(legal_root, store_href)}
  </footer>
</div></body></html>"""


def checkout_for(sku: ProductSKU, preferred: Optional[str] = None) -> str:
    if preferred == "hotmart" and sku.hotmart_url:
        return sku.hotmart_url
    if preferred == "gumroad" and sku.gumroad_url:
        return sku.gumroad_url
    return sku.gumroad_url or sku.hotmart_url or ""
