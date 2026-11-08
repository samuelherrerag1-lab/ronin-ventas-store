# Auditoría de los 55 productos — Ronin Ventas OS

**Fecha:** 2026-11-04, 22:41–23:20 (America/Bogota)  
**Método:** lectura de los 55 HTML, extracción de texto visible, conteo de ítems/controles y prueba en Edge headless (Playwright) a 1440×900. Sin servidor, sin modificar `data/`, `frontend/` ni `backend/`.  
**Snapshot:** `git status` muestra 10 entregables modificados en vuelo (los mismos que el dueño está reescribiendo). Esta auditoría refleja la versión leída entre 22:41 y 23:20; si el equipo cambia B05/B06/B12/M06 después, hay que revalidar esos SKUs. Los conteos y truncamientos son de este snapshot.
**Salida única:** este archivo.

## Veredicto en una línea

El catálogo base no es el problema: **10 productos son TOP, 35 MEDIO y 10 DÉBIL**. El problema es la capa de kits y mega-bundles: **8 de los 10 DÉBIL son bundles/kits**; el comprador paga por "12 activos" y recibe manuales, ebooks truncados o apps muertas.

> El dueño tiene razón a medias. "Demasiados no son ni la mitad de suficientes" es verdad para **M01, M02, M03, M04, M05, M06, K02 y K03**. No es verdad para **B01, B05, B09, E02, E03, A02, A11, A12, B12, L02 y L03**, que están por encima de la mediana y algunos son el mejor valor del catálogo.

## Cómo leer la tabla

- **Palabras:** texto visible renderizado (o texto estático sin `script/style` cuando el contenido está en pestañas). No cuenta JSON/JS. No es una medida de calidad.
- **Ítems:** unidades vendibles (hooks, prompts, fichas, capítulos, plantillas, componentes).
- **Controles:** inputs/selects/textareas funcionales al abrir; `†` = botones sin lógica. No se cuentan los botones de copiar como "controles".
- **P/U/I/D/C/VP:** profundidad, utilidad, interactividad, diseño, credibilidad, relación calidad/precio (0–10). **Score** = 0,22 P + 0,20 U + 0,12 I + 0,10 D + 0,18 C + 0,18 VP, redondeado.

## Tabla de los 55

| # | SKU | USD | Palabras | Ítems | Controles | P/U/I/D/C/VP | Score | Veredicto | Notas |
|---:|---|---:|---:|---|---|---|---:|---|---|
| 1 | **B01** | $19 | 30.864 | 500 hooks | 2 in / 1.028 btn | 9/10/8/9/9/9 | **9,08** | TOP | 500 hooks con ID, nicho, voltaje, formato y uso; 30.864 palabras renderizadas; filtros, favoritos y export. $0,038 por hook (b01:1416). |
| 2 | **K09** | $39 | 51.701 | 3 componentes | 39 in / 551 btn | 10/9/8/8/8/10 | **9,00** | TOP | E09 completo (17.259 palabras) + 200 respuestas (32.367) + A09 funcional; 51.701 palabras. $39 frente a $61 sueltos. |
| 3 | **B09** | $17 | 32.367 | 200 respuestas | 1 in / 409 btn | 9/10/7/8/8/10 | **8,86** | TOP | 200 respuestas A/B con contexto, mecanismo y CTA; 32.367 palabras; $0,085 por script. El mejor precio por script del catálogo (b09:87). |
| 4 | **B05** | $27 | 16.612 | 120 prompts | 9 in / 17 btn | 9/9/8/8/8/9 | **8,60** | TOP | 120 tarjetas únicas en 12 familias, con 2 variantes y 2 errores cada una; 16.612 palabras; laboratorio y checklist. El FAQ aclara que antes eran 40; hoy el DOM tiene 120 IDs distintos (b05:293). |
| 5 | **K01** | $49 | 14.782 | 3 componentes | 59 in / 87 btn | 9/9/8/8/8/9 | **8,60** | TOP | E01 completo + 500 hooks + A01 funcional; 3 componentes por $49 frente a $67 sueltos. La mejor puerta de entrada al arsenal. |
| 6 | **A12** | $22 | 2.069 | 6 países | 54 in / 18 btn | 8/9/9/9/8/9 | **8,60** | TOP | TRM COP/MXN editable, fees Hotmart/Gumroad, neto por plataforma y 6 países; 54 controles. El cálculo responde a cada cambio. |
| 7 | **A11** | $19 | 3.975 | 10 cortes | 62 in / 11 btn | 8/9/9/9/8/9 | **8,60** | TOP | 21 sliders + 24 campos; runway, fecha de libertad y 10 cortes de gasto; 3.975 palabras. $19 por la calculadora más útil del set. |
| 8 | **A02** | $24 | 4.076 | 10 peldaños | 38 in / 8 btn | 8/9/9/9/8/9 | **8,60** | TOP | Simulador de 10 peldaños con 5 sliders, AOV, ventas y tráfico requerido; 4.076 palabras; sin promesas de ingresos. |
| 9 | **E03** | $17 | 32.892 | 25 caps / 21 estructuras | 42 in / 81 btn | 10/10/3/9/7/10 | **8,52** | TOP | 32.892 palabras, 25 capítulos y 21 estructuras; 2,4 veces la mediana de los 12 ebooks (13.748 palabras). Portada dice $29 y catálogo $17 (e03:361): corregir precio. |
| 10 | **E02** | $19 | 31.865 | 17 caps / 30 rutas | 124 in / 7 btn | 10/10/3/9/7/10 | **8,52** | TOP | 31.865 palabras, 17 capítulos y 30 rutas puente; 124 checkboxes. Portada dice $29 y catálogo $19 (e02:384): corregir precio. |
| 11 | **K08** | $49 | 13.412 | 3 componentes | 34 in / 91 btn | 9/9/8/8/8/8 | **8,42** | MEDIO | E08 + 300 gatillos + A08 funcional; 3 componentes por $49 frente a $70. Queda fuera del top 10 por precio, no por calidad. |
| 12 | **K04** | $39 | 11.515 | 3 componentes | 4 in / 111 btn | 8/9/8/8/8/9 | **8,38** | MEDIO | E04 + 150 pines + A04 funcional; 3 componentes por $39 frente a $73. Buen kit, aunque E04 es el eslabón corto. |
| 13 | **B11** | $19 | 11.302 | 50 modelos | 1 in / 62 btn | 9/9/6/8/8/9 | **8,36** | MEDIO | 50 modelos con margen, horas, canal y barrera; 11.302 palabras; $0,38 por modelo. Denso y copiable. |
| 14 | **L02** | $0 | 3.253 | 27 hooks | 2 in / 37 btn | 8/9/6/8/8/10 | **8,32** | MEDIO | 27 hooks con familia, mecanismo y variantes; muestra real de B01; gratis. Un lead magnet que no da vergüenza. |
| 15 | **A08** | $29 | 1.742 | 495 léxicos | 9 in / 31 btn | 8/9/9/8/8/8 | **8,32** | MEDIO | 495 entradas léxicas, 3 voltajes y 5 reescrituras; el análisis responde al texto pegado. $29 es justo. |
| 16 | **L01** | $0 | 31.598 | 1 caso / 1 calc | 43 in / 41 btn | 9/8/6/9/8/9 | **8,26** | MEDIO | 31.598 palabras + calculadora; separa lo real de lo modelado y no promete ingresos. Lead magnet de lujo. |
| 17 | **B12** | $15 | 6.407 | 40 puntos | 196 in / 7 btn | 8/9/7/8/8/9 | **8,26** | MEDIO | 40 puntos, 30 días y 7 fugas; 196 checkboxes; $15. Densidad real, no relleno. |
| 18 | **B08** | $19 | 20.452 | 300 gatillos | 1 in / 311 btn | 8/9/7/8/8/9 | **8,26** | MEDIO | 300 frases con mecanismo y hook; 20.452 palabras; 6 categorías; $0,063 por gatillo. |
| 19 | **L03** | $0 | 4.918 | 12 variables | 23 in / 16 btn | 8/8/8/8/8/9 | **8,18** | MEDIO | Wizard de 12 variables que genera un meta-prompt real; 4.918 palabras; gratis. No es un PDF disfrazado. |
| 20 | **B10** | $21 | 11.461 | 50 objeciones | 1 in / 59 btn | 9/9/6/8/8/8 | **8,18** | MEDIO | 50 bloques con objeción, reencuadre, copy y CTA; 11.461 palabras; manual de 7 pasos. |
| 21 | **A05** | $34 | 1.878 | 25 bloques | 9 in / 65 btn | 8/8/9/8/8/8 | **8,12** | MEDIO | 25 bloques y 9 variables que sí entran al prompt final; inspector y export. $34 es el precio más alto del set de apps. |
| 22 | **A01** | $29 | 1.802 | 18 patrones / 126 plantillas | 25 in / 84 btn | 8/8/9/8/8/8 | **8,12** | MEDIO | 18 patrones × 7 componentes = 126 plantillas; lote de 15 hooks y analizador A/B. Funciona sin red. |
| 23 | **B04** | $22 | 13.881 | 150 pines | 1 in / 158 btn | 8/9/7/8/8/8 | **8,08** | MEDIO | 150 pines con titular, SEO, ruta y tablero; 105 dark + 45 Ron; 13.881 palabras. |
| 24 | **B03** | $17 | 3.004 | 75 hilos | 1 in / 159 btn | 8/9/7/8/8/8 | **8,08** | MEDIO | 75 hilos completos de 5 tuits (1.464 caracteres de media); filtro y export Markdown. |
| 25 | **B02** | $24 | 8.824 | 100 nichos | 1 in / 110 btn | 8/9/7/8/8/8 | **8,08** | MEDIO | 100 nichos con dolor, producto, precio y keywords; 8.824 palabras; export JSON/CSV. |
| 26 | **E09** | $17 | 17.259 | 10 caps / 30 variaciones | 29 in / 25 btn | 9/9/3/8/7/10 | **8,00** | MEDIO | 17.259 palabras y 30 variaciones; portada $19 vs catálogo $17 (e09:269). Corregir precio. |
| 27 | **K07** | $39 | 14.367 | 3 componentes | 8 in / 120 btn | 9/8/7/8/7/8 | **7,92** | MEDIO | E07 + 40 recetas + A07; 3 componentes por $39 frente a $77. A07 es el eslabón más simple. |
| 28 | **A04** | $27 | 2.757 | 50 titulares / 30 SEO | 5 in / 98 btn | 7/8/8/8/8/8 | **7,78** | MEDIO | Validador de 236 px, 50 titulares, 30 sets SEO y hash anti-colisión; 98 botones de copia. |
| 29 | **K10** | $39 | 12.552 | 3 componentes | 1 in / 206 btn | 8/8/7/8/7/8 | **7,70** | MEDIO | E10 + 50 objeciones + A10; 3 componentes por $39 frente a $64; A10 es el más estrecho. |
| 30 | **B06** | $24 | 6.714 | 24 prompts | 1 in / 24 btn | 8/8/7/8/8/7 | **7,70** | MEDIO | 24 prompts (no 14), 20 reglas anti-slop y ruta de 60 min; 6.714 palabras; el FAQ ya explica el cambio (b06:295). |
| 31 | **E12** | $21 | 13.192 | 10 caps / 6 países | 49 in / 9 btn | 9/9/3/8/7/8 | **7,64** | MEDIO | 13.192 palabras, 10 capítulos y casos Colombia/México/Argentina; 49 controles; $21. |
| 32 | **E11** | $15 | 11.976 | 6 caps | 73 in / 9 btn | 8/9/3/8/7/9 | **7,60** | MEDIO | 11.976 palabras y 6 capítulos; 73 checkboxes; a $15 es el ebook más barato del set. |
| 33 | **A09** | $27 | 2.721 | 5 presets / 40 headlines | 17 in / 176 btn | 7/8/8/8/7/8 | **7,60** | MEDIO | Stack, order bump y checkout en vivo; 17 controles; 2.721 palabras. Útil, no revolucionario. |
| 34 | **E08** | $22 | 13.433 | 11 caps / 14 sesgos | 25 in / 46 btn | 9/9/2/8/7/8 | **7,52** | MEDIO | 13.433 palabras, 11 capítulos y 14 sesgos; 25 checkboxes; contenido fuerte, poca interacción. |
| 35 | **E06** | $19 | 14.172 | 7 caps / 10 prompts | 36 in / 13 btn | 9/9/2/8/7/8 | **7,52** | MEDIO | 14.172 palabras, 20 reglas anti-slop y 10 prompts; 36 checkboxes. El '$29' del título es el producto que enseña, no el precio del ebook. |
| 36 | **E01** | $19 | 11.410 | 10 caps / 21 tablas | 50 in / 5 btn | 8/9/3/9/7/8 | **7,52** | MEDIO | 11.410 palabras, 10 capítulos y 21 tablas; 50 checkboxes; el manual más limpio del bloque PDF. |
| 37 | **B07** | $29 | 3.720 | 40 recetas | 1 in / 89 btn | 8/8/7/8/7/7 | **7,52** | MEDIO | 40 recetas con trigger, 8 pasos, comando y tiempo ahorrado; 3.720 palabras; $29 es el precio más alto de las bóvedas. |
| 38 | **K05** | $49 | 14.098 | 3 componentes | 75 in / 101 btn | 8/8/8/8/6/7 | **7,46** | MEDIO | E05 + 40 prompts (la versión vieja de B05, no los 120) + A05; 3 componentes por $49 frente a $88. La misma pestaña dice 120 (k05:1513) y 40 (k05:1518). |
| 39 | **E07** | $29 | 14.354 | 7 caps | 0 in / 16 btn | 9/9/2/8/7/7 | **7,34** | MEDIO | 14.354 palabras de arquitectura técnica (Playwright, cron, locks); 0 controles; no trae scripts descargables. |
| 40 | **E05** | $27 | 14.064 | 9 caps / 40 puntos | 68 in / 13 btn | 9/9/2/8/7/7 | **7,34** | MEDIO | 14.064 palabras, 9 capítulos y 40 puntos de control; 68 checkboxes; denso. |
| 41 | **K06** | $39 | 14.174 | 3 componentes | 39 in / 130 btn | 8/7/7/8/6/7 | **7,14** | MEDIO | E06 + 14 prompts (la versión vieja de B06, no los 24) + A06; 3 componentes por $39 frente a $72. B06 y A06 son los eslabones viejos. |
| 42 | **A07** | $19 | 3.076 | 6 modelos / 40 configs | 7 in / 93 btn | 7/7/7/8/7/7 | **7,10** | MEDIO | Calculadora FinOps con 6 modelos y 40 configuraciones; 3.076 palabras; precios de tokens hardcodeados sin fuente. |
| 43 | **E10** | $19 | 12.539 | 6 caps / 20 piezas | 0 in / 24 btn | 8/8/2/9/7/7 | **7,02** | MEDIO | 12.539 palabras y 6 capítulos; 0 controles; ensayo fuerte, poca ejecución descargable. |
| 44 | **E04** | $24 | 11.459 | 7 caps / 10 activos | 0 in / 4 btn | 8/8/2/8/7/7 | **6,92** | MEDIO | 11.459 palabras y 7 capítulos; promete 62 págs y entrega ~46; 0 controles. No es malo, es corto. |
| 45 | **A10** | $24 | 3.038 | 12 lentes / 30 consejos | 2 in / 163 btn | 7/6/8/8/7/6 | **6,84** | MEDIO | 12 lentes y 30 consejos; el textarea funciona, pero el catálogo de entrada es corto y el output se repite. |
| 46 | **A03** | $29 | 3.318 | 20 piezas / 50 hooks | 3 in / 130 btn | 7/5/6/8/6/5 | **6,04** | DÉBIL | 20 piezas y biblioteca real, pero `{tesis}` se usa 1 vez (a03:97): el output lo manda el nicho, no tu idea. $29 por un generador de plantillas. |
| 47 | **A06** | $29 | 2.621 | 50 títulos / 30 ejercicios | 5 in / 108 btn | 6/5/6/8/6/5 | **5,82** | DÉBIL | 8 capítulos fijos por formato (a06:79); el brief solo rellena 3 placeholders. La biblioteca es buena; el 'arquitecto' es un selector. |
| 48 | **K03** | $39 | 23.313 | 3 componentes | 44 in / 208 btn | 6/6/7/8/3/5 | **5,60** | DÉBIL | E03 truncado: 45 de 128 encabezados h2/h3 ausentes; 23.313 palabras vs 32.892. Conserva B03/A03, pero el 'Sistema Completo' no está completo. |
| 49 | **K02** | $39 | 15.110 | 3 componentes | 76 in / 29 btn | 6/6/7/8/3/5 | **5,60** | DÉBIL | E02 truncado: 65 de 124 encabezados h2/h3 ausentes; 15.110 palabras vs 31.865. Conserva B02/A02, pero falta medio ebook. |
| 50 | **M04** | $69 | 45.014 | 6 decl. / 3 completos | 0 / 168† | 7/6/2/8/4/5 | **5,40** | DÉBIL | E11/E12 y 50 modelos completos, pero B12 solo 7 de 40 puntos y A11/A12 son cáscaras (m04:5352). El título '6+2' cuenta doble (m04:55). |
| 51 | **M02** | $89 | 56.548 | 9 decl. / 3 completos | 0 / 319† | 6/5/2/8/2/4 | **4,44** | DÉBIL | E05-E07 completos; B06 viejo (14 prompts, no 24), B05 0/120 y B07 12/40; A05-A07 sin lógica (m02:5583). |
| 52 | **M03** | $79 | 65.178 | 9 decl. / 4 completos | 0 / 432† | 6/5/2/8/2/4 | **4,44** | DÉBIL | E08-E10 y B10 completos; faltan los 300 gatillos de B08 y las 200 respuestas de B09; A08-A10 sin lógica (m03:4944). |
| 53 | **M06** | $149 | 9.279 | 52 decl. / 0 entregados | 1 in / 82 chk | 5/3/4/9/3/2 | **3,98** | DÉBIL | Manual de instalación, índice y plan de 9.279 palabras (m06:294-296); ningún activo embebido. A $149 solo se defiende si el ZIP entrega los 52 archivos. |
| 54 | **M01** | $79 | 72.453 | 12 decl. / 4 ebooks | 0 / 398† | 5/4/2/8/2/2 | **3,66** | DÉBIL | 0 ocurrencias de HK-001/B02-001/B03-001/B04-001: las 4 bóvedas no están. E02/E03 truncados; 398 botones, 1 listener (m01:7636). |
| 55 | **M05** | $99 | 24.722 | 12 apps / 0 funcionales | 0 / 788† | 4/1/1/8/1/1 | **2,36** | DÉBIL | 12 apps en pestañas, pero el único JS es tabs/copy (m05:3122-3141); 'FORJAR LOTE' no cambia el DOM. A $99 es una galería, no una suite. |

† Los botones existen en el DOM pero no tienen listener: son decoración. En M01 hay 398; en M02, 319; en M03, 432; en M04, 168; en M05, 788.

## Top 10 (defendibles sin peros)

| # | SKU | Score | Por qué se defiende |
|---:|---|---:|---|
| 1 | **B01** | 9,08 | 500 hooks con ID, nicho y contexto; 30.864 palabras; filtros y export. $0,038 por hook. |
| 2 | **K09** | 9,00 | 51.701 palabras y 3 componentes: E09 + 200 respuestas + A09. $39 frente a $61 sueltos. |
| 3 | **B09** | 8,86 | 200 respuestas A/B; 32.367 palabras; $0,085 por script. El mejor precio por script. |
| 4 | **B05** | 8,60 | 120 prompts únicos, 12 familias, 2 variantes y 2 errores; 16.612 palabras. |
| 5 | **K01** | 8,60 | E01 completo + 500 hooks + A01 funcional; $49 frente a $67 sueltos. |
| 6 | **A12** | 8,60 | 6 países, fees y TRM editable; 54 controles; cálculo en vivo. |
| 7 | **A11** | 8,60 | 21 sliders + 24 campos; runway y fecha de libertad; 62 controles. |
| 8 | **A02** | 8,60 | 10 peldaños, 5 sliders y 4.076 palabras; modela la mecánica, no promete ingresos. |
| 9 | **E03** | 8,52 | 32.892 palabras, 25 capítulos y 21 estructuras; el mejor ebook por densidad. |
| 10 | **E02** | 8,52 | 31.865 palabras, 17 capítulos y 30 rutas; el mejor sistema de Pinterest del set. |

**Nota incómoda:** B05, A02, A11 y A12 están en la lista de reescritura del dueño y, sin embargo, son top 10. B05 tiene 120 prompts únicos verificados en el DOM; el FAQ aclara que antes eran 40. A02/A11/A12 son calculadoras que responden de verdad. Reescribirlos de cero es quemar equipo.

## Los 15 que más urge reescribir (o reparar)

No todos son DÉBIL. **P0** = no debería venderse así; **P1** = motor/contenido por debajo de la promesa; **P2** = mejora puntual, no demolición.

| Prioridad | SKU | Score | Qué está mal | Acción |
|---|---|---:|---|---|
| P0 | **M05** | 2,36 | 12 apps sin lógica: el único JS son pestañas y copiar (m05:3122-3141). | Rehacer con el JS real de A01-A12 o bajarlo a $19 como galería. |
| P0 | **M01** | 3,66 | Dice 12 activos; 0 hooks/nichos/hilos/pines embebidos y E02/E03 truncados; 398 botones, 1 listener (m01:7636). | Rehacer como ZIP de los 12 archivos reales; no vender este HTML como bundle. |
| P0 | **M06** | 3,98 | Manual/índice de 9.279 palabras; 0 de los 52 activos dentro (m06:294-296). | Entregar los 52 archivos + este manual; si no, $39 y llamarlo 'manual de instalación'. |
| P0 | **M03** | 4,44 | Faltan B08 (300 gatillos) y B09 (200 respuestas); A08-A10 sin lógica (m03:4944). | Incluir los datos y el JS o quitar esos activos del inventario. |
| P0 | **M02** | 4,44 | Faltan B05 (120 prompts), el B06 actualizado (24, no 14) y 28 de 40 recetas de B07; A05-A07 sin lógica (m02:5583). | Rehacer el pegado: el bundle debe contener los 9 activos actuales, no sus manuales viejos. |
| P0 | **M04** | 5,40 | B12 con 7 de 40 puntos; A11/A12 sin lógica; '6+2' cuenta doble (m04:55). | Incluir los 40 puntos y activar las calculadoras; corregir el título. |
| P0 | **K03** | 5,60 | E03 truncado: 45 de 128 encabezados ausentes; 23.313 vs 32.892 palabras. | Regenerar con el E03 completo; el corte está antes del capítulo 13 (e03:2208). |
| P0 | **K02** | 5,60 | E02 truncado: 65 de 124 encabezados ausentes; 15.110 vs 31.865 palabras. | Regenerar con el E02 completo; el corte está antes del capítulo 7 (e02:1683). |
| P1 | **A06** | 5,82 | 8 capítulos fijos por formato (a06:79); el brief solo rellena 3 placeholders. | Hacer que título/problema/promesa generen capítulos reales; hoy es un selector de plantilla. |
| P1 | **A03** | 6,04 | `{tesis}` se usa 1 vez (a03:97); el output lo decide el nicho, no tu idea. | Convertir la tesis en el eje de las 20 piezas; hoy es un generador de plantillas. |
| P1 | **A10** | 6,84 | 30 consejos precargados y 12 lentes; el output se repite y el catálogo de entrada es corto. | Añadir más entradas y variar las 12 lentes por nicho. |
| P1 | **E04** | 6,92 | 7 capítulos y 11.459 palabras para una promesa de 62 páginas; 0 controles. | Añadir plantillas/checklists y 2-3 capítulos; no reescribir el libro. |
| P2 | **E10** | 7,02 | 6 capítulos y 12.539 palabras; 0 controles; buen ensayo, poca ejecución. | Añadir workbook/plantillas; mantener el texto. |
| P2 | **A07** | 7,10 | 3.076 palabras; precios de tokens hardcodeados sin fuente. | Hacer editables las tarifas y enlazar la fuente; no tocar la UI. |
| P2 | **K06** | 7,14 | E06 está bien; B06 (14 viejos) y A06 (arquitectura fija) son los eslabones débiles. | Reemplazar B06 por los 24 actuales y arreglar A06; no rehacer E06. |

### Por qué estos 15 y no los que ya están asignados

De los 10 que el dueño ya puso en reescritura:

| SKU | Rank | Score | Diagnóstico |
|---|---:|---:|---|
| M06 | 53 | 3,98 | **Justificado**: es un manual, no el bundle. |
| B06 | 30 | 7,70 | MEDIO: 24 prompts, no 14; no urge reescribir, sí reposicionar. |
| B07 | 37 | 7,52 | MEDIO: 40 recetas técnicas; el problema es credibilidad/verificación, no falta de contenido. |
| B05 | 4 | 8,60 | **No reescribir**: 120 prompts únicos; el FAQ ya explica el cambio desde 40. |
| B12 | 17 | 8,26 | **No reescribir**: 40 puntos y 30 días; a $15 es de los mejores. |
| L02 | 14 | 8,32 | **No reescribir**: 27 hooks reales; lead magnet correcto. |
| L03 | 19 | 8,18 | **No reescribir**: wizard funcional de 12 variables. |
| A02 | 8 | 8,60 | **No reescribir**: simulador real de 10 peldaños. |
| A11 | 7 | 8,60 | **No reescribir**: 62 controles y cálculo en vivo. |
| A12 | 6 | 8,60 | **No reescribir**: 6 países y fees; cálculo en vivo. |

**Conclusión operativa:** solo M06 de los 10 asignados está en el fondo. Los otros nueve están entre el puesto 4 y el 37. Mientras tanto, **K02, K03, M01 y M05 no aparecen en la lista de reescritura** y son los que más daño hacen a la promesa de la tienda.

## Los 6 hallazgos que cambian la decisión

### 1. M05 es una galería de 12 apps muertas — $99

`m05_suite-12-micro-apps-html.html` tiene 12 pestañas y 788 botones, pero su único JavaScript son 20 líneas de tabs y copiar: `m05:3122-3141`. Probado en Edge: al abrir A01 y pulsar **FORJAR LOTE DE 15 HOOKS**, el DOM no cambia (12.185 caracteres antes y después). Lo mismo con las otras 11. El comprador paga $99 por capturas interactivas de un producto que no funciona. Es el peor SKU del catálogo.

### 2. M01 no contiene las 4 bóvedas que anuncia — $79

`m01_bundle-imperio-faceless.html` dice "12 ACTIVOS: 4 BLUEPRINTS + 4 BÓVEDAS + 4 APPS HTML" (`m01:55`). En 760 KB:

- `HK-001` (B01): **0 ocurrencias**.
- `B02-001` (B02): **0**.
- `B03-001` (B03): **0**.
- `B04-001` (B04): **0**.
- E02/E03 están truncados: faltan 65 y 45 encabezados respectivamente.
- 398 botones, un solo listener de pestañas (`m01:7636`).

Es un lector de ebooks parciales con manuales, no un bundle de 12 activos.

### 3. M06 es un manual, no los 52 productos — $149

`m06_ronin-all-access-vault.html` se describe como "Manual de instalación, índice interactivo y plan de uso" (`m06:295`) y pesa 9.279 palabras. Tiene 82 checkboxes y 10 enlaces, pero **ningún activo embebido**. A $149 solo se defiende si el ZIP que se entrega contiene los 52 archivos; si el comprador descarga este HTML, compró un índice.

### 4. K02 y K03 venden "Sistema Completo" con el ebook a la mitad

- **K02:** 15.110 palabras frente a 31.865 de E02; faltan **65 de 124** encabezados h2/h3. El corte ocurre antes del capítulo 7 de E02 (`e02:1683`), que no aparece en K02.
- **K03:** 23.313 palabras frente a 32.892 de E03; faltan **45 de 128** encabezados. El corte ocurre antes del capítulo 13 (`e03:2208`).

K02/K03 conservan B02/B03 y A02/A03, pero el comprador que paga $39 por el "sistema completo" no recibe el manual completo. Es el mismo defecto que arrastra M01.

**K05 también está desactualizado:** en su pestaña B05 convive el título "Bóveda de 120 Prompts" (`k05:1513`) con "Bóveda de 40 meta-prompts" (`k05:1518`) y "40 META-PROMPTS" (`k05:1531`). El kit no incluye los 120 prompts del B05 actual; incluye la versión vieja de 40.

### 5. Los mega-bundles M02/M03/M04 también son pegapáginas con pérdidas

- **M02 ($89):** E05-E07 completos; **0 de los 120 prompts de B05**, B06 viejo (14 prompts, no 24) y solo **12 de 40** recetas de B07; A05-A07 sin lógica (`m02:5583`).
- **M03 ($79):** E08-E10 completos y B10 (50), pero **0 de los 300 gatillos de B08** y **0 de las 200 respuestas de B09**; A08-A10 sin lógica (`m03:4944`).
- **M04 ($69):** E11/E12 y B11 (50 modelos) completos, pero **7 de 40** puntos de B12 y A11/A12 sin lógica (`m04:5352`). El título "6 ACTIVOS + 2 APPS" cuenta doble: son 2 ebooks + 2 bóvedas + 2 apps = 6 (`m04:55`).

### 6. Hay tres precios de portada que no coinciden con el checkout

| SKU | Dice la portada | Dice `catalog.json` | Evidencia |
|---|---:|---:|---|
| E02 | $29 | $19 | `e02:384` |
| E03 | $29 | $17 | `e03:361` |
| E09 | $19 | $17 | `e09:269` |

No es un detalle estético: el comprador ve un precio y paga otro. Unificar la fuente de verdad antes de publicar.

## Lo que sí está bien (y no hay que tocar)

- **Diseño:** los 55 comparten un sistema visual oscuro-editorial coherente, con 20–30 variables CSS, responsive y **0 recursos externos** (no hay CDN ni fuentes remotas). No es una plantilla genérica de Bootstrap; es una marca. El diseño no es el problema.
- **B01/B09/B05 son arsenales reales:** 500 hooks, 200 respuestas y 120 prompts con ID, contexto y mecanismo. A $17–27 son el mejor valor del catálogo.
- **E02/E03 son libros, no folletos:** 31.865 y 32.892 palabras, 17 y 25 capítulos, 30 rutas y 21 estructuras. A $19/$17, aunque la portada diga $29, son de los productos más densos.
- **A02/A11/A12 son calculadoras reales:** 10 peldaños, 62 controles y 6 países; responden a los inputs, no son maquetas.
- **B12/L02/L03 no necesitan reescritura:** 40 puntos, 27 hooks y un wizard de 12 variables; son de los mejores por dólar.
- **No hay promesas de ingresos garantizados:** los textos usan "no garantiza", "escenario" y "modelo". El problema no es el claim de ingresos; es el inventario y el precio.

## Empaquetado y precio: qué haría mañana

1. **Nada de PDF/EPUB/ZIP en `data/`.** Hay 0 `.pdf`, 0 `.epub` y 0 `.zip`; los 55 son HTML. Si la ficha promete "ZIP con Ebook PDF + Bóveda + App" (K01-K10) o "PDF/EPUB" (E01-E12), el comprador recibe otro formato. O se genera el ZIP/PDF real o se cambia la promesa.
2. **M06 a $149 solo con los 52 archivos.** Si el entregable es el HTML, vale $39 como manual. Si es el all-access, el ZIP debe incluir los 52 archivos y este manual como índice.
3. **M05: $99 → $19 mientras sea una galería.** Si se rehace con el JS de las 12 apps, $79–99 es defendible.
4. **M01: $79 → $39 mientras esté truncado.** Después de reconstruirlo con las 4 bóvedas y E02/E03 completos, $69–79.
5. **M02 $89 → $59 y M03 $79 → $49** hasta que incluyan B05/B07/B08/B09 completos. Si se arreglan, los precios actuales se defienden.
6. **M04 $69 → $49** hasta que A11/A12 funcionen y B12 tenga los 40 puntos. Con eso, $69 está bien.
7. **K02/K03: $39 → $19** hasta restaurar E02/E03. Si se restauran, $39 es correcto.
8. **K05: reemplazar la B05 vieja de 40 prompts por la de 120** o bajar a $39 y quitar el "120" de la pestaña. No pueden convivir "120" (`k05:1513`) y "40" (`k05:1518`) en el mismo producto.
9. **B01/B09 están infravalorados:** $19 por 500 hooks ($0,038/hook) y $17 por 200 respuestas ($0,085/script). Subirlos a $27–29 o usarlos como order bump. No hay que "mejorarlos"; hay que cobrarlos.
10. **B06 a $24 por 24 prompts** compite mal con B05 a $27 por 120. O se añaden 30+ prompts o baja a $17.
11. **A05 a $34** es el precio más alto de apps; si se empaqueta con B05 en K05, el kit ya lo justifica. Suelto, $29 es más honesto.
12. **K09 a $39 es el ancla de valor:** 51.701 palabras y 3 componentes. Es el producto que debería estar en la portada de la tienda, no M06.
13. **Unificar precio de portada y checkout** en E02/E03/E09 antes de cualquier campaña.

## Reparto de equipos (lo que cambiaría hoy)

- **Prioridad P0:** M05, M01, M06, M03, M02, M04, K02, K03. Si solo hay 4 equipos, empezar por K02, K03, M01 y M05: son los que rompen la promesa "Sistema Completo" y "12 apps".
- **Dejar 1 equipo en M06** (empaquetado/ZIP), no en reescritura de contenido.
- **B05/B07/B12/L02/L03/A02/A11/A12:** no reescribir de cero. B05 está bien (120 prompts y el FAQ explica el cambio desde 40); B07 necesita verificar comandos y claims; B12/L02/L03 están bien; A02/A11/A12 necesitan, como mucho, fuentes editables.
- **B06:** si el equipo ya está dentro, que añada prompts y reposicione; no lo demolan. Tiene 24, no 14.

## Límites de esta auditoría

- No se ejecutó el servidor ni se probó una compra real; se abrieron los archivos con `file://` en Edge headless.
- No se juzgó el copy de las landings de venta ni el checkout: solo los 55 entregables.
- Los scores son judgment con rúbrica fija; dos auditores pueden mover ±0,5. La evidencia (conteos, citas, pruebas de clic) está en la tabla y en los hallazgos.
- Los conteos de palabras no incluyen datos en JS; por eso B01 marca 30.864 (renderizado) y K01 14.782 (estático) aunque ambos contengan 500 hooks.
