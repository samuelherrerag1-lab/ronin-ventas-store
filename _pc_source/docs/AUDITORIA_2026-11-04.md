# Auditoría Independiente — Ronin Ventas OS

**Fecha:** 2026-11-04, 21:36–21:47 (America/Bogota)
**Auditor:** agente `auditor` (task-4), read-only sobre el código.
**Árbol auditado:** `C:\Users\EXAMPLE\Documents\ronin_ventas`, git baseline `0ed6ce7` + cambios en vuelo de 3 constructores.
**Estado del árbol durante la auditoría:** 27 archivos modificados + nuevos (`backend/services/json_store.py`, `publish_state.py`, `frontend/src/components/publish/*`, `README.md`, `.env.example`, etc.). Las líneas citadas son del snapshot 21:46; varios archivos estaban siendo reescritos en el momento de la lectura.

> **Veredicto de publicación: NO LISTO.** Hay 6 bloqueos duros (sección 8). El producto digital existe (55 entregables reales, 52–767 KB, offline), pero **no se puede cobrar ni entregar**: 0/52 SKUs tienen URL de checkout y el backend en ejecución no está accesible por LAN. La infraestructura de publicación (`/api/publish/*`, `publish_pack`, `scripts/build_publish_pack.py`, `deploy_store.ps1`) todavía no existe; está en vuelo por los constructores.

---

## 1. Resumen ejecutivo

| Área | Veredicto | Evidencia |
|---|---|---|
| Catálogo 55 SKUs / 55 rutas únicas / precios COP | **PASS** | `data/catalog.json`: 55 items, 52 de pago + 3 leads, 55 rutas únicas, sin duplicados, `price_cop = usd × 4200` en los 55 |
| Entregables 55/55 reales, offline, sin lorem/emojis | **PASS** (con salvedad) | `data/deliverables/`: 55/55 mapean al catálogo, 52–767 KB, 0 archivos <20 KB, 0 emojis; 3 HTML contienen `api.gumroad.com` solo como **código de ejemplo** del producto (no se ejecuta) |
| Checkout funcional (Gumroad + Hotmart) | **FAIL** | `catalog.json`: `gumroad_url` y `hotmart_url` vacíos en 55/55. Landing: "Checkout aún no configurado" (`landing_renderer.py:141-146`) |
| Doble checkout LatAm + Global | **FAIL** | Solo hay un CTA de compra en la landing, sin selector Hotmart/Gumroad; `checkout_for()` (`landing_renderer.py:212-217`) devuelve una sola URL |
| LAN móvil `0.0.0.0:8765` | **FAIL en ejecución** | Proceso PID 9640: `python -m uvicorn backend.main:app --host 127.0.0.1 --port 8765`. `http://192.0.2.1:8765` no conecta desde otro host (probado). `desktop_launcher.py:59` sí usa `BIND_HOST`, pero el proceso corriendo no |
| 7 módulos oficiales | **PASS parcial** | 8 pestañas existentes + "Centro de Publicación" en vuelo; el módulo 5 (Stan Store) no cobra (ver A2) y el 7 reporta sesiones falsas (A2) |
| Cero estados falsos (AGENTS §2) | **FAIL** | 7 focos confirmados (sección 4): Google CONECTADO sin sesión, "Publicado" local, checkout simulado, fallback de productos hardcodeado, etiqueta de modelo viejo, coste/latencia inventados, totales 55/8 por defecto |
| Cero emojis (AGENTS §4) | **FAIL (menor)** | `CatalogFactoryView.tsx:168` (✓), `StanAndStealthView.tsx:47` (✓), `social_feed_seed.py:39` (👇). 0 emojis en los 55 entregables |
| Límite 250 líneas | **FAIL transitorio** | `product_templates_elite.py` = 302 líneas (en reescritura ahora). Resto del árbol ≤246. `pytest` lo marca en rojo (ver §9) |
| Vertex AI migrado | **PASS con residuos** | `config.py:28-44` correcto; ledger real `data/finops-ledger.json` con `REDACTED_EXAMPLE_PROJECT`, modelo `gemini-3.1-flash-image`, $0.067, 1 imagen. Quedan referencias activas viejas en un SKILL y en la UI (M5) |
| Tests | **PARCIAL** | 49 passed / 1 failed (el fallo es de líneas por edición en vuelo). Tests débiles y con efectos sobre datos de producción (A9) |
| Seguridad LAN | **FAIL** | Endpoints que gastan dinero y escriben disco sin autenticación; CORS `*`; cookie-hosts del vault expuestos (C3) |
| Honestidad de documentación | **PARCIAL** | `README.md` ya describe `validate_deliverables.py`, `build_publish_pack.py`, `deploy_store.ps1` y el checkout API que **todavía no existen** (en vuelo) |

---

## 2. Metodología y límites

- Lectura completa de `backend/` (81–246 líneas por archivo), routers, servicios, tests, `data/*.json`, frontend `src/**` y script de arranque.
- Comprobaciones en vivo **de solo lectura** contra el backend del Lead en `127.0.0.1:8765` (no se reinició, no se mató).
- Ejecución de `pytest` y scripts de inspección read-only (conteos, hashes, line counts, escaneo de emojis/refs externas).
- **No se probó**: compra real en Gumroad/Hotmart, pago con Nequi/PSE, acceso desde un móvil físico, webhooks, ni el deploy a GitHub Pages. Tampoco se ejecutó `test-all` (gasta dinero Vertex) ni el endpoint `vertex-generate`.
- Los archivos en reescritura por otros agentes pueden haber cambiado después de la cita; todo hallazgo marcado *(en vuelo)* debe reconfirmarse en la MISIÓN 2.

---

## 3. Hallazgos CRÍTICOS

### C1 — 0/52 SKUs con URL de checkout: la tienda no puede cobrar · CONFIRMADO
- `data/catalog.json`: los 55 items tienen `gumroad_url: ""` y `hotmart_url: ""`.
- `backend/services/landing_renderer.py:136-146`: sin URL no hay botón de compra; muestra "Checkout aún no configurado" (honesto, pero deja el embudo en cero).
- `backend/services/landing_renderer.py:199-200`: anuncia "Order bump opcional (+$9 USD)" que no existe en ningún checkout real.
- **Impacto:** ingresos = $0 y `POST /api/catalog/{sku}/checkout` ni siquiera está montado todavía (`backend/routers/api_publish.py` y el endpoint de checkout no existen aún: verificado MISSING).
- **Fix:** implementar el endpoint de checkout (en vuelo), cargar las 52 URLs reales y hacer una compra de prueba de punta a punta (pago + entrega). Sin esto no se publica.

### C2 — El backend que corre NO escucha en LAN · CONFIRMADO en vivo
- Proceso: `C:\...\Python312\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8765` (PID 9640).
- `Get-NetTCPConnection -LocalPort 8765` → `LocalAddress 127.0.0.1`.
- `http://192.0.2.1:8765/api/health` desde el propio host → `No es posible conectar con el servidor remoto`.
- `backend/main.py:79-85` devuelve `lan_url` (`http://192.0.2.1:8765`) aunque ese enlace no escucha en LAN: **estado de red falso**.
- `desktop_launcher.py:59` sí hace `uvicorn.run(host=BIND_HOST)` con `BIND_HOST="0.0.0.0"` (`config.py:58`): el arranque oficial sería correcto, pero el proceso auditado no lo usa.
- **Impacto:** el requisito "accesible desde cualquier celular en la misma Wi-Fi" no se cumple. Y, peor, cuando se arranque en `0.0.0.0` se activa C3 (no hay auth).
- **Fix:** matar el proceso actual (lo hace el Lead), arrancar con `start_ronin_os.bat`/`desktop_launcher.py`, verificar desde el móvil `http://<LAN_IP>:8765` y añadir a `/api/health` el `bind_host` real (nunca deducir LAN de `get_lan_ip()`).

### C3 — Sin autenticación: cualquier cliente de la LAN puede gastar dinero, abrir Chrome y borrar datos · CONFIRMADO por código (se activa al arrancar en 0.0.0.0)
- `backend/routers/api_customizations.py:154-159` `POST /api/customizations/vertex-generate` → **genera imágenes de pago** ($0.067 c/u) sin auth ni rate limit.
- `backend/routers/api_customizations.py:140-142` `POST /test-all` → en paralelo ejecuta la sonda Vertex real (`probe_runners.py:29-60`), **una imagen pagada por clic** aunque el usuario solo quería ver conectores.
- `backend/routers/api_customizations.py:88-111` `POST /connect/{id}` → lanza Chrome con el perfil persistente en la máquina del dueño (ventana, proceso, posible login).
- `backend/routers/api_customizations.py:130-132` `GET /secrets` y `GET /` (`:50-85`) → devuelven `masked_secrets()` y `domains_with_cookies` del vault (`vault_inspector.py:73-86`): permite inferir cuentas/sesiones del dueño.
- `backend/routers/api_metrics.py:92-94` `DELETE /api/metrics/reset` → borra todo el histórico real.
- `backend/routers/api_catalog.py:42-79` → toggle-stan y generate-deliverable escriben en disco sin auth (el generate tiene guarda de tamaño, pero escribe si el archivo no existe).
- `backend/main.py:42-48` CORS `allow_origins=["*"]` (credentials ya en `False`, mejora reciente): cualquier web visitada por el dueño puede intentar POST al API local.
- **Impacto:** en una Wi-Fi compartida (oficina, café, hotel) cualquiera puede quemar saldo Vertex, abrir ventanas de login, borrar métricas o leer dominios con cookies. Es el hallazgo de seguridad más grave y contradice el modelo LAN de AGENTS §1.
- **Fix mínimo:** middleware que rechace métodos de escritura y `/secrets` cuando `request.client.host` no sea owner; token local en `.env` para mutaciones (`X-Ronin-Token`); confirmación explícita + rate limit en `vertex-generate`/`test-all`; nunca exponer `domains_with_cookies` fuera de owner. Para producción real: auth de sesión por dispositivo.

### C4 — Publicación real inexistente todavía · EN VUELO
- Verificado MISSING: `backend/routers/api_publish.py`, `backend/services/publish_pack.py`, `scripts/build_publish_pack.py`, `scripts/deploy_store.ps1`, `scripts/validate_deliverables.py`, `data/publish_site/`.
- `GET /api/publish/readiness` y `/api/publish/kit` hoy responden **200 HTML del dashboard** (ver A1), no JSON.
- `/store/` (mount nuevo en `main.py:65-69`) responde 200 HTML del SPA porque `data/publish_site/` no existe.
- **Impacto:** no hay cola de contenido publicable, sitio estático ni manifest; AGENTS exige 5–15 piezas/día y 55 rutas puente. Es el segundo bloqueo de "publicar mañana".
- **Fix:** completar task-1/3 y verificar `manifest.json` con 55 rutas + index + legal + assets en la MISIÓN 2.

---

## 4. Hallazgos ALTOS

### A1 — El catch-all del SPA devuelve 200 HTML para rutas `/api/*` inexistentes · CONFIRMADO en vivo
- `backend/main.py:115-120`: `@app.get("/{full_path:path}")` se registra después de los routers y captura **todo**, incluidos `/api/publish/...`, `/store/` y `/api/cualquier-cosa`.
- Evidencia: `GET http://127.0.0.1:8765/api/publish/readiness` → `200 <!DOCTYPE html>`; `GET /api/publish/kit?platform=threads` → `200 HTML`; `GET /store/` → `200 HTML`.
- **Impacto:** los consumidores (`fetch().json()`) lanzan "Unexpected token <"; el Publish Center mostrará un error críptico en vez de "Pendiente en backend"; los 404 honestos de API son imposibles; los monitores ven 200 donde no hay nada.
- **Fix:** catch-all que excluya `/api/` y `/store/` y devuelva `JSONResponse({"detail":"Not found"}, 404)`; o registrar un handler `@app.exception_handler(404)` y no mapear `{full_path:path}` para prefijos API.

### A2 — Estados falsos en la UI (viola AGENTS §2) · CONFIRMADO
1. **Google Master "CONECTADO" sin sesión.** `backend/services/probe_runners.py:116-147`: el test solo abre `chrome --headless --dump-dom about:blank` y, si el binario responde, devuelve `status="CONECTADO"` para el conector "Google Master Session (Chrome Vault)". No verifica sesión, cookies ni cuenta. Es un falso positivo estructural que el test de honestidad no cubre.
2. **"● Publicado" local.** `frontend/src/components/threads/ThreadsCloneView.tsx:177-179` y `PinterestCloneView.tsx:141-142`: el botón alterna `queued→published` en `data/social_feeds.json`; la redacción "Publicado" afirma una publicación que no ocurrió. (El nuevo `PublishKitPanel.tsx:44,103` sí dice "Publicado (local)" — la corrección debe aplicarse también a los clones).
3. **Checkout Stan Store simulado.** `StanAndStealthView.tsx:39-43,174-181`: "Pagar con Nequi / PSE / Efecty (Hotmart…)" y "Pago Rápido Internacional USD (Gumroad Apple Pay…)" solo muestran un toast; no navegan, no cobran, y el "Order Bump" (`:163-181`) solo suma $9 al texto. Es exactamente el "botón de pago que no funciona" que AGENTS prohíbe.
4. **Catálogo falso si falla el backend.** `StanAndStealthView.tsx:27-31`: si `products=[]` se muestran 3 productos hardcodeados con rutas que no existen (`/free/viral-hooks`; B01 apunta a `/app/prompts-vault`, cuyo slug real es `boveda-500-hooks-cinicos`). Precios $19/$27 hardcodeados.
5. **Modelo y coste Vertex inventados.** `BaitStudioView.tsx:181` muestra la etiqueta fija `gemini-2.5-flash-image` (el modelo real es `gemini-3.1-flash-image`); `:206-208` muestra "Generado en {latency || 11.8}s" y "$0.03 USD" fijos (coste real 0.067; el backend devuelve `elapsed_attempt_sec`, no `latency`). El cliente (`client.ts:96-104`) espera `latency_sec`, que el backend no envía: **siempre** se pintan 11.8 s falsos.
6. **Cifras por defecto.** `App.tsx:57` `lanUrl` por defecto `http://192.0.2.1:8765` (IP inventada); `:114` `totalConnectors = connectors.length || 8`; `:124` `totalSkus={products.length || 55}`: la barra lateral enseña 55 SKUs y 8 conectores incluso si el backend devolvió 0.
7. **Engagement simulado.** `social_feed_seed.py:165-172`: `mutate_thread_hook` incrementa `simulated_likes` en cada clic. La UI lo rotula "VISTA PREVIA — cifras de ejemplo" (`ThreadsCloneView.tsx:193-195`), por lo que es aceptable como demo, pero no debe mostrarse como métrica del Radar (no lo hace hoy).
- **Fix:** sustituir por datos reales o por placeholders explícitos ("sin datos", "pendiente en backend"); el estado de publicación debe llamarse "Marcado localmente" en los clones; eliminar el fallback hardcodeado; leer modelo/coste reales de `/api/customizations` y `/api/health`.

### A3 — El comprador no tendría cómo recibir el producto tras pagar
- `backend/services/delivery.py:29-31`: solo `127.0.0.1/::1/localhost` es owner; `main.py:97-107` bloquea `/deliverables/<pago>` a cualquier IP no local.
- No existe enlace firmado, token de compra, página de gracias ni webhook post-compra (grep de `webhook|token de descarga|download_href` no encuentra implementación; `landing_renderer.py:148-155` usa `download_href` solo para gratis).
- **Impacto:** aun con URLs de checkout, el cliente paga y no puede descargar el HTML desde el móvil. El funnel está roto en el último tramo. En Gumroad/Hotmart el archivo se sube a su plataforma; si los 55 HTML se entregan así, no hace falta `/deliverables` público, pero hay que decidirlo y ejecutarlo.
- **Fix:** subir los 55 HTML a Gumroad/Hotmart como "content" y configurar entrega automática; o generar tokens de descarga locales (HMAC de sku+email+exp) servidos por `/deliverables?token=`.

### A4 — Doble umbral de regeneración de entregables: riesgo de sobrescribir producto real o servir basura
- `backend/services/product_factory.py:27-31`: solo sobrescribe si el archivo **no** existe o pesa ≤60 000 B; no valida `</html>` ni tamaño mínimo.
- `backend/routers/api_catalog.py:61-74`: el router usa otro umbral, >1 500 B, y devuelve "generated" sin regenerar.
- **Impacto:** un HTML real de 45 KB sería machacado por el fallback (si se invoca la factory); un archivo truncado de 2 KB se marca generated para siempre. Dos fuentes de verdad para la misma decisión.
- **Fix:** un único servicio `ensure_deliverable(sku, force=False)` que valide HTML parseable, `</html>`, >20 KB y ausencia de placeholders; persistir un hash de generación y no sobrescribir sin `force`.

### A5 — `/api/health` reporta una LAN que no está sirviendo
- `backend/main.py:74-94` calcula `lan_ip` y devuelve `lan_url`, pero nunca refleja si el socket escucha en esa interfaz. Verificado: `lan_url` responde 200 en el texto y `ECONNREFUSED` en la práctica.
- **Fix:** incluir `bind_host`, o comprobar con un socket local antes de exponer `lan_url`; si no escucha, devolver `lan_url: null` + `lan_reason`.

### A6 — `product_templates_elite.py` fuera del límite de 250 líneas (en vuelo)
- Al inicio de la auditoría tenía 218 líneas y **contenido prohibido**: cargaba `fonts.googleapis.com` (CDN externo, rompe "100% offline" y la CSP nueva), emojis 📋/📥 en el HTML generado y estadísticas inventadas ("reembolso <1.2%", "margen >91%", "order bump 38% histórico").
- A las 21:46, el archivo estaba reescrito (docstring: "Entregable de RESPALDO (fallback), 100% offline... sin CDN ni emojis") y con **302 líneas**: el reemplazo arregla el fondo, pero `pytest::test_strict_atomic_file_line_limit` está **en rojo** ahora mismo.
- **Fix:** dividir en `product_templates_elite.py` (layout) + `product_templates_offline.py` (contenido/hooks), y re-ejecutar el gate. (En Misión 2 se verifica.)

### A7 — Race conditions restantes en persistencia JSON
- `backend/services/connector_diagnostics.py:102-108` y `:112-117`: escritura read-modify-write de `customizations_state.json` **sin lock**. `run_all_connector_tests` (`:60-89`) lanza 6 hilos que ejecutan `run_connector_test` → `_save_single_test_result` en paralelo, y `connect_worker.py:105-122` escribe el mismo archivo desde otro **proceso**. Se pierden resultados y toggles de skills.
- `backend/services/metrics_service.py:37-54`, `catalog_seed.py:156-169`, `social_feed_seed.py:156-162`: `write_text` sin lock ni escritura atómica. Dos importaciones CSV concurrentes pueden perder una.
- El nuevo `backend/services/json_store.py` (en vuelo) resuelve esto con locks + `os.replace`; **aún no lo usan** estos servicios (verificar en Misión 2).
- **Fix:** migrar los cuatro stores a `json_store.update_json`; `connector_diagnostics` debe recolectar resultados en memoria y persistir una sola vez al final.

### A8 — Conversión COP inconsistente entre métricas y catálogo + parser de importes frágil
- `backend/services/catalog_seed.py:7` `COP_RATE = 4200`; `backend/services/csv_sales_parser.py:7` `COP_TO_USD_RATE = 4000`. El mismo pago de 79 800 COP cuenta como $19.00 en el catálogo y $19.95 en el Radar (−5 % de descuadre).
- `csv_sales_parser.py:23-54`: `"79.800"` (formato CO) se limpia a `79.800` y se interpreta como **79.8 COP** → venta de $0.02. El separador de miles con punto no se detecta si no hay coma.
- `:126` genera `id = f"{source}_{order_id or row_idx}"`: sin `order_id`, reimportar el mismo CSV deduplica por número de fila (pierde ventas distintas o duplica según el orden).
- **Fix:** una sola constante de TRM en `config.py` (con fecha); parser que trate puntos de miles cuando el último bloque tiene 3 dígitos; exigir `order_id` y reportar filas sin él como error, no inventar id por índice.

### A9 — Los tests escriben en datos de producción y varios son débiles
- `tests/conftest.py:1-6` promete "Ningún test debe escribir en `data/`", pero:
  - `tests/test_bloque1.py:32-40` llama `POST /api/catalog/A01/generate-deliverable` (escribe/acredita entregable y `catalog.json`).
  - `tests/test_bloque1.py:42-48` hace toggle-stan sobre `E03` → **guarda** `data/catalog.json` (lo deja igual solo porque lo hace dos veces).
  - `tests/test_delivery_access.py:43-48` escribe un lead en `data/leads.json` (el path sí está parcheado en conftest; verificado que no mutó el archivo).
- `tests/test_honesty.py:54-62` (`test_published_sku_requires_checkout_url`) es **vacuo**: filtra `status == "published"`, y hoy los 55 están en `generated`; pasaría con 0/55 checkouts. No impide publicar sin pasarela.
- `tests/test_metrics_real.py:106-112` codifica `has_real_data=True` en modo demo, contradiciendo el banner de la UI ("Cifras ficticias").
- No hay un solo test para: `/api/publish/*`, checkout links, `/store`, CORS, ownership LAN de escrituras, CSP, 404 de API, emojis, ni enlaces externos en entregables.
- **Fix:** parchear `CATALOG_JSON_PATH` y `DELIVERABLES_DIR` en conftest; test de honestidad que exija checkout a todo SKU con `price_usd>0` si el sitio se considera publicable; tests de contrato para los endpoints nuevos; test de 404 JSON para `/api/*`.

### A10 — Sin lint, tipado ni CI (deuda estructural que ya causó bugs)
- `requirements.txt` solo; no hay `pyproject.toml`, `ruff`, `mypy`, `pre-commit` ni `.github/workflows/`. No hay `tsc --strict` gate en CI (sí en el plan manual).
- Consecuencias ya visibles: `ConnectResult` (domain.ts:125-134) no coincide con lo que devuelve `api_customizations.py:88-111` (devuelve el job); `SkillCustomizationItem.category` (domain.ts:86) no admite `"tools_engineering"` que produce `skills_loader.py:22`; `generateVertexImage` espera `latency_sec` y el backend devuelve `elapsed_attempt_sec` (A2.5). Un `tsc --noEmit` no detecta esto porque los tipos del borde HTTP están a mano; `mypy`/tests de contrato sí.
- **Fix:** adoptar lo de ronin_studio (§7): ruff + mypy + pytest config + CI; y tests de contrato JSON.

### A11 — Emojis residuales en UI y en seeds
- `frontend/src/components/catalog/CatalogFactoryView.tsx:168` (`✓ Copiado`), `StanAndStealthView.tsx:47` (`✓ Fórmula...`), `backend/services/social_feed_seed.py:39` (`👇` dentro de una auto-respuesta que se renderiza en el clon de Threads). AGENTS §4 prohíbe emojis en la UI; usar SVG.
- **Fix:** reemplazar por SVG/`aria-hidden` o texto; añadir test que falle si aparece un emoji en `frontend/src` o en contenido de `social_feeds.json`.

### A12 — Repo sucio: duplicados, backup sin documentar y scratch de agentes
- Raíz: `a01_app-forjador-hooks-virales.html` y `e01_maquina-silenciosa-pdf.html` son **duplicados exactos** de `data/deliverables` (hash verificado); `l02_calculadora-express-precio-digital.html` es **0 bytes** y no corresponde a ningún SKU; `b01_boveda-500-hooks-cinicos.html` (265 180 B) **NO es duplicado exacto** del entregable real (332 665 B) → es una versión vieja distinta: no moverlo como "duplicado" sin decidir cuál es canónica.
- `data/deliverables_backup/` (8 archivos, 150–200 KB) no está documentado ni en `.gitignore`.
- Nuevos scratch en vuelo: `scripts/_scratch_audit.py`, `data/_tmp_render.html` (de otros agentes).
- **Fix:** cuarentena verificada por hash (no por nombre); documentar o borrar `deliverables_backup`; `.gitignore` para `data/_tmp*`, `data/logs/`, `data/finops-ledger.json` (hoy no está ignorado y registra gasto real).

### A13 — Entrega de assets y rendimiento móvil
- `/generated_images` sirve 132 PNG de 1.2–1.6 MB sin `Cache-Control`; las vistas móviles cargan varios por pantalla. Los covers webp (122) son la versión correcta para web, pero el SPA usa PNGs grandes en Threads/Pinterest.
- **Fix:** headers `Cache-Control: public, max-age=31536000, immutable` en assets versionados; usar webp para avatares/escenas en la UI; `loading="lazy"` ya está en algunos.

---

## 5. Hallazgos MEDIOS

| ID | Archivo:línea | Hallazgo | Fix |
|---|---|---|---|
| M1 | `main.py:42-48` | CORS `allow_origins=["*"]` permite a cualquier web llamar al API local (POST/JSON). Credentials ya en False (bien), pero el comodín sigue habilitando unidades de disco | `allow_origins=["http://127.0.0.1:8765","http://localhost:8765", f"http://{lan_ip}:8765"]` |
| M2 | `README.md` (sección "Publicar") | Documenta `build_publish_pack.py`, `deploy_store.ps1`, checkout API y validate_deliverables como si existieran; hoy MISSING | No mergear el README hasta que los scripts existan, o marcarlos "en construcción" |
| M3 | `config.py:51-55`, `.gitignore` | El perfil Chrome con sesiones vive dentro del repo (`data/chrome_vault`). Gitignored, pero un backup/zip del repo lo arrastra | Ruta fuera del repo vía env (`RONIN_CHROME_PROFILE`), como ronin_studio |
| M4 | `vertex_image_service.py:169-246` | El servicio no es testeable sin gastar (cliente genai no inyectable); `MIN_VALID_IMAGE_BYTES=500` no valida formato con PIL; `elapsed_attempt_sec` es solo del último intento | Inyectar cliente (Protocol), Pydantic `ArtRequest`, validar con `PIL.Image.open`, reportar latencia total y por intento |
| M5 | `.agents/skills/hybrid-retina-vertex-renderer/SKILL.md:4,17`; `frontend/.../BaitStudioView.tsx:181`; `config.py:41`; `scripts/probe_vertex.py:29-31` | Residuos del proyecto/modelo viejo: el SKILL del proyecto manda usar `example-project-id`, `us-central1`, `gemini-2.5-flash-image` (activo si se invoca); la UI muestra el modelo viejo; `probe_vertex --all` incluye el proyecto viejo (aceptable como histórico, pero puede gastar en un proyecto que ya no es el oficial) | Actualizar el SKILL a `REDACTED_EXAMPLE_PROJECT…`, `global`, `gemini-3.1-flash-image`; quitar la etiqueta fija y leer del backend; borrar el proyecto viejo de la matriz o marcarlo "histórico" |
| M6 | `skills_loader.py:30` | Las 3 skills `ron_mode_*` se reportan `installed_on_disk=True` aunque no existan en `~/.agents/skills` (111 reales; el total listado es 114, AGENTS dice 112) | `installed_on_disk = (GLOBAL_SKILLS_DIR/sid).exists()` para todas; corregir el copy de "112" o sembrar las 3 skills que faltan |
| M7 | `Proyecto (frontend+backend)` | El "Order Bump interactivo +$9" de AGENTS no está implementado en ningún checkout: solo copy en `landing_renderer.py:199-200` y un checkbox que suma en memoria en `StanAndStealthView.tsx:163-181` | Implementarlo en el checkout real (Gumroad/Hotmart: producto de bump) o eliminarlo de la promesa de módulo |
| M8 | `metrics_service.py:175-222` | El modo demo devuelve `has_real_data=True`; cualquier consumidor salvo la UI puede confundirlo con datos reales | `has_real_data=False` + `is_demo_mode=True` en demo |
| M9 | `desktop_launcher.py:24-32` | Escribe logs en `data/logs/` sin `.gitignore`; el proceso actual usa **Python global** (`Python312`), no el `.venv` oficial | Ignorar `data/logs/`; arrancar siempre con `.venv\Scripts\python.exe` (el `.bat` lo hace si se usa el launcher) |
| M10 | `data/catalog.json` status | Los 55 SKUs están `status="generated"` y ninguno `published`; el status no se usa para bloquear la publicación | Definir semántica (`ready_spec` → `generated` → `published` con checkout + sitio + entrega probada) y hacerla cumplir en `/api/publish/readiness` |

---

## 6. Hallazgos BAJOS

1. `main.py:20,81` mezcla LF/CRLF (warning de git en 3 archivos) — normalizar vía `.gitattributes`.
2. Clave `stealth_Diagnostic` (D mayúscula) en `api_customizations.py:58` y `domain.ts:140` — inconsistente con el resto del contrato.
3. `landing_renderer.py:199-200` y deliverables mencionan "75% DTO" / "38% de aceptación histórica" sin fuente (en el fallback ya se corrigió; en el copy de UI sigue).
4. `StanAndStealthView.tsx:150-160` muestra "$418.50 USD (Notificación iOS 3:14 AM)" y un temario fijo ("8 capítulos", "15 hooks") para **cualquier** SKU: contenido no derivado del catálogo.
5. `/product_art` expone las 122 portadas (incluye v2 no usadas) en LAN; no es crítico (arte de marca), pero conviene servir solo `_v1`.
6. `tests/test_bridge_routes.py` recorre las 55 rutas y solo comprueba 200; no valida precio/checkout/portada en el HTML.
7. `api_feeds.py:13-19` `CreateBaitPostRequest` no limita longitudes (`post_text`, `notifications` sin `max_length`) → un POST puede inflar `social_feeds.json` sin límite.
8. `api_leads.py:36-51` guarda emails en JSON plano; legalmente conviene cifrar o al menos excluir de backups (hoy `.gitignore` no lo excluye: `data/leads.json` no está ignorado).

---

## 7. Cambio Vertex AI: verificación (MISIÓN 1)

**Configuración actual — PASS**
- `backend/config.py:28-35`: `VERTEX_PROJECT_ID = REDACTED_EXAMPLE_PROJECT` (override `GOOGLE_CLOUD_PROJECT`), `VERTEX_LOCATION = global`, `NANO_BANANA_MODEL = gemini-3.1-flash-image`, `NANO_BANANA_FALLBACK_MODEL = gemini-3.1-flash-lite-image`.
- `config.py:38-43`: costes `0.067 / 0.034` USD, coincidentes con `ronin_studio/docs/reconstruction/COST_MODEL.md:7-9`.
- `vertex_image_service.py`: reintentos por error transitorio, fallback a lite, mínimo de bytes antes de escribir, ledger FinOps con coste del modelo realmente usado, circuit breaker de $50.
- **Evidencia de llamada real:** `data/finops-ledger.json` → `REDACTED_EXAMPLE_PROJECT`, `gemini-3.1-flash-image`, `cost_usd 0.067`, `images 1`, timestamp `2026-11-05T02:36:55Z`. Coincide con la llamada verificada por el Lead.
- `/api/health` (versión nueva, aún no recargada en el proceso actual) expone `vertex.project_id/location/model/fallback/adc_present` (`main.py:87-93`): útil para el gate de Misión 2.

**Referencias obsoletas que siguen ACTIVAS — FAIL parcial**
| Archivo:línea | Contenido | Riesgo |
|---|---|---|
| `.agents/skills/hybrid-retina-vertex-renderer/SKILL.md:4,17` | `project="example-project-id"`, `location="us-central1"`, `gemini-2.5-flash-image` | **Alto**: es una skill del repo; si un agente la carga, configura el proyecto viejo y el modelo viejo |
| `frontend/src/components/bait/BaitStudioView.tsx:181` | etiqueta fija `gemini-2.5-flash-image` | Medio: UI miente sobre el modelo activo |
| `backend/config.py:41` | precio legacy `gemini-2.5-flash-image: 0.030` | Bajo: solo tabla de costes, no se usa para generar |
| `scripts/probe_vertex.py:29-31` | matriz `--all` incluye `example-project-id` y `gemini-2.5-flash-image` | Bajo/Medio: puede gastar en el proyecto viejo si se ejecuta `--all` |
| `tests/test_customizations_hub.py:41` | mock con texto `example-project-id` | Bajo: dato de test |

**Conclusión Vertex:** la migración es correcta y está comprobada con una llamada real; **no está limpia** la promesa "ninguna referencia activa al proyecto/modelo viejo": hay una skill del repo y una etiqueta de UI que siguen apuntando a lo viejo.

---

## 8. Bloqueos para publicar mañana (en orden de ejecución)

| # | Bloqueo | Responsable | Criterio de cierre |
|---|---|---|---|
| 1 | 0/52 URLs de checkout (C1) | Lead + backend-core | 52/52 con URL válida y una compra de prueba real en Gumroad y otra en Hotmart |
| 2 | LAN real: arrancar en `0.0.0.0` y verificar desde el móvil (C2) | Lead | `http://<LAN_IP>:8765/api/health` responde desde el celular; `/api/health` no miente sobre `lan_url` |
| 3 | Auth mínima para mutaciones/gasto en LAN (C3) | backend-core | `POST /vertex-generate`, `/test-all`, `/connect`, `DELETE /metrics/reset` devuelven 403 desde IP no owner o exigen token |
| 4 | Publish stack: router `/api/publish`, `publish_pack`, scripts, `/store` con manifest de 55 rutas + legales (C4) | backend-core + generadores + frontend | `manifest.json` con 55 rutas + index + legal; `/store/` sirve la tienda, no el dashboard |
| 5 | Cerrar el embudo de entrega post-pago (A3) | Lead | Tras compra de prueba, el comprador descarga el HTML correcto |
| 6 | Gates verdes: pytest (250 líneas incluidas), tsc, build (A6/A9) | todos | `pytest -q` 0 failed; `tsc --noEmit` 0 errores; build exit 0 |
| 7 | Quitar estados falsos de la UI y del diagnóstico (A2) | frontend + backend-core | "Publicado" → "Marcado local"; checkout Stan sin botón falso; Google Master deja de decir CONECTADO sin sesión; etiqueta de modelo real |
| 8 | SPA catch-all no debe tapar `/api/*` (A1) | Lead | `GET /api/no-existe` → 404 JSON |
| 9 | Privacidad/legales en el sitio: términos, privacidad, reembolso, licencia (`landing_renderer.py:24-29`) | generadores | 4 páginas en `publish_site/` y enlazadas desde cada landing |
| 10 | Limpieza mínima del repo (A12) | generadores | Sin duplicados exactos en raíz, sin `_tmp*`, `.gitignore` actualizado |

**Si solo hay tiempo para tres cosas:** 1) checkout URLs, 2) LAN real + auth, 3) publish stack completo con manifest verificado. Sin las tres, publicar mañana es vender un enlace que no cobra y un sitio que no sirve.

---

## 9. Estado de verificación ejecutada (Misión 1)

### pytest
```
.\.venv\Scripts\python.exe -m pytest tests -q
1 failed, 49 passed, 1 warning in 20.64s
FAILED tests/test_bloque1.py::test_strict_atomic_file_line_limit
  AssertionError: Archivos que violan el límite de 250 líneas:
  [('backend\\services\\product_templates_elite.py', 399)]
```
**Interpretación:** fallo **transitorio por edición en vuelo** (el archivo pasó de 218 → 399 → 302 líneas mientras se auditaba). Debe quedar en verde al cierre; no se corrige desde la auditoría.

### Backend en vivo (sin reiniciar)
```
PID 9640: python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8765
GET /api/health                     => 200 {"status":"ok","lan_ip":"192.0.2.1","lan_url":"http://192.0.2.1:8765"}
GET /api/catalog                    => 200 {total_skus:55, paid_skus:52, lead_magnets:3, unique_bridge_routes:55}
GET /blueprint/maquina-silenciosa-pdf => 200 landing HTML
GET /deliverables/l01_anatomia-post-418-usd.html => 200 HTML
GET /api/publish/readiness          => 200 HTML del SPA (no JSON)   [A1]
GET /api/publish/kit?platform=threads => 200 HTML del SPA (no JSON) [A1]
GET /store/                         => 200 HTML del SPA            [A1/C4]
GET /api/customizations/secrets     => 200 {}
http://192.0.2.1:8765/api/health => ECONNREFUSED                  [C2]
```

### Datos
- `catalog.json`: 55 items, 52 paid + 3 lead, 55 rutas únicas, 0 duplicados, 0 checkout URLs, COP = USD×4200 en todos.
- `deliverables/`: 56 archivos (55 HTML de catálogo + 0 extra), 52–767 KB, 0 con emojis, 0 con `<title>` faltante, 0 referencias externas ejecutables (los 3 `api.gumroad.com` son ejemplos de código).
- `social_feeds.json`: 55 posts de Threads + 12 pines (10 propios + 2 benchmark), todos `queued`.
- `product_art/web/covers`: 122 webp, existe `_v1` para los 55 SKUs; `generated_images`: 132 PNG (los 7 assets de UI referenciados existen).
- `finops-ledger.json`: 1 imagen real, $0.067, proyecto nuevo.
- Skills: 111 reales en `~/.agents/skills` + 3 `ron_mode_*` reportadas como instaladas sin estar en disco = 114 listadas.

### Emojis (frontend/src y backend)
```
frontend/src/components/catalog/CatalogFactoryView.tsx:168  U+2713
frontend/src/components/stan/StanAndStealthView.tsx:47      U+2713
backend/services/social_feed_seed.py:39                      U+1F447
data/deliverables/*.html: 0
```

### Límite 250 líneas (excluyendo data/, node_modules, .venv)
```
product_templates_elite.py 302  (en reescritura; era 218 con contenido prohibido)
resto: max 246 (vertex_image_service.py, MetricsRadarView.tsx)
```

---

## 10. Gap vs `ronin_studio` (sistema hermano)

### Prácticas ya adoptadas por ronin_ventas
| Práctica de ronin_studio | Estado en ronin_ventas |
|---|---|
| Coste real documentado (`COST_MODEL.md`: $0.067 img 1K, $0.034 lite) | ✅ `config.py:38-43` con los mismos precios |
| Sonda de modelos/proyecto antes de gastar (`scripts/probe_models.py`) | ✅ `scripts/probe_vertex.py` (proyecto activo + fallback; `--all` opcional) |
| Modelo/cliente Vertex con reintento y validación de bytes | ✅ `vertex_image_service.py` (retry transitorio, fallback, mínimo de bytes, ledger) |
| Límite de 250 líneas como gate ejecutable | ✅ test `test_strict_atomic_file_line_limit` (+ en ronin_studio es `scripts/line_count_sentinel.py`) |
| `.env.example` con overrides explícitos | ✅ `.env.example` (aún no carga automáticamente; config usa `os.environ`) |
| Documentar decisiones/operaciones en `docs/reconstruction/*` | ⚠️ Parcial: `docs/PLAN.md`, `RESEARCH.md`, `CRITIQUE_*`; no hay `OPERATIONS.md`/`PUBLICATION.md`/`COST_MODEL.md` propios |
| Honestidad como gate (`QA.md`, `VIRALITY_GATE.md`, `EVIDENCE.md`) | ⚠️ Parcial: `tests/test_honesty.py` cubre 4 casos, pero deja pasar A2 |

### Prácticas/tooling que ronin_ventas debería adoptar
1. **`pyproject.toml` con ruff + mypy strict + pytest config.** ronin_studio tiene `[tool.ruff]`, `[tool.mypy] strict=true`, `filterwarnings=["error"]`, `pytest --strict-markers`. Habría atrapado los 3 desajustes de contrato de A10. Coste: ~1 h.
2. **CI en `.github/workflows/ci.yml`.** ronin_studio corre ruff + mypy + pytest + sentinel de líneas + guard de identificadores legacy. Adaptar el "legacy guard" a ronin_ventas: prohibir emojis, `fonts.googleapis.com`, `example-project-id` y `gemini-2.5-flash-image` en árbol activo. Es el gate que este repo necesita.
3. **Cliente Vertex tipado e inyectable** (`nano_banana.py`: `ArtRequest`/`ArtAsset` Pydantic `frozen`, `Protocol GenaiClient`, `NanoBananaError`, `save()` que falla si el archivo queda vacío). Migrar `vertex_image_service.py` a ese patrón y añadir 3–4 tests sin red usando un cliente falso. Coste: ~2 h.
4. **Perfil de Chrome fuera del repo** (`RONIN_CHROME_PROFILE`) y secretos fuera de `data/` (M3). ronin_studio ya lo hace; reduce el riesgo de filtrar sesiones en un backup del repo.
5. **Runbook operativo con evidencia por publicación** (`docs/reconstruction/OPERATIONS.md` + `EVIDENCE.md`): cada pieza publicada con hora, canal, URL, métrica y veredicto. ronin_ventas tiene el Radar pero no el registro de evidencia; el `data/social_feeds.json` de 55 piezas "queued" no es evidencia de publicación.
6. **Checklist de publicación trust-first** (`PUBLICATION.md` / `PUBLICATIONS.md`): preflight (perfil, audit, selector, sin publicar), un bloque a la vez, fallo = no publicar. Adaptarlo a Threads/Pinterest manual con el Publish Center (la cola ya está en diseño).
7. **Benchmark de modelos documentado** (`benchmark_models.py` + `MODEL_BENCHMARK.md`): para justificar por qué gemini-3.1-flash-image y no pro/lite. ronin_ventas lo tiene en un comentario de `config.py`; falta la tabla reproducible.
8. **`pytest-cov` + gate de cobertura en rutas críticas** (billing/checkout/publish): no cobertura global, sino "estas rutas no bajan de X". ronin_studio tiene `[tool.coverage]` configurado (aunque sus suites estén incompletas; su QA.md lo admite).
9. **Golden set / e2e de UI** (`qa_piece.py`, Playwright, axe): ronin_studio lo declara pero sus carpetas `tests/ui|e2e` están vacías (TEST_STRATEGY.md:1). No copiarlo tal cual: aquí sí hace falta un mínimo Playwright para los 9 tabs + axe en las 3 vistas de publicación.
10. **Settings tipados** (`pydantic-settings`) en lugar de `_env()` disperso: una sola clase `Settings` valida project/model/limits al arrancar y falla rápido si el `.env` está mal.

**Advertencias sobre ronin_studio (no idealizarlo):** su `TEST_STRATEGY.md` está marcado OBSOLETO y reconoce tests vacíos; su `PUBLICATION.md` es histórico con stubs 501; su `nano_banana.py:1` dice `gemini-2.5-flash-image` en el docstring mientras el código usa `gemini-3.1-flash-image` (docstring obsoleto). Adoptar su tooling y su disciplina de gates, no su documentación sin verificar.

---

## 11. Plan de 7 días

| Día | Objetivo | Entregable verificable |
|---|---|---|
| D1 | Cerrar bloqueos 1–3: checkout URLs de los 52 SKUs + LAN real + auth mínima | 52/52 URLs; health desde móvil; 403 desde IP no owner en todos los POST sensibles |
| D2 | Publish stack: router `/api/publish`, `publish_pack` (55 rutas + index + 4 legales + assets + sitemap/robots/404 + content queue) y `/store` verificado | `manifest.json` con 55 rutas + 1 index; `/store/` sirve tienda; 0 recursos externos |
| D3 | Funnel de entrega post-pago (A3) + compra de prueba real Gumroad y Hotmart | Dos compras de prueba con entrega del archivo correcto y métricas importadas por CSV |
| D4 | Honestidad: eliminar A2 completo + A11 emojis + A5 health + A1 catch-all API | Tests de honestidad nuevos en verde; `/api/no-existe` → 404 JSON; 0 emojis en árbol activo |
| D5 | Hardening técnico: json_store en los 4 stores, CSV/TRM unificados, umbral único de entregables, tests de contrato | pytest con ≥15 tests nuevos; sin write_text en stores; TRM única |
| D6 | Tooling ronin_studio: ruff + mypy + CI + guard legacy + typed Vertex client | CI verde en push; guard bloquea referencias viejas y emojis |
| D7 | Despliegue controlado: GitHub Pages o Cloudflare con dominio, smoke test externo, backup de `data/` y rotación de secretos | URL pública con SSL, 55 rutas + checkout, compra de prueba desde un móvil externo, `data/` respaldado fuera del repo |

**Criterio diario de parada:** si un gate (pytest/tsc/build/readiness) no está verde, no se avanza al siguiente día; se documenta el bloqueo y se pide decisión.

---

## 12. Nota de honestidad del propio auditor

- No se cobró ni se creó ningún producto real; no se probaron pagos. Las conclusiones de C1/C4 son por inspección de código/datos y por endpoints en vivo.
- El backend vivo es el del Lead con el código de las 21:36; varias correcciones posteriores (CORS, CSP, `/store`, `/api/health` con Vertex, `json_store`, plantilla offline) ya están en el árbol pero **no recargadas** en el proceso. No las he contado como PASS: hay que re-verificarlas en MISIÓN 2 tras reinicio.
- Un archivo citado puede haber cambiado de línea al momento de leer este informe. Las citas son del snapshot 21:46.

---

## 13. Actualización post-auditoría (21:57, sin cerrar MISIÓN 2)

Correcciones observadas en vivo y en el árbol después del snapshot. **No cuentan como PASS** hasta la reverificación final:

- **C2 corregido en ejecución:** backend reiniciado en `0.0.0.0:8765` (PID 18924 al momento de esta nota). `http://192.0.2.1:8765/api/health` → 200; `/deliverables/e01_...` → 403 desde IP LAN y `/deliverables/l01_...` → 200.
- **C4 corregido (infraestructura):** ya existen `backend/routers/api_publish.py`, `publish_pack.py`, `publish_content.py`, `scripts/build_publish_pack.py`, `validate_deliverables.py`, `deploy_store.ps1`, `data/publish_site/` con manifest (55 rutas, 138 archivos, 16,5 MB, 4 legales, sitemap/robots/404, content threads/pinterest, assets covers/pins/ron).
- **A1 corregido:** `main.py:132-135` devuelve 404 JSON para `/api/*` inexistentes (`/api/no-existe` → 404 JSON verificado).
- **C3 mitigado (no cerrado):** `backend/security_middleware.py` con token opcional `RONIN_API_TOKEN` y rate-limit 1/20 s en `test-all` y `vertex-generate`. Sin token definido la LAN sigue abierta a escrituras; `/connect`, `/secrets` y `DELETE /metrics/reset` no tienen rate-limit. Criterio acordado con el Lead: **PARCIAL documentado**, no FAIL.
- **Exposición de pagos en `/store`:** `main.py:93-94` rechaza entregables de pago; verificado `/store/deliverables/l01..l03` → 200 y `/store/deliverables/e01...` → 404; nuevo `tests/test_store_exposure.py`.
- **Feeds:** el baseline de 55 posts de Threads resultó ser 50 posts idénticos de test + 5 reales (verificado por el Lead con `git show HEAD`). La reducción a 4 posts reales es una limpieza correcta, no una pérdida de inventario; queda como **bloqueo MEDIO de contenido** (4 posts/día < 5–15/día de AGENTS), no como fallo de datos.
- **Vertex:** el conector muestra `REDACTED_EXAMPLE_PROJECT` y `gemini-3.1-flash-image`; el SKILL del proyecto fue actualizado. Pendiente de verificar en MISIÓN 2 que no queden etiquetas viejas en UI ni referencias activas.
- **Sitio estático:** 0 recursos externos en los 61 HTML; 55/55 landings enlazan las 4 páginas legales; sitemap con 60 `<loc>` (55 rutas + 4 legales + raíz `//` cuando `base_url` está vacío — corregir con `--base-url` u omitir la raíz). Las landings **dinámicas** del backend no enlazan legales (MEDIO).

