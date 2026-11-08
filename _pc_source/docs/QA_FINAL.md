# QA FINAL — Reverificación Independiente (MISIÓN 2)

**Fecha:** 2026-11-04, 22:03 (America/Bogota)
**Auditor:** agente `auditor` (task-4), independiente y read-only (solo escribió `docs/AUDITORIA_2026-11-04.md` y este archivo).
**Árbol:** commit `1a7a304` ("revision profunda 2026-11-04… 85 tests"), working tree **limpio** (`git status --short` = 0 líneas).
**Backend vivo:** `0.0.0.0:8765`, PID 19396 (`python -m uvicorn backend.main:app --host 0.0.0.0 --port 8765`). No lo reinicié ni lo detuve.
**Alcance:** gates técnicos + integración real de endpoints + sitio estático + datos. **No** se hicieron compras reales (no hay checkout configurado) ni se generaron imágenes Vertex pagadas.

---

## 1. Veredicto

> **TÉCNICAMENTE VERDE / PUBLICACIÓN NO APTA TODAVÍA.**
>
> Los gates técnicos auditables (G1–G13 y G18) pasan con evidencia (pytest 85/85, tsc/build limpios, 250 líneas, entregables 55/55, LAN, 404 honestos, sitio estático con 55 rutas + legales, higiene); seguridad PARCIAL documentada (G14).
> **La publicación sigue bloqueada por negocio, no por código:** `GET /api/publish/readiness` devuelve `ready:false` con `blockers:["checkout"]` porque **0/52 SKUs de pago tienen URL de Gumroad/Hotmart**, y la cola de Threads tiene **4 piezas** (por debajo del mínimo de 5–15/día de AGENTS). Sin checkout no hay compra; sin compra no se puede verificar la entrega post-pago.

| # | Gate | Resultado | Evidencia |
|---|---|---|---|
| G1 | `pytest tests -q` | **PASS** | `85 passed, 1 warning in 22.73s` |
| G2 | `npx tsc --noEmit` | **PASS** | `TSC_EXIT=0` (sin errores) |
| G3 | `npm run build` | **PASS** | `✓ built in 6.65s`, `index-DQ16QNjZ.css 107.71 kB`, `index-OqHvS6jI.js 401.83 kB`, `BUILD_EXIT=0` |
| G4 | Límite 250 líneas (.py/.ts/.tsx fuera de data/) | **PASS** | `VIOLACIONES >250: []`; máximo exacto 250 (`validate_deliverables.py`, `CheckoutLinksPanel.tsx`, `MetricsRadarView.tsx`) |
| G5 | Cero emojis en UI | **PASS** | `frontend/src` = 0 emojis pictográficos; `dist` 0 CDNs. Observación BAJA: `backend/services/social_feed_seed.py:39` conserva `👇` en una auto-respuesta (contenido de post, no chrome de UI) |
| G6 | `scripts/validate_deliverables.py` | **PASS** | `Validos: 55/55 · con avisos: 34`; `B01 hooks: 500 parseados, 0 duplicados exactos`; `VALIDATE_EXIT=0` |
| G7 | LAN real `192.0.2.1:8765` | **PASS** | `/api/health` → 200; `/store/` → 200 (36 745 B); `/api/publish/readiness` → 200 JSON |
| G8 | API inexistente → 404 JSON | **PASS** | `GET /api/noexiste` → 404 `{"detail":"Endpoint de API no encontrado: /api/noexiste"}` |
| G9 | `/store/` + 55 rutas | **PASS** | 200; 55 enlaces de producto únicos; 59 `index.html` de landings/legales; assets 55 covers; `/assets/index-*.css` 200 |
| G10 | Sitemap + legales | **PASS** | `sitemap.xml` XML válido con **60 `<loc>`** = 55 rutas + 4 legal + raíz `/`; 4 páginas legales (terminos/privacidad/reembolso/licencia); 0 landings sin enlaces legales; 0 recursos externos en 61 HTML |
| G11 | Entregable de pago desde LAN | **PASS** | `GET /deliverables/e01_maquina-silenciosa-pdf.html` desde `192.0.2.1` → **403**; `GET /deliverables/l01_...` → **200** (293 794 B) |
| G12 | `/store` no expone pagos | **PASS** | sólo copia `deliverables/l01..l03`; `/store/deliverables/e01...` → **404**; traversal (`../`, `..%2f`, `..%5c`) → 404; página de pago muestra "Checkout aún no configurado" (honesto) y **0** hrefs a `/deliverables` |
| G13 | Vertex nuevo + sin referencias activas viejas | **PASS con residuo BAJO** | `/api/health` → `REDACTED_EXAMPLE_PROJECT` / `global` / `gemini-3.1-flash-image` (fallback lite); conector `vertex_ai` CONECTADO con evidencia; `data/finops-ledger.json` = 1 imagen real, `$0.067`, modelo/proyecto nuevos; SKILL del proyecto y UI de Bait actualizados. **Residuo:** `scripts/probe_vertex.py:29,31` conserva la matriz histórica (`example-project-id`, `gemini-2.5-flash-image`) para `--all`; `backend/config.py:41` precio legacy; mock de test. Ninguna se usa en ejecución normal |
| G14 | Seguridad de escrituras en LAN | **PARCIAL (documentado)** | `RONIN_API_TOKEN` opcional: sin token, `POST` desde LAN llega al endpoint (422 de validación, no 401). Rate-limit 1/20 s en `test-all` y `vertex-generate`; guard 409 si hay imagen en curso (`backend/security_middleware.py`, `tests/test_security_middleware.py`). Documentado en `README.md:66-96` y `.env.example:26-27`. **Riesgo residual:** CORS `*` en preflight; `/customizations/connect`, `/customizations/secrets` y `DELETE /metrics/reset` sin rate-limit; sin token la LAN puede gastar saldo Vertex (~$0.067 cada 20 s por IP) |
| G15 | Publicación realmente lista (`readiness`) | **FAIL (bloqueo de negocio)** | `ready:false`, `blockers:["checkout"]`: 0/52 SKUs con checkout; `counts.checkout_ready=0`; 6/7 checks OK (deliverables, vertex, art, routes, content, site). `next_actions` lo dice explícitamente: crear 52 productos en Gumroad/Hotmart y pegar URLs |
| G16 | Cola de contenido publicable | **PARCIAL (limitación MEDIA)** | 4 Threads + 10 pines propios (12 con 2 benchmarks excluidos), todos `queued`, `published_to_network:false`. Limpieza de 50 posts de test del baseline **verificada y correcta**; quedan 4 piezas/día < mínimo AGENTS 5–15/día |
| G17 | Compra y entrega post-pago | **NO VERIFICABLE** | No hay checkout configurado; no se hizo compra real. Sin URL no se puede probar que el comprador reciba el HTML (riesgo A3 de la auditoría) |
| G18 | Higiene del repo | **PASS con residuales BAJOS** | root limpio (8 archivos esperados); duplicados/0-byte y backup de feeds en `data/_cuarentena/` con README; `scripts/_scratch_audit.py` y `data/_tmp_render.html` eliminados. **Residuales:** `data/deliverables_backup/` sigue trackeado sin documentar; `data/leads.json` (PII futura) y `data/finops-ledger.json` trackeados en git; `.gitignore` tiene `data/_cuarentena/` duplicado |
| G19 | Entorno Python oficial | **PARCIAL** | El proceso del backend corre con `...\Python312\python.exe` (global), no con `.venv\Scripts\python.exe` (regla AGENTS §2). `pytest` sí se ejecutó con el `.venv` oficial |

**Gates en verde:** 14 PASS (G1–G13 + G18; G13 con residuo BAJO) · 2 PARCIAL (G14 seguridad, G16 contenido) + 1 PARCIAL operativo (G19) · 1 FAIL de publicación (G15, negocio) · 1 no verificable (G17).

---

## 2. Evidencia literal por gate

### G1 — pytest
```
cd C:\Users\EXAMPLE\Documents\ronin_ventas
.\.venv\Scripts\python.exe -m pytest tests -q
........................................................................ [ 84%]
........................................................................ [100%]
85 passed, 1 warning in 22.73s
```
Warnings: sólo `StarletteDeprecationWarning` de `httpx` en `fastapi.testclient` (no fallo). 14 archivos de test, incluidos los nuevos `test_publish_readiness.py`, `test_checkout_links.py`, `test_backend_hardening.py`, `test_security_middleware.py`, `test_store_exposure.py`. La propia suite incluye `test_data_dir_not_mutated_by_suite` (hash de los JSON reales antes/después) y `test_strict_atomic_file_line_limit`.

### G2/G3 — frontend
```
cd frontend
npx tsc --noEmit        -> TSC_EXIT=0 (sin salida)
npm run build
dist/assets/index-DQ16QNjZ.css   107.71 kB │ gzip:  30.68 kB
dist/assets/index-OqHvS6jI.js    401.83 kB │ gzip: 114.10 kB
✓ built in 6.65s        -> BUILD_EXIT=0
```
`frontend/dist/index.html` no tiene `src/href` externos (fuentes empaquetadas; 0 CDNs). El backend sirve el SPA (`GET /` → 200) y el CSS hasheado (`GET /assets/index-DQ16QNjZ.css` → 200, 107 714 B).

### G4 — 250 líneas
```
VIOLACIONES >250: []
max files: 250 scripts/validate_deliverables.py
           250 frontend/src/components/publish/CheckoutLinksPanel.tsx
           250 frontend/src/components/metrics/MetricsRadarView.tsx
           246 backend/services/vertex_image_service.py
```
Excluidos `.venv/`, `node_modules/`, `__pycache__/`, `data/`, `.git/`. El límite es "no superar 250"; 250 exactas pasa.

### G5 — emojis
```
frontend/src: 0 emojis pictográficos (antes había ✓ en CatalogFactoryView y StanAndStealthView, ya retirados)
backend: 1 (social_feed_seed.py:39, 👇 dentro de una auto-respuesta de Threads)
data/deliverables: 0 emojis pictográficos; 40 HTML usan glifos tipográficos (→ 833, ✓ 50, ★ 22, ↘/↗…)
```
Interpretación: la UI de la app cumple cero emojis y el build no carga CDNs. El `👇` es texto de contenido (se renderiza en el clon); el estándar §4 apunta a la UI, así que se registra como observación BAJA, no como FAIL. Los glifos de los productos son tipografía de los entregables (la regla "cero emojis" del Grill #5 aplica a las réplicas visuales), no pictogramas.

### G6 — validación de entregables
```
.\.venv\Scripts\python.exe scripts\validate_deliverables.py
...
Validos: 55/55 · con avisos: 34
B01 hooks: 500 parseados, 0 duplicados exactos
VALIDATE_EXIT=0
```
Avisos de credibilidad (no fallos): menciones de `placeholder`/`{{ }}` en meta-prompts (L03 es esperado), pocas palabras en bóvedas de listas, y garantías/claims en contexto negado o citado. Detalle completo en `docs/GENERADORES_VALIDACION.md`.

### G7/G11 — LAN y control de acceso (desde `192.0.2.1`)
```
GET http://192.0.2.1:8765/api/health                  => 200 JSON
GET http://127.0.0.1:8765/api/health                     => 200 {"vertex":{REDACTED_EXAMPLE_PROJECT…,gemini-3.1-flash-image},"publish_site_ready":true,"frontend_built":true}
GET LAN /store/                                          => 200 (36 745 B)
GET LAN /api/publish/readiness                           => 200 JSON (1 868 B)
GET LAN /deliverables/l01_anatomia-post-418-usd.html     => 200 (293 794 B)
GET LAN /deliverables/e01_maquina-silenciosa-pdf.html    => 403 {"detail":"Este producto es de pago…"}
GET LOCAL /deliverables/e01_maquina-silenciosa-pdf.html  => 200 (141 484 B, owner local)
```

### G8 — 404 honesto de API
```
GET /api/noexiste => 404
{"detail":"Endpoint de API no encontrado: /api/noexiste"}
```
`main.py:132-135` captura `/api/{path:path}` antes del SPA catch-all. Cabeceras de seguridad presentes: `Content-Security-Policy` (sin CDNs, `default-src 'self'`), `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`, `X-Frame-Options: SAMEORIGIN`, `Permissions-Policy`.

### G9/G10/G12 — sitio estático
```
data/publish_site/manifest.json: skus=55, paid_skus=52, lead_magnets=3, routes=55, files=138, checkout_ready=0
/store/ => 200; 55 enlaces de producto únicos; 59 index.html (55 rutas + 4 legales)
legal: tienda enlaza legal/terminos|privacidad|reembolso|licencia/ (4/4 resuelven)
55/55 landings enlazan legal; 0 enlaces legales rotos; 0 recursos externos (61 HTML escaneados)
sitemap.xml: XML válido, 60 <loc> = 55 puente + 4 legal + raíz /
robots.txt presente; 404.html presente; assets/covers = 55 webp
/store/deliverables/l01..l03 => 200; /store/deliverables/e01_maquina-silenciosa-pdf.html => 404
traversal: /store/../deliverables/e01…, /store/..%2f…, /store/..%5c… => 404
landing de pago: "Checkout aún no configurado", 0 hrefs a /deliverables
landing gratis: link relativo ../../deliverables/l02_27-hooks-prohibidos.html
```

### G13 — Vertex
```
/api/health.vertex = {project_id: REDACTED_EXAMPLE_PROJECT, location: global,
                      model: gemini-3.1-flash-image, fallback_model: gemini-3.1-flash-lite-image,
                      adc_present: true}
/api/customizations → conector vertex_ai: CONECTADO, detail "Vertex AI Nano Banana 2 operativo (imagen nb2_… generada y validada)"
data/finops-ledger.json: {project_id: REDACTED_EXAMPLE_PROJECT…, total_spent_usd: 0.067, images: 1,
                          entries:[{model: gemini-3.1-flash-image, cost_usd: 0.067, at: 2026-11-05T02:36:55Z}]}
grep árbol activo: sin referencias a example-project-id / gemini-2.5-flash-image en config/UI/SKILL
residual: scripts/probe_vertex.py:29,31 (matriz --all), backend/config.py:41 (precio legacy), test mock
```

### G14 — seguridad (PARCIAL documentado)
```
Preflight CORS desde Origin: https://evil.example => 200, access-control-allow-origin: *
LAN POST /api/catalog/E01/checkout con gumroad_url "http://..." => 422 (validación https), NO 401
LAN POST /api/publish/mark status inválido => 422, NO 401
=> RONIN_API_TOKEN no está definido en el proceso actual: la LAN puede escribir (por diseño)
```
Documentado en `README.md` §"Seguridad de la red local" y `.env.example`. `backend/security_middleware.py`: token opcional + rate-limit 1/20 s por cliente en `test-all` y `vertex-generate` + guard 409 si hay generación Vertex en curso; cubierto por `tests/test_security_middleware.py` (3 tests). **Sin token no hay autenticación real:** el dueño debe definirlo si el Wi-Fi no es de confianza. El CORS `*` sigue abierto (mitigado porque no hay credenciales y por la Private Network Access de Chrome, pero es residual).

### G15/G16 — readiness y contenido (lo que bloquea publicar)
```
GET /api/publish/readiness:
  ready: false
  blockers: ["checkout"]
  counts: {skus:55, paid:52, leads:3, checkouts:0, checkouts_gumroad:0, checkouts_hotmart:0,
           skus_missing_checkout:52, threads:4, pins:10, art_covers:55, deliverables:55}
  checks OK: deliverables 55/55 · vertex · art 55/55 · routes 55 · content 4 threads + 10 pines · site manifest
  check BLOCK: checkout 0/52
  next_actions[0]: "Crear los 52 productos en Gumroad (USD / Apple Pay) y Hotmart (COP / Nequi / PSE / Efecty)
                    y pegar cada URL de checkout en Publish Center (POST /api/catalog/checkout-bulk). Faltan 52 SKUs."
```
`GET /api/publish/kit?platform=threads` → 4 items, `published_to_network:false`, nota "el sistema NO publica en Threads ni Pinterest".
`GET /api/publish/kit?platform=pinterest` → 10 items propios (benchmarks excluidos), `image_url` absoluto con el host de la petición.
`GET /api/catalog` → 55 SKUs (52 pago + 3 lead), 55 rutas únicas, `checkout_ready_count: 0`.
**Contexto de la limpieza de feeds (verificado por el Lead con `git show HEAD`):** el baseline tenía 55 posts, de los cuales 50 eran idénticos de test ("Prueba de inyección…") + 5 reales; la reducción a 4 es correcta, está respaldada en `data/_cuarentena/social_feeds_20261104_214653.json.bak` y no es un FAIL de datos. Sí es una **limitación MEDIA de inventario** (4 piezas < mínimo 5–15/día).

### G18/G19 — higiene y entorno
```
git log -1: 1a7a304 revision profunda 2026-11-04…
git status --short: 0 líneas (árbol limpio)
root: .env.example, .gitignore, AGENTS.md, desktop_launcher.py, README.md, requirements.txt, start_ronin_os.bat
data/_cuarentena/: a01 (dup exacto), b01 (versión vieja, no dup), e01 (dup exacto), l02 (0 B), README.md, social_feeds_20261104_214653.json.bak
residual: data/deliverables_backup/ trackeado; data/leads.json, metrics_real.json, social_feeds.json, finops-ledger.json trackeados
server: ...\Python312\python.exe -m uvicorn (no .venv) → desviación operativa de AGENTS §2
```

---

## 3. Hallazgos residuales (no bloquean el código, sí la operación)

| ID | Severidad | Hallazgo | Fix recomendado |
|---|---|---|---|
| Q1 | **BLOQUEO de negocio (CRÍTICO para publicar)** | 0/52 SKUs con checkout (`readiness.ready=false`). Sin URL de Gumroad/Hotmart no hay forma de cobrar; las landings honestamente dicen "Checkout aún no configurado" | Crear los 52 productos (o al menos el set de lanzamiento) y pegar URLs vía `POST /api/catalog/checkout-bulk` / Publish Center; hacer 1 compra de prueba por pasarela |
| Q2 | **MEDIA (contenido)** | 4 piezas de Threads + 10 pines propios < 5–15 piezas/día de AGENTS | Generar/sembrar al menos 5–15 piezas diarias (una por SKU) reutilizando `build_default_threads_posts` como base, y re-exportar el sitio |
| Q3 | **MEDIA (operación)** | `RONIN_API_TOKEN` opcional: sin definir, la LAN puede escribir y gastar Vertex ($0.067/20 s por cliente por rate-limit) | Definir token en el `.bat`/PowerShell del dueño o restringir escrituras a owner cuando no haya token; documentar en el runbook del día de publicación |
| Q4 | **MEDIA (seguridad)** | CORS `allow_origins=["*"]` en preflight | Restringir a `http://127.0.0.1:8765`, `http://localhost:8765` y `http://<LAN_IP>:8765` |
| Q5 | **MEDIA (legal/UX)** | Las landings **dinámicas** (`/blueprint/<slug>` servidas por FastAPI) no enlazan legales; solo las estáticas de `/store` | Pasar `legal_root="/store/legal"` (o equivalente) en `api_bridge.py` cuando exista el sitio |
| Q6 | **MEDIA (privacidad/ops)** | `data/leads.json` (emails), `metrics_real.json`, `social_feeds.json` y `finops-ledger.json` están trackeados en git | Mover leads/finops a `.gitignore` o a `data/local/`; hoy están vacíos pero con leads reales se commitearán PII |
| Q7 | **MEDIA (entrega)** | No verificable la entrega post-pago (sin checkout). `/deliverables/<pago>` sólo se sirve a localhost | Definir el mecanismo de entrega (subir HTML a Gumroad/Hotmart o token firmado) y probarlo con una compra real |
| Q8 | **BAJA (entorno)** | Backend vivo con Python global `Python312` en vez del `.venv` oficial | Arrancar siempre con `start_ronin_os.bat` (que usa `.venv`) y documentarlo |
| Q9 | **BAJA (limpieza)** | `data/deliverables_backup/` (8 archivos) trackeado sin documentación; `.gitignore` con `data/_cuarentena/` duplicado | Documentar/eliminar el backup y limpiar el `.gitignore` |
| Q10 | **BAJA (residuo Vertex)** | `scripts/probe_vertex.py --all` conserva la matriz histórica con `example-project-id` / `gemini-2.5-flash-image`; `config.py:41` precio legacy | Marcar la matriz como "histórica/no usar" o eliminarla; conservar el precio legacy sólo si se usa |
| Q11 | **BAJA (contenido)** | `social_feed_seed.py:39` conserva `👇` en una auto-respuesta | Sustituir por texto sin emoji si se aplica el estándar §4 también al contenido |
| Q12 | **BAJA (estética/copy)** | 40 entregables usan glifos tipográficos (→, ✓, ★). No son emojis pictográficos, pero si el Grill #5 exige cero glifos en réplicas, hay que decidirlo | Criterio explícito: tipografía permitida en producto, no en chrome de UI |

---

## 4. Qué falta exactamente para decir "PUBLICABLE" (orden)

1. **Checkout (Q1):** crear los 52 productos en Gumroad/Hotmart y cargar URLs (`checkout-bulk`). Gate: `readiness.ready == true`.
2. **Contenido (Q2):** cola ≥5–15/día por red; re-exportar `publish_site` y revisar `content/threads.json`/`content/pinterest.json`.
3. **Compra + entrega (Q7):** 1 compra de prueba real por pasarela y verificar que el comprador recibe el archivo correcto (Gumroad/Hotmart entregan por su plataforma o se define token de descarga).
4. **Operación (Q3):** decidir el modo de red del día (token definido o Wi-Fi de confianza) y anotarlo.
5. **Deploy:** `scripts/deploy_store.ps1 -Confirm` con `--base-url` real (el sitio actual se generó con `base_url=""`; canonical/OG quedan relativos y el sitemap usa `/`). Regenerar con el dominio final antes de subir.
6. Re-ejecutar este QA (6 gates críticos: readiness, pytest, build, `/store`, 403 de pago, LAN) tras 1–3.

---

## 5. Nota de independencia

- No modifiqué código, datos ni configuración. Sólo escribí `docs/AUDITORIA_2026-11-04.md` y este `docs/QA_FINAL.md`.
- No reinicié el backend del Lead (PID 19396 sigue en `0.0.0.0:8765`). No ejecuté `POST /api/publish/export-site`, ni compras, ni generación Vertex pagada.
- La verificación se hizo sobre el commit `1a7a304` con working tree limpio. Cualquier cambio posterior requiere re-verificación de los gates afectados.
- El fallo de pytest de la MISIÓN 1 (`product_templates_elite.py` 399 líneas) quedó resuelto en el commit final: el archivo está dividido y el tree <250; hoy `pytest` está 85/85.
