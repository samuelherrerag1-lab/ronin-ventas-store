"""Entregable de RESPALDO (fallback), 100% offline y sin claims.

No fabrica un "producto élite" con estadísticas inventadas: genera un esqueleto
de trabajo marcado como respaldo, con CSS/JS reales y la portada real del SKU
incrustada en base64 (sin CDNs ni conexión).

Reglas aplicadas de la auditoría (A6/B3):
- Sin enlaces externos ni fuentes de Google.
- Sin emojis ni glifos decorativos.
- Sin promesas de ingresos ni cifras sin fuente.
- La etiqueta de hooks se calcula con `len(HOOKS)`, no se escribe a mano.
- La fábrica nunca usa este archivo para pisar un entregable verificado ni un
  lead magnet (ver `product_factory.is_protected_deliverable`).

Las secciones, CSS y JS viven en `product_templates_sections.py` para respetar
el límite de 250 líneas por archivo.
"""

import json

from backend.models.catalog_models import ProductSKU
from backend.services.product_templates_sections import (
    CSS,
    HOOKS,
    JS,
    PLAN_DAYS,
    QA_ITEMS,
    build_modules,
    cover_data_uri,
    esc,
    nav_buttons,
)


def _sku_json(sku: ProductSKU) -> str:
    return json.dumps(
        {
            "sku_id": sku.sku_id,
            "title": sku.title,
            "subtitle": sku.subtitle,
            "format": sku.format,
            "niche": sku.niche,
            "price_usd": sku.price_usd,
            "price_cop": sku.price_cop,
            "bridge_route": sku.bridge_route,
            "hook_angle": sku.hook_angle,
            "deliverable_spec": sku.deliverable_spec,
        },
        ensure_ascii=False,
    )


def build_script(sku: ProductSKU) -> str:
    """Inyecta los datos del SKU y las listas en el JS offline."""
    return (
        JS.replace("__SKU_JSON__", _sku_json(sku))
        .replace("__HOOKS_JSON__", json.dumps(HOOKS, ensure_ascii=False))
        .replace("__PLAN_JSON__", json.dumps(PLAN_DAYS, ensure_ascii=False))
        .replace("__QA_JSON__", json.dumps(QA_ITEMS, ensure_ascii=False))
    )


def build_cover_html(sku: ProductSKU) -> str:
    cover = cover_data_uri(sku.sku_id)
    if not cover:
        return '<div class="notice">Portada no encontrada en disco para este SKU. No se inventa arte.</div>'
    return (
        f'<img class="cover" src="{cover}" alt="Portada de {esc(sku.title)}" '
        'width="260" height="390">'
    )


def render_elite_product_html(sku: ProductSKU) -> str:
    """Devuelve la plantilla de respaldo completa, offline y sin claims."""
    title = esc(sku.title)
    cover_html = build_cover_html(sku)
    modules = build_modules(sku)
    script = build_script(sku)
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — Plantilla de respaldo</title>
<style>{CSS}</style>
</head>
<body>
<aside>
  <div class="brand">
    <div class="tag">@ronOverthinks · respaldo</div>
    <h2>{esc(sku.sku_id)} · {title}</h2>
    <div style="font-size:11px;color:var(--muted);margin-top:4px;font-family:var(--mono)">100% offline · sin CDN</div>
  </div>
  <nav id="navBar">{nav_buttons()}</nav>
  <div style="padding:14px;border-top:1px solid var(--line);font:11px var(--mono);color:var(--muted)">
    <div>Precio de catálogo: <strong style="color:var(--gold)">${sku.price_usd:.0f} USD</strong></div>
    <div>Ruta puente: {esc(sku.bridge_route)}</div>
  </div>
</aside>
<main>
  <div class="topbar">
    <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center">
      <span class="badge badge-red">PLANTILLA DE RESPALDO</span>
      <span class="badge badge-green">{esc(sku.format)}</span>
      <span class="badge badge-gold">{esc(sku.niche)}</span>
    </div>
    <button class="ghost" onclick="exportMarkdown()">Descargar Markdown</button>
  </div>
  <div class="content">
    <div class="notice">
      Documento generado automáticamente porque no había un entregable verificado en disco.
      No sustituye al producto original y no contiene estadísticas ni promesas de ingresos.
      Si eres el comprador, escribe al correo del recibo de compra para recibir la versión definitiva.
    </div>
    <div style="margin-bottom:18px">{cover_html}</div>
    {modules}
    <footer>
      Archivo de respaldo generado por Ronin Ventas OS. Sin promesas de ingresos. Sin resultados garantizados.
      Licencia personal no transferible para quien recibió este archivo desde su compra o descarga verificada.
      Ruta: {esc(sku.bridge_route)} · SKU {esc(sku.sku_id)}
    </footer>
  </div>
</main>
<div id="toast" class="toast">Copiado al portapapeles</div>
<script>{script}</script>
</body>
</html>"""
