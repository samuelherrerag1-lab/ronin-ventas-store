# Productos premium A — M06, B05, B06, B07 y B12

Reescritura profunda de cinco entregables del catálogo, con contenido estático verificable,
interacción real, progreso local y diseño dark premium 100 % offline.

- **Responsable:** `productos-a` (task-7)
- **Repo:** `C:\Users\USER\Documents\ronin_ventas`
- **Alcance:** `data/deliverables/m06_ronin-all-access-vault.html`,
  `b05_boveda-prompts-ingenieria-inversa.html`, `b06_arsenal-prompts-creacion-ebooks.html`,
  `b07_boveda-flujos-automatizacion-local.html`, `b12_arsenal-auditoria-fugas-dinero.html`.
- **Sin tocar:** generador (`product_factory` / `product_templates_elite`), backend, frontend,
  catálogo, `social_feeds`, portadas de arte y el servidor `:8765`.

---

## 1. Diagnóstico medido: por qué no alcanzaban

Los cinco archivos eran *shells de interfaz* con el contenido en arrays de JavaScript. La
apariencia era de producto, pero al medir el HTML real (texto visible sin ejecutar JS) el
contenido se caía:

| SKU | KB | Palabras visibles antes | Controles de progreso | Copiar | Diagnóstico |
| --- | ---: | ---: | ---: | ---: | --- |
| M06 | 84,8 | 4.955 | 0 | 0 | Índice de enlaces y catálogo maestro; sin manual de instalación, sin criterios por activo, sin buscador ni filtros. |
| B05 | 281,0 | 1.705 | 0 | 0 | 40 prompts metidos en JS: al leer el HTML solo queda la portada. Sin verificación, sin laboratorio, sin checklist. |
| B06 | 66,4 | 1.882 | 0 | 1 | 14 prompts sin cadena de producción, sin ejemplos, sin generadores, sin plantillas operativas. |
| B07 | 71,3 | 2.605 | 0 | 1 | 40 recetas con nombre y poco más: sin disparador verificable, sin snippet ni plan de reversión, sin medición del ahorro. |
| B12 | 140,4 | 4.685 | 0 | 0 | 40 puntos con cálculo, pero sin plan de 30 días, sin matriz de reasignación, sin checklist y sin gráficos. |

Patrones comunes detectados al revisar el HTML anterior:

1. **Volumen falso.** B05 pesaba 281 KB y solo mostraba 1.705 palabras: el 90 % del peso era
   CSS/JS de plantilla, no contenido útil. B06 tenía 9 etiquetas `h2`, una de ellas
   («Preguntas Frecuentes») repetida tres veces.
2. **Listas sin mecanismo.** Los prompts y recetas se presentaban como títulos; no había
   contrato de salida, ejemplo, error típico ni criterio para saber si el resultado servía.
3. **Cero continuidad.** No había checklists, progreso guardado ni exportación: el comprador
   no podía saber qué había hecho ni retomarlo al día siguiente.
4. **Interacción de fachada.** B06 tenía 2 campos de entrada y 5 botones; B07, 3 y 6. Los
   botones de «copiar» del lote anterior no existían como tales (0 atributos `data-copy`).
5. **Referencias externas sueltas.** Algunos archivos mantenían URLs `http(s)` de ejemplo en
   el texto y enlaces de salida; el estándar del proyecto pide cero dependencia de red.

---

## 2. Estándar aplicado

Barra de calidad que se exigió a los cinco archivos:

- **≥ 8.000 palabras visibles estáticas o ≥ 100 ítems de datos útiles.** Todas las páginas
  llevan el contenido en el markup; el JS solo filtra, copia, calcula y guarda.
- **100 % offline.** CSS y JS propios, tipografías del sistema, iconos SVG inline. Cero CDN,
  cero fuentes externas, cero `http(s)` en todo el archivo (verificado con regex).
- **Interacción real:** buscador global, filtros por categoría/nivel, checklist con progreso en
  `localStorage`, copiar al portapapeles, exportar estado JSON y plan Markdown, reinicio.
- **Herramientas propias por producto:** laboratorio de prompts (B05), generador de títulos,
  índice y calculadora de margen (B06), calculadora de ahorro (B07), calculadoras de fuga,
  hora real y runway (B12), índice de 52 activos con rutas copiables (M06).
- **Diseño dark premium:** sistema visual común, acento por SKU, jerarquía editorial, tarjetas
  con densidad medida, iconos SVG (cero emojis), foco visible, `prefers-reduced-motion`.
- **Honestidad:** sin promesas de ingresos, sin cifras inventadas, sin placeholders/TODO, con
  secciones explícitas de límites y licencia.
- **Responsive real:** comprobado a 390 px y 1440 px sin desbordamiento horizontal.

---

## 3. Método (OpenCode V2 + pipeline local determinista)

1. **Fábrica OpenCode V2.** Se verificó el daemon en `127.0.0.1:28894` y la sesión de la
   Fábrica `ses_e64c0d9b1ffe56MtJmi0RNNym4` con modelo `deepseek-v4.1-flash`, variante `max` y
   `cost: 0`. Se le envió una auditoría externa acotada del B06 (solo lectura, sin ejecutar
   comandos) para contraste de calidad. La respuesta se registra en la sección 6.
2. **Generación.** El contenido se estructuró como datos (listas de activos, prompts, recetas,
   puntos de fuga) y se renderizó con un pipeline Python local sobre un sistema de diseño
   compartido. Se eligió esta vía porque garantiza de forma determinista las condiciones
   duras del producto: HTML estático, cero red, cero marcadores, recuento de palabras
   reproducible y validación automática en cada iteración.
3. **Bucle de QA por archivo:** generar → medir palabras/ítems/`http`/marcadores → ejecutar
   `scripts/validate_deliverables.py` → extraer JS y validar con `node --check` → abrir con
   Playwright/Chrome y probar buscador, filtros, copiar, calculadoras y progreso → captura
   desktop y móvil → revisar la imagen → corregir.
4. **Conservación de la mejor versión.** Cada original se copió a
   `data/_cuarentena/productos/<archivo>.v1-backup.html` antes de reemplazarlo. La versión
   nueva solo se promovió después de pasar validación y verificación en navegador.

---

## 4. Antes / después

Métricas medidas sobre el HTML entregado (texto visible sin `<script>`/`<style>`). «Copiar»,
«checks» e «inputs» cuentan controles reales en el marcado.

| SKU | KB antes → después | Palabras antes → después | Ítems de datos | Checks | Copiar | Inputs | Botones |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: |
| M06 | 84,8 → **227,6** | 4.955 → **9.643** | 52 activos con función, momento y combinaciones | 0 → **82** | 0 → **64** | 0 → **83** | 5 → **89** |
| B05 | 281,0 → **398,7** | 1.705 → **20.456** | 120 prompts en 12 familias | 0 → **47** | 0 → **120** | 7 → **55** | 54 → **152** |
| B06 | 66,4 → **178,3** | 1.882 → **8.142** | 24 prompts + 6 plantillas + 3 casos completos | 0 → **47** | 1 → **32** | 2 → **72** | 5 → **60** |
| B07 | 71,3 → **209,3** | 2.605 → **8.626** | 40 recetas + 12 comandos | 0 → **43** | 1 → **52** | 3 → **49** | 6 → **76** |
| B12 | 140,4 → **179,9** | 4.685 → **8.034** | 40 puntos de fuga en 7 categorías | 0 → **100** | 0 → **1** | 51 → **189** | 7 → **26** |

Interactividad nueva por producto:

- **M06:** 10 pestañas, buscador, filtros por formato y nicho, 64 rutas copiables, 82 puntos de
  control (instalación + plan + activación) con progreso y exportación.
- **B05:** buscador y filtros por familia y nivel, 120 prompts copiables, constructor de
  prompts en vivo, evaluador 0-100, 8 cadenas, 47 puntos de checklist.
- **B06:** generador de 12 títulos con datos propios, generador de índice de 10 capítulos,
  calculadora de margen con comisión fija y reembolsos, rellenador de variables, 32 bloques
  copiables, 47 puntos de control y persistencia de inputs.
- **B07:** calculadora de ahorro (minutos → horas → valor), filtros por categoría y nivel,
  52 snippets copiables, 43 puntos de control.
- **B12:** 40 puntos con dos campos editables cada uno (coste y horas) que suman en vivo,
  deslizador de rescate, gráfico de barras por categoría, proyección SVG a 12 meses,
  calculadoras de hora real y runway, 100 puntos de control.

---

## 5. Qué se construyó en cada SKU

### M06 · THE INSIDER VAULT
Dejó de ser un índice de enlaces. Ahora es un **manual de instalación + índice interactivo +
plan de uso**: qué incluye el bundle que se entrega por Gumroad, 12 pasos de instalación con
comandos y criterio de éxito, los 52 activos con «qué resuelve / cuándo usarlo / con qué se
combina», seis rutas por cuello de botella, plan de 30 días, 25 reglas de operación, 82 puntos
de activación, sistema de versiones y actualización manual, licencia y límites.

### B05 · Bóveda de 120 prompts
120 prompts completos (rol, contexto, entrada, contrato de salida, ejemplo, variantes, errores)
en 12 familias: reconocimiento de oferta, hooks, voz, páginas, embudos, producto y precio,
mercado, canales, automatización, auditoría, modelos de negocio y escalado. Añade anatomía del
prompt, 12 variables globales, 8 cadenas de ejecución, laboratorio que arma prompts y evaluador
que puntúa cualquier prompt antes de usarlo.

### B06 · Arsenal de prompts para ebooks de 29
Cadena de 24 prompts en 6 etapas (demanda, arquitectura, escritura, prueba, anti-slop, oferta),
flujo de 7 pasos con criterio de no avanzar, 6 plantillas, 3 casos completos con índice y
página, 20 reglas anti-slop y tres generadores offline (títulos, índice, margen). Incluye
calculadora declarada como aritmética, no como proyección.

### B07 · 40 recetas de automatización local
40 recetas con disparador, herramienta gratuita, pasos verificables, snippet copiable, criterio
de éxito, ahorro estimado, riesgo y plan de reversión. Añade mapa de la operación, instalador
de 7 días, biblioteca de 12 comandos, calculadora de ahorro con mantenimiento, 20 errores y
checklist de 43 puntos.

### B12 · Auditoría de fugas de tiempo y dinero
40 puntos de control en 7 categorías, cada uno con pregunta, señal, coste típico, esfuerzo,
acción y destino del rescate. Tres calculadoras reales (fuga total con rescate, hora real,
runway), gráfico de barras por categoría, proyección SVG, matriz de reasignación, guía de
cancelación y negociación, plan de 30 días y 100 puntos de control con progreso.

---

## 6. Verificación (evidencia literal)

### 6.1 Validador oficial

```powershell
PS> .\.venv\Scripts\python.exe scripts\validate_deliverables.py
 B05  OK    399.8 KB  20456 palabras
 B06  OK    179.1 KB   8142 palabras
 B07  OK    210.1 KB   8626 palabras
 B12  OK    180.5 KB   8034 palabras
 M06  OK    228.1 KB   9643 palabras
Validos: 55/55 · con avisos: 32
B01 hooks: 500 parseados, 0 duplicados exactos
```

Los cinco archivos del lote están en estado **OK**, sin fallos duros ni avisos de credibilidad
(`claim`, `placeholder`, `TODO`, `lorem`, `http`). El recuento global sigue 55/55.

### 6.2 Métricas propias

```text
m06_ronin-all-access-vault.html            KB= 227.6 words= 9643 http=0 OK
b05_boveda-prompts-ingenieria-inversa.html KB= 398.7 words=20456 http=0 OK
b06_arsenal-prompts-creacion-ebooks.html   KB= 178.3 words= 8142 http=0 OK
b07_boveda-flujos-automatizacion-local.html KB= 209.3 words= 8626 http=0 OK
b12_arsenal-auditoria-fugas-dinero.html    KB= 179.9 words= 8034 http=0 OK
```

### 6.3 JavaScript y navegador real

- `node --check`: 10 bloques `<script>` extraídos de los cinco archivos → **todos OK**.
- Playwright con Chrome real sobre `file://`:
  - 0 errores de consola/página en los cinco archivos.
  - Buscador: consulta sin coincidencias → 0 resultados. Contador corregido: al buscar dentro
    de una pestaña muestra `0 aquí · 121 en total`, no un total engañoso de pestañas ocultas.
  - Filtros: B05 familia → 10 prompts; B06 etapa → 4 prompts; B07 categoría → 6 recetas;
    B12 categoría → 6 puntos.
  - B05: el constructor produce prompt completo («Actúa como analista…») y el evaluador
    puntúa 0-100 con diagnóstico.
  - B06: 12 títulos generados, índice de 10 capítulos, margen con comisión fija y reembolsos
    (417,68 USD netos en el escenario de prueba con 10 % de reembolsos), rellenador de
    variables operativo y persistencia de inputs verificada tras recargar la página.
  - B12: coste 80 → rescate 48 (60 %), hora real 6,47 USD, runway 10 meses.
  - Copiar: doble clic sobre un botón no lo deja bloqueado; vuelve a «Copiar» en 1,2 s.
  - Progreso: checkboxes disparan cambio y actualizan barra/porcentaje (`1/47 · 2%`).
- Responsive 390×844: `scrollWidth = 390 = innerWidth` en los cinco (sin overflow), 0 errores JS.

### 6.4 Evidencia visual

Capturas desktop y móvil en `data/_cuarentena/productos/screens_A/` (10 PNG). Se revisaron
visualmente con el inspector de imágenes para comprobar jerarquía, acentos, legibilidad y
ausencia de recortes.

### 6.5 Auditoría externa con OpenCode V2

- Daemon: `http://127.0.0.1:28894` respondió; sesión de la Fábrica
  `ses_e64c0d9b1ffe56MtJmi0RNNym4` con `deepseek-v4.1-flash`, `variant=max`, `cost=0`.
- Se envió un prompt acotado (solo lectura, sin ejecutar comandos) pidiendo 5 debilidades
  concretas de B06. La respuesta llegó y las cinco observaciones eran válidas; se aplicaron:

| # | Hallazgo del auditor | Corrección aplicada |
| --- | --- | --- |
| 1 | Las plantillas se copian con variables `[TEMA]`, `[AVATAR]`, `[PRECIO]` sin resolver. | Nuevo **rellenador de variables** en B06 (pega el prompt, completa 4 campos, copia el resultado) + aviso en la sección de prompts. |
| 2 | La calculadora de margen omitía la comisión fija por venta y los reembolsos. | Calculadora ampliada: comisión % + **0,50 USD fijos por venta** + reembolsos % + impuesto, con desglose visible. |
| 3 | El botón Copiar guardaba el HTML en cada clic: doble clic lo dejaba fijado en «Copiado». | Corregido en el shell común de los cinco productos: se guarda el original una vez, se bloquea durante el feedback y se restaura en 1,2 s. |
| 4 | El contador de búsqueda sumaba resultados de pestañas ocultas. | Ahora muestra `N aquí · M en total` cuando hay búsqueda o filtros activos. |
| 5 | «Guardar generadores» persistía solo texto y no lo recargaba. | Persistencia real de los inputs en `localStorage` y rehidratación al abrir; el botón se renombró a «Guardar inputs». |

- Tras aplicar las correcciones se regeneraron los cinco archivos y se repitieron las
  verificaciones: validador oficial en OK, `node --check` en OK, Playwright sin errores y
  pruebas específicas de los cinco casos corregidos.

## 7. Copias de seguridad y restauración

Originales conservados en `data/_cuarentena/productos/`:

| SKU | Copia |
| --- | --- |
| M06 | `m06_ronin-all-access-vault.v1-backup.html` (87.833 B) |
| B05 | `b05_boveda-prompts-ingenieria-inversa.v1-backup.html` (292.109 B) |
| B06 | `b06_arsenal-prompts-creacion-ebooks.v1-backup.html` (68.196 B) |
| B07 | `b07_boveda-flujos-automatizacion-local.v1-backup.html` (73.089 B) |
| B12 | `b12_arsenal-auditoria-fugas-dinero.v1-backup.html` (145.700 B) |

Para restaurar una versión anterior:

```powershell
cd C:\Users\USER\Documents\ronin_ventas
Copy-Item "data\_cuarentena\productos\b05_boveda-prompts-ingenieria-inversa.v1-backup.html" `
          "data\deliverables\b05_boveda-prompts-ingenieria-inversa.html" -Force
.\.venv\Scripts\python.exe scripts\validate_deliverables.py
```

---

## 8. Límites y pendientes

1. **Margen de palabras.** B06 (8.142) y B12 (8.034) superan el umbral de 8.000 por poco. Cualquier
   edición futura debe volver a medir; si se recorta contenido, hay que añadir otro bloque.
2. **Validación editorial humana.** El contenido es original y verificable, pero conviene una
   pasada humana de tono y claims antes de publicarlo: el estándar prohíbe promesas de ingresos
   y el validador automático no juzga persuasión.
3. **Arte de portada.** No se regeneraron portadas ni se gastó Vertex AI; los SKU conservan su
   arte actual. Si el rediseño de portadas llega después, este lote no lo bloquea.
4. **Peso.** B05 pesa ~400 KB; es correcto para un archivo offline, pero conviene comprobarlo en
   la entrega de Gumroad (descarga y apertura en móvil) antes de publicar.
5. **Tests.** No se ejecutó `pytest` completo (fuera del alcance de la tarea); la verificación se
   hizo con el validador oficial del repo, `node --check` y Playwright.
6. **Sin tocar** backend, frontend, catálogo, generador ni `social_feeds`. El servidor `:8765`
   no se reinició.

---

*Generado por `productos-a` para task-7. Reproducible con los comandos de la sección 6.*
