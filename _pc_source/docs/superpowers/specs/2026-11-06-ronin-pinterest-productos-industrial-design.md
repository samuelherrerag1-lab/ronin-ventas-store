# Ronin — Pinterest + Productos a Nivel Industrial

**Fecha:** 2026-11-06
**Proyecto:** `ronin_ventas` — `@ronOverthinks`
**Estado:** Aprobado por el dueño (2026-11-06). Pendiente de builder check antes de plan de ejecución.

## 1. Intent y el porqué

El sistema actual produce 55 SKUs y 154 Threads + 72 Pines, pero el dueño nunca vio el resultado y al abrir `#pinterest_clone` y `#catalog_factory` lo descartó todo: infografías saturadas de 8px con cifras falsas (STEALTH 96, $47.00, 92% margen), Ron protagonista aburrido repetido 11 veces, portadas con Ron gigante, y un lead magnet L02 de sólo 27 hooks (≈1% de un producto aceptable).

La causa raíz no es estética, es estrategia: se olvidó la idea inicial — Caballo de Troya frío que ataca el ego y vende por gula, no folleto. La corrección es volver a la idea con métricas medibles y generación industrial.

Lo que sigue es **rehacer el layer visual y de productos a nivel industrial**, incluso si implica reescribir deliverables desde 0. El backend FastAPI (`0.0.0.0:8765`), el puente semántico 55 rutas y el Bait Studio se conservan como infraestructura. Lo que se tira es todo lo demás visual.

## 2. Goals / Non-Goals / Anti-Goals

### Goals
- Pinterest publicable en frío: 1 headline legible a 236px, 1 prueba visual, 1 ruta puente. 70% Dark Luxury / 30% Ron apoyo, medido por contenido visual, no por etiqueta JSON.
- Gobierno Ron verificable por código: Ron nunca protagonista full-bleed.
- Productos con estándar industrial: libro ≥20k palabras visibles con estructura, bóveda con ítems con ID verificables, app con lógica viva, kit sin truncado, bundle como ZIP real o nada.
- Generación reproducible: Vertex sólo fondo 1000x1500, texto compuesto en SVG/PIL, gate 236px, anti-repetición, pool ≥20 fondos únicos.

### Non-Goals
- Recolorear o parchar los actuales pines/covers. Se descartan, no se retocan.
- Cambiar precio para “arreglar” un producto malo. El precio se unifica después de mejorar el producto, no antes.
- Publicación automática en redes. La cola sigue siendo manual con seguimiento local.

### Anti-Goals (lo que sería un fracaso aunque funcione)
- Un pin bonito que nadie guarda ni clickea.
- Un ebook de 11k palabras vendido como “62 páginas”.
- Un bundle $99 con botones muertos.
- Ron grande y triste mirando el móvil sobre un cajero.
- **DEGRADAR CUALQUIER PRODUCTO JAMÁS (ley del dueño 2026-11-06).** Si algo es poco/desgradable por subasta, se expande 10x/100x y se mejora. Nada se renombra a Guía barata ni se baja de precio para esconder pobreza. La única palabra válida es EXPANSIÓN industrial.

## 3. Constraints

- Límite estricto 250 líneas por archivo `.py/.ts/.tsx`.
- Entorno Python oficial `C:\Users\EXAMPLE\Documents\ronin_ventas\.venv`.
- Cero placeholders en entregables, cero emojis en UI, cero estados falsos (`tests/test_honesty.py`).
- Vertex: proyecto `example-project-id`, `global`, `gemini-3.1-flash-image` (fallback `gemini-3.1-flash-lite-image`), ADC gcloud, ledger en `data/finops-ledger.json`, breaker `FINOPS_CIRCUIT_BREAKER_USD` (default 50).
- Gumroad: 10 drafts E01-E10 con pago ya conectado (2026-11-06). Falta habilitar/publicar. Hotmart sigue pendiente KYC.
- Marca: `@ronOverthinks`, Insider Cínico. Arte canónico en `data/generated_images/ron_canonical_seed.png` — referencia, no arte publicable.
- Sitio estático: `data/publish_site/` con `base_url` real, sitemap/robots/legal. Checkout honesto “aún no configurado” si falta URL.

## 4. Approaches (2-3 consideradas)

### A) Quirúrgico (descartada por lenta)
Sólo regenerar 10 pines + 5 SKUs de lanzamiento. Pro: cobra en 14 días. Contra: deja 47 SKUs malos que contaminan tienda y destruirían credibilidad el día 15. No cumple la exigencia industrial del dueño.

### B) Rehacer todo desde 0 (descartada por innecesaria)
Tirar backend + UI + puente. Contra: backend ya pasa 119/120 tests, build y LAN funcionales. Tirarlo es quemar 3 semanas sin ganar nada.

### C) Rehacer layer visual + productos, conservar infraestructura (elegida)
La elegida por el dueño 2026-11-06. Se descarta 100% pines/fondos/covers actuales, se reescribe `PinPosterCanvas` a 1 solo sistema, se regenera pool visual con nuevo gobierno Ron, y se rehacen los deliverables débiles a estándar industrial (incluso de 0 si hace falta). El backend y Bait Studio se conservan.

## 5. Las partes del cómo (decididas)

### 5.1 Gobierno Ron — ley mecánica
- **Máximo 30% de pines** con Ron. **0% en Dark Luxury frío**. Medido por inspector visual, no por `visual_theme`.
- **Tamaño 15-20% del frame, esquina inferior, de apoyo:**
  - Apuntando a un objeto/producto/`$418.50`, sacando un libro de una caja, resaltando un panel con linterna, con una lupa sobre un hook.
  - **Acción narrativa sólo en portadas de producto** (mismo apuntar/highlight, ligeramente mayor, pero nunca protagonista centrado).
- **Eliminados como fondo publicable:** `pin_ron_3am_blueprint.png`, `pin_ron_threads_atm.png`, `pin_ron_escape_matrix.png`, `pin_ron_dark_psychology.png`, `pin_luxury_watch_espresso.png` (es Ron, no reloj). Se conservan en cuarentena para referencia de consistencia.
- **Pool:** mínimo 20 fondos únicos. **Máximo 1 uso por fondo / 72h**. Repetir 11 veces = violación automática en CI.
- Verificación: script que cuente píxeles Ron >30% del frame rechazado; `product_art/manifest.json` marca `ron:true` sólo si es apoyo, no protagonista.

### 5.2 Pinterest — Caballo de Troya real
- **Formatos:** 1000x1500 exacto (no 864x1184 ni 768x1344). Verificado con Pillow antes de escribir JSON.
- **Composición (1 solo sistema, no 6 arquetipos):**
  - Fondo fotográfico sin texto.
  - **Headline 4-6 palabras, Bold, ≥110px a 1000w (≈26px a 236px)**, máx 2 líneas, en tercio oscuro reservado. Keyword al inicio para SEO, gancho de ataque para humano.
  - **Badge 1** (ej. `E01`, `B01`, `3:14 AM`, `$19`) + handle `@ronOverthinks` abajo. Nada más.
  - Prohibido: Protocolo 3 Fases, STEALTH 96, LATENCIA 0.12s, $47.00 simulado, 92% margen, “55 Rutas Puente Semánticas”, benchmark competidor.
- **Título SEO ≠ headline póster.** Título (100-150 chars) vive en metadata Pinterest; headline póster es el ataque. Hoy se mezclan, por eso los títulos de 60-70 chars se truncan.
- **DIVERSIDAD ESTÉTICA OBLIGATORIA (ley del dueño 2026-11-06):** NO solo Luxury. 20 pines deben parecer 20 ideas distintas que llaman al click: foto editorial Dark Luxury, persona vendiendo/comprando con móvil, mano con tarjeta Nequi/PSE, setup con logs, ajedrez, reloj, terminal con notificaciones, persona de espaldas con panel, Ron pequeño apuntando, pie en escenario, etc. Cada pin ataca un dolor distinto, sin copiar el anterior.
- **Los 72 actuales se descartan.** Se parte de 0 con lote inicial de 20 fichas el 1er día (14 sin Ron + 6 máximo con Ron apoyo, idealmente 3-4), una por ruta única, cada una atacando un dolor distinto (sin que la cara se vea obligatorio para Luxury — eso era invención del builder, nunca dicho por el dueño). En Ron apoyo la cara SÍ puede verse (cara canónica con ojeras), pero Ron pequeño 15-20% en esquina señalando, nunca protagonista.
- **Regla Ron 3-6/20:** máximo 3-6 pines de 20 llevan Ron. Los demás 14-17 son sin Ron. Cara de Ron sí permitida cuando aparece, pero pequeña y activa (apunta, resalta, sostiene), jamás grande y pasiva mirando móvil.

### 5.3 Portadas de producto
- **Las 55 actuales (`data/product_art/web/covers/*.webp` v1/v2) se descartan.** 3:4 sin título legible, Ron gigante, OCR roto (“MAQUINA SILENCIOSA DE ARCHIVOS PDF”).
- **Nueva portada:** objeto protagonista (libro/bóveda/app renders) + título corto + precio, y **Ron 15% en esquina apuntando/resaltando** (único lugar donde su acción se permite mayor). Variante Luxury sin Ron para fríos. No se reutiliza póster Pinterest (2:3) como portada (3:4).

### 5.4 Productos — estándar industrial, EXPANSIÓN SIEMPRE
- **LEY: jamás degradar, jamás renombrar a barato, jamás bajar de precio para tapar pobreza.** Todo lo que es poco se expande 10x/100x.
- **Libro/Ebook (E01-E12):** ≥20.000 palabras visibles reales con frameworks, tablas, casos, ejercicios, criterio de decisión. Si no llega, se expande con capítulos nuevos reales, no con relleno ni párrafos estirados. Hoy sólo E02 (31.8k) y E03 (32.8k) pasan. Los otros 10 (11-17k) se expanden 10x hasta 20k+ o no se publican.
- **Bóveda (B01-B12):** ítems con ID (`HK-001`, `B02-001`…), conteo verificable en DOM, capa estática imprimible + PDF. B02/B03/B04/B08 hoy son JS invisible a print/SEO — se remaquetan. B06 caníbaliza B05 (24 vs 120 prompts) — se expande a 150+ o no se publica.
- **Micro-App (A01-A12):** lógica viva (input → cálculo accionado). A03/A06/A10 hoy son selector de plantilla — se rehace motor real (la `{tesis}`/brief genera, no selecciona) o no se publican.
- **Kit (K01-K10):** suma sin truncado. Hoy K02 16.8k vs E02 31.8k (-47%), K03 26.2k vs E03 32.8k — se regenera con ebook completo verificable por `h2` count. Si truncado, no se vende como “Completo”.
- **Mega-Bundle (M01-M06): APARCADOS por orden del dueño 2026-11-06 — “mientras no me interesan, son estúpidos”. No se rehacen ni se venden hasta nuevo orden.**
- **Lead magnets (L01-L03):** L02 con 27 hooks queda **suspendido hasta expansión industrial**. Industrial = ≥500 hooks con nicho/mecanismo/voltaje + workbook imprimible + archivo sample (expansión 20x de los 27). L01 (31.6k + calculadora) y L03 (wizard 12 vars) se protegen.
- **Precios:** 1 sola fuente (`data/catalog.json`) después de mejorar. Portada + landing se regeneran mecánicamente desde ahí. Nunca se “arregla” un mal producto bajando precio.
- **Filtro publicación (crítica):** 0 SKUs están publicados hoy. Un agente cínico revisa producto a producto y dice **por qué NO lo compraría**. El sistema solo alcanza 10 APROBADOS para que el dueño los revise y apruebe para tráfico. Sin ese gate, nada sale a tienda aunque esté `generated`.

### 5.3 Portadas de producto
- **Las 55 actuales (`data/product_art/web/covers/*.webp` v1/v2) se descartan.** 3:4 sin título legible, Ron gigante, OCR roto (“MAQUINA SILENCIOSA DE ARCHIVOS PDF”).
- **Nueva portada:** objeto protagonista (libro/bóveda/app renders) + título corto + precio, y **Ron 15% en esquina apuntando** (único lugar donde su acción se permite mayor). Variante Luxury sin Ron para fríos. No se reutiliza póster Pinterest (2:3) como portada (3:4).

### 5.4 Productos — estándar industrial, EXPANSIÓN SIEMPRE
- **LEY: jamás degradar, jamás renombrar a barato, jamás bajar de precio para tapar pobreza.** Todo lo que es poco se expande 10x/100x.
- **Libro/Ebook (E01-E12):** ≥20.000 palabras visibles reales con frameworks, tablas, casos, ejercicios, criterio de decisión. Si no llega, se expande con capítulos nuevos reales, no con relleno ni párrafos estirados. Hoy sólo E02 (31.8k) y E03 (32.8k) pasan. Los otros 10 (11-17k) se expanden 10x hasta 20k+ o no se publican.
- **Bóveda (B01-B12):** ítems con ID (`HK-001`, `B02-001`…), conteo verificable en DOM, capa estática imprimible + PDF. B02/B03/B04/B08 hoy son JS invisible a print/SEO — se remaquetan. B06 caníbaliza B05 (24 vs 120 prompts) — se expande a 150+ o no se publica.
- **Micro-App (A01-A12):** lógica viva (input → cálculo accionado). A03/A06/A10 hoy son selector de plantilla — se rehace motor real (la `{tesis}`/brief genera, no selecciona) o no se publican.
- **Kit (K01-K10):** suma sin truncado. Hoy K02 16.8k vs E02 31.8k (-47%), K03 26.2k vs E03 32.8k — se regenera con ebook completo verificable por `h2` count. Si truncado, no se vende como “Completo”.
- **Mega-Bundle (M01-M06): APARCADOS por orden del dueño 2026-11-06 — “mientras no me interesan, son estúpidos”. No se rehacen ni se venden hasta nuevo orden.**
- **Lead magnets (L01-L03):** L02 con 27 hooks queda **suspendido hasta expansión industrial**. Industrial = ≥500 hooks con nicho/mecanismo/voltaje + workbook imprimible + archivo sample (expansión 20x de los 27). L01 (31.6k + calculadora) y L03 (wizard 12 vars) se protegen.
- **Precios:** 1 sola fuente (`data/catalog.json`) después de mejorar. Portada + landing se regeneran mecánicamente desde ahí. Nunca se “arregla” un mal producto bajando precio.
- **Filtro publicación (crítica):** 0 SKUs están publicados hoy. Un agente cínico revisa producto a producto y dice **por qué NO lo compraría**. El sistema solo alcanza 10 APROBADOS para que el dueño los revise y apruebe para tráfico. Sin ese gate, nada sale a tienda aunque esté `generated`.

### 5.5 Threads — regeneración
- Coincidente con la auditoría, pero con vara alta: 150/154 sin `hook_pattern`, replies plantilla x23-34, `duplica CTR` contradictorio, 131 sin CTA, 62 de 1 slide.
- Se conserva voz que sí funciona: desmentido “no te voy a decir que esto te hace rico”, matemáticas impares con comisión (`29,62 USD`), anti-urgencia “sin cuenta regresiva”, mecanismo concreto (40 recetas, 300 palabras por gatillo).
- Nueva cola: 1 hook_pattern real por post, 1 ruta puente única con CTA directo, 2 auto-respuestas únicas (no plantilla), 72h anti-duplicación de ruta/anzuelo.

### 5.6 Bait Studio — se conserva (relativamente bien)
- Sólo refinamiento iOS 17.5: reloj 73% ancho, barra estado 54pt, tarjeta 361px radio 22, blur 34, círculos 72px, fondo con grano. Nada que reescribir.

### 5.7 Agente Cínico — filtro de 10 para publicar
- Agente independiente (`model=inherit` según AGENTS §3) lee cada deliverable de 0 a 10 y escribe en `docs/CRITIQUE_10_DIGNOS.md`: por qué NO lo compraría, defectos técnicos, score por eje, y top 5 mejoras por impacto.
- El agente **expande, no degrada**. Si un producto no pasa, la salida es plan de expansión 10x/100x con capítulos/ítems/motor nuevos, jamás “renombrar a guía barata”.
- Meta: ≥10 productos con veredicto “SÍ lo compraría” para que el dueño los revise y apruebe para tráfico. Sin esos 10, no se crea drafts Gumroad ni se hace tráfico.
- Cobertura: primero los 10 de Gumroad ya creados (E01-E10) + B01/B09/B05/L01/A02/A11/A12/K09 — los que por suma industrial tienen chance. Si un candidato cae, se expande y vuelve a revisión, no se publica mediocre.

## 6. Lo que queda para el builder
- Detalle de los 20 prompts Vertex por sub-vía (fondo sin texto, `gemini-3.1-flash-image`, semilla `ron_canonical_seed.png` sólo para Ron apoyo).
- Implementación Pillow/SVG para componer headline/badge/handle en 1000x1500.
- Skript `scripts/audit_pins.py` que falla en: tamaño ≠1000x1500, Ron>30% si `luxury`, fondo repetido <72h, URL repetida <72h, headline >48 chars, ilegible a 236px.
- `scripts/validate_deliverables.py` extendido: `words(K02)>=words(E02)`, `HK-*/Bxx-*` presentes en M/K, botones con listener (JS query + click test), ebook <20k = FAIL si dice “páginas/libro”.
- Conectar Gumroad: habilitar los 10 drafts ya pagables (E01-E10), verificar `published` por API, comprar 1 vez, capturar entrega.
- Decisión log: cuarentena de arte descartado (`data/_cuarentena/ron_protagonist_*`) vs borrado definitivo.

---
*Este doc no contiene código. Es la especificación aprobada para que el plan de ejecución se escriba después de la revisión del builder.*
