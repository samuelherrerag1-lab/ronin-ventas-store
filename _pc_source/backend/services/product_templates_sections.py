"""Secciones, CSS y JS del entregable de respaldo.

Separado de `product_templates_elite.py` para respetar el límite de 250 líneas
por archivo (AGENTS.md). Sin enlaces externos, sin emojis y sin cifras de
ingresos: solo estructura, herramientas locales y textos verificables.
"""

import base64
import html
import json
from functools import lru_cache

from backend.config import DATA_DIR
from backend.models.catalog_models import ProductSKU

HOOKS = [
    "El problema no es que falte información: es que nadie la empaqueta en un orden ejecutable.",
    "Un entregable se juzga por lo que el comprador logra en los primeros diez minutos.",
    "Si tu oferta necesita una explicación de tres párrafos, todavía no es una oferta.",
    "La promesa debe poder comprobarse esta semana; si no, es una fantasía con buen diseño.",
    "Diseñar para búsqueda es más rentable que diseñar para el aplauso inmediato.",
    "Cada campo extra en el checkout es una decisión de compra que le devuelves al comprador.",
    "El precio se defiende con especificidad: qué incluye, qué no, cuánto tarda.",
    "Una ruta puente propia evita que tu tráfico dependa de un dominio ajeno.",
    "El catálogo se ordena por problema resuelto, no por formato de archivo.",
    "Una prueba de compra real vale más que veinte opiniones.",
    "La licencia clara protege al comprador y al negocio; la ambigüedad no.",
    "El soporte se diseña antes de la venta: cómo descarga, cómo instala, cómo pide ayuda.",
    "Los datos del comprador son una responsabilidad, no un activo para vender.",
    "Si no puedes explicar tu producto sin exagerar, aún no has terminado de definirlo.",
    "Publicar menos y medir mejor supera a publicar todos los días sin registro.",
    "El criterio de muerte de una pieza debe definirse antes de lanzarla.",
    "Una colección de plantillas invisibles no se vende: escríbelas completas o recórtalas.",
    "La coherencia entre precio, promesa y contenido es lo que evita reembolsos.",
    "La distribución se planifica igual que el producto: archivo, canal, fecha, métrica.",
    "Un sistema se mantiene cuando la siguiente persona puede usarlo sin ti.",
]

PLAN_DAYS = [
    "Día 1: definir el problema específico y el comprador concreto.",
    "Día 2: escribir la promesa en una frase verificable.",
    "Día 3: fijar el contenido exacto del entregable y su licencia.",
    "Día 4: maquetar el entregable y probarlo sin conexión.",
    "Día 5: asignar precio y comprobar que la pasarela cobra en la moneda correcta.",
    "Día 6: conectar la ruta puente con doble checkout (si hay pasarelas configuradas).",
    "Día 7: hacer una compra de prueba completa y recorrer la entrega.",
    "Día 8: preparar la primera tanda de piezas de contenido.",
    "Día 9: publicar y registrar hora, canal y enlace.",
    "Día 10: revisar clics a la ruta puente.",
    "Día 11: ajustar la pieza con peor resultado y documentar el cambio.",
    "Día 12: comprobar soporte y plantilla de respuestas.",
    "Día 13: revisar términos, privacidad, reembolso y licencia en el sitio.",
    "Día 14: decidir con datos: corregir, repetir o retirar la oferta.",
]

QA_ITEMS = [
    "El archivo abre sin conexión y sin errores en consola.",
    "El título, el precio y la ruta puente coinciden con el catálogo.",
    "La compra de prueba entrega el archivo correcto.",
    "La política de reembolso y la licencia son visibles antes de pagar.",
    "No hay lorem ipsum, cifras sin fuente ni promesas de ingresos.",
    "El correo de soporte aparece en el recibo de compra.",
]

CSS = "\n".join([
    "*{box-sizing:border-box;margin:0;padding:0}",
    ":root{--bg:#07090e;--side:#0b0e17;--panel:#111522;--line:#1f273d;--accent:#10b981;--gold:#f59e0b;--danger:#ef4444;--text:#f3f4f6;--muted:#94a3b8;--mono:ui-monospace,SFMono-Regular,Consolas,monospace}",
    "body{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;display:flex;min-height:100vh}",
    "aside{width:288px;background:var(--side);border-right:1px solid var(--line);display:flex;flex-direction:column;flex-shrink:0}",
    ".brand{padding:18px;border-bottom:1px solid var(--line)}.tag{font-family:var(--mono);font-size:10px;font-weight:700;color:var(--accent);letter-spacing:.1em;text-transform:uppercase}",
    ".brand h2{font-size:15px;margin-top:4px}nav{flex:1;overflow-y:auto;padding:10px 8px}",
    ".nav-item{display:flex;gap:10px;width:100%;padding:9px 12px;border-radius:8px;border:1px solid transparent;background:transparent;color:var(--muted);font-size:12px;cursor:pointer;text-align:left;margin-bottom:3px}",
    ".nav-item:hover{background:rgba(255,255,255,.03);color:#fff}.nav-item.active{background:var(--panel);border-color:var(--line);color:#fff;font-weight:600}.num{font-family:var(--mono);font-size:10px;color:var(--accent)}",
    "main{flex:1;display:flex;flex-direction:column;min-width:0}.topbar{padding:14px 28px;border-bottom:1px solid var(--line);display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;background:rgba(11,14,23,.85);position:sticky;top:0;z-index:10}",
    ".content{padding:24px 28px;max-width:960px;width:100%}.tab-content{display:none}.tab-content.active{display:block}",
    "h1,h2,h3,h4{letter-spacing:-.02em}h2{font-size:20px;margin-bottom:10px}h3{font-size:15px;margin-bottom:8px}p{color:var(--muted);font-size:13px;line-height:1.65}",
    ".badge{display:inline-flex;padding:3px 9px;border-radius:99px;font:600 11px var(--mono);border:1px solid var(--line)}",
    ".badge-green{background:rgba(16,185,129,.12);color:var(--accent);border-color:rgba(16,185,129,.3)}.badge-gold{background:rgba(245,158,11,.12);color:var(--gold);border-color:rgba(245,158,11,.3)}",
    ".badge-red{background:rgba(239,68,68,.12);color:var(--danger);border-color:rgba(239,68,68,.3)}",
    ".notice{border:1px solid rgba(245,158,11,.4);background:rgba(245,158,11,.07);border-radius:12px;padding:14px;margin-bottom:18px;font-size:12px;line-height:1.6;color:#fbd38d}",
    ".card{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:20px;margin-bottom:18px}",
    ".cover{width:100%;max-width:260px;border-radius:12px;border:1px solid var(--line);display:block;margin-bottom:16px;aspect-ratio:2/3;object-fit:cover}",
    ".grid-2{display:grid;grid-template-columns:1fr 1fr;gap:16px}.kpi{font:800 26px var(--mono);color:var(--accent);margin:4px 0}",
    "label{display:block;font:600 11px var(--mono);text-transform:uppercase;letter-spacing:.05em;color:var(--muted);margin:8px 0 5px}",
    "input,select{width:100%;background:#080a10;border:1px solid var(--line);color:#fff;border-radius:8px;padding:9px 11px;font-size:13px}",
    "button{background:var(--accent);color:#05130b;font-weight:700;border:none;border-radius:8px;padding:9px 14px;cursor:pointer;font:600 12px var(--mono)}button.ghost{background:transparent;color:var(--text);border:1px solid var(--line)}",
    ".hook{background:#0b0e17;border:1px solid var(--line);border-radius:10px;padding:12px 14px;margin-bottom:9px;position:relative}.hook p{color:var(--text);font-size:13px;padding-right:74px}",
    ".copy{position:absolute;right:12px;top:12px;font:10px var(--mono);background:var(--panel);color:var(--muted);border:1px solid var(--line);padding:3px 7px;border-radius:6px;cursor:pointer}",
    ".check{display:flex;align-items:flex-start;gap:10px;background:#0b0e17;border:1px solid var(--line);border-radius:9px;padding:11px 13px;margin-bottom:7px;cursor:pointer;font-size:12px;color:var(--text)}",
    ".check.done{border-color:var(--accent);background:rgba(16,185,129,.05)}",
    "pre{background:#080a10;border:1px solid var(--line);border-radius:10px;padding:12px;font:12px var(--mono);color:#a5b4fc;overflow-x:auto;line-height:1.45}",
    ".toast{position:fixed;bottom:20px;right:20px;background:var(--accent);color:#04120a;font:700 12px var(--mono);padding:9px 14px;border-radius:8px;display:none;z-index:100}",
    "footer{border-top:1px solid var(--line);margin-top:26px;padding-top:14px;font:11px var(--mono);color:#6e6e7a;line-height:1.7}",
    "@media(max-width:820px){body{display:block}aside{width:100%;border-right:none;border-bottom:1px solid var(--line)}nav{display:flex;gap:6px;overflow-x:auto;padding:8px}.nav-item{width:auto;white-space:nowrap}.content{padding:18px 16px}.grid-2{grid-template-columns:1fr}}",
])

JS = "\n".join([
    "const SKU = __SKU_JSON__;",
    "const HOOKS = __HOOKS_JSON__;",
    "const PLAN = __PLAN_JSON__;",
    "const QA = __QA_JSON__;",
    "function $(id){return document.getElementById(id);}",
    "function esc(value){const d=document.createElement('div');d.textContent=String(value);return d.innerHTML;}",
    "function switchTab(index){document.querySelectorAll('.tab-content').forEach(function(el){el.classList.remove('active');});document.querySelectorAll('.nav-item').forEach(function(el){el.classList.remove('active');});var tab=$('tab'+index);if(tab){tab.classList.add('active');}var items=document.querySelectorAll('.nav-item');if(items[index-1]){items[index-1].classList.add('active');}}",
    "function calc(){var goal=parseFloat($('goal').value)||0;var price=parseFloat($('price').value)||0;var variable=parseFloat($('variable').value)||0;var margin=price-variable;var units=margin>0?Math.ceil(goal/margin):0;$('units').textContent=String(units);$('gross').textContent=margin>0?'$'+(units*price).toFixed(2)+' USD':'Margen negativo';$('margin').textContent='$'+margin.toFixed(2)+' USD';}",
    "function renderHooks(){var q=($('hookSearch').value||'').toLowerCase();var list=HOOKS.filter(function(h){return h.toLowerCase().indexOf(q)>=0;});$('hooks').innerHTML=list.map(function(h){return '<div class=\"hook\"><p>'+esc(h)+'</p><button class=\"copy\" data-hook=\"'+esc(h)+'\">Copiar</button></div>';}).join('');document.querySelectorAll('[data-hook]').forEach(function(btn){btn.addEventListener('click',function(){copyText(btn.getAttribute('data-hook'));});});}",
    "function storageKey(){return 'ronin:fallback:'+SKU.sku_id+':';}",
    "function loadChecked(prefix){try{return JSON.parse(localStorage.getItem(storageKey()+prefix)||'[]');}catch(e){return [];}}",
    "function saveChecked(prefix,values){localStorage.setItem(storageKey()+prefix,JSON.stringify(values));}",
    "function renderList(container,prefix,items){var checked=loadChecked(prefix);$(container).innerHTML=items.map(function(text,i){var done=checked.indexOf(i)>=0;return '<div class=\"check '+(done?'done':'')+'\" data-list=\"'+prefix+'\" data-index=\"'+i+'\"><input type=\"checkbox\" '+(done?'checked':'')+' aria-label=\"'+esc(text)+'\"><span'+(done?' style=\"text-decoration:line-through;opacity:.6\"':'')+'>'+esc(text)+'</span></div>';}).join('');document.querySelectorAll('[data-list=\"'+prefix+'\"]').forEach(function(row){row.addEventListener('click',function(){var idx=parseInt(row.getAttribute('data-index'),10);var list=loadChecked(prefix);var pos=list.indexOf(idx);if(pos>=0){list.splice(pos,1);}else{list.push(idx);}saveChecked(prefix,list);renderList(container,prefix,items);});});}",
    "function copyText(text){var toast=$('toast');var done=function(){toast.style.display='block';setTimeout(function(){toast.style.display='none';},1600);};if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(text).then(done,done);}else{var area=document.createElement('textarea');area.value=text;document.body.appendChild(area);area.select();document.execCommand('copy');area.remove();done();}}",
    "function manifest(){return JSON.stringify(SKU,null,2);}",
    "function exportMarkdown(){var md='# '+SKU.title+' ('+SKU.sku_id+')\\n\\n**Precio:** $'+SKU.price_usd+' USD\\n**Ruta:** '+SKU.bridge_route+'\\n\\n> Plantilla de respaldo generada automáticamente. No sustituye al entregable verificado.\\n\\n## Hooks\\n'+HOOKS.map(function(h,i){return (i+1)+'. '+h;}).join('\\n');var blob=new Blob([md],{type:'text/markdown'});var link=document.createElement('a');link.href=URL.createObjectURL(blob);link.download=SKU.sku_id.toLowerCase()+'_respaldo.md';link.click();}",
    "document.addEventListener('DOMContentLoaded',function(){$('manifest').textContent=manifest();renderHooks();renderList('planList','plan',PLAN);renderList('qaList','qa',QA);calc();});",
])


def esc(value: object) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


@lru_cache(maxsize=128)
def cover_data_uri(sku_id: str) -> str:
    candidates = (
        DATA_DIR / "product_art" / "web" / "covers" / f"{sku_id}_v1.webp",
        DATA_DIR / "product_art" / "web" / f"{sku_id}.webp",
    )
    for candidate in candidates:
        try:
            if candidate.is_file() and candidate.stat().st_size > 0:
                payload = base64.b64encode(candidate.read_bytes()).decode("ascii")
                return f"data:image/webp;base64,{payload}"
        except OSError:
            continue
    return ""


def nav_buttons() -> str:
    labels = (
        "Alcance y respaldo", "Errores que invalidan", "Calculadora de equilibrio",
        f"Bóveda de {len(HOOKS)} hooks", "Arquitectura de la oferta", "Plan de 14 días",
        "QA antes de publicar", "Exportar manifiesto",
    )
    return "".join(
        f'<button class="nav-item{" active" if i == 1 else ""}" onclick="switchTab({i})">'
        f'<span class="num">{i:02d}</span> {esc(label)}</button>'
        for i, label in enumerate(labels, start=1)
    )


def _tab(index: int, title: str, body: str) -> str:
    active = " active" if index == 1 else ""
    return f'<div id="tab{index}" class="tab-content{active}"><div class="card">{body}</div></div>'


def build_modules(sku: ProductSKU) -> str:
    """Construye los 8 módulos del entregable de respaldo."""
    title, tag = esc(sku.title), '<span class="tag">'
    tab1 = (
        f'{tag}Módulo 01 · Alcance</span><h2>{title}</h2><p>{esc(sku.subtitle)}</p>'
        f'<p style="margin-top:10px"><strong style="color:var(--text)">Ángulo del SKU:</strong> {esc(sku.hook_angle)}</p>'
        f'<p style="margin-top:10px"><strong style="color:var(--text)">Entregable declarado:</strong> {esc(sku.deliverable_spec)}</p>'
        '<div class="grid-2" style="margin-top:16px"><div><h3>Qué es esta plantilla</h3>'
        '<p>Un esqueleto de trabajo con la estructura editorial del producto y herramientas locales '
        '(checklist, calculadora aritmética, manifiesto) para reconstruir el entregable sin conexión.</p></div>'
        '<div><h3>Qué no es</h3><p>No es el producto final, no promete resultados y no incluye cifras de ingresos. '
        'Si el archivo verificado existe, la fábrica lo preserva y este documento no se sirve.</p></div></div>'
    )
    tab2 = (
        f'{tag}Módulo 02 · Integridad</span><h2>Errores que invalidan un entregable</h2>'
        '<ul style="list-style:none;display:grid;gap:9px;margin-top:12px">'
        '<li style="color:var(--muted);font-size:13px">Mostrar cifras de ingresos sin fuente ni fecha.</li>'
        '<li style="color:var(--muted);font-size:13px">Prometer ingresos garantizados o resultados automáticos.</li>'
        '<li style="color:var(--muted);font-size:13px">Dejar lorem ipsum, marcadores de plantilla o secciones vacías.</li>'
        '<li style="color:var(--muted);font-size:13px">Depender de CDNs, fuentes remotas o conexión a internet.</li>'
        '<li style="color:var(--muted);font-size:13px">Ocultar la licencia, el reembolso o la política de datos.</li></ul>'
        '<p class="notice" style="margin-top:14px">Esta plantilla se genera solo cuando falta el archivo verificado. '
        'Nunca sobrescribe un entregable existente ni un lead magnet.</p>'
    )
    tab3 = (
        f'{tag}Módulo 03 · Aritmética</span><h2>Calculadora de punto de equilibrio</h2>'
        '<p>Aritmética simple, no un pronóstico: cuántas unidades cubren un objetivo, con su margen.</p>'
        '<div class="grid-2" style="margin-top:14px"><div>'
        '<label for="goal">Objetivo mensual (USD)</label><input id="goal" type="number" value="500" min="0">'
        f'<label for="price">Precio unitario (USD)</label><input id="price" type="number" value="{sku.price_usd:.0f}" min="0">'
        '<label for="variable">Costo variable por unidad (USD)</label><input id="variable" type="number" value="0" min="0">'
        '<button onclick="calc()">Calcular</button></div><div>'
        '<div style="font:11px var(--mono);color:var(--muted)">UNIDADES NECESARIAS</div><div id="units" class="kpi">0</div>'
        '<div style="font:11px var(--mono);color:var(--muted)">MARGEN POR UNIDAD</div><div id="margin" class="kpi" style="color:var(--gold)">$0</div>'
        '<div style="font:11px var(--mono);color:var(--muted)">INGRESO BRUTO IMPLICADO</div><div id="gross" class="kpi" style="color:#60a5fa">$0</div>'
        '</div></div><p class="notice" style="margin-top:14px">Este cálculo no garantiza ventas ni ingresos: '
        'solo divide un objetivo entre un margen.</p>'
    )
    tab4 = (
        f'{tag}Módulo 04 · Marco</span><h2>Bóveda de {len(HOOKS)} hooks de marco</h2>'
        '<p>Frases de marco para adaptar, no casos de éxito. Ninguna afirma resultados.</p>'
        '<input id="hookSearch" placeholder="Filtrar hooks por palabra" aria-label="Filtrar hooks" '
        'oninput="renderHooks()" style="margin:12px 0"><div id="hooks"></div>'
    )
    tab5 = (
        f'{tag}Módulo 05 · Oferta</span><h2>Arquitectura de la oferta</h2>'
        '<div class="grid-2" style="margin-top:12px">'
        '<div><h3>Producto</h3><p>Un entregable verificado, con licencia personal no transferible y soporte declarado.</p></div>'
        f'<div><h3>Ruta puente</h3><p>URL semántica propia ({esc(sku.bridge_route)}) antes de la pasarela, para medir sin quemar dominio.</p></div>'
        '<div><h3>Checkout</h3><p>Solo se activa cuando la pasarela esté configurada. Si falta, la landing lo dice.</p></div>'
        '<div><h3>Contenido</h3><p>Cola editorial con enlace corto y registro de publicación en una hoja local.</p></div></div>'
        '<p class="notice" style="margin-top:14px">Ningún paso promete ingresos; cada uno produce evidencia medible o no se considera hecho.</p>'
    )
    tab6 = (
        f'{tag}Módulo 06 · Ejecución</span><h2>Plan de 14 días</h2>'
        '<p>Marca el avance. Sin promesas: solo tareas y su comprobación.</p><div id="planList" style="margin-top:14px"></div>'
    )
    tab7 = (
        f'{tag}Módulo 07 · Control</span><h2>QA antes de publicar</h2>'
        '<p>Si un punto falla, no se publica.</p><div id="qaList" style="margin-top:14px"></div>'
    )
    tab8 = (
        f'{tag}Módulo 08 · Manifiesto</span><h2>Manifiesto del SKU</h2><pre id="manifest"></pre>'
        '<div style="display:flex;gap:10px;margin-top:14px;flex-wrap:wrap">'
        '<button onclick="copyText(manifest())">Copiar manifiesto JSON</button>'
        '<button class="ghost" onclick="exportMarkdown()">Descargar documento Markdown</button></div>'
    )
    return "".join([
        _tab(1, "Alcance", tab1), _tab(2, "Integridad", tab2), _tab(3, "Aritmética", tab3),
        _tab(4, "Marco", tab4), _tab(5, "Oferta", tab5), _tab(6, "Ejecución", tab6),
        _tab(7, "Control", tab7), _tab(8, "Manifiesto", tab8),
    ])
