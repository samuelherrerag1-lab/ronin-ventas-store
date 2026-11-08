# Capturas iOS — réplica del lockscreen 17.5/18 y pantallas de app

Documento técnico del renderer "anzuelo". Objetivo: que las capturas se lean como
la pantalla de un iPhone 15 Pro real, no como una tarjeta web con un reloj grande.

## 1. Alcance

| Archivo | Cambio |
| --- | --- |
| `backend/services/ios_lockscreen_css.py` | CSS del lockscreen reescrito con medidas reales, material translúcido, fallback de `backdrop-filter`, tema claro/oscuro y sello |
| `backend/services/ios_html_templates.py` | Fondo embebido, Dynamic Island, status bar, iconos SVG de marca, notificaciones, fuentes base64 |
| `backend/services/ios_app_templates.py` | Notas (papel claro/oscuro, checks reales) y dashboard Stripe (chart, lista, tab bar) |
| `backend/services/playwright_bait_renderer.py` | Pipeline HTML→PNG reutilizable, sello impreso desde HTML, verificación por archivo (no por exit code) |
| `scripts/render_ios_variants.py` | 8 variantes + hoja de contactos + manifest |
| `scripts/compare_ios_capture.py` | Comparación A/B/DIFERENCIA + métricas (solo Pillow) |
| `docs/CAPTURAS_IOS.md` | Este documento |
| `data/captures/ios/` | Antes, después, comparaciones y hoja de contactos |

## 2. Medidas verificadas

Pantalla base: 393 × 852 pt, export @3x = 1179 × 2556 px (iPhone 15 Pro / 16).
Valores en puntos (pt) salvo que se indique.

| Elemento | Medida iOS | Implementación | Comprobación |
| --- | --- | --- | --- |
| Lienzo | 393 × 852 pt @3x | viewport 393×852, `device_scale_factor=3` | PNG 1179×2556 |
| Safe area | 59 / 34 pt | status bar 54 + isla; home a 8 pt | ficha de dispositivo |
| Dynamic Island | 125 × 37 pt, top 11, radio 999 | `125px × 37px`, `top:11px` | bbox medido: 124.7 pt de ancho |
| Status bar | 54 pt de alto | `height:54px`, iconos centrados | — |
| Hora de status | 17 pt semibold, tracking -0.3 | `font-size:17px`, `-0.3px`, tabular | — |
| Celda / WiFi / batería | 18×12 / 17×12 / 27×13 | SVG `currentColor` | — |
| Candado | 22 pt | SVG `lock.fill` | — |
| Fecha | 17 pt semibold | `17px`, tracking -0.35 | — |
| Reloj | ~96 pt de altura óptica | `font-size:112px`, tracking -3.9, line-height .92 | glifo ≈ 90 pt en PNG |
| Widgets | 155 × 64 pt, radio 18 | blur 24, borde .5 pt | — |
| Notificación | 361 pt de ancho, radio 20 | `left/right:16px`, `radius:20px` | — |
| Icono de app | 38 × 38 pt, radio 10 | SVG 38×38 | — |
| Tipos notificación | título 15 semibold / cuerpo 15 / hora 13 | — | — |
| Separación tarjetas | 8 pt | `margin-bottom:8px` | — |
| Acciones | círculo 50 pt, inset 30 pt | blur 22, borde .5 pt | — |
| Home indicator | 134 × 5 pt, bottom 8 | `134px × 5px` | medido: 134.0 × 5.0 pt |
| Sello | 22–26 px @3x | `font-size:8px` (=24 px), esquina inferior izquierda | — |

Fuentes consultadas:

- Insets por modelo, 1179×2556 / 393×852 / safe area 59–34: [iPhone safe-area insets by model](https://burakkose.me/apps/screen-specs/iphone-safe-area-insets/)
- Shell iOS (isla 125×37 top 11, home 139×5, safe area 59/34, radio de pantalla 55): [app.md · apple-design-skill](https://raw.githubusercontent.com/naplesblue/apple-design-skill/main/app.md)
- Escala tipográfica iOS (17 pt cuerpo, 15 pt secundario, 11 pt tab bar, títulos 34/17): [iOS Design Guidelines](https://www.learnui.design/blog/ios-design-guidelines-templates.html)
- Layout y safe areas (documento oficial): [Apple HIG · Layout](https://developer.apple.com/design/human-interface-guidelines/layout)

Discrepancias documentadas:

- La guía de shell indica home indicator 139×5; el encargo pide 134×5. Se implementó **134×5** (coincide con el estándar de iPhone X en adelante).
- El reloj se cita como "~96 pt" en el encargo. Medido sobre capturas, los dígitos ocupan ~90 pt de alto y ~297 pt de ancho con 5 glifos; se implementó `font-size:112px`, que reproduce esa altura óptica. Si se usara `font-size:96px` el reloj quedaría ~20 % más pequeño que en un iPhone real.

## 3. Cómo se renderiza

1. El HTML se genera en Python con las fuentes SF Pro de `data/fonts` embebidas en base64 y el fondo como `data:image/jpeg`.
2. `render_html_to_png()` intenta Playwright Chromium (393×852, DSF 3, JS desactivado); si no hay binario, usa **Chrome headless** con `--window-size=393,852 --force-device-scale-factor=3`; si no hay Chrome, cae a un lienzo Pillow de emergencia.
3. La CSP del documento bloquea scripts. No hay recursos externos: solo `data:` y fuentes locales.
4. El sello se imprime desde el HTML; el pipeline valida el PNG por archivo y tamaño (>5000 bytes), no por el exit code del navegador.

## 4. Modos y variantes

`render_ios_bait_screenshot_png` mantiene los 3 modos del endpoint:

- `ios_lockscreen` — lockscreen con Dynamic Island, candado, fecha, reloj, notificaciones Gumroad/Hotmart/Stripe y sello.
- `iphone_note_3am` — Notas iOS: nav amarilla, título 26 pt, cuerpo 17 pt, lista con viñetas, checklist con 2 ítems hechos y 1 pendiente, barra de herramientas. Variante clara tipo papel (`theme="light"`).
- `stripe_gumroad_dashboard` — dashboard Stripe Express: header de cuenta, segmentado Hoy/7D/30D, volumen bruto, gráfico con grilla y punto final, KPIs, transacciones y tab bar.

Variantes generadas por `scripts/render_ios_variants.py`:

| # | Variante | Qué muestra |
| --- | --- | --- |
| 01 | `lockscreen_dark_wallpaper` | foto editorial + 2 notificaciones |
| 02 | `lockscreen_dark_no_wallpaper` | degradado oscuro (sin asset) |
| 03 | `lockscreen_light_no_wallpaper` | tema claro + degradado lavanda |
| 04 | `lockscreen_dark_widgets` | widgets de Stripe bajo el reloj |
| 05 | `lockscreen_titanium_one_notif` | wallpaper titanium + 1 notificación |
| 06 | `notes_3am_dark` | Notas en modo oscuro |
| 07 | `notes_3am_light` | Notas en modo papel |
| 08 | `stripe_dashboard` | dashboard completo |
| — | `contact_sheet.png` | hoja de contactos con las 8 |

## 5. Sello de simulación

- Texto: `SIMULACIÓN · MOCKUP — NO ES UNA VENTA REAL`.
- Activo por defecto, 24 px @3x (8 pt), esquina inferior izquierda, blanco al 44 % (gris oscuro en modo papel).
- `BAIT_WATERMARK=0` lo desactiva **solo para uso interno** (pruebas de composición). No se elimina del código.

## 6. Uso

```powershell
# 8 variantes + hoja de contactos + manifest
.\.venv\Scripts\python.exe scripts\render_ios_variants.py

# solo un subconjunto
.\.venv\Scripts\python.exe scripts\render_ios_variants.py --only notes

# comparación A/B/DIFERENCIA
.\.venv\Scripts\python.exe scripts\compare_ios_capture.py --all
.\.venv\Scripts\python.exe scripts\compare_ios_capture.py antes.png despues.png --threshold 12
```

## 7. Antes / después

Capturas "antes" tomadas del endpoint vivo antes del cambio; "después" generadas
con el código nuevo (mismo viewport y datos):

- Antes: `data/captures/ios/before/lockscreen_dark.png`, `notes_3am.png`, `stripe_dashboard.png`
- Después: `data/captures/ios/01_lockscreen_dark_wallpaper.png`, `06_notes_3am_dark.png`, `08_stripe_dashboard.png`
- Comparaciones: `data/captures/ios/compare_*.png`
- Hoja de contactos: `data/captures/ios/contact_sheet.png`

Métricas de `compare_ios_capture.py --all` (umbral 10/255):

| Captura | MAE | Píxeles distintos | Diferencia fuerte (>32) | Bytes antes → ahora |
| --- | --- | --- | --- | --- |
| Lockscreen | 17.01 | 25.51 % | 7.03 % | 2.109.136 → 2.515.643 |
| Notas | 26.24 | 14.18 % | 13.83 % | 172.821 → 252.799 |
| Stripe | 25.85 | 28.84 % | 13.18 % | 181.540 → 255.354 |

Cambios que explican la diferencia:

1. Dynamic Island 125×37 con lente, antes inexistente.
2. Status bar con la **hora** a la izquierda (como un iPhone con isla), en lugar del operador "TIGO".
3. Reloj con tracking -3.9 y sombra suave; fecha 17 pt.
4. Notificaciones ancladas abajo con material translúcido, icono 38 pt y tipografía 15/13 pt; se eliminó el encabezado "Centro de notificaciones" y el botón X porque el lockscreen real no los muestra (solo aparecen al desplegar el centro de notificaciones).
5. Iconos de marca dibujados en SVG: "g" de Gumroad sobre `#FF90E8`, llama de Hotmart sobre degradado naranja, "S" de Stripe sobre `#635BFF`.
6. Sello discreto en la esquina inferior izquierda (antes era una píldora amarilla centrada sobre el home indicator).
7. Notas: fecha bajo el título, cuerpo 17 pt, checklist real (2 hechos + 1 pendiente), variante papel.
8. Stripe: chart con grilla, KPI, transacciones con iconos, próxima liquidación y tab bar.

## 8. Diferencias reales y pendientes

No es una réplica idéntica. Lo que todavía no coincide:

- **No hay bisel ni chasis**: se renderiza solo la pantalla del iPhone, no el hardware con marco y botones.
- **Iconos de marca aproximados**: los SVG de Gumroad/Hotmart/Stripe son reconstrucciones de trazo, no los assets oficiales de prensa. La llama de Hotmart es una aproximación.
- **Wallpaper claro sintético**: el tema claro usa un degradado porque en `data/generated_images` no hay una foto clara y el alcance no permite añadir assets. Se ve como un fondo desenfocado, no como una foto editorial.
- **Tipografía**: se usa SF Pro Display Regular/Medium/Bold (woff local), no la familia variable exacta de iOS 17/18 ni SF Pro Rounded.
- **Navegador**: Playwright no tiene binarios instalados en el venv (`chromium_headless_shell-1194` ausente), así que el render real cae a Chrome headless. Instalar `playwright install chromium` aceleraría y estabilizaría el pipeline.
- **Servidor vivo**: el proceso de `127.0.0.1:8765` corre sin `--reload`. `POST /api/customizations/render-ios-png` responde 200 y >5000 bytes, pero sigue sirviendo las plantillas anteriores hasta reiniciar el backend. El código nuevo se verificó llamando `render_ios_bait_screenshot_png` directamente (3 modos, 1179×2556, >5000 bytes).
- **Validación contra captura real**: las medidas vienen de fichas técnicas y guías, no de un screenshot propio del mismo wallpaper; falta una comparación 1:1 en dispositivo físico.
- **Contenido**: las cifras siguen siendo datos de ejemplo del llamador; la captura es un mockup, no evidencia de ventas.
