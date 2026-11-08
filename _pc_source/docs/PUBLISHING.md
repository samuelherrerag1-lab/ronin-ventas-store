# Publicación real en Threads y Pinterest (Chrome persistente)

Este módulo publica desde la UI web real de `threads.net` y `pinterest.com` con
una sesión de Chrome persistente. No usa APIs no oficiales ni cookies a mano:
abre Chrome con perfil en disco, rellena el compositor/pin builder como un
humano y mide la URL del post/pin antes de declarar éxito.

**Regla de honestidad:** sin login medido el job falla con `login_required` y el
paso exacto para resolverlo. El modo seco (`dry_run=true`) es el valor por
defecto: navega, rellena y captura screenshot, pero nunca pulsa Publicar.

## 1. Montaje en `backend/main.py` (lo hace el Lead, no este módulo)

```python
from backend.routers.api_social_publish import router as social_publish_router

app.include_router(social_publish_router)
```

El router se sirve bajo el prefijo `/api/social`. Requiere `playwright==1.56`
(ya instalado) y Chrome instalado (`channel="chrome"`).

## 2. Login humano UNA vez

Opción A (recomendada): una sola ventana con una pestaña por plataforma.

```powershell
curl.exe -X POST http://127.0.0.1:8765/api/social/login/all `
  -H "Content-Type: application/json" -d "{\"timeout_s\":3600}"
```

Abre Chrome persistente con `https://www.threads.net/login` y
`https://www.pinterest.com/login` en dos pestañas. Inicia sesión en cada una: el
flujo sondea cada 3 s, guarda la sesión medida (URL, avatar/compositor,
screenshot, `account_label`) en `data/publish_jobs/sessions.json`, escribe el
estado del flujo en `data/publish_jobs/login_flow.json` y cierra la ventana
cuando detecta ambas sesiones (o al agotar el timeout). No cierres la ventana a
mano.

Opción B: una plataforma a la vez.

```powershell
# 1) Abre la ventana persistente en la pantalla de login de la plataforma
curl.exe -X POST http://127.0.0.1:8765/api/social/login/threads
curl.exe -X POST http://127.0.0.1:8765/api/social/login/pinterest

# 2) Inicia sesión TÚ en la ventana de Chrome que se abre.
#    El keeper sondea la página cada 3 s y, cuando detecta la sesión, la guarda
#    como estado medido y cierra la ventana. No cierres la ventana a mano.

# 3) Comprueba el estado honesto (sin abrir Chrome)
curl.exe http://127.0.0.1:8765/api/social/session/threads

# 4) Verificación profunda (abre Chrome y mide ahora)
curl.exe -X POST http://127.0.0.1:8765/api/social/session/threads/verify
```

Estado guardado en `data/publish_jobs/sessions.json`:
`{logged_in, status, account_label, evidence, checked_at, screenshot, stale}`.
`evidence` es literal (URL + selectores observados). Nunca se marca conectado
por configuración ni por cookies sin medir.

### Coordinación del perfil `data/chrome_vault`

- Si existe `data/_locks/chrome_vault.owner`, el publicador **no abre** el perfil
  y responde `409` explicando quién lo tiene. Es protección contra corrupción.
- Para desarrollo/pruebas, usa un perfil aparte:

```powershell
$env:RONIN_SOCIAL_PROFILE_DIR = "data/chrome_vault_test"
$env:RONIN_SOCIAL_CHANNEL = "chrome"   # o "chromium" para el bundled de Playwright
```

## 3. Publicar: modo seco y publicación real

```powershell
# Modo seco (por defecto si se omite dry_run): navega, rellena, captura
curl.exe -X POST http://127.0.0.1:8765/api/social/publish `
  -H "Content-Type: application/json" `
  -d "{\"platform\":\"threads\",\"ids\":[\"th_001\"],\"dry_run\":true}"

# Publicación real (solo desde acción explícita "Publicar ahora")
curl.exe -X POST http://127.0.0.1:8765/api/social/publish `
  -H "Content-Type: application/json" `
  -d "{\"platform\":\"threads\",\"ids\":[\"th_001\"],\"dry_run\":false}"

# Progreso del job
curl.exe http://127.0.0.1:8765/api/social/jobs/<job_id>
```

Cada job se guarda en `data/publish_jobs/<job_id>.json` con: petición, pasos,
estado de sesión medido, piezas (`queued`/`running`/`dry_run_ok`/`published`/
`published_unverified`/`failed`), URL del post/pin, errores literales,
screenshots y confirmación. Los screenshots viven en
`data/publish_jobs/evidence/` y se sirven por
`GET /api/social/jobs/{job_id}/evidence/{filename}`.

Una pieza solo es `published` si el publicador midió la URL del post/pin. Si se
pulsó Publicar pero no hubo confirmación medible, la pieza es `failed`; si hubo
texto de éxito pero no URL, queda `published_unverified` (sin inventar enlace).

## 4. Endpoints

| Método | Ruta | Uso |
| --- | --- | --- |
| GET | `/api/social/status` | Perfil, sesiones, login (simple y multi-pestaña), scheduler, jobs |
| POST | `/api/social/login/all` | UNA ventana con dos pestañas y espera de login humano |
| POST | `/api/social/login/{platform}` | Abre ventana de login humano una vez |
| GET | `/api/social/session/{platform}?verify=true` | Estado medido (opcionalmente re-medir) |
| POST | `/api/social/session/{platform}/verify` | Medición real ahora |
| GET | `/api/social/queue?platform=threads` | Piezas de la cola real con estado |
| POST | `/api/social/publish` | Crea job (`dry_run` por defecto true) |
| GET | `/api/social/jobs` | Últimos jobs |
| GET | `/api/social/jobs/{job_id}` | Detalle completo y evidencia |
| GET | `/api/social/jobs/{job_id}/evidence/{filename}` | Screenshot de evidencia |
| GET/POST | `/api/social/schedule` | Ver/editar programación |
| POST | `/api/social/schedule/tick` | Ejecutar un tick manual |
| POST | `/api/social/scheduler/start` | Arrancar el hilo daemon |

## 5. Selectores usados (con fallbacks)

Threads: el compositor se abre por la ruta real `/intent/post?text=<urlencoded>`
(medida el 2026-11-04: muestra `div[contenteditable='true']` e
`input[type='file']`), que no depende del botón del feed. Si esa ruta falla,
fallback al botón del feed (`[role='button'][aria-label*='Escribe para crear']`,
`[aria-label*='Nuevo hilo']`). La publicación se confirma cuando el compositor se
cierra o aparece texto de éxito, y la URL solo se acepta si pertenece a
`/@<cuenta_propia>/post/<id>` y al abrirla el cuerpo contiene el texto publicado
(este chequeo se añadió tras detectar que un selector del feed devolvía el post
de otra cuenta). Botón de publicar: `get_by_role("button", name=/^(publicar|post)$/i)`
con fallback CSS.

Pinterest: el creador orgánico real es
`https://www.pinterest.com/pin-creation-tool/` (no `pin-builder`, que abre el
creador de anuncios). La primera vez aparece un tutorial de 4 pasos que se
cierra con "Siguiente". Se sube la imagen normalizada a 1000x1500 (Pillow, sin
deformar), título `input[placeholder*='Explica en qué consiste' i]`,
descripción `div[contenteditable='true'][aria-label*='Describe tu Pin' i]`,
link `input[type='url']`, tablero
`[data-test-id='board-dropdown-select-button']` (deshabilitado hasta subir la
imagen; si el tablero no existe se crea con el diálogo
`[data-test-id='board-form-submit-button']` y se verifica que el botón muestre
el nombre). Publicar: `get_by_role("button", name=/^publicar$/i)`. La URL del pin
se acepta solo si al abrirla contiene el título/descripción publicados.

**Links de pin:** `RONIN_PUBLIC_BASE_URL` (o el `base_url` del manifest del
sitio) debe ser un dominio PÚBLICO. Pinterest rechaza `localhost` e IP privadas
(mensaje real: "¡Vaya! Esa URL no es válida"), así que sin dominio público el
pin se publica SIN link y el job lo deja anotado. Cuando exista dominio, se
publica/edita el pin con el link a la ruta puente.

## 6. Programación (N piezas/día) y auto-respuestas

Configuración en `data/publish_jobs/schedule.json` (modo seco por defecto):

```powershell
curl.exe -X POST http://127.0.0.1:8765/api/social/schedule `
  -H "Content-Type: application/json" `
  -d "{\"enabled\":true,\"dry_run\":true,\"threads_per_day\":5,\"pinterest_per_day\":5,\"times_local\":[\"09:00\",\"13:00\",\"18:00\"]}"
```

El hilo daemon (cada 120 s, `RONIN_SOCIAL_TICK_S`) ejecuta como máximo una
franja por día y no duplica piezas ya publicadas (índice
`data/publish_jobs/published_index.json`). En pytest o con
`RONIN_SOCIAL_SCHEDULER=0` el hilo no arranca.

Tras publicar de verdad un post de Threads, se encolan sus 2 auto-respuestas
(`data/publish_jobs/reply_queue.json`) con vencimiento a 7 y 26 minutos
(`RONIN_SOCIAL_REPLY_DELAYS_MIN`). El scheduler las publica cuando vencen, con
máximo 3 intentos y error literal guardado.

## 7. Pausas humanas, captcha y bloqueos

- Entre piezas reales hay pausas de 20-60 s (`RONIN_SOCIAL_MIN_DELAY` /
  `RONIN_SOCIAL_MAX_DELAY`). En modo seco no se aplican.
- Antes de publicar se busca texto de captcha/checkpoint en la página; si
  aparece, el job falla con `bloqueado: ...` y screenshot.
- Un solo Chrome automatizado a la vez (lock interno): login y publicación no se
  pisan; si está ocupado responde `409`.

## 8. Panel de control (frontend)

`frontend/src/components/publish/AutoPublishPanel.tsx` (dentro del Publish
Center) muestra: estado de sesión por plataforma, botón "Abrir login",
"Verificar", selector de piezas, modo "Probar en seco" / "Publicar ahora" (doble
pulsación explícita), progreso en vivo, enlaces a los posts y errores literales.
Sin router montado, el panel muestra "Pendiente en backend" (no se rompe).

## 9. Tests

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_social_publisher.py -q
```

15 tests con Playwright mockeado (sin abrir navegador): detección de login y
captcha, honestidad de `login_required`, modo seco sin clic en Publicar,
publicación real con URL + auto-respuestas, fallo literal por pieza,
persistencia de jobs/evidencia, validación e idempotencia del scheduler, cola de
respuestas y normalización 1000x1500 del pin.

## 10. Estado actual verificado (2026-11-04 23:10-23:29 America/Bogota)

Sesiones medidas y guardadas en `data/publish_jobs/sessions.json`:

- Threads: `logged_in=true`, cuenta `ronoverthinks`, evidencia
  `URL=https://www.threads.com/ · a[href^='/@'] · [aria-label*='Crear']`,
  screenshot `data/publish_jobs/evidence/session_threads_20261104_232938.png`.
- Pinterest: `logged_in=true`, cuenta `ronOverthinks`, evidencia
  `URL=https://www.pinterest.com/business/hub/ · [data-test-id='header-profile']`,
  screenshot `data/publish_jobs/evidence/session_pinterest_20261104_232949.png`.

Publicaciones REALES verificadas abriendo la URL y comparando contenido:

- Threads `th_001` (SKU E01): https://www.threads.com/@ronoverthinks/post/DfWJECeFZeS
  · job `job_20261104_231000_4513c0` · 2026-11-05T04:10:31Z ·
  screenshot `..._th_001_publicado_20261104_231030.png` (toast "Publicado").
- Pinterest `pin_001` (SKU E01): https://www.pinterest.com/pin/1106618939723059213/
  · job `job_20261104_232721_0bd400` · 2026-11-05T04:28:20Z · título
  "Cómo Crear y Vender Productos Digitales en Automático (Sistema PDF Sin Cara)"
  · tablero "Ingresos Digitales & Sistemas Faceless" · **sin link de destino**:
  no hay dominio público todavía y Pinterest rechazó la URL LAN. Se editará con
  el link a `/blueprint/maquina-silenciosa-pdf` cuando el sitio esté desplegado.

Auto-respuestas de `th_001`: 2 pendientes en
`data/publish_jobs/reply_queue.json` (`due_at` 04:17:31Z y 04:36:31Z) con la URL
real del post. El hilo del scheduler no está corriendo porque el router aún no
está montado en `main.py` y no hay proceso daemon; por eso siguen `pending`
(sin inventar publicación). Al montar el router, `POST /api/social/schedule`
con `enabled=true` las publica al vencer (máx. 3 intentos, error literal).
