# Notas del backend (task-1 — backend-core)

Documento de operación de lo que cambió en el backend para poder publicar y
cobrar de verdad. Sin estados falsos: lo que no está medido se declara pendiente.

## 1. Contrato de la API de publicación (`backend/routers/api_publish.py`)

Router ya montado en `main.py` como `publish_router` (prefix `/api/publish`).

| Endpoint | Respuesta |
| --- | --- |
| `GET /api/publish/readiness` | `{ready, checks:[{id,label,ok,detail}], blockers, counts, next_actions}`. Checks: `deliverables`, `checkout`, `vertex`, `art`, `routes`, `content`, `site`. `counts` incluye `skus, paid, leads, checkouts, checkouts_gumroad, checkouts_hotmart, skus_missing_checkout, skus_missing_checkout_ids, threads, pins, art_covers, art_cover_files, deliverables`. `ready = (blockers == [])`. |
| `GET /api/publish/kit?platform=threads\|pinterest&limit=N` | `{platform, base_url, count, items:[{id,platform,text,image_url,target_route,target_sku_id,status}], tracking:"local", published_to_network:false, note}`. `target_route` es absoluto desde `request.base_url`. `image_url` es `null` si la imagen no existe en disco (nada de imágenes 404). Los pines benchmark de competencia quedan excluidos. |
| `POST /api/publish/mark` | Body `{platform, item_id, status:"queued"\|"published"}`. Guarda SOLO seguimiento local en `data/publish_state.json` y devuelve `tracked_locally:true`, `published_to_network:false`, `publication_url:null`, `note`. **No publica en Threads/Pinterest.** Valida plataforma/estado (422) e ítem existente (404). |
| `POST /api/publish/export-site` | Import LAZY de `backend.services.publish_pack.build_site(base_url)`. Devuelve `{status:"ok", base_url, manifest}`; 503 si el módulo no existe o no expone `build_site`; 500 con el detalle si `build_site` falla. |
| `GET /api/publish/site-manifest` | `{status:"ok", manifest}` o 404 honesto si no se ha exportado; 500 si el manifest está corrupto. |

## 2. Checkout real por SKU (`backend/routers/api_catalog.py`)

- `POST /api/catalog/{sku_id}/checkout` — body `{gumroad_url?, hotmart_url?}`.
  Validación: `https` obligatorio, host permitido (`gumroad.com`, `hotmart.com` y
  subdominios + `CHECKOUT_ALLOWED_HOSTS`), máximo 500 caracteres, sin credenciales
  embebidas. Cadena vacía **borra** el campo; campo ausente **no cambia**.
  422 con el motivo literal; 404 si el SKU no existe.
- `POST /api/catalog/checkout-bulk` — body
  `{"links": {"E01": {"gumroad_url":"https://...", "hotmart_url":""}, ...}}`.
  Devuelve `{updated, skipped, errors:[{sku_id, reason}], checkout_ready_count, paid_skus}`.
  Persiste en una sola escritura atómica.
- `GET /api/catalog` añade `checkout_ready` por ítem, `checkout_ready_count` y
  `load_warning` (si `catalog.json` estaba corrupto y se regeneró).

Esto es lo único que falta para cobrar: hoy hay **0/52 SKUs con checkout**. La
acción está en `next_actions` de readiness: crear producto en Gumroad/Hotmart y
pegar cada URL (o usar checkout-bulk).

## 3. Seguridad opcional (`backend/security_middleware.py`)

- Ya montado en `main.py` con `install_security(app)`.
- Si `RONIN_API_TOKEN` está definida: todo POST/PUT/PATCH/DELETE exige header
  `X-Ronin-Token` o `?token=`. Si NO está definida, el comportamiento es el
  anterior (LAN abierta) — **decisión de operación, no de código**.
- Rate limit en memoria: `POST /api/customizations/test-all` y
  `POST /api/customizations/vertex-generate` aceptan 1 llamada / 20 s por cliente
  (429 con `retry_after_sec`).
- `POST /api/customizations/test-all` devuelve 409 si hay una generación de imagen
  Vertex en curso (`image_job_guard`).
- Variables: `RONIN_API_TOKEN`, `CHECKOUT_ALLOWED_HOSTS` (lista separada por comas).

## 4. Correcciones de honestidad y datos

- **A1 falsos verdes**: `probe_runners.test_chrome_vault` ya no lanza un Chrome
  headless con perfil temporal vacío. Ahora lee la base de cookies del Chrome
  Vault (`data/chrome_vault/Default/Network/Cookies`) y busca cookies de sesión
  de google.com: sin evidencia => `SIN_VERIFICAR` con el motivo literal.
- **A1 "Publicado"**: el toggle de feeds NO escribe `published` en el JSON; el
  estado real vive en `data/publish_state.json` (seguimiento local) y cada
  respuesta añade `published_to_network:false` + `publication_note`.
- **A1 "Mutar con IA"**: la respuesta declara `engine:"template_variant"`,
  `ai_used:false` y dejó de inflar `simulated_likes` con random.
- **A2 métricas**: TRM única COP 4200 (antes 4000 en el parser y 4200 en el
  catálogo), tabla FX con fecha para USD/COP/BRL/EUR, parseo de miles colombianos
  ("79.800" = 79800), el order bump ya no cuenta como venta
  (`product_sales_count`, `order_bumps_count`, `order_bumps_revenue_usd`), y el
  "funnel" se declara atribución aproximada por prefijo de SKU (`attribution_note`).
- **A3 atomicidad**: `backend/services/json_store.py` centraliza lock por archivo,
  escritura `tmp + os.replace` y cuarentena de JSON corrupto. Aplicado a catálogo,
  feeds, leads, métricas, customizations, jobs de conexión y secretos. Un
  `catalog.json` corrupto ya no tumba `/api/catalog`: se mueve a
  `catalog.corrupt-<fecha>.json`, se regenera por defecto y se devuelve
  `load_warning`.
- **A3 datos de producción**: `tests/conftest.py` aísla catálogo, feeds, leads,
  métricas, estado de conectores y de publicación en `tmp_path`. Un test falla si
  la suite modifica los JSON reales de `data/`. Se limpió
  `data/social_feeds.json`: 4 posts canónicos (`th_001`…`th_004`) + 12 pines
  (10 propios + 2 benchmarks). Backup del original en
  `data/_cuarentena/social_feeds_20261104_214653.json.bak`.
- **M4**: los teardowns de competencia salieron del router a
  `data/competitor_notes.json` con `reviewed_at`, `source` y
  `status:"observación manual sin verificar"`; si el archivo no existe, la API
  devuelve lista vacía y lo declara.
- **M5**: CSV limitado a 2 MB (413), fecha ISO obligatoria, plataforma validada
  (nada de "instagram" guardado como pinterest) y la respuesta nunca devuelve
  emails de clientes (`all_sales` vacío y emails a `null`).
- **A8**: un lead exige consentimiento explícito y un SKU existente; ya no
  devuelve un PDF que no corresponde.
- **B7**: `test_catalog_generate_real_deliverable` verifica tamaño >20 KB,
  `</html>`, `<title>` y entrega protegida; `test_published_sku_requires_checkout_url`
  ya no es vacuo (valida https/host y demuestra el invariante configurando checkout).

## 5. Pendiente / conocido (no es código de este task)

- **Checkout 0/52**: acción de negocio (crear productos y pegar URLs).
- `data/publish_site/` fue generado con `base_url=""` (URLs relativas). Antes de
  desplegar, regenerar con el dominio real:
  `.\.venv\Scripts\python.exe scripts\build_publish_pack.py --base-url https://tu-dominio`.
  Con `base_url=""` el sitemap deja la raíz como `//` (bug del generador, task de
  generadores).
- El `content/pinterest.json` del sitio incluye los 2 pines benchmark; el kit de
  la API los excluye. Revisar en el task de generadores.
- Exposición LAN: los entregables de pago se bloquean para IPs no locales
  (`delivery.is_owner`). El token opcional (sección 3) es la segunda capa.
