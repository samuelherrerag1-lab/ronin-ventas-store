# Reporte de Mejoras — Ronin Ventas OS

**Fecha:** 04/11/2026 (America/Bogota) · **Alcance:** sistema completo (backend, frontend, datos, generadores, publicación) · **Método:** auditoría de código, pruebas reales con pytest/build/smoke, llamada real a Vertex AI, auditoría independiente y 4 subagentes de corrección en paralelo.

---

## 1. Resumen ejecutivo

El sistema pasó de ser **una demo convincente que no podía vender** a **un sistema publicable con un único bloqueo de negocio**: faltan las URLs de checkout de los 52 productos de pago. Todo lo demás necesario para publicar ya existe, funciona y está verificado con evidencia.

| Antes | Ahora |
|---|---|
| Vertex apuntaba al proyecto viejo (`example-project-id`, `us-central1`, `gemini-2.5-flash-image`) | Proyecto nuevo `REDACTED_EXAMPLE_PROJECT`, `global`, `gemini-3.1-flash-image` + fallback lite, retry 429/503, ledger de coste real y sonda `scripts/probe_vertex.py` |
| 0 rutas puente servidas / landings inexistentes | 55 landings dinámicas + 55 landings estáticas con portada, precio, canonical/OG y legales |
| 0 checkout; botones que simulaban compra | `POST /api/catalog/{sku}/checkout` + `checkout-bulk` con validación https/host; UI para pegar URLs; 52 blockers honestos mientras falten |
| 0 lead magnets entregables (URL a un PDF inexistente) | Leads con lock, consentimiento y entrega del HTML real (`/deliverables/l01…`) |
| Entregables de pago públicos en `/deliverables` | Guard por host + defensa en `/store` + test de regresión (pago 403 desde LAN, lead magnet 200) |
| UI dependía de Tailwind CDN y cdnfonts (sin internet se rompía) | Tailwind 3.4 compilado (CSS 34.5 KB → 107.7 KB con utilidades), 0 URLs remotas, fuentes self-hosted |
| "Publicado" y "Mutar con IA" falsos | `published` exige URL/fecha; el estado local dice "marcado localmente"; "mutar" se declara variante de plantilla y no infla likes |
| Alertas `CONECTADO` sin evidencia (Google Master) | La sonda verifica cookies reales del vault; si no hay sesión queda `SIN_VERIFICAR` |
| 50 posts de prueba idénticos en el feed real | Cola limpia: 4 posts canónicos + 10 pines propios (benchmarks separados) |
| Sin git, sin README, sin .env.example, sin docs de publicación | Repo git con baseline + `.gitignore`, README operativo, `.env.example`, `docs/BACKEND_NOTES.md`, `docs/GENERADORES_VALIDACION.md`, `docs/AUDITORIA_2026-11-04.md`, `docs/QA_FINAL.md` |
| 50 tests | 85 tests verdes (incluye publicación, checkout, store exposure, honestidad, 250 líneas) |

**Veredicto:** listo para publicar **contenido y tienda** hoy mismo; listo para **cobrar** en cuanto se peguen las 52 URLs de Gumroad/Hotmart (≈20–40 min de trabajo manual).

---

## 2. Correcciones por área

### 2.1 Vertex AI / generadores de imagen (bloqueante #1 resuelto)
- `backend/config.py`: proyecto, región, modelo y fallback configurables por entorno (`GOOGLE_CLOUD_PROJECT`, `VERTEX_LOCATION`, `NANO_BANANA_MODEL`, `NANO_BANANA_FALLBACK_MODEL`, `FINOPS_CIRCUIT_BREAKER_USD`). Precios reales por modelo (0.067 / 0.034 USD).
- `backend/services/vertex_image_service.py` reescrito: reintentos con espera creciente solo para errores transitorios (429/RESOURCE_EXHAUSTED/503/deadline), fallback automático al modelo lite, validación de bytes (>500 B) antes de declarar éxito, escritura con extensión según mime, ledger propio en `data/finops-ledger.json` y `vertex_status()` para health/readiness.
- `scripts/probe_vertex.py`: sonda real sin UI (matriz proyecto/región/modelo). Ejecución verificada: `gemini-3.1-flash-image` OK (974 KB, 15.5 s) y `gemini-3.1-flash-lite-image` OK (42 KB, 7.2 s). Una generación real por el servicio quedó registrada: $0.067, 1 imagen, modelo nuevo.
- `backend/services/playwright_bait_renderer.py` + `ios_html_templates.py` + `ios_app_templates.py`: escape HTML de todos los campos, allowlist de wallpaper con resolución segura (anti path traversal), CSP `script-src 'none'`, JavaScript deshabilitado en Chromium y sello visible **"SIMULACIÓN · MOCKUP — NO ES UNA VENTA REAL"** en cada captura.
- `.agents/skills/hybrid-retina-vertex-renderer/SKILL.md` actualizado al proyecto/modelo nuevos (era una referencia activa al proyecto viejo).

### 2.2 Productos y generadores (55 SKUs)
- `product_factory.py` (142 líneas): guardián único de 20 KB (`MIN_DELIVERABLE_BYTES`), `force=False`, lead magnets L01–L03 intocables, validación pre-escritura (`</html>`, `<title>`, tamaño) y escritura atómica. Ya no puede pisar un producto real con la plantilla.
- `product_templates_elite.py` (127) + `product_templates_sections.py` (227): fallback 100% offline, portada real incrustada en base64, 0 emojis, 0 cifras inventadas (se eliminaron "93%", "1.2%", "38%", "44%"), etiqueta de hooks correcta (20, antes decía 15) y aviso visible de que es plantilla de respaldo, no producto verificado.
- `scripts/validate_deliverables.py`: 55/55 válidos. Avisos reales: 34 (claims citados/negados 41, `placeholder` editorial, L03 con variables intencionales de meta-prompt, algunos productos bajo 2.000 palabras). **0 claims positivos de ingresos garantizados.**
- Limpieza de basura: 4 archivos de la raíz movidos a `data/_cuarentena/` con hashes y README; B01 raíz se conservó porque **no** era duplicado exacto (decisión del auditor respetada).

### 2.3 Publicación (55 rutas, tienda, legales, contenido)
- `backend/services/publish_pack.py` + `publish_content.py` + `publish_legal.py`: `build_site(base_url="")` genera `data/publish_site/` con:
  - tienda `index.html` (55 SKUs, portadas, precios, estado de checkout),
  - 55 rutas semánticas (`/blueprint`, `/boveda`, `/app`, `/sistema`, `/vault`, `/gratis`),
  - 4 legales reales (términos, privacidad Ley 1581, reembolso, licencia) + hub, enlazados desde tienda y landings,
  - `content/threads.json` y `content/pinterest.json` (cola real, sin benchmarks) + README de publicación manual,
  - `sitemap.xml` (60 `<loc>`), `robots.txt`, `404.html`, `manifest.json`,
  - assets (55 portadas, 10 pines, 3 piezas de Ron) y **solo los 3 lead magnets** en `deliverables/`.
- `scripts/build_publish_pack.py --summary --verify` → **VERIFY PASS**: 55 rutas + index + legales + 0 recursos externos.
- `scripts/deploy_store.ps1`: deploy a GitHub Pages en modo plan por defecto; solo ejecuta con `-Confirm`. No se creó ni publicó ningún repo externo.
- `render_landing(..., base_url="")` retrocompatible, con canonical/OG absolutos, portada y footer legal; elimina la viñeta de pasarela cuando no hay checkout (no promete un pago que no existe).
- `backend/routers/api_publish.py`: `/api/publish/readiness`, `/kit`, `/mark`, `/export-site`, `/site-manifest`; `mark` declara explícitamente `published_to_network: false` y `tracked_locally: true`.
- Publish Center en el frontend: checklist con semáforo y blockers reales, cola copiable, checkout por SKU y en bloque, exportación del sitio con manifest y enlace a `/store/`.

### 2.4 Backend / datos / honestidad
- `json_store.py`: lock por archivo, `tmp + os.replace`, cuarentena de JSON corrupto; aplicado a catálogo, feeds, métricas, leads, conectores y diagnóstico.
- FX única COP 4200; parseo de "79.800"; conversión BRL/EUR; order bumps separados de ventas; atribución etiquetada como aproximada (ya no se llama "funnel" a un `startswith`).
- `probe_runners.py`: Google Master verifica cookies reales de sesión (deja de ser un falso verde).
- `api_feeds`: `published`/`mutate-hook` honestos, sin inflar likes simulados.
- Leads: lock, consentimiento explícito, validación de SKU y entrega del HTML real.
- Teardowns de competencia movidos a `data/competitor_notes.json` con fecha y "sin verificar".
- CSV: límite 2 MB, fecha ISO, sin PII en la respuesta.
- `security_middleware.py`: token opcional `RONIN_API_TOKEN`, rate-limit 1/20 s en `test-all` y `vertex-generate`, 409 si hay job Vertex en curso.
- `main.py`: CORS válido y **restringido a orígenes local/LAN** (una web externa ya no puede leer la API), headers de seguridad (CSP, nosniff, referrer, frame), 404 JSON para `/api/*` inexistentes, `/store` dinámico con guard de entregables, health con estado real de Vertex y sitio.

### 2.5 Frontend
- Tailwind compilado offline (CDN y cdnfonts eliminados), `puppeteer-core` fuera, 0 emojis/glifos, 0 URLs remotas en el build.
- Errores de API visibles con reintento, `ErrorBoundary`, estados vacíos honestos ("sin datos", "Pendiente en backend"), sin totales inventados (`|| 55`, `|| 8` eliminados), sin productos fake en Stan, checkout deshabilitado si no hay URL.
- Accesibilidad: `aria-label` en botones icon-only, Escape/focus en modales, contraste y tamaños revisados; responsive del Bait Lab corregido (ya no desborda a 360/390 px).
- Modelo/coste de Vertex mostrados desde el backend real (no "gemini-2.5" ni "$0.03" fijos).

---

## 3. Verificación (evidencia)

| Gate | Comando | Resultado |
|---|---|---|
| Tests backend | `.\.venv\Scripts\python.exe -m pytest tests -q` | **85 passed, 0 failed** (baseline: 50) |
| Tipos frontend | `cd frontend; npx tsc --noEmit` | **0 errores** |
| Build frontend | `npm run build` | **exit 0** (CSS 107.7 KB con utilidades, JS 401.8 KB) |
| Productos | `scripts\validate_deliverables.py` | **55/55 válidos**, 34 avisos, 0 claims positivos |
| Sitio estático | `scripts\build_publish_pack.py --summary --verify` | **VERIFY PASS** (55 rutas + 4 legales + 60 loc, sin recursos externos) |
| Vertex real | `scripts\probe_vertex.py` | **OK** primary + fallback; 1 imagen de servicio registrada en ledger |
| LAN | `http://192.0.2.1:8765/api/health` | **200** (servidor en `0.0.0.0`) |
| Tienda | `/store/`, `/store/legal/terminos/`, `/store/blueprint/…` | **200** (65 HTML sin recursos externos) |
| Pago desde LAN | `/deliverables/e01_…` | **403** |
| Lead magnet | `/deliverables/l02_…` | **200** (59 KB) |
| API inexistente | `/api/noexiste` | **404 JSON** |
| CORS | preflight con `Origin: http://evil.example` | **400 sin ACAO** (solo LAN/localhost) |
| Límite 250 | `test_strict_atomic_file_line_limit` | **verde** (0 archivos >250) |
| Emojis | escaneo frontend/backend/build | **0** |

Auditoría independiente: `docs/AUDITORIA_2026-11-04.md` (Misión 1, 6 bloqueos iniciales) y `docs/QA_FINAL.md` (Misión 2, 14 gates PASS · 2 PARCIAL documentados · 1 FAIL de negocio = checkout · 1 no verificable = compra real). El veredicto del auditor coincide con este reporte: **técnicamente verde, publicación bloqueada por negocio (checkout), no por código**.

---

## 4. Bloqueos y decisiones que dependen de ti

1. **Checkout 0/52 (ÚNICO bloqueo de negocio).** Hay que crear los productos en Gumroad (USD) y Hotmart (COP/Nequi/PSE) y pegar sus URLs. Ya existe el flujo rápido:
   - UI: Publish Center → "Checkout por SKU" o "pegar en bloque" (`SKU,URL` o JSON).
   - API: `POST /api/catalog/checkout-bulk` con `{"links":{"E01":{"gumroad_url":"https://..."}}}`.
   - El sitio y las landings dejarán de mostrar "checkout pendiente" automáticamente.
2. **Hosting / deploy.** El sitio está generado y verificado; falta decidir dominio y ejecutar:
   `scripts\build_publish_pack.py --base-url https://TU-DOMINIO --verify` y `scripts\deploy_store.ps1 -Confirm`. No se creó ningún repo ni se publicó nada externo sin tu confirmación.
3. **Volumen de contenido.** Quedan 4 posts de Threads + 10 pines propios reales (los 50 posts que había eran basura idéntica de tests; se eliminaron con backup). Cubre 1–2 días, no la cadencia de 5–15 piezas/día. Recomendación: expandir con la fábrica OpenCode V2 y volver a exportar el sitio.
4. **Seguridad LAN.** Si el Wi-Fi no es de confianza, define `RONIN_API_TOKEN` antes de arrancar (documentado en README). Sin token, cualquier equipo de la red puede escribir en la API; el gasto caro está limitado a 1 llamada/20 s.
5. **Entrega automática / entitlement.** Hoy el backend sirve los productos al operador (localhost) y los lead magnets al público; la entrega al comprador la hacen Gumroad/Hotmart con sus propios archivos. Si quieres entrega propia con token revocable + webhook de compra, es el siguiente sprint (no necesario para empezar a vender con las pasarelas).
6. **Calidad de producto.** 34 avisos de validación, la mayoría falsos positivos (garantías citadas/negadas) o decisiones editoriales. Los reales a revisar antes de escalar: B02/B03/B04/B08 con menos de 2.000 palabras, M06 (vault de $149 que es un índice) y los claims en primera persona de B09. No se reescribieron productos sin tu criterio.

---

## 5. Qué aprendimos de `ronin_studio` (sistema hermano)

| Práctica de ronin_studio | Adoptada en ronin_ventas |
|---|---|
| Proyecto/región/modelo de Vertex documentados y centralizados | Sí: `config.py` + `.env.example` + `probe_vertex.py` |
| Retry para 429/503 con espera creciente | Sí: en `vertex_image_service` (imagen) |
| Coste real por modelo y ledger (COST_MODEL) | Sí: `data/finops-ledger.json` ($0.067/imagen) |
| Validación de bytes/mime antes de escribir arte | Sí: >500 B + mime → extensión |
| Seed canónico de Ron + referencias de continuidad | Sí: `ron_canonical_seed.png` en el prompt/estilo |
| `docs/reconstruction` (arquitectura/operaciones verificadas) | Sí: README + BACKEND_NOTES + auditoría + QA_FINAL + este reporte |
| `scripts/probe_models.py` (sonda de modelos) | Sí: `scripts/probe_vertex.py` |
| `pnpm build`/`tsc` como gate | Sí: build + tsc en la verificación |
| Límite de líneas por archivo (line_count_sentinel) | Sí: test de 250 líneas (85 tests verdes) |
| Variables de entorno documentadas | Sí: `.env.example` |

No adoptado (a propósito): publicación automática en redes (ronin_studio tampoco la tiene; ambos sistemas preparan el contenido y publican manual), y Veo/TTS (fuera del alcance de ventas).

---

## 6. Cómo publicar mañana (checklist operativa)

1. `start_ronin_os.bat` → PC `http://127.0.0.1:8765` (el móvil verá la IP LAN en el header).
2. Publish Center: crear/pegar las 52 URLs de checkout (modo bloque) y verificar que "0 sin checkout" baja a 0.
3. Revisar 2–3 landings de `/store/…` (precio, CTA, legales).
4. `scripts\build_publish_pack.py --base-url https://TU-DOMINIO --verify`.
5. `scripts\deploy_store.ps1 -Confirm` (GitHub Pages) y abrir la URL pública.
6. Publicar el contenido de `data/publish_site/content/` (Threads/Pinterest) copiando texto + imagen + link; marcar cada pieza en el Publish Center (seguimiento local).
7. Importar ventas: Radar → CSV de Gumroad/Hotmart (2 MB máx.) y revisar el criterio de 14 días.
8. (Opcional, seguridad) definir `RONIN_API_TOKEN` si la Wi-Fi no es de confianza.

---

## 7. Plan de 7 días sugerido

| Día | Objetivo |
|---|---|
| 1 | Pegar 52 checkouts, deploy del sitio, publicar 5 piezas (Threads/Pinterest) |
| 2 | Expandir cola a 20 posts + 20 pines con la fábrica; programar cadencia |
| 3 | QA de productos: B02/B03/B04/B08 (palabras), M06 (vault real o retirar), B09 (claims en 1ª persona) |
| 4 | Entrega propia con token + webhook Gumroad/Hotmart (opcional) y página de gracias |
| 5 | Primer corte de métricas reales (CSV) y decisión "Doblar o Matar" |
| 6 | Endurecer LAN (token en UI/localStorage) y backups automáticos |
| 7 | Revisión de conversión por ruta y ajuste de precios/order bump |

---

## 8. Archivos nuevos y cambiados (resumen)

- **Nuevos:** `backend/routers/api_publish.py`, `backend/services/{publish_state,publish_pack,publish_content,publish_legal,json_store,security_middleware}.py`, `backend/services/product_templates_sections.py`, `scripts/{probe_vertex,validate_deliverables,build_publish_pack}.py`, `scripts/deploy_store.ps1`, `README.md`, `.env.example`, 9 componentes del Publish Center, 8 tests nuevos, 4 docs.
- **Reescritos/ajustados:** `backend/config.py`, `backend/main.py`, `vertex_image_service.py`, `product_factory.py`, `product_templates_elite.py`, `landing_renderer.py`, `catalog_seed.py`, `social_feed_seed.py`, `metrics_service.py`, `csv_sales_parser.py`, `probe_runners.py`, `connectors_*`, `playwright_bait_renderer.py`, plantillas iOS, `AGENTS.md`, `frontend/index.html`, `App.tsx`, `Sidebar.tsx`, vistas de Threads/Pinterest/Stan/Catálogo/Métricas/Bait/Brand/Hub, `package.json`, `index.css`.
- **Datos:** `data/catalog.json` (checkout_ready), `data/social_feeds.json` limpio con backup en `data/_cuarentena/`, `data/competitor_notes.json`, `data/finops-ledger.json`, `data/publish_site/`, `data/_cuarentena/`.
- **Git:** repo inicializado con baseline `0ed6ce7` y commit final de la revisión.

---

*Sin promesas de ingresos. Sin estados falsos: todo lo que este reporte afirma fue medido con los comandos de la sección 3.*
