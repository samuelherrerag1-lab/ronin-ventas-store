# Auditoría Cínica del Sistema

**Corte:** 03/11/2026, 23:08 (hora local).  
**Alcance:** `backend/**/*.py`, `frontend/src/**/*.ts(x)`, `tests/*.py`, `docs/PLAN.md`, `docs/CRITIQUE_LAUNCH_SET.md`, `AGENTS.md`, `data/catalog.json`, `data/social_feeds.json`, los 55 archivos de `data/deliverables/` y el `frontend/dist/` existente.  
**Método:** lectura completa del código; `pytest` (1 fallo / 39 pasados al corte); `tsc --noEmit` (limpio); sondas con `TestClient` sobre la app real; análisis estático de los 55 HTML (tamaño, palabras visibles, enlaces, hashes, PDF/ZIP); inspección del CSS compilado. No ejecuté `npm run build` para no tocar artefactos. El navegador de la sesión estaba desconectado: los hallazgos de UI son de código o de cálculo, no de una prueba visual en dispositivo.

**Nota de honestidad:** no modifiqué código, productos ni configuración. Sí hubo efectos secundarios en `data/`: las sondas de diagnóstico escribieron resultados reales en `data/customizations_state.json`, y las corridas de `pytest` agregaron posts de prueba al feed real (ver A3). El repositorio se estaba editando durante la auditoría: el “Identity Studio” se creó entre 22:50 y 22:56 y se cableó en `App.tsx` después de las 23:00. El corte y los hashes están fechados arriba; si algo cambió después, la cita literal sigue identificando el punto.

---

## Resumen ejecutivo

El sistema no vende. No es una opinión: `docs/PLAN.md:20-22` lo admite (0/55 rutas servidas, 0/55 checkout, 0 publicaciones) y el código lo confirma. Lo que sí hace es fabricar 55 archivos HTML y un dashboard que parece un negocio.

Los 52 productos de pago están en una carpeta estática sin compra ni entitlement: cualquiera con la URL los descarga. Los 3 lead magnets pierden 39 de cada 40 correos concurrentes y devuelven un PDF que no existe. Las 55 rutas puente devuelven el clon de Threads, no una oferta. Los botones de Nequi/PSE muestran un aviso y no cobran.

La seguridad es la de un prototipo: API sin autenticación en `0.0.0.0`, CORS que refleja cualquier origen y un path traversal que lee y escribe JSON arbitrario. La combinación permite que cualquier equipo en el Wi-Fi —y una web maliciosa si el navegador no bloquea el acceso a la red local— lea el catálogo, borre métricas, gaste Vertex y, cuando exista, robe el token de Gumroad.

La honestidad está en los documentos, no en la UI: el PLAN dice 0/55 y la UI muestra “Publicado”; el test de Google Master certifica “CONECTADO” con un Chrome temporal y sin cuenta. El activo más vendible son los bundles M01–M05, que sí compilan contenido real. El más vergonzoso es M06: $149 por un índice de 36 enlaces rotos.

Antes de agregar una función más hay que cerrar la sangría: gate de entregables, 5 landings con checkout real, leads atómicos con entrega y autenticación en la API. Sin eso, cada hora de desarrollo agranda la demo, no los ingresos.

---

## Tabla de los 10 hallazgos más graves

| # | Hallazgo | Severidad | Evidencia | Estado |
|---|---|---|---|---|
| 1 | Los 52 productos de pago se descargan gratis | Crítico | `backend/main.py:38` monta `/deliverables`; `GET /deliverables/e01_maquina-silenciosa-pdf.html` → 200, 141.484 B | Probado |
| 2 | Cero checkout y cero rutas puente | Crítico | 0/52 con `gumroad_url`/`hotmart_url`; `/blueprint/...` → 200, 4.966 B (dashboard); `StanAndStealthView.tsx:39-43` solo muestra un toast | Probado |
| 3 | El lead magnet pierde leads y su URL de entrega es un 404 | Crítico | 40 POST concurrentes → 1 guardado; `api_leads.py:79` devuelve `_expediente.pdf`; 0 PDFs en disco | Probado |
| 4 | Path traversal lee/escribe JSON arbitrario | Crítico | `GET /api/customizations/connect/..%5Ccatalog/status` → 200 con `catalog.json` dentro de `job` | Probado |
| 5 | API sin auth en `0.0.0.0` y CORS abierto | Crítico | `main.py:20-26`; `Origin: http://evil.example` → ACAO reflejado + ACAC `true` | Probado |
| 6 | M06 ($149) es un índice de enlaces rotos | Crítico | 86.297 B, 5.310 palabras, 36 enlaces; 4 probados → dashboard | Probado |
| 7 | Capturas de ingresos falsas sin marca de simulación | Crítico | `social_feed_seed.py:38-41`; `playwright_bait_renderer.py` no agrega “simulación” | Código |
| 8 | “Publicado” y “Mutar con IA” son falsos | Alto | `api_feeds.py:51` cambia el string; `social_feed_seed.py:167` usa `random.choice` | Código |
| 9 | Los ingresos se calculan mal | Alto | BRL/EUR 1:1 USD; COP 4.000 vs 4.200; bumps contados como ventas | Probado |
| 10 | La UI no funciona sin internet | Alto | `frontend/index.html:8` carga Tailwind desde CDN; el CSS compilado no tiene utilidades | Probado |

---

## Crítico (rompe el negocio)

### C1. El catálogo de pago es un directorio público

**Qué pasa.** `backend/main.py:37-39` monta `data/deliverables/` como `StaticFiles` en `/deliverables`. No hay token, sesión, compra ni entitlement. `backend/routers/api_catalog.py:20` construye el nombre `{sku}_{slug}.html` y `:37-38` devuelve los 55 items con `slug`; el propio catálogo es el índice de descargas.

**Evidencia.** Probado: `GET /deliverables/e01_maquina-silenciosa-pdf.html` → `200`, `text/html`, 141.484 bytes. `GET /deliverables/a01_app-forjador-hooks-virales.html` → 200, 171.953 bytes. No hace falta ni el catálogo: los nombres son predecibles y M06 publica 36 rutas.

**Por qué importa.** Es el fallo que anula todo lo demás. Cualquier persona en la LAN —y cualquiera en internet si abres el puerto para Pinterest— se lleva los 52 productos. Un reembolso no puede revocar nada porque no hay licencia ni acceso ligado a una compra. El “All-Access Vault” de $149 es redundante: el vault real es `/deliverables`.

**Dirección.** Sacar `DELIVERABLES_DIR` del mount público. Servir cada archivo con un token firmado de un solo uso, ligado a `order_id` y `sku_id`, con expiración. Los archivos internos del operador van en otro directorio. M06 debe incrustar el contenido o dejar de venderse como vault.

---

### C2. No hay checkout y no hay rutas puente: el sistema no puede cobrar

**Qué pasa.** `data/catalog.json` tiene 52 SKUs de pago y **0** con `gumroad_url` o `hotmart_url`. `frontend/src/components/stan/StanAndStealthView.tsx:39-43` define `handleCheckoutClick`, que solo hace `setCheckoutNotice(...)` y un `setTimeout`: no abre Hotmart, no abre Gumroad, no navega. `backend/main.py:61-68` captura cualquier ruta y devuelve `frontend/dist/index.html`.

**Evidencia.** Probado:
- `/blueprint/maquina-silenciosa-pdf` → `200`, `text/html`, 4.966 B (el dashboard).
- `/vault/ronin-all-access-vault` → `200`, 4.966 B.
- `/gratis/27-hooks-prohibidos` → `200`, 4.966 B.
- `grep` de `gumroad_url|hotmart_url` en `frontend/src` solo encuentra definiciones de tipo (`domain.ts:16-17`, `CatalogFactoryView.tsx:9`), nunca un uso.
- `docs/PLAN.md:20-22` lo admite: “Rutas puente servidas: 0 de 55”, “Checkout configurado: 0 de 55”, “Publicación real: 0”.

**Por qué importa.** El visitante de un pin llega al clon interno de Threads, con el botón “Publicar” muerto. No ve precio, no ve oferta, no ve checkout. La única conversión posible es que el operador copie el link de Gumroad a mano, y ese link no existe en el catálogo. No hay `api_bridge.py`, `landing_renderer.py`, `store_publisher.py` ni `publisher.py`: los archivos que el PLAN promete no están en disco.

**Dirección.** Implementar 5 landings server-rendered (no 55) con `schema.org/Product`, precio, garantía, privacidad, dos botones reales y order bump. Guardar las URLs en `catalog.json`; hacer que “Pagar” navegue. Las otras 50 rutas deben devolver un 404 honesto, no el dashboard.

---

### C3. El lead magnet pierde 39 de cada 40 correos y entrega un PDF inexistente

**Qué pasa.** `backend/routers/api_leads.py:55-75` hace `_load()` → `append` → `_save()` sin lock ni transacción. `_save` escribe el JSON completo con `write_text`. Dos requests concurrentes leen el mismo estado y el último pisa al primero.

**Evidencia.** Probado con 40 POST concurrentes (16 hilos) contra el endpoint real, con `LEADS_JSON_PATH` en un temporal:
- 40 respuestas `200`.
- **1 lead guardado.**
- 39 correos perdidos.

Además, `api_leads.py:79` devuelve:
`/deliverables/{sku_id.lower()}_expediente.pdf`
No existe un solo `.pdf` en el repo (`Get-ChildItem -Recurse -Include *.pdf` → 0). El archivo real de L01 es `data/deliverables/l01_anatomia-post-418-usd.html`. `L01` captura el correo con `fetch('/api/leads')` y luego llama a `window.print()`: el comprador puede guardar un PDF desde el diálogo del navegador, pero no hay archivo descargable, no hay envío por correo y la URL que devuelve el backend está muerta. No hay SMTP, no hay ESP, no hay doble opt-in, no hay baja. `data/leads.json` tiene 0 leads.

**Por qué importa.** Es el único mecanismo de adquisición del embudo. Un lead magnet que no captura, no entrega y no puede enviar nada no es un embudo: es un formulario decorativo. Y `LeadPayload.consent: bool = True` (línea 28), con L01 enviando `consent:true` sin casilla, no cumple una ley de datos seria (Ley 1581 de Colombia exige consentimiento previo, expreso e informado).

**Dirección.** SQLite con `INSERT` atómico y `UNIQUE(email, source)`. Entrega real: PDF pregenerado o el HTML + instrucciones, servido con token. Un ESP (Resend/Postmark) con doble opt-in, baja y exportación. Casilla de consentimiento y política de privacidad visibles.

---

### C4. Path traversal: lectura y escritura de JSON arbitrario, sin auth

**Qué pasa.** `backend/services/connect_jobs.py:22-25`:
```python
return CONNECT_JOBS_DIR / f"{connector_id}.json"
```
`connector_id` viene del path param sin validar. `backend/routers/api_customizations.py:114-122` devuelve el `job` crudo. En Windows, `%5C` es separador y no lo normaliza el router.

**Evidencia.** Probado:
- `GET /api/customizations/connect/..%5Ccatalog/status` → `200`, y el cuerpo trae `"job":[{"sku_id":"E01",...` — es `data/catalog.json` completo.
- `POST /api/customizations/connect/..%5Cleads/stop` escribe el JSON: probado en un directorio temporal, `stop_job("..\\leads")` agregó `status`, `detail` y `updated_at` a un `leads.json` ajeno.

**Por qué importa.** Cuando `data/secrets.json` exista (lo crea `store_secret` al cosechar el token de Gumroad), la misma lectura devuelve el `access_token` en claro: `masked_secrets()` solo enmascara el campo `secrets`, no el `job`. Es lectura arbitraria de JSON en el proyecto y escritura arbitraria de JSON, desde la red, sin credenciales. También lee `frontend/package.json`, `data/customizations_state.json` y cualquier otro `.json` alcanzable con `..\`.

**Dirección.** Validar `connector_id` con `^[a-z_]{1,32}$`; resolver el path y verificar que el padre sea `CONNECT_JOBS_DIR`; devolver solo un DTO, nunca el archivo crudo. En `stop`, usar el `connector_id` validado.

---

### C5. API sin autenticación en `0.0.0.0` + CORS que refleja cualquier origen

**Qué pasa.** `backend/main.py:18` crea la app sin dependencia de auth. `backend/main.py:20-26`:
```python
allow_origins=["*"],
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
```
Starlette refleja el origen cuando hay credenciales.

**Evidencia.** Probado:
- `GET /api/health` con `Origin: http://evil.example` → `access-control-allow-origin: http://evil.example`, `access-control-allow-credentials: true`.
- Preflight `OPTIONS /api/metrics/reset` → `200`, métodos `DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT, QUERY`.

**Por qué importa.** Cualquier equipo en el mismo Wi-Fi puede llamar sin credenciales; una página web también puede intentarlo, y el CORS le permite leer la respuesta salvo que el navegador bloquee Private Network Access. Los endpoints destructivos o caros están abiertos:
- `DELETE /api/metrics/reset` borra las métricas reales.
- `POST /api/customizations/test-all` genera una imagen Vertex real (cuesta dinero) y lanza Chrome.
- `POST /api/customizations/connect/{id}` abre Chrome con el perfil persistente del vault.
- `GET /api/customizations/secrets` devuelve los secretos enmascarados, con email y user_id en claro.

**Dirección.** Bind a `127.0.0.1` por defecto; para móvil, un token de sesión (cookie `HttpOnly` o bearer) y CORS limitado al origen de la app. Los endpoints de escritura y los que gastan dinero exigen confirmación y rate limit.

---

### C6. M06: el producto más caro es un índice de enlaces que no llevan a ninguna parte

**Qué pasa.** `M06 — THE INSIDER VAULT (All-Access: Los 52 Productos + Actualizaciones)` cuesta **$149**. El archivo `data/deliverables/m06_ronin-all-access-vault.html` pesa 86.297 bytes, tiene 5.310 palabras visibles, 1 `<h1>`, 8 `<h2>` y 36 enlaces. No incrusta ni un producto: lista títulos, precios y rutas.

**Evidencia.** Probado:
- 36 `href` a `/blueprint/...`, `/boveda/...`, `/app/...`.
- `/blueprint/maquina-silenciosa-pdf` → 200, 4.966 B (dashboard).
- `/boveda/boveda-500-hooks-cinicos` → 200, 4.966 B.
- `/app/app-forjador-hooks-virales` → 200, 4.966 B.
- `/vault/ronin-all-access-vault` (la ruta del propio M06) → 200, 4.966 B.
- 0 PDFs, 0 ZIPs en el repo.

**Por qué importa.** El comprador paga $149 y recibe una tabla de contenidos con enlaces que abren el panel interno. No hay “actualizaciones de por vida” porque no hay canal de entrega ni versión. Es el SKU con mayor riesgo de contracargo y de denuncia. Los bundles M01–M05 sí compilan contenido real (M05 23.168 palabras; M01–M04 38.464–72.413), así que el problema no es el formato: es M06.

**Dirección.** O se reconstruye M06 como un ZIP con los 52 archivos y un mecanismo de actualización, o se elimina del catálogo. Mientras tanto, no se puede vender.

---

### C7. Capturas de ingresos falsas sin marca de simulación

**Qué pasa.** El “Laboratorio de Capturas Anzuelo” genera pantallas iOS con notificaciones de Gumroad/Hotmart (“You made a sale!”, “¡Venta realizada!”, “$418.50 USD”) y cifras impares. `backend/services/social_feed_seed.py:38-41` siembra notificaciones falsas; `backend/services/playwright_bait_renderer.py` renderiza el HTML y devuelve `status: "ok"`. En ningún punto se agrega “simulación”, “ejemplo” o “no es una venta real” dentro del PNG.

**Evidencia.** El clon de Threads etiqueta los contadores como “VISTA PREVIA — cifras de ejemplo” (`ThreadsCloneView.tsx:193-195`), pero la etiqueta desaparece cuando el usuario exporta la imagen. El archivo `ios_html_templates.py` interpola las notificaciones sin escape (ver A5), así que el texto es exactamente lo que el operador escriba.

**Por qué importa.** Si la captura se publica como prueba de ingresos —que es el uso previsto— es publicidad engañosa (Ley 1480 de 2011, Colombia) y viola las políticas de Meta y Pinterest sobre contenido engañoso. No es un problema de estética: es la causa más probable de suspensión de cuenta, contracargos y una reclamación. La regla de `AGENTS.md` (“sin hacer promesas directas de ingresos”) no se cumple: la imagen *es* la promesa.

**Dirección.** Marca de agua obligatoria “SIMULACIÓN” en el PNG y en la vista previa; metadatos que lo declaren; usar las capturas solo como mockup de producto, nunca como prueba. Si se quiere prueba real, publicar una captura del dashboard propio con datos tapados y fecha.

---

## Alto (rompe una función)

### A1. Tres estados falsos: SSO “CONECTADO”, “Publicado” y “Mutar con IA”

**Google Master.** `backend/services/probe_runners.py:116-147` lanza Chrome headless con `--user-data-dir` a un **directorio temporal vacío** y `about:blank`; si el proceso devuelve 0, reporta `status="CONECTADO"` para `google_master` con el nombre “Google Master Session (Chrome Vault)”. No toca el vault, no abre Google, no verifica una sesión. El test `tests/test_customizations_hub.py:103-113` lo certifica: `assert d["status"] == "CONECTADO"`. `frontend/src/App.tsx:115` convierte cualquier conector verde en `ssoStatus = 'CONECTADO'`, así que este falso verde pinta el badge de SSO.

**Publicado.** `backend/routers/api_feeds.py:46-54` cambia `post.status` entre `queued` y `published` y guarda el JSON. No hay llamada a Threads/Pinterest, no hay URL, no hay timestamp de publicación, no hay evidencia. Lo mismo en `:57-65` para pins. El PLAN (`docs/PLAN.md:254`) dice que `status` solo debe pasar a `published` con URL; el código lo ignora.

**Mutar con IA.** `backend/services/social_feed_seed.py:165-172`:
```python
template = random.choice(HOOK_MUTATION_TEMPLATES)
...
post.simulated_likes += random.randint(45, 190)
```
No hay IA: hay 5 plantillas y un random. La UI lo llama “Mutar hook con IA” (`ThreadsCloneView.tsx:170`). Cada clic infla los likes simulados y muta el post. De hecho, el post canónico `th_001` ya no dice “$418.50”: está mutado y acumula más de 7.200 likes simulados.

**Por qué importa.** El sistema se vende como “cero estado falso” (`AGENTS.md`), pero tres de sus funciones centrales son teatro. Un operador puede creer que publicó, que conectó Google o que mejoró un hook con IA cuando nada de eso ocurrió.

**Dirección.** Google Master debe verificar una cookie/sesión real en el vault (o quedarse en `SIN_VERIFICAR`). `published` exige URL y timestamp devueltos por la plataforma; si no, el botón se llama “Marcar como listo” y no “Publicado”. “Mutar” se etiqueta como “Variante de plantilla” o se conecta a un modelo real con costo y evidencia.

---

### A2. La matemática de ingresos está mal y el embudo es inventado

**Qué pasa.**
- `backend/services/csv_sales_parser.py:7`: `COP_TO_USD_RATE = 4000.0`. `backend/services/catalog_seed.py:7`: `COP_RATE = 4200`. Dos tasas para el mismo negocio.
- `csv_sales_parser.py:118-123`: solo convierte `COP`. Si la moneda es `BRL` o `EUR`, deja `amount_usd = amount` y `amount_cop = amount * 4000`.
- `backend/services/metrics_service.py:93` y `:112`: `total_sales = len(sales)`; los order bumps se guardan como `SaleRecord` con `is_order_bump=True` y se cuentan como ventas. El AOV y la conversión se inflan.
- `metrics_service.py:164-166`: el “funnel” se calcula por prefijo de SKU (`E`/`A` → `via_a`, `B` → `via_b`, resto → `via_c`). No hay UTM, no hay ruta, no hay atribución. La UI lo etiqueta “Vía A (Ebooks/Apps)” (`MetricsRadarView.tsx:231-233`), lo que contradice la Vía A real de `AGENTS.md` (capturas anzuelo).

**Evidencia.** Probado con un CSV:
```
BR-1,2026-11-01,E01 Test,R$ 100,BRL
EU-1,2026-11-01,E01 Test,100 EUR,EUR
```
Resultado: `[(100.0, 'BRL'), (100.0, 'EUR')]`. R$100 vale ~$18; €100 vale ~$108. El sistema los suma como $200.

**Por qué importa.** El Radar toma decisiones “Doblar o Matar” con estos números. Un aumento de ventas en reales se lee como dólares; un bump de $9 se lee como una venta completa; el embudo por prefijo no dice qué pieza vendió. Es peor que no medir: mide mal y da confianza.

**Dirección.** Una sola fuente de FX con fecha; convertir BRL/EUR/USD/COP; separar `sales` de `bumps` en el resumen; atribución real por `route`/UTM capturada en el checkout; no llamar “funnel” a un `startswith`.

---

### A3. Los datos viven en JSON sin atomicidad, sin backups y sin git; los tests los contaminan

**Qué pasa.** Todos los stores son `write_text(json.dumps(...))`: `catalog_seed.py:169`, `api_leads.py:46`, `metrics_service.py:28`, `social_feed_seed.py:162`, `connectors_hub.py:31`, `connector_diagnostics.py:109`. No hay escritura atómica (tmp + replace), no hay lock, no hay versión de esquema. `catalog_seed.py:158-160` hace `json.loads` sin `try`: un byte corrupto en `catalog.json` rompe `/api/catalog` y todas las vistas. `metrics_service.py:16-22`, `api_leads.py:31-40` y `connectors_hub.py:19-26` se tragan la excepción y devuelven vacío; el siguiente guardado sobrescribe la historia.

**Evidencia.**
- No hay `.git` ni `.gitignore` (`Test-Path .git` → `False`). No hay historial ni rollback. El único backup son 8 archivos en `data/deliverables_backup/`.
- `pytest` no aísla `FEEDS_JSON_PATH` ni `CATALOG_JSON_PATH`: `tests/conftest.py:28-38` solo parchea customizations, metrics y leads. `tests/test_bloque1.py:65-85` hace `POST /api/feeds/threads/from-bait` y `mutate-hook` contra el feed real.
- Estado observado: `data/social_feeds.json` tiene **55 threads**, de los cuales **50** son “Prueba de inyección desde el laboratorio de anzuelos” con `post_id` correlativos (`th_005`…`th_055`). `th_001` fue mutado y acumula más de 7.200 likes simulados. Mis corridas de `pytest` agregaron los últimos; el bug es de la suite, no de una corrida: cada `pytest` crea uno más.
- `data/generated_images/` tiene 118 PNG, 195 MB, solo 57 hashes únicos (61 duplicados); no hay poda.
- `data/` pesa 767 MB; el Chrome Vault, 156 MB.

**Por qué importa.** Un corte de luz, un disco lleno o un `write_text` interrumpido dejan el catálogo ilegible y sin backup. La suite que debería proteger los datos los ensucia: cada `pytest` mete un post de prueba en el feed que ve el usuario. Y sin git, un cambio malo no se puede revertir.

**Dirección.** SQLite (o al menos `tmp` + `os.replace` + `fcntl`/`msvcrt` lock) para leads, métricas, catálogo y feeds; backups automáticos con retención; `.gitignore` que excluya `data/chrome_vault`, `data/secrets.json`, `data/leads.json`; aislar `FEEDS_JSON_PATH` y `CATALOG_JSON_PATH` en `conftest.py`; un test que falle si `data/` cambia después de la suite.

---

### A4. La UI depende de un CDN: sin internet no hay estilos (y el “LAN” puede dar 127.0.0.1)

**Qué pasa.** `frontend/index.html:8`:
```html
<script src="https://cdn.tailwindcss.com"></script>
```
No hay Tailwind en `package.json` ni en el build. El CSS compilado (`frontend/dist/assets/index-C7mver8c.css`, 34.512 B) no contiene ni una utilidad (0 coincidencias de `.flex{`, `.grid{`, `.min-h-screen`): son las fuentes y el CSS propio. Todas las clases de layout se generan en el navegador con el CDN.

**Evidencia.** Inspección del `dist` existente. `frontend/index.html:40` también carga `fonts.cdnfonts.com` para SF Pro (fuente de Apple, licencia dudosa). Si el CDN no responde, el dashboard queda como una lista de texto sin grid, sin sidebar y sin responsive.

**El “LAN”.** `backend/config.py:36-43` obtiene la IP con un socket UDP a `8.8.8.8:80`. No es una detección de interfaz: si no hay ruta por defecto (LAN aislada, Wi-Fi sin gateway), cae en `127.0.0.1`. `frontend/src/App.tsx:57` arranca con `http://192.168.1.10:8765` hardcodeado y lo muestra con un punto verde pulsante antes de que responda `/api/health`. Si el backend falla, el operador ve una IP falsa y un “LAN” que no existe.

**Por qué importa.** El caso de uso declarado es “PC + móvil en la misma red”, a menudo sin internet. En ese escenario la UI no se ve y el enlace que copias para el móvil puede ser `127.0.0.1`. La promesa “100% offline” es cierta para los 55 productos, no para la app.

**Dirección.** Compilar Tailwind en el build (`tailwindcss` + `postcss`, o migrar a CSS modules); self-host de fuentes; detectar la LAN con `socket.gethostbyname_ex`/`psutil.net_if_addrs` y mostrar “sin red” en vez de una IP inventada.

---

### A5. El renderizador iOS ejecuta HTML del usuario en el Chromium del servidor (XSS/SSRF) y lee imágenes por traversal

**Qué pasa.** `backend/services/ios_html_templates.py:119-132` interpola `headline_metric`, `sub_metric`, `notifications`, `date_label` y `timestamp_label` sin `html.escape`. `backend/services/playwright_bait_renderer.py:91` hace `page.set_content(html_str, wait_until="load")`, que ejecuta scripts. El endpoint `POST /api/customizations/render-ios-png` no tiene auth.

**Evidencia.** Probado en memoria: `build_ios17_lockscreen_html('<img ...>', 'sub', ['<script>document.title=1</script>'], ...)` devuelve el `<script>` literal, sin escapar (`raw script present: True`, `escaped? False`). El `<img>` de `headline_metric` no aparece porque el widget está desactivado, pero el `<script>` de `notifications` sí.

**Por qué importa.** Un atacante en la LAN puede inyectar JS que corre en el navegador headless del servidor. Desde ahí puede llamar a la API local sin auth (borrar métricas, lanzar `test-all` y gastar Vertex, abrir Chrome con el vault) y leer respuestas porque el CORS las permite. Combinado con C4, puede pedir `..%5Csecrets` y exfiltrar el token de Gumroad. Además, `_wallpaper_data_uri` (`ios_html_templates.py:72-88`) usa `GENERATED_IMG_DIR / wallpaper_filename` con el nombre que manda el cliente: `..\..\...` lee cualquier imagen del disco y la incrusta en el PNG.

**Dirección.** `html.escape` en todos los campos; allowlist de `wallpaper_filename` (`^[a-z0-9_]+\.png$`) y resolución con `Path.resolve()` + `is_relative_to`; lanzar Chromium con `--disable-web-security` no, con red bloqueada y sin acceso al host; autenticar el endpoint.

---

### A6. El generador de productos fabrica cifras, promete 15 hooks y entrega 20, y puede sobrescribir lead magnets

**Qué pasa.** `backend/services/product_templates_elite.py` es el fallback que genera un “entregable élite” cuando falta un archivo. No es élite: es una plantilla de 29.845 bytes y ~1.270 palabras visibles, idéntica en estructura y contenido salvo los campos del SKU (título, subtítulo, precio, nicho, gancho y ruta).

**Evidencia.**
- `:60` dice “15 Hooks Cínicos de Alto Voltaje”; el array `HOOKS` tiene **20** (probado: `hooks in array 20`, `label ['15']`).
- `:60` dice “Han sido probados contra audiencias frías sin inversión publicitaria”. Es falso: son 20 frases fijas.
- `:54` afirma “El 93% de cursos en video nunca se completan”, “reembolso inferior al 1.2%”, “margen neto superior al 91%”.
- `:56` afirma “tasa de aceptación histórica del 38%” del order bump.
- `:62` afirma “pedir teléfono o dirección física destruye el 44% de los carritos”.
- `:28` del `product_factory.py`: sobrescribe si el archivo no existe o mide **menos de 60.000 bytes**. Los lead magnets miden 56.241–59.939 bytes: si alguien llama a `generate_all_micro_apps()` (hoy es una función muerta, ver B1), los reemplaza por la plantilla. `api_catalog.py:64` usa otro guardia (>1.500 bytes) y no sobrescribe; dos políticas contradictorias para el mismo archivo.

**Por qué importa.** Si `data/deliverables/` se pierde (disco, limpieza, migración), regenerar produce 52 clones de un documento de 1.270 palabras con estadísticas inventadas, no los productos que se venden. Y el texto incluye afirmaciones de ingresos sin fuente, justo lo que el `CRITIQUE_LAUNCH_SET` señaló.

**Dirección.** Un solo guardia (`is_file()` + hash/versión), nunca sobrescribir sin confirmación. Si el generador se mantiene, que sea un esqueleto vacío y marcado, no un producto con claims. Corregir 15→20 o eliminar 5 hooks; borrar las cifras o citar fuente.

---

### A7. El panel de 112 skills no controla nada y el gate de verificación está rojo

**Qué pasa.** `backend/services/connectors_hub.py:153-162` guarda `skill_toggles[skill_id] = enabled`. `backend/services/skills_loader.py:31` lee ese booleano **solo para mostrarlo** en la tabla. No hay ningún consumidor que active/desactive una skill, un prompt o un agente. El “Customizations & Connectors Hub (SSO 1-Clic + 112 Skills Globales)” es una tabla de exhibición con interruptores decorativos.

**El gate.** Al corte, `pytest` da **1 fallo / 39 pasados**:
```
FAILED tests/test_bloque1.py::test_strict_atomic_file_line_limit
Archivos que violan el límite de 250 líneas:
[('frontend\\src\\components\\brand\\painters.ts', 273)]
```
`painters.ts` pertenece al “Identity Studio” que se cableó en `App.tsx:17,33,202` durante esta auditoría. La función existe y se ve, pero su archivo de pintura tiene 273 líneas: viola la regla atómica de `AGENTS.md` y rompe el único test de disciplina. `docs/PLAN.md:16-17` afirma “28/28 verde” y “0 archivos >250”; hoy son 40 tests, 1 rojo y 1 archivo >250.

**Por qué importa.** El sistema presume de verificación real, pero el gate se rompe en la primera característica nueva que se agrega, y el panel que promete “112 skills” no cambia el comportamiento del sistema. Es la definición de teatro operativo: mucho tablero, ningún actuador.

**Dirección.** O se cablean los toggles a los prompts/agents (y se prueba el efecto), o se elimina la tabla. Partir `painters.ts` en dos archivos ≤250 o eliminar la vista si no está terminada. El gate debe correr en CI, no en la memoria del operador.

---

### A8. Cumplimiento y entrega: sin términos, sin privacidad, sin licencia, sin reembolso, sin revocación

**Qué pasa.** No hay páginas de términos, privacidad, reembolso o licencia. `LeadPayload.consent` es `True` por defecto (`api_leads.py:28`) y L01 manda `consent:true` sin casilla. Los 55 entregables no llevan licencia de uso ni marca de compra; el archivo se puede compartir sin rastro. La entrega es una URL estática (C1), así que un reembolso no revoca el acceso. No hay factura ni impuestos propios; si se usa Gumroad/Hotmart como merchant of record, ellos cubren el IVA, pero el “clon de Stan” no existe como checkout.

**Evidencia.** `grep` de `privacy|terms|refund|license|factura|iva` en `frontend/src` y `backend` no encuentra páginas ni endpoints. `data/deliverables/*.html` no incluye una sección de licencia; el único texto legal es la marca `@ronOverthinks`.

**Por qué importa.** Vender a LatAm sin política de privacidad para el correo, sin baja y sin licencia es exposición legal y una objeción de compra. Un comprador que pide reembolso se queda con el archivo y con la URL. Y un afiliado no tiene contrato ni atribución (ver D).

**Dirección.** Páginas de términos/privacidad/reembolso con fecha; casilla de consentimiento explícita; licencia personal en cada producto; entrega con token revocable; registro de compra para soporte.

---

### A9. El Circuit Breaker de FinOps no mide el gasto de este proyecto

**Qué pasa.** `backend/services/vertex_image_service.py:49-51` consulta `get_finops_summary()` y compara `total_spent_usd + 0.03 > circuit_breaker_limit_usd`. `get_finops_summary` (`connectors_hub.py:35-49`) lee `data/finops-ledger.json` o el ledger de **otro proyecto** (`C:\Users\USER\Documents\Generador de Contenido\finops-ledger.json`). Nunca escribe el gasto de este proyecto. El “breaker” puede no dispararse nunca, o dispararse por el gasto de otro sistema.

**Evidencia.** Probado: `get_finops_summary()` devuelve `ledger_source: "sibling"`, `ledger_path: C:\Users\USER\Documents\Generador de Contenido\finops-ledger.json`, `total_spent_usd: 0.96`, `circuit_breaker_limit_usd: 100.0`. `data/finops-ledger.json` no existe. La UI muestra tres cifras distintas: si `customizations` es null, la sidebar cae en `0.00 / 50` (`App.tsx:116-117`); con el ledger actual, `0.96 / 100`; Bait Studio muestra `$0.96 / $1.00` por el fallback hardcodeado (`BaitStudioView.tsx:105-107`).

**Por qué importa.** El gasto real de Vertex no se registra; el operador no sabe cuánto lleva gastado. Un `test-all` repetido puede quemar el saldo sin que el breaker lo vea. Y la cifra que ve el usuario es la de otro proyecto.

**Dirección.** Un ledger propio, escrito en cada generación, con costo real por modelo; breaker por proyecto; la UI muestra una sola cifra y su fuente. Si no hay ledger, `ledger_found: false` y no se muestra un número inventado.

---

### A10. Los productos estrella siguen teniendo defectos de credibilidad verificables

**Qué pasa.** El `CRITIQUE_LAUNCH_SET` ya auditó los 5; no lo repito. Verifiqué que algunas correcciones se hicieron (E03 ya dice $29 en portada; L01 ya hace `fetch('/api/leads')`) y que otras siguen mal.

**Evidencia.**
- **B01:** 500 hooks, pero **199** terminan con una de cuatro frases idénticas (50 + 50 + 50 + 49) y **49** incluyen el paréntesis `(cifra ilustrativa: valídala antes de publicar)` *dentro* del hook, lo que lo vuelve impublicable. Ejemplo: “Lo replica un script en 4 minutos (cifra ilustrativa: valídala antes de publicar).”
- **E02:** 13.076 palabras visibles; el PLAN exige 20.000 (`docs/PLAN.md:154`). Las 30 rutas son de finanzas personales, no del catálogo.
- **L01:** 4.135 palabras; el CTA `/sistema/catalogo-ronin-ventas-os` (línea 482) no existe en el catálogo y devuelve el dashboard.
- **B09:** 29.371 palabras, pero los scripts en primera persona con cifras inventadas contradicen la propia regla del manual: “Usar cifras inventadas. Una cifra falsa se convierte en una captura y la captura se convierte en una crisis.” Ejemplo real del archivo: “Hotmart registró 27 checkouts iniciados para 7 pagos completados en mi cuenta.”
- **E03:** el único ebook que supera 20.000 palabras visibles (20.139) y el único con precio interno alineado.

**Por qué importa.** Vender 52 SKUs con 5 auditados y 47 sin auditar es una lotería de reembolsos. Los defectos no son estéticos: son afirmaciones que el comprador puede comprobar en 2 minutos (el “500” con 199 finales iguales, el “15” del generador, el PDF que no llega).

**Dirección.** Un QA gate por producto: palabras, enlaces, claims, print, precio, licencia. No publicar hasta pasar. B01: eliminar el paréntesis y reescribir los 199 finales. E02: 20k o bajar el precio. L01: CTA real.

---

## Medio (degrada)

### M1. Errores y estados sin salida en la UI

- `App.tsx:61-78`: `Promise.all` de 4 endpoints. Si uno falla, no se setea **ninguno**; la UI queda vacía y solo hay un `console.error`. No hay estado de error ni reintento por sección.
- `App.tsx:86-97`: los handlers (`handleMutateHook`, `handleToggleThreadStatus`, `handleTogglePinStatus`, `handleToggleStan`) no tienen `try/catch`. Un 404 o un 500 produce una promesa rechazada y ningún mensaje; el botón “no hace nada”.
- `ThreadsCloneView.tsx:86`: el botón “Publicar” no tiene `onClick`. Los de responder, repostear y compartir (`:156-166`) tampoco.
- `PinterestCloneView.tsx:107`: “Guardar” no guarda en Pinterest; cambia el estado local a `published`.
- `MetricsRadarView.tsx:216`: “Mutar Gancho Verbal” llama `onMutateHook(p.piece_id)`; si el `piece_id` es una métrica manual (`th_winner_01`) y no un post del feed, el endpoint devuelve 404 y el botón no hace nada.
- `MetricsRadarView.tsx:38-43`: “Reset” borra todo con un `window.confirm`, sin exportar ni backup.

### M2. Móvil: el laboratorio de anzuelos no cabe en un teléfono

`BaitStudioView.tsx:158` tiene un contenedor fijo `w-[346px]` dentro de una tarjeta con `p-4` (32 px) y una página con `p-2.5` (20 px). En un viewport de 390 px: 390 − 20 − 32 = 338 < 346; en 360 px: 308 < 346. Desborda horizontalmente en todos los teléfonos comunes. No lo probé en dispositivo (cálculo). `M06` no tiene `@media` y su tabla de 52 productos no está pensada para 390 px.

### M3. Fallbacks que inventan catálogo, conectores y finanzas

- `StanAndStealthView.tsx:27-31`: si `products` está vacío, muestra 3 productos inventados (`E01 Manual Faceless Threads`, `B01 Bóveda 100 Prompts`, `L01 Cheat-Sheet 18 Hooks`) con rutas que no existen (`/app/prompts-vault`, `/free/viral-hooks`). El banner de arriba dice “VISTA PREVIA — Precios Reales Catálogo” (`:99`). No son los precios reales.
- `App.tsx:124`: `totalSkus={products.length || 55}`. Si el backend devuelve 0, la sidebar dice “55 SKUs”.
- `App.tsx:114`: `totalConnectors = connectors.length || 8`. Si no hay conectores, dice “8”.
- `BaitStudioView.tsx:105-107`: si `finops` no llegó, muestra `$0.96 / $1.00`; el ledger real dice `$0.96 / $100`.

### M4. Datos de competencia hardcodeados y sin fuente

`backend/routers/api_customizations.py:59-84` devuelve tres “teardowns” con handles (`@lluvia.creates`, `@alinagrace.digital`, `@comousarapps`), seguidores (168, 3.066, 14.500), cadencias y afirmaciones como “usa claims y capturas de $567/día como anzuelo visual puro”. No hay fecha, fuente ni captura. Se presentan en la UI como “Ingeniería Inversa de Cuentas Competidoras”. Es riesgo de difamación y desinformación; además, envejece mal.

### M5. CSV y métricas: entrada sin límites y PII en la respuesta

- `api_metrics.py:77-89`: `await file.read()` sin límite de tamaño; `csv_content` sin límite. Un archivo de 500 MB agota la memoria.
- `CsvImportResult` incluye `all_sales` (`metrics_models.py:46`), y `import_sales_csv` lo devuelve: los emails de clientes viajan en la respuesta JSON. No se usan en la UI.
- `MetricsImportModal.tsx:69`: la ruta manual se sintetiza como `/blueprint/{sku}`, incorrecta para B/K/M/L. La atribución nace mal.
- `api_metrics.py:23-32`: `date` es un string libre, sin validar; se puede registrar una métrica con fecha “hola”.

### M6. Duplicados, archivo vacío y backup manual

En la raíz hay copias de productos (`a01_...html`, `b01_...html`, `e01_...html`, `l02_calculadora-express-precio-digital.html`) que no son las que sirve la API (`data/deliverables/`). `l02_calculadora-express-precio-digital.html` pesa **0 bytes**. `data/deliverables_backup/` tiene 8 archivos, sin fecha ni política. Dos versiones del mismo producto invitan a editar la equivocada.

### M7. Accesibilidad y teclado

Botones icono-only sin `aria-label` (Pinterest guardar/compartir, Threads responder/repostear/compartir), modales sin `Escape` ni focus trap (`CatalogFactoryView.tsx:189-209`, el modal LAN en `App.tsx:210-231`), etiquetas de 9 px, contraste bajo en textos `zinc-500` sobre `#090b10`. No es lo que rompe la venta, pero excluye lectores de pantalla y teclado.

### M8. Documentación que promete archivos que no existen

`docs/PLAN.md` referencia `backend/services/session_probes.py` (línea 65), `store_publisher.py` (110), `api_bridge.py` y `landing_renderer.py` (200), `publisher.py` (254) y `scripts/audit_launch_set.py` (167). Ninguno existe (`Test-Path` → False). También dice “28/28 verde” y “0 archivos >250” cuando el corte da 39/40 y `painters.ts` 273. El PLAN es el documento más honesto del repo en su baseline (0/55, 0/55), pero su “estado implementado” está adelantado.

---

## Bajo (deuda)

- **B1.** Funciones muertas: `connectors_hub.launch_connector_login` (línea 93) y `product_factory.generate_all_micro_apps` (línea 46) no se llaman desde ningún lado. La segunda, si se llamara, sobrescribe lead magnets (A6).
- **B2.** Dependencia muerta: `puppeteer-core` en `frontend/package.json` no se usa en `src`.
- **B3.** Símbolos en vez de emojis: el generador usa `📋` y `📥` (`product_templates_elite.py:68`); 23 entregables usan `✓/★/✕/✎` (más de 100 ocurrencias). No son emojis de sistema, pero violan el espíritu de “cero emojis” de `AGENTS.md` y el `📋/📥` es literal.
- **B4.** Logs solo a consola: `desktop_launcher.py:38` corre uvicorn sin archivo ni rotación. Si la ventana se cierra, no hay evidencia de la venta ni del error.
- **B5.** `connect_jobs._is_alive` usa `tasklist /FI PID` y `stop_job` hace `taskkill /T /F` sobre el PID guardado. Tras un reinicio, un PID reciclado puede matar un proceso ajeno. Bajo, pero es un `kill` sin verificar el nombre del proceso.
- **B6.** Sin cabeceras de seguridad (CSP, `X-Content-Type-Options`, `Referrer-Policy`, `frame-ancestors`). La app embebe HTML propio en iframes; una CSP mínima evitaría sorpresas.
- **B7.** Tests que no prueban lo que dicen: `test_catalog_generate_real_deliverable` solo verifica `bytes > 500` (`test_bloque1.py:39`); `test_published_sku_requires_checkout_url` pasa porque **ningún** SKU está `published` (`test_honesty.py:54-62`), no porque haya checkout. El segundo da falsa confianza sobre el problema C2.
- **B8.** Falta `README` de operación: no hay instrucciones de backup, restauración, rotación de tokens ni de qué hacer si `catalog.json` se corrompe. El `start_ronin_os.bat` solo arranca.

---

## Lo que está bien

- Los 55 entregables existen, pesan 12 MB en total, son distintos entre sí (55 hashes únicos) y no dependen de CDNs (salvo enlaces de ejemplo en A05).
- El catálogo tiene exactamente 52 SKUs de pago + 3 lead magnets y 55 rutas únicas, sin duplicados.
- El estado vacío de métricas es honesto: `has_real_data: false`, `aov: null`, “SIN DATOS SUFICIENTES”; el modo demo está etiquetado y separado.
- `vault_inspector.py` reporta hechos medidos (cookies legibles, dominios, Playwright) y deja `liarjs_target_score: null`; no inventa fingerprint.
- Las sondas de Gumroad y GitHub usan la API/CLI reales y devuelven el error literal; las de redes sociales se quedan en `SIN_VERIFICAR` en vez de fingir sesión.
- `tests/conftest.py` aísla leads, métricas y customizations (el problema es que no aísla feeds/catálogo).
- `tsc --noEmit` pasa limpio; los tipos del frontend compilan (no ejecuté `npm run build`).
- M01–M05 incrustan contenido real (23.168–72.413 palabras visibles), no solo enlaces.
- El endpoint de leads valida el correo con regex, deduplica por `email+source` y limita a 50.000.
- `docs/CRITIQUE_LAUNCH_SET.md` es una auditoría de producto específica y correcta en la mayoría de sus señalamientos; es el mejor documento del repo.

---

## Plan de corrección en 3 sprints

### Sprint 1 — Cerrar la sangría (5–7 días)

**Objetivo:** que el sistema pueda cobrar una vez sin regalar el catálogo ni perder el lead.

1. **Entitlement real.** Sacar `DELIVERABLES_DIR` del mount público. Servir cada producto con un token firmado (HMAC, `order_id`, `sku_id`, expiración 24 h, un solo uso). Los archivos del operador, en otro directorio.
2. **5 landings, no 55.** `api_bridge.py` + `landing_renderer.py` con `/blueprint/{5 slugs}`, precio, garantía, privacidad, dos botones reales y bump. Las otras 50 devuelven 404 honesto. Cargar `gumroad_url`/`hotmart_url` en `catalog.json` y hacer que “Pagar” navegue.
3. **Leads atómicos y entrega real.** SQLite con `UNIQUE(email, source)`; PDF pregenerado o HTML con token; ESP con doble opt-in, baja y exportación; casilla de consentimiento.
4. **Seguridad mínima.** Bind `127.0.0.1` por defecto; token de sesión para LAN; CORS solo el origen de la app; validar `connector_id`; `html.escape` en el renderer; allowlist de wallpaper; rate limit en Vertex/test-all.
5. **Matar los falsos verdes.** Google Master se queda `SIN_VERIFICAR` hasta verificar una cookie real; `published` exige URL; “Mutar” se renombra o se conecta a un modelo real.

**Aceptación:** una venta de prueba con checkout real, archivo entregado por token y lead en SQLite; 0 archivos de pago públicos; 0 “CONECTADO” sin evidencia.

### Sprint 2 — Producto y datos (7–10 días)

**Objetivo:** que lo que se vende sea defendible y que los números no mientan.

1. **Un solo FX y atribución.** Convertir USD/COP/BRL/EUR con fecha; separar ventas de bumps; guardar `route`/UTM en la orden; reemplazar el “funnel por prefijo” por atribución real.
2. **SQLite para todo.** Catálogo, leads, métricas, feeds y estado de conectores con migraciones, `tmp+replace`, backups diarios y restauración probada. `.gitignore` para `data/chrome_vault`, `data/secrets.json`, `data/leads.json`.
3. **Arreglar los 5 del lanzamiento.** B01: quitar los 49 paréntesis y reescribir los 199 finales. E02: 20k o bajar precio. L01: CTA real y PDF. B09: quitar testimonios en primera persona. E03: mantener. QA gate por producto (palabras, enlaces, claims, print, precio, licencia).
4. **Legal y entrega.** Términos, privacidad, reembolso, licencia personal; consentimiento explícito; factura/recibo; watermark “SIMULACIÓN” en las capturas.
5. **Offline real.** Tailwind compilado, fuentes self-hosted, detección de LAN sin `8.8.8.8`, estados de error/reintento, botones muertos resueltos, overflow móvil.

**Aceptación:** 5 productos pasan el gate; el dashboard funciona sin internet; el 100% de los enlaces de producto responden 200; 0 posts de prueba en el feed.

### Sprint 3 — Escala (10–14 días)

**Objetivo:** vender más sin volver a la demo.

1. **Afiliados y atribución.** Links por afiliado, cupones, comisión sobre neto, cookie 30–60 días, reporte por canal.
2. **Webhooks y entrega automática.** Gumroad/Hotmart → orden → token → email; revocación en reembolso; reenvío.
3. **Radar real.** Ingresos, AOV, refunds, conversión por ruta y por pieza; “Doblar o Matar” sobre datos atribuidos, no sobre prefijos.
4. **Operación.** Logs con rotación, retención de imágenes (máx. 30 días o 500 MB), alarma de disco, healthcheck, supervisión del proceso, backup/restore mensual, `.git` con historial.
5. **CI.** `pytest`, `tsc --noEmit`, link checker, claims scanner y auditoría de producto en cada push. Borrar `brand/*` no importado o integrarlo; `painters.ts` ≤250; el gate debe estar verde por código, no por narrativa.

**Aceptación:** 10 ventas/semana con atribución, tasa de reembolso <5%, 0 pasos manuales entre pago y entrega, y un restore de backup probado.

---

## Apéndice: reproducción

```powershell
cd C:\Users\USER\Documents\ronin_ventas

# 1. Gate oficial (ojo: cada corrida agrega un post de prueba al feed real; ver A3)
.\.venv\Scripts\python.exe -m pytest tests -q
cd frontend; npx tsc --noEmit; cd ..

# 2. Producto de pago servido gratis
Invoke-WebRequest http://127.0.0.1:8765/deliverables/e01_maquina-silenciosa-pdf.html -UseBasicParsing |
  Select-Object StatusCode, @{n='Bytes';e={$_.RawContentLength}}

# 3. Ruta puente que devuelve el dashboard
Invoke-WebRequest http://127.0.0.1:8765/blueprint/maquina-silenciosa-pdf -UseBasicParsing |
  Select-Object StatusCode, @{n='Bytes';e={$_.RawContentLength}}

# 4. Path traversal (lectura de catalog.json)
Invoke-WebRequest "http://127.0.0.1:8765/api/customizations/connect/..%5Ccatalog/status" -UseBasicParsing |
  Select-Object -ExpandProperty Content | Select-String "sku_id"

# 5. CORS reflejado
$r = Invoke-WebRequest http://127.0.0.1:8765/api/health -Headers @{Origin='http://evil.example'} -UseBasicParsing
$r.Headers['Access-Control-Allow-Origin']; $r.Headers['Access-Control-Allow-Credentials']

# 6. Conteo de PDFs/ZIPs
(Get-ChildItem -Recurse -File -Include *.pdf,*.zip | Where-Object { $_.FullName -notmatch '\.venv' }).Count
```

**Nota:** la sonda 4 es de solo lectura. No ejecutes el `stop` con un `connector_id` manipulado: escribe JSON (probado en temporal, ver C4). No corras `pytest` si no quieres que el feed real gane otro post de prueba.

---

## Veredicto

**Demo de negocio, no negocio.** La fábrica de contenido existe y el dashboard es convincente; la tienda, la entrega, la medición y la seguridad no existen. El sistema sabe que no vende (PLAN 0/55) y la UI lo disimula. Hasta que los 52 archivos de pago dejen de ser públicos, exista un checkout real y los leads no se pierdan, cada nueva función es decoración.
