# Plan de Conversión a Sistema Funcional — Ronin Ventas OS

**Versión:** 2 · 03/11/2026
**Alcance:** pasar de "demo que aparenta funcionar" a "sistema que produce ingresos".
**Regla:** cada fase termina con evidencia verificable. Nada se declara listo sin prueba.

---

## 0. Baseline medido

| Métrica | Valor real |
|---|---|
| Entregables en disco | 55/55, 0 faltantes |
| Palabras visibles totales | 514.562 (promedio 9.355) |
| Entregables con export PDF | 21/55 |
| Tests | 28/28 verde (entorno propio `.venv`) |
| Archivos >250 líneas | 0 |
| Cuentas realmente conectadas | **0** |
| Cookies en Chrome Vault | Solo `gumroad.com`, sin verificar validez |
| Rutas puente servidas | **0 de 55** |
| Checkout configurado | **0 de 55** |
| Publicación real | **0** |

---

## Fase 0 — Entorno aislado ✅

- `.venv` propio en `ronin_ventas`, `requirements.txt` con versiones fijas.
- `start_ronin_os.bat` usa el venv local.
- `AGENTS.md` corregido: prohibido depender del venv de otro proyecto.
- `tests/conftest.py` aísla `data/`: ningún test vuelve a sembrar estado falso.

---

## Fase 1 — Honestidad de estado ✅

- Estado sembrado purgado (`data/customizations_state.json` limpio).
- `connect` dejó de devolver `"connected"`: ahora `browser_opened` / `chrome_not_found` / `launch_failed` / `not_requested`.
- Eliminados `liarjs_target_score: 96`, `ua_rotation_disabled`, `webgl_gpu_consistent`, `worker_thread_consistent` y las barras 98/96/100/94.
- Nuevo `vault_inspector.py`: reporta cookies legibles, dominios reales y si Playwright existe.
- Diagnóstico descarta resultados sembrados (`mock_id`, `Mock Connector`, `detail: "OK"`).
- `metrics_real.json` en cero.
- `tests/test_honesty.py`: 6 guardarraíles.
- **Resultado en vivo:** 8 conectores en `SIN_VERIFICAR`. Fingerprint `null`. Cero verde falso.

---

## Fase 2 — Cuentas y conectores reales

### 2.1 Lo que solo puedes hacer tú (barrera legal, no técnica)

| Cuenta | Requisito | Por qué no puedo hacerlo yo |
|---|---|---|
| Gumroad | Crear cuenta + datos fiscales | Verificación de identidad |
| Hotmart | Cuenta de productor + KYC + datos bancarios | Verificación de identidad y contrato |
| Pinterest Business | Cuenta + sitio verificado | Propiedad del dominio |
| Threads | Cuenta @ronoverthinks | Propiedad de la cuenta |

Yo automatizo todo lo que ocurre **después** del primer inicio de sesión.

### 2.2 Verificación real de sesión

| Archivo | Cambio |
|---|---|
| `backend/services/session_probes.py` *(nuevo)* | Playwright con `channel="chrome"` + `user_data_dir=CHROME_VAULT_DIR`. Busca un marcador de sesión autenticada y devuelve la evidencia literal. |
| `backend/services/probe_runners.py` | `test_social_domain` pasa de "red alcanzable" a "sesión verificada". Sin marcador → `SIN_VERIFICAR`, nunca verde. |
| `backend/routers/api_customizations.py` | `/connect/{id}` abre login, devuelve `awaiting_login`; la UI hace polling de `/test/{id}`. |
| `frontend/.../HubConnectorDeck.tsx` | Botón "Abrir login y verificar", estado en vivo, evidencia y hora. |

**Marcadores por conector:**

| Conector | Marcador de CONECTADO |
|---|---|
| Google Master | Avatar de cuenta en `accounts.google.com` |
| Threads | `a[href="/settings"]` y ausencia de formulario de login |
| Pinterest | `[data-test-id="header-profile"]` |
| Gumroad | `a[href*="/products"]` + cookie `_gumroad_app_session` válida |
| Hotmart | `[data-testid="user-menu"]` |
| GitHub | `gh auth status` con exit 0 |
| Vertex AI | Generación real validada (ya funciona) |
| OpenCode V2 | `GET /api/session` con sesión canónica (ya funciona) |

**Criterio de aceptación:** cada conector solo puede pintar verde con marcador encontrado. Hoy: 2 verdes reales (Vertex, OpenCode), 1 dudoso (GitHub vía CLI), 5 grises.

### 2.3 Estado de la Fase 2

Implementado y probado:

| Pieza | Archivo | Estado |
|---|---|---|
| Trabajador de conexión en proceso aparte | `backend/services/connect_worker.py` | ✅ abre Chrome con el vault y detecta login en ~4 s |
| Gestión de trabajos y secretos | `backend/services/connect_jobs.py` | ✅ estados, PID, parada, secretos enmascarados |
| Endpoints | `/connect/{id}`, `/connect/{id}/status`, `/connect/{id}/stop`, `/secrets` | ✅ 4 tests |
| UI de progreso real | `useConnectorJobs.ts` + `HubConnectorDeck.tsx` | ✅ polling cada 2 s, sin progreso simulado |
| Extracción de token Gumroad | `connect_worker._harvest_gumroad` | ✅ busca candidatos y valida contra `GET /v2/user` |

**Decisión pendiente del usuario:** dominio público. Sin dominio se puede operar con subdominio gratuito (Cloudflare Pages o GitHub Pages). El checkout de Gumroad/Hotmart no lo necesita.

---

## Fase 3 — Tienda automatizada, afiliados y SEO

### 3.1 Creación de productos

| Plataforma | Vía | Requisito |
|---|---|---|
| Gumroad | **API v2** (`POST /v2/products`) con token personal | Token en `.env` (`GUMROAD_TOKEN`) |
| Hotmart | **Playwright** sobre el panel (no hay API pública de productos) | Sesión activa en el vault |

`backend/services/store_publisher.py` *(≤250 líneas)*:
- Crea/actualiza el producto con título, descripción, precio, moneda y portada.
- Sube el archivo entregable como contenido descargable.
- Devuelve la URL pública del checkout y la guarda en `catalog.json`.
- Modo `--dry-run` obligatorio antes de escribir nada.

### 3.2 Afiliados

| Plataforma | Mecánica | Comisión propuesta |
|---|---|---|
| Hotmart | Programa de afiliados nativo por producto | 40–50% digital |
| Gumroad | "Affiliates" por producto | 30–40% |

Reglas: comisión solo sobre ventas netas, cookie de atribución de 30–60 días, material creativo listo (pines + hilos + swipe copy) para que el afiliado no invente.

### 3.3 SEO real

- Cada producto tiene landing indexable con `schema.org/Product` + `Offer`, `canonical`, OG y meta description.
- Pinterest: keyword en título, descripción y nombre del tablero; 1000×1500; URL única por pieza.
- Threads: keyword en la primera línea; sin reciclar URL en <72h.
- `sitemap.xml` y `robots.txt` generados por el propio backend.

**Criterio de aceptación:** producto creado en Gumroad devuelve URL de checkout real; `catalog.json` la contiene; la landing la usa.

---

## Fase 4 — Auditoría cínica y mejora profunda de los 5

### Selección confirmada

| Rol | SKU | Producto | Precio |
|---|---|---|---|
| Gratis | **L01** | El Desglose del Experimento de $418.50 | $0 |
| Entrada | **B01** | Bóveda de 500 Hooks Cínicos | $19 |
| Core Threads | **E03** | Threads: El Algoritmo de la Polarización | $29 |
| Core Pinterest | **E02** | Pinterest: El Cajero Oculto | $29 |
| Motor 1ª hora | **B09** | Bóveda de 200 Auto-Respuestas | $27 |

### 4.1 Auditoría (en curso)
Crítico Cínico independiente lee los 5 archivos y produce `docs/CRITIQUE_LAUNCH_SET.md`:
por qué no compraría cada uno, defectos técnicos verificables, puntuación por eje y top 5 de mejoras por impacto en ventas.

### 4.2 Mejora

**Estándar de extensión: mínimo 20.000 palabras reales por producto.** No 12.000.
Un producto de 20.000 palabras es un libro corto: solo se sostiene con estructura
real (frameworks, guiones, tablas, ejercicios, criterios de decisión), nunca con
relleno. Cada entrega se audita por palabras visibles y por densidad útil.

- Export PDF verificado en los 5.
- Portada propia dentro del producto + tarjeta social 1200×630 + pin 1000×1500.
- Bloque de Order Bump y CTA de puente.
- B09: añadir estructura `<h2>` y print (ya supera 20k).
- B01: capa estática imprimible sobre el array JS.
- L01: captura de email real (hecho) y calculadora multi-variable.
- E03/E02: pasar de 14.8k/10k a 20k+ con capítulos nuevos, no con párrafos estirados.

**Criterio de aceptación:** `scripts/audit_launch_set.py` valida palabras, print, portada, pin, checkout y JS en los 5.

### 4.3 Estado de la Fase 4

Crítica recibida en `docs/CRITIQUE_LAUNCH_SET.md` (8.492 palabras). Puntajes: E03 63 · E02 56 · B09 45 · L01 43 · B01 41.

**Verificado y corregido (lote 1):**

| Producto | Corrección | Evidencia |
|---|---|---|
| B01 | `130` → `500` en título, hero, dossier y footer | 4 reemplazos; el array tiene 500 hooks con id |
| B01 | 49 × "(Evidencia comprobada en Stripe)" → "(cifra ilustrativa: valídala antes de publicar)" | 49 reemplazos |
| E03 | Precio de portada, chip, footer y 6 CTAs: `$17` → `$29` | `$29` en 9 puntos; resto son escenarios modelados |
| E02 | Chip de portada y 2 filas "Este ebook": `$19` → `$29` | El `$19` restante es el producto de ejemplo "Caja Mínima" |
| L01 | CSS de impresión reescrito: fondo blanco, texto `#111`, mockup e interactivos ocultos | PDF real de 16 páginas, legible; antes 14 con bloques negros |
| L01 | Promesa de portada ya no fija "18 páginas" | Dice "expediente imprimible" |
| L01 | Captura de email real: `POST /api/leads` + deduplicación + fallback offline honesto | Probado E2E: correo queda en `data/leads.json`; 3 tests nuevos |

**Pendiente del lote 2:**

| Producto | Pendiente | Bloqueo |
|---|---|---|
| L01 | CTA muerto (`/sistema/...`) | Depende de Fase 5 (rutas puente) |
| L01 | La "prueba" es una recreación CSS | Decisión de contenido: reencuadrar o captura real |
| B01 | 370 hooks son plantilla con el nicho cambiado | Trabajo de redacción |
| B01 | Capa estática imprimible | Trabajo de maquetación |
| B09 | 0 export PDF, 1 solo `<h2>` | Trabajo de maquetación |
| B09 | Scripts con testimonios en primera persona y variantes contradictorias | Trabajo de redacción |

---

## Fase 5 — Puente y checkout

`backend/routers/api_bridge.py` + `backend/services/landing_renderer.py` (ambos ≤250 líneas).

- Sirven `/blueprint/…`, `/boveda/…`, `/app/…`, `/sistema/…`, `/vault/…`, `/gratis/…` con landing server-rendered.
- Solo las 5 rutas de lanzamiento quedan activas; las otras 50 devuelven "próximamente" con 404 honesto.
- Order Bump, UTM y regla de rotación de 72h.

**Criterio de aceptación:** ninguna ruta puente devuelve el HTML del dashboard; cada una tiene precio, checkout y bump.

### Estado de la Fase 5

✅ Las 55 rutas puente sirven landing propia (`backend/routers/api_bridge.py` + `landing_renderer.py`).
✅ Cada landing incluye precio, qué incluye, ángulo, order bump y `schema.org/Product`.
✅ Si el SKU no tiene URL de checkout, la landing muestra "Checkout aún no configurado" en vez de un botón falso.
✅ Un prefijo incorrecto devuelve 404 (no se duplican landings).
⏳ Falta rellenar `gumroad_url` / `hotmart_url` cuando existan los productos.

---

## Fase 5.5 — Estándar visual iPhone 17.5 (v2) ✅ backend

Reconstruido midiendo capturas reales de iPhone 15 Pro (738×1600 escaladas a 393×852 pt).

| Elemento | Medida de referencia | Implementado |
|---|---|---|
| Reloj | ~73% del ancho de pantalla | `114px`, `-3.6px`, `tnum` |
| Fecha / now playing | y≈106 pt, 15.5px | `.now-line` con icono de reproducción |
| Barra de estado | 54 pt, batería con porcentaje dentro | SVG señal + wifi + batería numérica |
| Notificación | icono 34, título bold, hora a la derecha, cuerpo 2 líneas | anatomía corregida |
| Tarjetas | 361px, radio 22, blur 34 | ✅ |
| Acciones | círculos 72px | ✅ |
| Fondo | intercambiable, con grano | incrustado en base64 (no falla nunca) |

Pendiente: replicar el mismo estándar en `IosBaitFrame.tsx` (vista previa React) y en el teléfono embebido de L01.

---

## Fase 5.6 — Módulo de Identidad de Marca

Objetivo: una sola fuente de verdad para la imagen de marca y su distribución.

1. **Avatar canónico:** subir o generar, recorte circular, fondo transparente, variantes 1:1 (Threads, Pinterest, Gumroad, Hotmart, favicon).
2. **Banners por plataforma:** 1500×500 (Threads), 1200×628 (Open Graph), 1000×1500 (pin).
3. **Aplicación automática:** Playwright entra a cada plataforma con la sesión del vault y sube la imagen; devuelve URL de confirmación o el error literal.
4. **Versionado:** cada cambio de identidad queda con fecha y hash para no romper la consistencia entre canales.

**Criterio de aceptación:** un clic actualiza el avatar en Threads y Pinterest, con captura de verificación.

---

## Fase 6 — Pines y Threads

1. **Pin factory:** 1000×1500, prueba de legibilidad a 236px, mix 70% Dark Luxury / 30% Ron.
2. **Threads factory:** hook + 5 slides + 2 auto-respuestas de 1ª hora.
3. **QA gate:** legibilidad, similitud, URL repetida, cifras impares, cero promesas de ingreso.
4. Lote inicial: 10 pines + 5 hilos, uno por producto.

**Criterio de aceptación:** lote auditado con 0 fallos y hora de publicación asignada.

---

## Fase 7 — Publicación real

`backend/services/publisher.py` (≤250 líneas): Playwright sobre Chrome Vault, devuelve URL de confirmación o el error literal del DOM. `status` solo pasa a `published` con URL. Rate limit conservador y confirmación humana antes de la primera publicación.

---

## Fuera de alcance por ahora

- Las 50 rutas puente restantes.
- Los 10 Kits y 6 Mega-Bundles.
- Refactor estético completo de Radar/Conectores.
- Publicación sin supervisión.
