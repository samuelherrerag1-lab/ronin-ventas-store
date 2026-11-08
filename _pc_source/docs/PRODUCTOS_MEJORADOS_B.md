# Productos premium B — L02, L03, A02, A11, A12

Fecha: 2026-11-04 · Responsable: `productos-b` · Repo: `C:\Users\USER\Documents\ronin_ventas`

Lote B del encargo «productos de verdad»: dos lead magnets y tres micro-apps reescritos a
estándar premium, 100% offline, con interacción funcional y diseño dark propio. Este documento
registra el diagnóstico anterior, lo que se construyó, la evidencia de verificación y lo que
queda pendiente.

---

## 1. Método

### 1.1 OpenCode V2 (fábrica oficial)

Se usó el daemon OpenCode V2 en `http://127.0.0.1:28894` con la sesión de la Fábrica de
Productos `ses_e64c0d9b1ffe56MtJmi0RNNym4`, modelo `opencode-go/deepseek-v4.1-flash`
(`variant: max`, `cost: 0`), cabecera `x-opencode-directory` apuntando al repo y autenticación
Basic leída de `C:\Users\USER\.config\opencode\service.json`.

- **L02** se delegó completo a OpenCode V2 (prompt con requisitos duros de HTML único,
  offline, dark premium, 27 hooks con mecanismo/variantes/ejemplos/error/detonante, 8.000+
  palabras, 6+ controles). OpenCode escribió
  `data/_cuarentena/productos/opencode/l02_v2.html` (244 KB, 14.387 palabras visibles).
  Tras mi auditoría (sintaxis, enlaces, emojis, controles) se promovió a
  `data/deliverables/l02_27-hooks-prohibidos.html`.
- **L03, A02, A11, A12** se autorizaron directamente con `write`/`edit` y diseño propio. La
  razón es de fiabilidad: los requisitos de estos cuatro (wizard con validación, motor de
  cálculo, gráficos SVG condicionados, tablas editables y persistencia) exigían control exacto
  del DOM y del JS; delegarlos habría costado más ciclos de auditoría que productlos. El
  método OpenCode se usó donde aportaba: contenido masivo y biblioteca de datos.

### 1.2 Reglas aplicadas a los cinco

- Un solo archivo HTML autocontenido, sin CDN, sin fuentes externas, sin imágenes remotas.
- CSS y JS propios; tema dark premium con acentos terracota/oro/verde; iconos SVG inline;
  cero emojis (verificado con regex de rangos Unicode).
- Controles funcionales reales: inputs, selects, sliders, checkboxes, calculadoras, gráficos
  SVG construidos en JS, copiar al portapapeles, exportar CSV/JSON/MD/TXT y `localStorage`.
- Sin placeholders, sin `TODO`, sin lorem ipsum, sin promesas de ingresos garantizados; los
  textos de proyección dicen explícitamente que son aritmética de supuestos del usuario.
- Responsive 360/390/768/1440; `prefers-reduced-motion`; `:focus-visible`; `aria-label` en
  controles y en gráficos.

---

## 2. Diagnóstico del lote anterior

| SKU | Estado anterior | Problema principal |
| --- | --- | --- |
| L02 | 57,9 KB · 3.202 palabras · 2 inputs · 0 SVG · sin localStorage | Los 27 hooks eran una lista plana: nombre + frase. Sin mecanismo psicológico, sin variantes por nicho, sin probador ni filtros. Cero recurso visual. |
| L03 | 55,9 KB · 4.115 palabras · 1 input · 5 botones · sin localStorage | El «meta-prompt» era un texto que se copiaba; no había wizard, ni validación de variables, ni checklist, ni ejemplos de salida. Sin persistencia. |
| A02 | 114,1 KB · 1.295 palabras · 4 inputs · 1 slider · 2 emojis | Simulador con números pero sin manual: no explicaba fórmulas, mezcla, AOV ni cómo leer el diagnóstico. Emojis prohibidos. |
| A11 | 134,6 KB · 1.862 palabras · 47 inputs · 21 sliders · 2 emojis | Muchos controles, poca sustancia: no había plan de 30 días, ni perfiles, ni explicación de recortes; la fecha de libertad no estaba conectada a una narrativa de decisión. |
| A12 | 110,7 KB · 1.490 palabras · 26 inputs · 3 sliders · 4 emojis | No había coste de vida por ciudad, ni validación de tasas, ni explicación de spread/comisiones; emojis en la UI. |

Los cinco originales se conservan en `data/_cuarentena/productos/*.ORIGINAL.html` (copia
byte a byte, verificada por hash antes de reescribir).

---

## 3. Resultado después (medido, no estimado)

Métricas estáticas = texto visible fuera de `<script>`/`<style>` (mismo criterio del validador).
Métricas renderizadas = `document.body.innerText` en Chromium con todo el JS ejecutado.
Controles renderizados = inputs + selects + textareas contados en el DOM final.

| SKU | Antes KB | Después KB | Palabras antes | Palabras estáticas | Palabras renderizadas | Controles antes | Controles renderizados | SVG | localStorage | Ítems útiles | Validador |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :---: | ---: | :---: |
| L02 | 57,9 | 244,0 | 3.202 | 14.387 | 15.908 | 37 | 176 (3 inputs + 3 selects + 1 textarea + 1 slider + 168 botones) | 86 | Sí | 270+ | OK |
| L03 | 55,9 | 78,5 | 4.115 | 4.538 | 4.918 | 6 | 46 (23 inputs/checkboxes + 4 selects + 3 textareas + 16 botones) | 32 | Sí | 117 | OK |
| A02 | 114,1 | 89,7 | 1.295 | 3.548 | 4.076 | 23 | 56 (38 inputs + 10 selects + 8 botones) + 13 sliders | 45 | Sí | 82 | OK |
| A11 | 134,6 | 72,4 | 1.862 | 2.626 | 3.975 | 85 | 76 (62 inputs + 11 botones + 3 sliders) | 42 | Sí | 87 | OK |
| A12 | 110,7 | 70,9 | 1.490 | 2.758 | 3.377 | 50 | 45 (33 inputs + 3 selects + 6 botones + 3 sliders) | 40 | Sí | 96 | OK |

Nota sobre bytes: A02/A11/A12 pesan menos que antes porque el contenido duplicado y el CSS
muerto se eliminaron; el contenido útil y la interacción aumentaron. L02 creció 4,2× porque
pasó de lista a manual con 324 variantes y 15.908 palabras renderizadas.

### 3.1 Conteo de ítems útiles (para la barra «≥80 ítems»)

- **L02 — 270+**: 27 hooks × 10 campos reales (nombre, texto, mecanismo, por qué funciona,
  3 variantes por nicho, 2 ejemplos de uso, error típico, detonante medible) + 7 leyes +
  anatomía en 3 capas + protocolo de 30 días + 4 formatos de exportación.
- **L03 — 117**: 12 variables explicadas + 40 encargos de extracción + 20 puntos de checklist
  + 12 recetas + 3 ejemplos de salida + 10 FAQ + 20 errores frecuentes.
- **A02 — 82**: 10 peldaños editables + 20 experimentos priorizados + 24 puntos de checklist
  + 12 casos arquetípicos + 10 FAQ + 6 filas de benchmarks.
- **A11 — 87**: 20 recortes + 30 acciones de plan + 12 perfiles + 5 activos iniciales
  editables (ampliables a 12) + 10 FAQ + 10 errores.
- **A12 — 96**: 24 ciudades editables + 20 líneas de coste de conversión + 20 acciones de plan
  + 12 jugadas de arbitraje + 10 FAQ + 10 errores.

---

## 4. Qué hace cada producto ahora

### L02 · 27 Hooks Prohibidos (manual de operaciones)

- 27 hooks con texto literal, mecanismo psicológico, lógica de feed, 3 variantes por nicho
  (324 en total), ejemplos copiables, error típico y detonante medible.
- Probador de hook real: pega tu primera línea, obtiene puntuación 0-100 en 5 dimensiones
  (especificidad, tensión, prueba, claridad, salida) con gauge y barras SVG y diagnóstico
  textual de mejora.
- Biblioteca interactiva: buscador, filtro por familia, slider de intensidad, filtro de
  favoritos, contador de resultados, progreso de lectura 27/27 guardado en `localStorage`.
- Copiar hook, copiar todos, exportar selección (`.md`/`.txt`), reiniciar progreso.
- Capítulos de prosa: anatomía del feed, 7 leyes de polarización sana, test A/B de 30 días y
  límites éticos/riesgo de cuenta.

### L03 · Extractor de Competencia (meta-prompt + wizard)

- Wizard de 6 pasos con 12 variables; validación en vivo de los 6 requisitos y barra de
  progreso. Genera un meta-prompt completo con rol, referencia, formato, precio, nicho,
  audiencia, objetivo, profundidad, restricción, formato de salida, evidencia, dimensiones y
  criterio de calidad.
- Reglas de honestidad embebidas en el prompt: citar evidencia, marcar `[EVIDENCIA]`,
  `[INFERENCIA]`, `[DESCONOCIDO]`, prohibir estimar ingresos ajenos y reproducir párrafos.
- Checklist de 20 puntos con progreso persistente; 40 encargos de extracción; 12 recetas;
  3 ejemplos de salida completos; 20 errores frecuentes; FAQ.
- Copiar, exportar `.md`, exportar `.txt`, guardar borrador en `localStorage`, cargar preset.

### A02 · Simulador de Escalera de Ingresos

- 10 peldaños editables (nombre, tipo, precio, mezcla) con normalización automática.
- Palancas: visitas, conversión, bump, upsell, crecimiento, meta y horizonte.
- Cálculo en vivo de ingreso, AOV, compradores, ventas, RPV, tráfico necesario para la meta,
  meses hasta la meta y peldaño más fuerte/débil.
- Dos gráficos SVG propios (ingreso por peldaño y proyección con línea de meta) que se
  redibujan con cada cambio.
- Escenarios guardables en `localStorage`: guardar, cargar, borrar y comparador de dos o más.
- Exportación CSV/JSON, copiar resumen, reinicio, caso ejemplo, validación de meta/horizonte.
- Manual de 13 secciones: fórmulas, lectura del diagnóstico, anatomía de los peldaños,
  benchmarks honestos, 12 casos, protocolo de 30 días, errores, glosario, 20 experimentos,
  24 puntos de checklist y plantillas de copy por peldaño.

### A11 · El Reloj de Escape 9-5

- Runway, brecha mensual, ingreso por activos, colchón objetivo y fecha de libertad
  proyectada, recalculados en vivo.
- Tabla de activos editable (precio, unidades/mes, margen %) con add/delete y total.
- 20 recortes con checkbox, importe editable, efecto inmediato en gasto/runway y meses
  ganados; gráfico comparativo SVG antes/después.
- Curva de runway SVG con umbral de colchón y marca del mes de agotamiento.
- Plan de 30 días verificable, 12 perfiles de partida, 10 errores, FAQ, glosario.
- Persistencia en `localStorage`, copiar plan, exportar CSV/JSON, reinicio y caso ejemplo.

### A12 · Tablero de Arbitraje de Divisas

- Tres tasas editables (USD/COP, USD/MXN, USD/BRL) con fecha de observación, doble validación
  (rango de referencia con aviso + rango absoluto con rechazo) y mensajes por campo.
- Comisiones modeladas: plataforma, spread y envío; ingreso bruto en la moneda elegida, neto
  en USD y eficiencia neta/bruta.
- 24 ciudades con costo de vida local editable, costo en USD, poder de compra, ahorro mensual,
  filtro por moneda, orden por poder de compra/costo/ahorro y selección de ciudad activa.
- Proyección SVG de ahorro acumulado con línea de meta y meses para la meta.
- Exportación CSV/JSON, copiar resumen, guardar estado, restaurar tasas y restaurar costos.
- Manual de 10 secciones con 20 líneas de coste, 12 jugadas, riesgos, plan de 30 días, errores
  y glosario; FAQ de 10 preguntas.

---

## 5. Verificación ejecutada

| Gate | Comando / método | Resultado |
| --- | --- | --- |
| Entregables del catálogo | `.\\.venv\\Scripts\\python.exe scripts\\validate_deliverables.py` | **exit 0 · 55/55 válidos**; los 5 de este lote sin fallos (L02 quedó sin avisos tras retirar una mención) |
| Sintaxis JS | extracción de `<script>` + `node --check` por archivo | OK en los 5 |
| HTML completo | `<title>` presente y cierre `</html>` | OK en los 5 |
| Recursos externos | regex de `src/poster/link href/@import/url()` http(s) | 0 en los 5 |
| UTF-8 | conteo de `\ufffd` | 0 en los 5 |
| Emojis | regex `U+1F300-1FAFF`, `U+2600-27BF`, `U+2B00-2BFF` sobre texto renderizado | 0 en los 5 |
| JS en navegador real | Playwright + Chrome 156, `file://`, consola y `pageerror` | **0 errores** en los 5 |
| Interacción real | Playwright: sliders, guardado, wizard, demo, tasas, checkboxes | Verificado: A02 ingreso $1.496 → $4.487 al subir visitas y escenario persistido; L03 genera prompt de 2.951 caracteres con secciones ROL y HONESTIDAD; A11 runway 23,0 meses y fecha marzo 2027 con reservas actualizadas; A12 neto $2.837 → $4.729 y rechazo de tasa absurda; L02 diagnóstico activo, gauge y 27 tarjetas filtrables |
| Responsive | scrollWidth a 390 px | 0 desbordamiento horizontal en los 5 |
| Capturas | `data/_cuarentena/productos/screens/` | `*_before.png` (tras interacción), `*_top.png`, `*_mobile.png` |

---

## 6. Backups y conservación de la mejor versión

- Originales: `data/_cuarentena/productos/<sku>.ORIGINAL.html` (copia exacta; hash SHA-256
  parcial registrado antes de reescribir).
- Copia de trabajo de OpenCode para L02:
  `data/_cuarentena/productos/opencode/l02_v2.html` (fuente del entregable promovido).
- Capturas de evidencia: `data/_cuarentena/productos/screens/`.
- No se perdió ninguna versión anterior: el reemplazo se hizo solo después de que la versión
  nueva pasó validador, `node --check`, Playwright y revisión visual.

---

## 7. Pendientes y límites honestos

1. **Palabras vs. ítems.** L02 supera 8.000 palabras por sí solo (14.387). L03, A02, A11 y A12
   cumplen la barra por la vía de «≥80 ítems útiles» (117, 82, 87 y 96), no por palabras
   estáticas (3.500-4.900). Si el criterio del dueño exige 8.000 palabras en cada app, falta
   añadir capítulos de prosa a las tres apps; el motor y los datos ya están listos.
2. **Diseño de los tres apps**: es coherente y premium, pero no se ha validado con usuarios
   reales ni contra una referencia visual externa. Se verificó con capturas desktop/móvil.
3. **L02**: el contenido completo lo generó OpenCode V2; yo auditué estructura, sintaxis,
   honestidad y controles, y corregí la única mención a «garantizado». No reescribí su prosa.
4. **A12**: los costos de vida son estimaciones de trabajo editables, no datos oficiales;
   están declarados como tales en el producto. No modela impuestos ni regulación cambiaria.
5. **A11**: la fecha de libertad es una simulación con crecimiento de activos definido por el
   usuario; no incluye inflación ni impuestos.
6. **A02**: los benchmarks son rangos de referencia, no estadísticas del nicho; están marcados
   como tales.
7. No se ejecutó `pytest` completo ni se reinició el servidor 8765 (fuera de mi encargo).
8. No se tocaron backend, frontend, catálogo ni otros entregables.
