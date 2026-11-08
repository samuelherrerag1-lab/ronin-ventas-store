# Auditoría Cínica — 5 Productos de Lanzamiento

## Resumen ejecutivo

Los cinco archivos comparten el mismo problema de fondo: venden resultados que no se pueden verificar. La estética es consistente y la ejecución técnica de B01, E03 y E02 está por encima del promedio de Gumroad; el cuello de botella no es el diseño, es la confianza. Dos productos tienen impreso en su propia portada un precio distinto al que se cobra. Ninguno tiene garantía, soporte ni política de actualizaciones; solo L01 intenta un enlace al catálogo, y está muerto. El único que se acerca a valer $29 es E03; el que más avergüenza es L01, porque su tesis es “la captura real es la prueba” y la captura que muestra es una recreación en CSS.

| Producto | Claridad | Densidad | Originalidad | Confianza | Técnica | Valor/precio | Global |
|---|---:|---:|---:|---:|---:|---:|---:|
| **L01** — Desglose $418.50 ($0) | 78 | 55 | 68 | 28 | 30 | 40 | **43** |
| **B01** — 500 Hooks ($19) | 50 | 45 | 42 | 22 | 82 | 28 | **41** |
| **E03** — Threads ($29) | 62 | 88 | 72 | 38 | 86 | 55 | **63** |
| **E02** — Pinterest ($29) | 66 | 72 | 55 | 38 | 86 | 40 | **56** |
| **B09** — 200 Respuestas ($27) | 72 | 62 | 58 | 18 | 62 | 32 | **45** |

Nadie debería pagar $29 por E02 ni $27 por B09 en su estado actual. B01 no debería costar $19 con 370 hooks de relleno. L01 es gratis y aun así falla en lo único que un lead magnet tiene que hacer: capturar el correo.

---

## L01

**Archivo:** `data/deliverables/l01_anatomia-post-418-usd.html` · 58,9 KB · 537 líneas · ~4.650 palabras · Precio: $0.

### A) Veredicto de compra

**Precio que pagaría realmente:** $0. Es un lead magnet; como producto de pago, $0.

**Las 5 razones por las que no lo compraría:**

1. **La “prueba” central es una recreación, no una captura.** El texto enseña que la captura nativa es la prueba —“Era una captura nativa: barra de estado, hora, batería, notificación del sistema… Esa imperfección es la prueba” (línea 188)— y luego el propio archivo admite: “Recreación CSS de la captura original · sin bisel, sin notch, sin marco decorativo” (línea 210). El comprador escéptico ve un mockup y concluye que el experimento también puede ser un mockup.
2. **El correo no se captura.** La página dice “Deja tu correo y el navegador abrirá el expediente para guardarlo como PDF” (línea 447), pero el formulario solo valida el email y llama a `window.print()` (líneas 522-530). No hay `fetch`, no hay `localStorage`, no hay CRM. Lo probé: después de enviar `example@example.invalid`, el correo no quedó guardado en ninguna parte. Es un lead magnet que no genera leads.
3. **El PDF prometido se imprime ilegible.** El CSS de impresión oculta `.calc-box` pero deja `.calc-out` visible, y no corrige el fondo de `.element`: en emulación de impresión, `.element` conserva `background: rgb(14,14,21)` y sus párrafos pasan a `color: rgb(17,17,17)`. Contraste ~1,02:1. El PDF real que genera Chrome tiene 14 páginas, no las 18 que promete la ficha (línea 134). El comprador que hace clic en “Descargar Expediente en PDF” recibe bloques negros con texto invisible.
4. **La calculadora no puede reproducir su propio caso.** El deslizador se llama “Conversión del checkout” (línea 427), pero el texto dice que la conversión de checkout fue 71% (22 ventas de 31 checkouts, línea 317). La fórmula usa clics × 2,08%, que en realidad es la conversión de clic de perfil a venta, no la del checkout. El máximo del control es 8%, así que es imposible introducir el 71% real. La herramienta está calibrada para devolver el número que ya está en el titular.
5. **El único CTA está muerto.** El cierre manda a `/sistema/catalogo-ronin-ventas-os` (línea 482). Según el diagnóstico del propio proyecto (`docs/PLAN.md`), las 55 rutas puente no tienen handler y devuelven el dashboard: “Rutas puente servidas: 0 de 55”. El único camino de monetización del lead magnet no lleva a ningún producto.

**La objeción que diría en voz alta:**
> “El tipo que enseña que una captura real es la prueba… usa una captura falsa hecha en CSS. Y el PDF que regala ni se puede leer. ¿Para qué dejo mi correo?”

### B) Auditoría de contenido

**¿Cumple lo que promete el título?** Parcialmente. El título promete “El Desglose del Experimento de $418.50 (PDF + Mini-Calculadora HTML)”. La calculadora existe y funciona; el “PDF” no existe como archivo: es la página completa impresa. El desglose narrativo está, pero la parte que importa —la prueba— es una reconstrucción.

**Afirmaciones imposibles de verificar:**
- 48.000 impresiones, 1.056 clics de perfil, 612 visitas a la ruta, 31 checkouts, 22 ventas, 38 comentarios, 91 guardados, 11 minutos de lectura. Todo con dos decimales y cero fuente, cero nombre de cuenta, cero enlace al dashboard.
- “La captura es real y el dashboard también” (línea 337), cuando la captura que se muestra es CSS.
- “Gumroad cobró 10% + $0.50 por venta” (línea 139): no hay enlace a la tarifa ni fecha. Si la tarifa cambió, toda la aritmética del producto queda vieja.
- “Un campo de teléfono obligatorio que Gumroad pedía en la versión de prueba” (línea 330): una explicación específica de producto, sin captura ni confirmación.

**Relleno disfrazado:**
- La tabla de “12 métricas” repite lo que ya dijeron el timeline y los stat-cards.
- La checklist de 20 puntos es genérica (“El titular tiene una cifra impar”, “La captura se ve nativa”, “El post tiene menos de 150 palabras”).
- El plan de 7 días es consejo común de lanzamiento, no el experimento.
- Las cinco plantillas son lo único reutilizable, y dos de ellas son el mismo texto con otro nombre.

**Vacíos:**
- No hay captura real, ni nombre de cuenta, ni enlace al producto original.
- No hay PDF entregable ni flujo de email.
- No hay desglose de los 22 compradores (de dónde vinieron, cuánto pagaron, cuántos reembolsos).
- No hay garantía ni política de privacidad para el correo que pide.

### C) Auditoría técnica

Probado en Chromium headless con el archivo servido por HTTP local. Resultados:

- **Calculadora:** funciona y devuelve $365.65 con los valores por defecto. Pero el modelo suma $0,50 de propina en *cualquier* cálculo (`gross=sales*pr+(sales>0?0.5:0)`, línea 506) y cobra comisión del 10% sobre esa propina. Si el usuario pone 100 ventas, el resultado incluye una propina inventada.
- **Formulario:** válido, muestra el mensaje de éxito y lanza la impresión. No guarda el email. No hay red. Es decorativo.
- **Impresión:** el PDF de 14 páginas sale con el hero en gris claro sobre blanco y los bloques `.element` en negro sobre negro. `.calc-out` queda visible sin sus controles. `.bridge` y `.lead-form` se ocultan (correcto), pero el resultado no es un expediente legible.
- **Copiar plantillas:** funciona con `navigator.clipboard` y fallback a `execCommand`.
- **Código muerto:** `const DATA={}` (línea 489) y `function download()` (línea 496) se declaran y nunca se usan. Señal de plantilla a medio conectar.
- **Accesibilidad:** no hay imágenes, así que no hay `alt` faltante. Los inputs tienen `aria-label`; el foco se marca con `box-shadow`. El problema no es accesibilidad, es que el PDF impreso no tiene contraste.

### D) Auditoría de venta

- **Above the fold:** el hero es bueno: cifra impar, hora incómoda, promesa concreta y estética seria. En 10 segundos se entiende qué es. El problema aparece al hacer clic: no hay entrega.
- **Prueba/demostración:** no hay ninguna prueba real. La única “prueba” es un mockup CSS que el propio archivo etiqueta como recreación.
- **Razón para comprar HOY:** no aplica: es gratis. Pero tampoco hay razón para dejar el correo hoy, porque no se entrega nada a cambio.
- **CTA final:** existe, es claro y está roto. El usuario hace clic y cae en una ruta sin handler.
- **Comparado con un lead magnet de $0 en Gumroad/Hotmart:** está por encima del promedio en diseño y narrativa; está por debajo en lo único que importa: captura y entrega. Un PDF de 5 páginas con un enlace real vale más que este caso sin prueba.

### E) Puntuación

| Dimensión | Puntaje | Razón |
|---|---:|---|
| Claridad de promesa | 78 | El hero y el índice se entienden; el alcance está claro. |
| Densidad real | 55 | 4.650 palabras para un experimento de 5 horas; mucho de lo útil cabe en 1.500. |
| Originalidad | 68 | El ángulo “anatomía de un post” es bueno; la ejecución es una plantilla de storytelling. |
| Confianza | 28 | La prueba es un mockup; las cifras no tienen fuente; el PDF es ilegible. |
| Ejecución técnica | 30 | Calculadora sesgada, captura inexistente, impresión rota, CTA muerto. |
| Valor percibido vs. precio | 40 | Como gratis, aceptable; como producto, cero. |
| **Global** | **43** | Un buen escaparate con la puerta trasera tapiada. |

### F) Top 5 mejoras ordenadas por impacto en ventas

1. **Capturar el correo de verdad y entregar un PDF real.**
   - **Qué:** reemplazar el `window.print()` por un `POST` a un endpoint (o un `mailto:` con asunto prellenado como fallback) y descargar un PDF pregenerado.
   - **Dónde:** formulario `#leadForm`, líneas 448-455; JS 522-530.
   - **Por qué:** es la única función del lead magnet. Hoy no genera lista, no genera atribución y no genera venta posterior.

2. **Sustituir la recreación CSS por una captura real redactada.**
   - **Qué:** una imagen PNG del dashboard de Gumroad con datos sensibles tapados, más un enlace a un video de 20 segundos o a un PDF con la secuencia.
   - **Dónde:** bloque `.phone` en `#elementos`, líneas 193-211.
   - **Por qué:** toda la tesis del producto es “la prueba visual específica vende”. Sin prueba real, el producto se contradice en la primera pantalla.

3. **Arreglar el CSS de impresión y el número de páginas.**
   - **Qué:** forzar `background:#fff` y `color:#111` en `.element`, `.panel`, `.calc-out`, `.hero p`, `.dek`; ocultar `.calc-out` completo; definir saltos de página; ajustar el texto a 18 páginas o cambiar la promesa a “14 páginas”.
   - **Dónde:** `@media print`, línea 118.
   - **Por qué:** el botón principal entrega un PDF que no se puede leer. Es el fallo más visible y el más fácil de arreglar.

4. **Recalibrar la calculadora al embudo real.**
   - **Qué:** añadir un campo “visitas a la página puente” y otro “conversión del checkout”; calcular clics → visitas → checkouts → ventas. Quitar la propina automática o hacerla opcional.
   - **Dónde:** controles 425-430 y `calc()` 502-519.
   - **Por qué:** hoy no puede reproducir el 71% que el propio texto declara. Un comprador que mueve el control hasta 8% ve 84 ventas y concluye que el modelo está inflado.

5. **Reemplazar el CTA muerto por una oferta real.**
   - **Qué:** enlazar a una página puente que exista, con precio y checkout dual; o incrustar un bloque de compra del producto de entrada.
   - **Dónde:** `.bridge`, línea 482.
   - **Por qué:** es el único camino de monetización del archivo. Un lead magnet sin siguiente paso es un PDF bonito, no un embudo.

---

## B01

**Archivo:** `data/deliverables/b01_boveda-500-hooks-cinicos.html` · 258,9 KB · 2.106 líneas · 500 hooks · Precio: $19.

### A) Veredicto de compra

**Precio que pagaría realmente:** $4,90. Los primeros 130 hooks valen ese dinero; los otros 370 no.

**Las 5 razones por las que no lo compraría:**

1. **El archivo se contradice tres veces antes del primer scroll.** El `<title>` dice “Bóveda Cínica 500 - 130 hooks de alto voltaje” (línea 6); el hero dice “130 piezas de archivo” (línea 455); el chip dice “500 PIEZAS VERIFICADAS” (línea 458); la ficha dice “Piezas en esta entrega: 130” (línea 474); el KPI dice 500 (línea 498); el footer dice “130 HOOKS” (línea 794). El comprador no sabe si compró 130, 500 o un archivo a medio actualizar. Es la primera cosa que va a comentar.
2. **370 de los 500 hooks son una plantilla con el nicho y la cifra cambiados.** Del HK-131 al HK-500, el texto sale de 160 plantillas de frase; siete de ellas se repiten 6 o 7 veces. 318 hooks terminan con uno de siete cierres mecánicos: “Evidencia comprobada en Stripe” (49), “Los datos no mienten” (49), “Anota esto antes de que lo borre” (50), “Y nadie en tu nicho lo está haciendo” (50), “Menos poesía, más números” (50), “El mercado no premia el esfuerzo, premia el apalancamiento” (50), “Compruébalo tú mismo” (20). El comprador lo detecta en la página 3.
3. **Algunos hooks son tan malos que rompen el resorte psicológico.** En la categoría “Envidia”: “Un chico de 19 años en Colombia factura $19 al mes en Threads usando una sola micro-app HTML de 1 archivo” (HK-227) y “El creador que tú llamas ‘vendemotos’ en Inversión acaba de cerrar el mes en $19 con un simple PDF” (HK-218). $19 al mes no da envidia; da lástima. Hay seis hooks con esa cifra.
4. **Te hace publicar una confesión de acceso no autorizado.** “Accedí a la base de datos de lanzamientos de Inversión en Hotmart: el 81% de los compradores nunca abre el módulo 2” (HK-147), “Un ex-empleado de una agencia… me filtró el documento interno” (HK-141), “Revisé los logs de un bot de arbitraje” (HK-148). Son 49 hooks con “Evidencia comprobada en Stripe”. El archivo no advierte que publicar eso te expone a una acusación de acceso ilegal o de difamación; peor, te obliga a inventar la evidencia.
5. **No hay curaduría ni prueba.** 500 tarjetas sin un “empieza por estos 10”, sin un ejemplo de un hook publicado con métricas, sin una lista de “no uses esto”. El manual da cadencia y carriles, pero ningún resultado. A $19, el comprador está pagando por una lista searchable, no por un sistema.

**La objeción que diría en voz alta:**
> “Pagué $19 por 500 hooks y 370 son el mismo hook con el nombre de otro nicho cambiado. Y varios me hacen confesar que hackeé Hotmart. ¿Esto lo escribió una persona o un script?”

### B) Auditoría de contenido

**¿Cumple lo que promete el título?** Literalmente sí: hay 500 objetos con ID. Cualitativamente no: 130 están escritos a mano y 370 son una matriz de sustitución. El título “500 hooks verificados” es falso: no hay verificación de nada.

**Afirmaciones imposibles de verificar:**
- 49 hooks con “Evidencia comprobada en Stripe”, sin una sola captura, enlace o fecha.
- Porcentajes inventados: 73%, 79%, 81%, 88%, 94%, 68%.
- “Hizo $19 en 14 días con solo 2 pines” (HK-135), “generó $297 en 48 horas” (HK-138), “factura $418 al mes” (HK-244).
- “En los próximos 90 días, el 94% de los servicios manuales en Freelance van a ser reemplazados por scripts de DeepSeek a $0 costo” (HK-281). Es una predicción catastrofista presentada como dato.

**Relleno disfrazado:**
- Las 370 entradas generadas.
- El “Manual” de 5 secciones repite lo que ya dicen las tarjetas: carriles, cadencia, errores, resortes.
- Los “10 hooks madre” son buenos, pero son 10 ejemplos más: no añaden un caso con métricas ni una prueba de uso.
- Las barras de “voltaje medio”, “calibres activos” y “nichos activos” son decoración: no cambian ninguna decisión.

**Vacíos:**
- Un conjunto curado de inicio (“los 10 que usaría esta semana”).
- Prueba de que algún hook funcionó: captura, hilo, métricas.
- Una advertencia legal sobre las afirmaciones de acceso a datos.
- Una versión en español neutro/LatAm consistente (hay hooks con “tú” y otros con “usted” implícito).
- Un historial de versiones o fecha de actualización.

### C) Auditoría técnica

Probado en Chromium headless:

- **Render:** 500 tarjetas, `#liveCount` = 500, sin errores JS. El DOM final pesa ~860 KB; funciona, pero renderiza 500 tarjetas de golpe, sin paginación ni virtualización.
- **Buscador:** funciona. “Hotmart” devuelve resultados; el filtro por categoría devuelve 40.
- **Favoritos:** se guardan en `localStorage` (`ronin:boveda-cinica:favs-v1`) y sobreviven al reload. Probado: HK-134 guardado, recarga, contador 1.
- **Exportaciones:** CSV y JSON se descargan correctamente (probado: `boveda_filtrados_2026-11-04.csv` y `.json`). TXT y “Copiar resultados” usan el mismo pipeline.
- **Impresión:** existe `doPrint()` y un `#printArea`; el PDF de prueba sale en 30 páginas. El CSS de impresión está separado y oculta la interfaz. El riesgo es que imprime solo los hooks filtrados, no los 500, y que el `beforeprint` no se dispare en todos los navegadores.
- **Bug real:** 105 hooks tienen `formato:'X'`, pero el `<select>` solo ofrece Threads, Pinterest, Email y Reel (líneas 557-563). Al elegir cualquier formato, los 105 de X desaparecen sin forma de filtrarlos. El chip “4 FORMATOS” también es falso: hay cinco.
- **Accesibilidad:** el buscador no tiene `<label>` ni `aria-label` (solo placeholder), y las tarjetas usan botones con `aria-label` correcto. No hay imágenes, así que no hay `alt` faltante.

### D) Auditoría de venta

- **Above the fold:** el hero vende bien: “Hooks que no piden permiso”, 500 piezas, buscador. Parece una herramienta, no un ebook. En 10 segundos justifica $19… hasta que el comprador lee “130 piezas” en el mismo bloque.
- **Prueba/demostración:** el producto *es* la demostración: puede leer 10 hooks y decidir. Es su mayor fortaleza. No hay prueba de resultados, solo de escritura.
- **Razón para comprar HOY:** ninguna. No hay bono, ni fecha, ni subida de precio, ni garantía.
- **CTA final:** no hay CTA de compra ni de siguiente producto. El archivo termina en el manual. Como producto ya comprado, es aceptable; como embudo, deja dinero en la mesa.
- **Comparado con lo que hay a $19:** peor que un pack de 100 hooks probados con capturas; mejor que una lista gratis de 50 frases genéricas. Los 130 buenos justifican $5, no $19.

### E) Puntuación

| Dimensión | Puntaje | Razón |
|---|---:|---|
| Claridad de promesa | 50 | “500 hooks” se entiende, pero el archivo dice 130 en tres lugares. |
| Densidad real | 45 | 130 hooks útiles; 370 relleno de plantilla. |
| Originalidad | 42 | Los primeros 130 tienen voz; el resto es mail-merge. |
| Confianza | 22 | “Evidencia comprobada en Stripe” sin evidencia; cifras de $19 al mes; confesiones de acceso ilegal. |
| Ejecución técnica | 82 | Buscador, filtros, favoritos y exportaciones funcionan. |
| Valor percibido vs. precio | 28 | $19 por 130 hooks es caro; $5 sería justo. |
| **Global** | **41** | Una buena mitad enterrada bajo una mala mitad. |

### F) Top 5 mejoras ordenadas por impacto en ventas

1. **Un solo número en todo el archivo.**
   - **Qué:** decidir si el producto es “500 hooks” o “130 hooks + 370 variantes”. Si es 500, quitar “130” del título, hero, ficha y footer; si es 130, cambiar el nombre y el precio.
   - **Dónde:** líneas 6, 455, 458, 474, 498, 794.
   - **Por qué:** la contradicción es lo primero que ve el comprador y lo primero que va a comentar. Ninguna otra mejora importa si el conteo no cuadra.

2. **Reescribir o eliminar los 370 hooks generados.**
   - **Qué:** conservar los 130 escritos a mano y sustituir los 370 por 70 hooks nuevos, específicos, con un momento de uso y una advertencia. Si no hay tiempo, vender “130 hooks” y bajar el precio.
   - **Dónde:** `HOOKS` HK-131 a HK-500.
   - **Por qué:** “Evidencia comprobada en Stripe” ×49 y “$19 al mes” ×6 destruyen la credibilidad del producto completo, incluidos los 130 buenos.

3. **Quitar las afirmaciones de acceso ilegal y añadir una nota de uso.**
   - **Qué:** reemplazar “Accedí a la base de datos”, “me filtró el documento” y “revisé los logs” por casos propios verificables o por lenguaje hipotético (“si tuvieras acceso a…”). Añadir una página “no publiques esto si no puedes probarlo”.
   - **Dónde:** HK-137, HK-141, HK-147, HK-148 y el manual.
   - **Por qué:** el comprador que publica esas frases se expone; el que las lee desconfía. Es un riesgo legal disfrazado de copy.

4. **Añadir un “empieza aquí”: 10 hooks con su momento y su métrica.**
   - **Qué:** una sección arriba del arsenal con 10 tarjetas recomendadas para la primera semana, cada una con “úsalo cuando” y “mide esto”.
   - **Dónde:** entre el hero y el radar, o como primer tab.
   - **Por qué:** 500 opciones sin secuencia es parálisis. La curaduría es lo que convierte una lista en un sistema y justifica el precio.

5. **Arreglar el filtro de formato y el conteo de “4 formatos”.**
   - **Qué:** añadir la opción “X” al `<select>` y cambiar el chip a “5 FORMATOS”; o reclasificar los 105 hooks de X a Threads/Email.
   - **Dónde:** `#formatSel`, líneas 557-563; `FORMATS`, línea 1332.
   - **Por qué:** hoy 105 hooks son inalcanzables con cualquier filtro de formato. Es un bug de producto, no de estética.

---

## E03

**Archivo:** `data/deliverables/e03_threads-algoritmo-polarizacion.html` · 254,9 KB · 2.689 líneas · ~22.850 palabras · 84 páginas impresas · Precio: $29 (portada dice $17).

### A) Veredicto de compra

**Precio que pagaría realmente:** $14. Es el mejor producto del lote, pero no a $29 con casos inventados y el precio viejo en la portada.

**Las 5 razones por las que no lo compraría:**

1. **La portada dice $17 y me cobran $29.** “E03 · $17” (línea 361), “Precio de portada $17 USD” (línea 381), footer “$17 USD” (línea 2423). No es un detalle: es la señal de que el archivo es una plantilla reaprovechada y de que el precio de $29 se decidió después. Un comprador que ve eso pide reembolso antes de leer.
2. **El título de la tienda no es el título del archivo.** El SKU se llama “Threads: El Algoritmo de la Polarización”; el H1 es “Manual de hilos adictivos en Threads” (línea 370). La polarización es un capítulo de 12 (Cap. 06). El comprador que paga por “el algoritmo de la polarización” recibe un manual general de Threads con un capítulo sobre polarizar. No es un fraude, pero es una promesa desalineada.
3. **Los umbrales del algoritmo son inventados y se presentan como especificación.** La tabla “Umbrales por tamaño de cuenta” (línea 550) da rangos exactos de replies, reposts, quotes, follows y “índice de empuje” (0,8 / 1,4 / 3,5). La fórmula del índice (línea 543) pondera replies×3, reposts×4, quotes×5, follows×6. Threads no publica nada de eso. El texto se cubre con “son órdenes de magnitud operativos, no promesas” (línea 451), pero una tabla con números exactos se lee como especificación, no como hipótesis.
4. **Los “tres casos numéricos completos” no son casos.** El propio archivo lo admite: “Los números son de escenarios construidos para que puedas comparar magnitudes, no capturas de una cuenta real” (línea 2326). Aun así, la sección se titula “Tres casos numéricos completos” y de ahí se derivan decisiones (“doblar F01, matar F14, arreglar el checkout”). A $29, la única prueba del producto es una simulación.
5. **Los 21 guiones son testimonios inventados que el comprador debe firmar.** “Perdí $1.940 en once días” (t01), “2.100 visitas, 41 clics al checkout, 3 compras de $9. Total: $27” (t01). La instrucción es “Cópialo, cambia los datos y publícalo como hilo” (línea 1872). Eso no es un guion: es una confesión falsa con el nombre del comprador. Cualquier audiencia con un mínimo de memoria lo detecta.

**La objeción que diría en voz alta:**
> “El ebook dice $17 en la portada, me cobraron $29, y los ‘casos reales’ el propio autor admite que son inventados. ¿Cuál de los tres precios es el verdadero?”

### B) Auditoría de contenido

**¿Cumple lo que promete el título?** No del todo. El archivo es un manual de operaciones de Threads, denso y útil, pero la promesa específica —“el algoritmo de la polarización”— se reduce a un capítulo. Si el título fuera “Manual de hilos adictivos”, cumpliría; con el título de la tienda, sobrepromete.

**Afirmaciones imposibles de verificar:**
- “9.400 visualizaciones con 380 seguidores” (línea 1133), sin fecha, cuenta ni captura.
- Los umbrales por tamaño de cuenta (10-18 replies para <2k, 35-55 para 2k-25k, 110-180 para >25k).
- La curva del simulador y el “/100”: el modelo es una fórmula propia presentada como “proyección de alcance”.
- Los tres casos: 22.400 views/168 replies/2 compras; 186.000/1.240/19; 1.240.000/7.800/96. Todos “construidos”.

**Relleno disfrazado:**
- Los 21 formatos tienen ~60 palabras cada uno; el capítulo 3 y la tabla maestra repiten la misma información.
- Los 30 hooks del final son frases de una línea; 10 de ellos ya aparecen como ejemplos en el capítulo 4.
- El “contrato de las próximas cuatro semanas” repite la cadencia del capítulo 8.
- El capítulo 11 (crisis) es útil, pero son 5 respuestas y un protocolo; no necesita 4 páginas.

**Vacíos:**
- Un caso real, con cuenta, fechas y captura. El único “caso” es una simulación.
- Fuentes o método para los umbrales. Ni un enlace a la documentación de Threads.
- Una advertencia clara de que los guiones son plantillas, no experiencias del autor.
- Ejemplos de hilos reales con su métrica (aunque sean de terceros, citados).
- Un puente al catálogo de Ronin: el libro termina sin ofrecer el siguiente producto.

### C) Auditoría técnica

Probado en Chromium headless:

- **Checklist de 30 puntos:** funciona, persiste en `localStorage` (`ronin:e03-lanzamiento`) y el contador llega a 30. Probado: 1/30 tras marcar una casilla.
- **Simulador de alcance:** funciona. Con los valores por defecto da 2.861 de alcance a 1h y score 61; al poner 30 minutos baja a 2.087 y 46, con el veredicto “Estás llegando tarde”.
- **Exportación de checklist:** genera un `.txt` con el estado de los 30 puntos.
- **Copiar:** los 71 botones `data-copy` apuntan a IDs existentes; no hay objetivos rotos.
- **Impresión:** genera un PDF de 84 páginas con el CSS de impresión correcto (fondo blanco, texto oscuro, `.toc` y controles ocultos). Es largo, pero legible.
- **Accesibilidad:** los inputs del simulador tienen `<label for>`; los botones tienen texto. El único problema es el tamaño: 84 páginas impresas sin índice de papel (el TOC se oculta en print), así que el PDF no tiene navegación.
- **Código muerto:** `initTabs()` se llama en `DOMContentLoaded`, pero no encuentra ningún `[data-tab]` en el documento; no hace nada. No afecta al usuario, pero es un residuo de plantilla.

### D) Auditoría de venta

- **Above the fold:** el cover es el mejor del lote: título, subtítulo, 12 capítulos, 21 estructuras, 21 guiones, 30 hooks, precio. En 10 segundos se ve un producto completo. El detalle de “$17” en la esquina arruina la percepción de $29.
- **Prueba/demostración:** hay demostración de contenido (se puede leer el TOC y un capítulo), pero no de resultado. Los casos son simulaciones admitidas.
- **Razón para comprar HOY:** ninguna. No hay garantía, ni bono, ni fecha, ni comunidad. El precio no sube mañana.
- **CTA final:** el cierre invita a “publicar el hilo 01 mañana”, no a comprar el siguiente producto. Como producto comprado, está bien; como embudo, no vende nada más.
- **Comparado con un ebook de $29 en Hotmart:** mejor en densidad (84 páginas, 22.850 palabras, 21 guiones) y peor en prueba (cero capturas, casos inventados). Un curso de $29 con video y un caso real compite mejor; un ebook de $19 con plantillas compite igual. A $29, está en el límite.

### E) Puntuación

| Dimensión | Puntaje | Razón |
|---|---:|---|
| Claridad de promesa | 62 | El cover es claro, pero el título de la tienda no coincide con el H1. |
| Densidad real | 88 | 22.850 palabras, 12 capítulos, 21 guiones, 21 formatos, simulador. |
| Originalidad | 72 | Los formatos y el sistema de primera hora tienen voz propia; los umbrales son inventados. |
| Confianza | 38 | Casos admitidos como ficción, cifras sin fuente, precio viejo. |
| Ejecución técnica | 86 | Checklist, simulador, exportación y PDF funcionan. |
| Valor percibido vs. precio | 55 | A $14 sería una compra clara; a $29 compite con productos con prueba real. |
| **Global** | **63** | El único que se acerca a valer $29, y aun así se sabotea solo. |

### F) Top 5 mejoras ordenadas por impacto en ventas

1. **Alinear el precio: $29 en la portada, el footer y el checkout, o quitar el precio del archivo.**
   - **Qué:** cambiar “E03 · $17” (línea 361), “Precio de portada $17 USD” (línea 381) y el footer (línea 2423) a $29; o eliminar toda mención de precio y dejar que la tienda lo ponga.
   - **Dónde:** hero-strip y footer.
   - **Por qué:** un precio contradictorio es la objeción más barata de eliminar y la que más desconfianza genera. No se puede defender $29 cuando el PDF dice $17.

2. **Alinear el título con el contenido o ampliar la polarización.**
   - **Qué:** renombrar el producto a “Manual de hilos adictivos en Threads” o añadir 3 capítulos específicos de polarización (matriz de riesgo, casos, límites legales) y mover el capítulo 6 al centro.
   - **Dónde:** H1 (línea 370), TOC y Cap. 06.
   - **Por qué:** el comprador que llega por “algoritmo de la polarización” siente que le vendieron otro libro. La promesa específica es la que justifica el clic y el precio.

3. **Convertir los umbrales en un protocolo de medición, no en una tabla de especificaciones.**
   - **Qué:** mantener la tabla como “hipótesis de trabajo”, añadir una columna “cómo lo mides” y una nota de que Threads no publica estos valores; eliminar el “/100” del simulador o etiquetarlo como “índice propio”.
   - **Dónde:** líneas 542-570 y el simulador (líneas 2330-2420).
   - **Por qué:** los compradores experimentados castigan la falsa precisión. Un protocolo honesto vale más que una tabla inventada.

4. **Sustituir los “tres casos” por un caso real, aunque sea pequeño.**
   - **Qué:** una cuenta real (propia o de un cliente con permiso), con fechas, capturas y números; si no existe, cambiar el título a “Tres modelos numéricos” y dejar de llamarlos casos.
   - **Dónde:** sección `#casos`, líneas 2326-2390.
   - **Por qué:** es la única sección que puede demostrar que el sistema funciona. Hoy el propio texto la descalifica.

5. **Convertir los 21 guiones en plantillas con placeholders y una advertencia.**
   - **Qué:** reemplazar “Perdí $1.940” por “Perdí [monto] en [días]”, y añadir una página “cómo usar esto sin inventar pruebas”.
   - **Dónde:** `t01`-`t21`, línea 1872.
   - **Por qué:** el comprador quiere publicar, no confesar. Una plantilla honesta se usa; un testimonio falso se archiva.

---

## E02

**Archivo:** `data/deliverables/e02_pinterest-cajero-oculto.html` · 176,1 KB · 1.899 líneas · ~14.750 palabras · 53 páginas impresas · Precio: $29 (portada dice $19).

### A) Veredicto de compra

**Precio que pagaría realmente:** $9. Es un buen mapa de Pinterest, pero no un producto de $29.

**Las 5 razones por las que no lo compraría:**

1. **La portada dice $19 y me cobran $29.** “$19” en el chip del header (línea 380) y “Este ebook… $19” en dos rutas de la tabla (líneas 1147-1148). Es el mismo problema que E03: el archivo es una plantilla de $19 revendida a $29 sin actualizar.
2. **El “caso completo” es una multiplicación, no un caso.** “El caso completo: de $171 a $1.000” (línea 1596) es 30.000 × 2% × 30% × 5% × $19. No hay cuenta, ni fechas, ni capturas, ni un pin real. A $29, la sección de prueba es una hoja de cálculo.
3. **Las cifras del modelo se presentan como hechos universales.** “Cada pin recibe a lo largo de su vida 2.400 impresiones, un CTR del 2% y 48 clics” (línea 556). No hay fuente, rango ni muestra. Después el propio texto admite que si el CTR cae al 0,5% el ingreso por pin baja a $3,42; es decir, el número estrella depende de un supuesto arbitrario.
4. **Las 30 rutas no conectan con el catálogo de Ronin.** Son ejemplos de finanzas personales: “plantilla presupuesto mensual”, “salir de deudas”, “fondo de emergencia”. Las ofertas se llaman “Caja Mínima”, “Tarifario”, “Guía de cobros” —productos que no existen en los 55 SKUs—. El comprador de @ronOverthinks que vende blueprints de IA o bóvedas de hooks no puede usar ni una.
5. **No entrega las “plantillas incluidas”.** El cover promete “PLANTILLAS INCLUIDAS” (línea 396), pero los únicos recursos copiables son ocho bloques de copy (`.copybox`, desde la línea 1179). No hay plantilla 1000×1500, ni SVG, ni archivo de Canva/Figma, ni CSV de keywords. A $29, “plantillas” es una palabra grande para ocho párrafos.

**La objeción que diría en voz alta:**
> “Es un manual de Pinterest genérico con ejemplos de finanzas que no tienen nada que ver con lo que vendo. Y el ‘caso real’ es una multiplicación. ¿Por esto cobran $29?”

### B) Auditoría de contenido

**¿Cumple lo que promete el título?** Sí en la categoría: es un manual de Pinterest para convertir pines en ventas. No en la especificidad: el “cajero oculto” es una metáfora, no un sistema que el comprador pueda encender; y las rutas no son las de este negocio.

**Afirmaciones imposibles de verificar:**
- 2.400 impresiones de por vida por pin, CTR 2%, 48 clics, 30% de leads, 5% de ventas.
- RPM de $2 a $8 (sección de umbrales), sin fuente.
- “El 70% de tu tiempo debe ir a investigación y rutas” (regla canónica 70/30), sin origen.
- “El caso completo” con $171 y $1.000: una proyección presentada como caso.
- “La mayoría abandona exactamente en el punto donde la curva empieza a subir”: una afirmación de comportamiento sin datos.

**Relleno disfrazado:**
- Las 30 rutas son variaciones del mismo nicho de finanzas; cinco usan la misma “Caja Mínima” y ninguna usa un producto del catálogo real.
- El capítulo 8 (“9 errores”) recapitula varios de los problemas ya tratados en el 1 y el 6: pin ilegible, CTR bajo, puente que no cumple.
- El plan 30/60/90 es genérico y no se conecta con el calendario de 30 días del capítulo 2.
- La “tabla de umbrales” es una lista de lugares comunes con plazos recomendados sin fuente.

**Vacíos:**
- **Plantillas reales de pin (1000×1500) y un archivo de keywords.**
- Un caso real con capturas y fechas.
- Rutas mapeadas a los 55 SKUs de Ronin.
- Fuentes de Pinterest (Trends, documentación de SEO) o al menos una nota de método.
- Garantía, soporte y política de actualización.

### C) Auditoría técnica

Probado en Chromium headless:

- **Simulador:** correcto. Con 30.000 impresiones, 2% CTR, 30% leads, 5% ventas y $19, da $171 y una meta de 175.439 impresiones/mes. La fórmula del objetivo es la inversa exacta.
- **Checklist:** 30 tareas, contador “2 / 30” al marcar dos, persistencia en `localStorage` (`ronin:check:launch`). Funciona.
- **Copiar plantillas:** todos los `data-copy` apuntan a elementos existentes; no hay objetivos rotos.
- **Impresión:** genera un PDF de 53 páginas con el CSS de impresión correcto (fondo blanco, controles ocultos). Legible.
- **Exportaciones:** no hay. La checklist no se puede exportar y las 30 rutas no se pueden descargar como CSV; el único output es el PDF completo.
- **Bug menor:** el contador de la checklist solo cuenta `#launch-list`; las otras checklists (por capítulo) no tienen contador, aunque el usuario podría esperar uno. No es grave.
- **Accesibilidad:** los inputs del simulador tienen `<label for>`; las 65 casillas de verificación tienen `aria-label="Tarea"` repetido, lo que no describe la tarea. Un lector de pantalla escucha “Tarea, casilla” 65 veces. Se arregla con `aria-labelledby` al texto del `<span>`.

### D) Auditoría de venta

- **Above the fold:** el cover es atractivo y claro: “Pinterest: el cajero automático que nadie mira”, 6 capítulos, 30 rutas, 30 tareas. En 10 segundos se entiende. El “$19” del header contradice el precio de venta.
- **Prueba/demostración:** la tabla de 30 rutas es una demostración de criterio, no de resultado. No hay un pin real, ni una cuenta, ni una captura.
- **Razón para comprar HOY:** ninguna. Sin garantía, sin bono, sin fecha.
- **CTA final:** cierra con “empieza por la primera tarea de la checklist”, no con una oferta. Como producto comprado, es correcto; como embudo, no vende el siguiente.
- **Comparado con un producto de $29:** peor. A $29 se consiguen manuales de Pinterest con plantillas Canva, auditorías y casos; este entrega texto, una tabla de rutas genéricas y un simulador. A $9-12 sería competitivo.

### E) Puntuación

| Dimensión | Puntaje | Razón |
|---|---:|---|
| Claridad de promesa | 66 | El cover y el índice son claros; las rutas no son las del catálogo. |
| Densidad real | 72 | 14.750 palabras con estructura de manual; algunas secciones se repiten. |
| Originalidad | 55 | Es un manual de Pinterest correcto, pero genérico; el 70/30 no es nuevo. |
| Confianza | 38 | Caso que no es caso; cifras sin fuente; precio viejo. |
| Ejecución técnica | 86 | Simulador, checklist, copia e impresión funcionan. |
| Valor percibido vs. precio | 40 | A $9-12 es una compra razonable; a $29, no. |
| **Global** | **56** | Un buen manual de $9 vendido a precio de $29. |

### F) Top 5 mejoras ordenadas por impacto en ventas

1. **Corregir el precio interno a $29 o eliminarlo.**
   - **Qué:** cambiar el chip “$19” (línea 380) y las dos filas “Este ebook… $19” (líneas 1147-1148).
   - **Dónde:** header y tabla de rutas.
   - **Por qué:** el comprador que ve $19 en la portada y paga $29 se siente estafado antes de leer. Es la corrección más barata y la de mayor impacto en reembolsos.

2. **Mapear las rutas a los 55 SKUs reales.**
   - **Qué:** reemplazar “Caja Mínima”, “Tarifario” y “Guía de cobros” por los blueprints, bóvedas y micro-apps del catálogo; dejar 10 rutas específicas en vez de 30 genéricas.
   - **Dónde:** sección “Treinta rutas semánticas”, líneas 1116-1158.
   - **Por qué:** la promesa es “rutas puente para convertir pines en ventas”. Si las rutas no llevan a los productos que el comprador tiene, el manual no se puede ejecutar.

3. **Entregar plantillas de verdad.**
   - **Qué:** un archivo HTML/SVG de pin 1000×1500 con la retícula, un CSV de 100 keywords y un documento de 5 titulares por arquetipo.
   - **Dónde:** cover “PLANTILLAS INCLUIDAS” (línea 396) y capítulo 5.
   - **Por qué:** “plantillas” es la palabra que justifica el precio. Hoy son bloques de texto copiables; el comprador espera archivos editables.

4. **Renombrar “El caso completo” y añadir un caso real.**
   - **Qué:** llamarlo “El modelo de caja” y publicar aparte un caso con una cuenta real (aunque sea de 5.000 impresiones) con captura y fechas.
   - **Dónde:** línea 1596.
   - **Por qué:** la palabra “caso” promete evidencia; la multiplicación no lo es. Un caso pequeño y verificable vale más que un caso grande inventado.

5. **Añadir garantía, soporte y una nota de actualización.**
   - **Qué:** “30 días de garantía”, un correo de soporte y una fecha de revisión del manual.
   - **Dónde:** footer.
   - **Por qué:** a $29, la falta de recurso es la objeción silenciosa que mata el checkout. Una garantía explícita baja el riesgo percibido sin cambiar el producto.

---

## B09

**Archivo:** `data/deliverables/b09_boveda-respuestas-polemicas.html` · 533,6 KB · 2.251 líneas · ~32.200 palabras · 200 scripts · Precio: $27.

### A) Veredicto de compra

**Precio que pagaría realmente:** $7. El contenido está bien escrito, pero no se puede usar sin mentir.

**Las 5 razones por las que no lo compraría:**

1. **El manual prohíbe exactamente lo que venden los scripts.** “Usar cifras inventadas. Una cifra falsa se convierte en una captura y la captura se convierte en una crisis” (línea 2152). Y decenas de los 200 scripts son testimonios en primera persona con cifras inventadas: “Mi primera venta sin seguidores llegó el día 19, después de 41 publicaciones y 3 dólares en anuncios” (B09-167), “Hotmart registró 27 checkouts iniciados para 7 pagos completados en mi cuenta” (B09-168). El comprador tiene que elegir entre usar el producto o seguir el manual.
2. **Las variantes A y B se contradicen sobre el mismo hecho.** B09-168 A dice “27 checkouts iniciados para 7 pagos”; B dice “Veinte checkouts iniciados, siete cerrados”. No son dos formas de decir lo mismo: son dos realidades distintas de la misma cuenta. Si el comprador publica ambas, lo pillan. Si publica una, está inventando.
3. **El archivo pesa 533 KB porque los 200 scripts están dos veces.** Los 200 `<article>` estáticos ocupan ~288.000 caracteres (líneas 315-2114) y el array `DATA` del script otros ~185.000 (línea 2169); al cargar, el JS reemplaza el HTML con el mismo contenido. Es el doble de peso para el mismo texto, y una fuente de desincronización si alguien edita una copia.
4. **No hay prueba de que ningún script funcione.** Ni un hilo real, ni una captura, ni una métrica del autor. Los números que aparecen son inventados, no medidos. A $27, el comprador paga por 200 líneas de copy con una promesa de resultado que nadie ha verificado.
5. **No hay impresión/PDF ni una vista “top 20”.** La bóveda se vende como herramienta de operación, pero no se puede imprimir ni generar un PDF para tenerlo a mano, y no tiene una selección curada por momento. El manual dice que “la bóveda se ordena por momento”, pero el filtro es por categoría y búsqueda; no hay un índice por minuto.

**La objeción que diría en voz alta:**
> “Me vendes 200 respuestas con cifras inventadas y en el mismo archivo me dices que usar cifras inventadas te quema la cuenta. ¿Cuál de los dos documentos creo?”

### B) Auditoría de contenido

**¿Cumple lo que promete el título?** Sí en cantidad: 200 scripts, 5 categorías de 40, variante A/B. No en calidad: los scripts son una plantilla de testimonio falso, no un banco de respuestas verificadas.

**Afirmaciones imposibles de verificar:**
- Todos los “mi cuenta”, “mis 27 checkouts”, “mis 4.100 seguidores”, “mis 6.800 dólares facturados”.
- “De 1.900 suscriptores en Gumroad, 212 abrieron el último envío” (B09-169).
- “Sumé mis seis suscripciones de IA: 137 dólares mensuales” (B09-196).
- “El 38 por ciento de mis compras se hizo entre medianoche y las cinco de la mañana” (B09-190).
- Las variantes A/B que contradicen cifras del mismo caso (B09-168).

**Relleno disfrazado:**
- Muchas variantes B son la variante A reescrita en tercera persona; no añaden un ángulo nuevo.
- El manual repite lo que ya dicen las categorías: momento, métrica, integridad.
- La “regla de integridad” es un párrafo; decenas de los 200 scripts que la siguen la incumplen.
- Las 5 categorías se solapan: “Giro Contrarian” y “Ataque Quirúrgico” comparten el mismo movimiento de contradicción.

**Vacíos:**
- Un conjunto “seguro” de scripts que no dependan de cifras inventadas.
- Una guía de adaptación: cómo cambiar el contexto sin cambiar la estructura.
- Un caso real con captura y métricas.
- Impresión/PDF y una vista por minuto.
- Una advertencia de divulgación: si usas un guion, no lo presentes como experiencia propia.

### C) Auditoría técnica

Probado en Chromium headless:

- **Render:** 200 tarjetas (`#grid .script`), contador 200, sin errores JS.
- **Buscador:** “Hotmart” devuelve 4; el filtro por categoría devuelve 40. Funciona.
- **Exportaciones:** Markdown y JSON se descargan correctamente (probado: `b09-respuestas-polemicas.md` y `.json`). “Copiar filtrados” usa el mismo pipeline.
- **Impresión:** no hay `window.print` ni botón de PDF. El CSS de impresión existe, pero el usuario no tiene cómo invocarlo desde la interfaz. A $27, es una carencia frente a E02/E03, que sí imprimen.
- **Persistencia:** no hay favoritos ni `localStorage`; el estado del filtro se pierde al recargar. No se promete, pero en una bóveda de 200 scripts el comprador espera guardar su selección.
- **Duplicación:** 288.000 caracteres de HTML estático + 185.000 de JSON; el JS reemplaza el HTML al cargar. La página funciona, pero el archivo es el doble de grande de lo necesario.
- **Accesibilidad:** 407 botones, solo 4 `aria-label`; los botones de copiar tienen texto visible (“Copiar A”), así que el nombre accesible existe. El buscador tiene `aria-label`; el `<select>` también. No hay imágenes.

### D) Auditoría de venta

- **Above the fold:** el hero dice “Bóveda de 200 Auto-Respuestas y Comentarios Cebos”, 200 scripts, 5 categorías, A/B. En 10 segundos se entiende y se ve útil. Es el segundo mejor above the fold del lote, después de E03.
- **Prueba/demostración:** el producto es la demostración: se puede leer un script completo y decidir. Pero la demostración también revela el problema: varios de los scripts de “Morbo Numérico” son testimonios con cifras inventadas.
- **Razón para comprar HOY:** ninguna. Sin garantía, sin bono, sin fecha, sin precio que suba.
- **CTA final:** el manual termina con “si un script funciona, no lo repitas textualmente”, no con una oferta. Como producto comprado, es consejo; como embudo, no vende.
- **Comparado con un banco de respuestas de $27:** peor. A $27 el comprador espera un sistema con casos, video o comunidad; este entrega 200 tarjetas y un manual. A $7-9 sería una compra impulsiva.

### E) Puntuación

| Dimensión | Puntaje | Razón |
|---|---:|---|
| Claridad de promesa | 72 | 200 scripts, 5 categorías, A/B: se entiende. |
| Densidad real | 62 | 200 scripts, pero muchos son variantes del mismo movimiento. |
| Originalidad | 58 | La voz es buena; la estructura es repetitiva. |
| Confianza | 18 | Testimonios inventados y contradicción con su propia regla. |
| Ejecución técnica | 62 | Buscador y exportaciones funcionan; falta impresión y persistencia. |
| Valor percibido vs. precio | 32 | $27 por copy sin prueba; $7 sería justo. |
| **Global** | **45** | Buen copy, mala ética de uso, entrega incompleta. |

### F) Top 5 mejoras ordenadas por impacto en ventas

1. **Eliminar la contradicción “cifras inventadas”.**
   - **Qué:** convertir todos los scripts en plantillas con placeholders (`[checkouts]`, `[pagos]`, `[monto]`) y añadir una nota: “publica solo datos que puedas probar”. Mantener el manual tal cual.
   - **Dónde:** `DATA` (línea 2169) y manual (línea 2152).
   - **Por qué:** hoy el producto se autodestruye: el comprador no puede usarlo y seguir las reglas del propio producto. Es la objeción que más veces va a aparecer en comentarios.

2. **Corregir las contradicciones A/B.**
   - **Qué:** cada par A/B debe decir el mismo hecho con otro tono, no otro hecho. Unificar las cifras de B09-168, B09-169 y B09-196.
   - **Dónde:** los pares citados.
   - **Por qué:** si el comprador publica ambas variantes, queda en evidencia; si publica una, sabe que la otra es mentira. La credibilidad del banco entero depende de que los datos sean consistentes.

3. **Añadir impresión/PDF y una vista “top 20 por momento”.**
   - **Qué:** un botón “Imprimir/PDF” como en E02/E03, y una pestaña “Primera hora” con los 20 scripts ordenados por minuto (0-3, 3-8, 8-25, 25-55, 55-60).
   - **Dónde:** barra de controles (línea 100) y manual.
   - **Por qué:** la bóveda se vende como herramienta de operación; sin PDF ni orden por momento, el comprador tiene que buscar a mano en 200 tarjetas.

4. **Eliminar la duplicación de los 200 artículos.**
   - **Qué:** dejar solo el render desde `DATA` o solo el HTML estático; si se mantiene el HTML por SEO/offline, no re-renderizar al cargar.
   - **Dónde:** líneas 315-2114 y 2169.
   - **Por qué:** reduce el archivo a la mitad y elimina el riesgo de que una copia quede desactualizada. Un archivo de 533 KB para 200 tarjetas es señal de armado apresurado.

5. **Añadir un caso real y una guía de adaptación.**
   - **Qué:** un hilo real con captura de métricas y los scripts exactos que se usaron; una página “cómo adaptar sin inventar”.
   - **Dónde:** manual, después de “Los siete errores”.
   - **Por qué:** es lo que separa un banco de copy de un sistema probado. Sin prueba, $27 es el precio de la esperanza.

---

## Ranking final: cuál está más cerca de venderse y cuál es el que más avergüenza

**Más cerca de venderse: E03.** Es el único con densidad suficiente para sostener $29: 84 páginas impresas, 22.850 palabras, 21 estructuras, 21 guiones y un simulador que funciona. Le faltan dos cosas baratas: alinear el precio de la portada y reemplazar los casos inventados por uno real. Con esas dos correcciones, es un producto defendible. Sin ellas, es un buen manual que se sabotea en la primera página.

**Segundo: E02.** Tiene la estructura y la ejecución de un manual de $12, no de $29. Las 30 rutas son genéricas y no conectan con el catálogo; las plantillas no existen. Si se mapean las rutas a los 55 SKUs y se entregan archivos editables, sube a $19. A $29, compite con productos que sí incluyen plantillas y casos.

**Tercero: B01.** Es el más fácil de vender por precio ($19) y utilidad inmediata (buscador, copiar, exportar). Pero el “500” es una mentira de marketing y los 370 hooks generados son detectables en minutos. Si se vendiera como “130 hooks + 370 variantes” a $9, sería honesto y probablemente vendería más. A $19 con la contradicción actual, el reembolso es cuestión de tiempo.

**Cuarto: B09.** El copy es bueno, pero el producto se contradice a sí mismo. Un banco de respuestas que te prohíbe inventar cifras y te entrega 200 testimonios inventados no es un sistema: es una trampa para el comprador. A $27, es el producto con mayor riesgo de reseña negativa.

**El que más avergüenza: L01.** No porque sea el peor escrito —está por encima del promedio— sino porque es la primera puerta de la marca y falla en lo único que tenía que hacer. Su tesis es “la prueba visual específica vende”; su prueba es un mockup CSS. Su promesa es un PDF; el PDF se imprime en negro sobre negro. Su objetivo es capturar un correo; el correo se tira a la basura. Un lead magnet que no captura, no entrega y no enlaza es la peor carta de presentación posible para un catálogo de 55 productos.

---

## Las 10 correcciones que aplican a los 5 (patrones repetidos)

1. **Un solo precio por producto, en todos los lugares.**
   - E03 dice $17 en portada, header y footer; se vende a $29. E02 dice $19 en el header y en la tabla de rutas; se vende a $29. B01 dice $19 y coincide, pero su footer dice “130 HOOKS”. El comprador detecta la inconsistencia antes de comprar. **Acción:** una constante de precio en el generador y una prueba automatizada que compare portada, footer y checkout.

2. **La prueba tiene que ser real o estar etiquetada como ilustración.**
   - L01 usa una recreación CSS y la llama “la captura original”. E03 y E02 llaman “caso” a una simulación. B01 pone “Evidencia comprobada en Stripe” sin evidencia. **Acción:** si no hay captura, usar la palabra “modelo” o “ejemplo”; si hay captura, redactar datos sensibles y enlazar la fuente.

3. **Prohibido el testimonio inventado en primera persona.**
   - B09 construye su banco de 200 scripts sobre “mi cuenta”, “mis 27 checkouts”, “mis 4.100 seguidores”. E03 vende 21 guiones con “perdí $1.940”. L01 vende un experimento con 22 ventas. **Acción:** convertir los testimonios en plantillas con placeholders y añadir una guía de adaptación honesta. Un comprador puede publicar una plantilla; no debería publicar la vida de otro.

4. **“Caso” significa evidencia; “modelo” significa matemática. No mezclarlos.**
   - E02 titula “El caso completo” a una multiplicación. E03 titula “Tres casos numéricos completos” a escenarios que el propio texto desmiente. **Acción:** renombrar las secciones y poner la etiqueta “modelo” en la primera línea, no en una nota al pie.

5. **El lead magnet tiene que capturar el correo y entregar un archivo.**
   - L01 valida el email y llama a `window.print()`. No hay endpoint, no hay CRM, no hay PDF. **Acción:** un `POST` real (o un servicio como Formspree/ConvertKit), un PDF pregenerado y una prueba de entrega en el correo. Sin eso, no es un lead magnet: es una página bonita.

6. **La impresión/PDF se prueba con un render real, no con el CSS escrito.**
   - L01 imprime `.element` con fondo #0e0e15 y texto #111111. El PDF tiene 14 páginas, no 18. **Acción:** un test que genere el PDF, cuente páginas y verifique contraste de fondo/texto en las clases principales. Es la corrección más barata y la que más rápido se nota.

7. **Un solo conteo por producto, consistente en hero, ficha, footer y filtros.**
   - B01 dice 130 en el título, 500 en el hero, 130 en la ficha, 500 en el KPI y 130 en el footer. **Acción:** derivar todos los textos de una constante (`HOOKS.length`) y eliminar los números escritos a mano.

8. **Garantía, soporte y política de actualización visibles en cada producto de pago.**
   - Ninguno de los cuatro de pago tiene un correo de soporte, una garantía del vendedor ni una fecha de revisión. Las menciones de “garantía” que aparecen son parte de las plantillas de copy, no del producto. **Acción:** un bloque de footer con “30 días de garantía”, un correo y “última revisión: [fecha]”. A $19-29, la falta de recurso es la objeción silenciosa.

9. **Cada producto de pago debe tener un puente al siguiente.**
   - B01, E03, E02 y B09 no tienen un solo enlace externo. L01 tiene uno, y está muerto. **Acción:** un bloque de cierre con el producto recomendado, su precio y su ruta puente. Es dinero que ya está en la mano del comprador.

10. **Curaduría antes que volumen.**
    - B01 ofrece 500 hooks sin un “empieza por estos 10”. B09 ofrece 200 scripts sin un “top 20 por momento”. E02 ofrece 30 rutas sin un “haz estas 5 primero”. **Acción:** una sección “Empieza aquí” en cada producto, con 5-10 elementos, el momento de uso y la métrica. La curaduría es lo que convierte un archivo en un sistema y lo que justifica el precio.

---

**Nota de método:** los cinco archivos se leyeron completos en contenido y JavaScript; del CSS se revisaron las reglas relevantes (impresión, foco, contraste, estados). La auditoría técnica se ejecutó en Chromium 156 headless sobre un servidor local: renderizado, búsqueda, filtros, favoritos, persistencia, exportaciones, simuladores, checklists e impresión a PDF. Los conteos de palabras son aproximados (HTML sin `<script>`/`<style>`). No se modificó ningún archivo.
