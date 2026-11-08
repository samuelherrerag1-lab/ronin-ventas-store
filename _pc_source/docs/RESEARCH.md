# Investigación de Plataformas y Lanzamiento (2026)

Documento de investigación técnica para el sistema Ronin Ventas OS (`@ronOverthinks`).
Fecha de recolección: **3 de noviembre de 2026**. Todo dato sin fuente enlazada se marca **"sin confirmar"**.

Método: lectura directa de documentación oficial, del código fuente público de Gumroad (`main`, consultado 2026-11-03), de los artefactos de build del portal de developers de Hotmart, y de foros técnicos (Hacker News vía API Algolia). Se descartaron blogs de SEO sin fuente primaria.

---

## Resumen accionable (máx 15 líneas)

1. Gumroad sí permite automatizar el ciclo completo: crear producto, subir archivo (multipart 100 MB, máx 20 GB), precio, cupones, variantes, landings HTML propias y webhooks. Es la única de las cuatro plataformas con API de creación real.
2. Hotmart **no** tiene API para crear productos digitales; solo cupones, payment links, ventas, suscripciones y webhooks. Los 52 SKUs de pago deben registrarse a mano una vez y automatizar el resto.
3. Pinterest API en Trial **publica pines invisibles al público** (sandbox). Publicar de verdad exige Standard access con video de OAuth y revisión. La automatización de UI está prohibida explícitamente por sus guías.
4. Threads sí es publicable por API sin App Review si la cuenta es "tester" de tu propia app: 250 posts/24 h, tokens de 60 días. Es el canal más automatizable de los dos sociales.
5. Cloudflare Workers Static Assets sirve estáticos **gratis e ilimitado**; GitHub Pages prohíbe uso comercial y Vercel Hobby es solo no comercial. Los 55 puentes van a Cloudflare, no a Vercel ni GitHub.
6. La política 3.7/3.8 de Hotmart (mar-2026) prohíbe prometer ganancias y exhibir lujo/dinero para vender: las capturas de dashboards con cifras son riesgo directo de bloqueo.
7. Pinterest prohíbe "redirigir Pins existentes a nuevos destinos": reciclar un pin hacia otra de las 55 rutas es infracción, no táctica.
8. A $9 el fee fijo de Gumroad se come 15,6%; a $27 baja a 11,9%. Precio de entrada mínimo defendible: $19, con bump de $9.

---

## 1. Gumroad

### Hechos verificados

**API y autenticación**

- La API v2 responde en `https://api.gumroad.com/v2/...` y también en `https://gumroad.com/api/v2/...` (las rutas se dibujan dos veces en `config/routes.rb`, bloque `api_routes`). [Fuente: `antiwork/gumroad`, `config/routes.rb`, líneas 67-235, consultado 2026-11-03](https://github.com/antiwork/gumroad/blob/main/config/routes.rb)
- Autenticación por `access_token` en query/body o cabecera `Authorization: Bearer <token>`. Sin token válido: HTTP 401. [Fuente: `ApiDocumentation/Errors.tsx` + `rack_attack.rb` (extractor `v2_product_token`), consultado 2026-11-03](https://github.com/antiwork/gumroad/blob/main/app/javascript/components/ApiDocumentation/Errors.tsx)
- **Ruta exacta del token**: iniciar sesión en Gumroad → `gumroad.com/settings/advanced` → formulario "Create application" (Application icon, Application name, Redirect URI) → botón **"Generate access token"**. Para uso propio el Redirect URI puede ser `http://127.0.0.1`. [Fuente: help center, artículo 280 "Create an application", renderizado desde `app/views/help_center/articles/contents/_280-create-application-api.html.erb`, consultado 2026-11-03](https://github.com/antiwork/gumroad/blob/main/app/views/help_center/articles/contents/_280-create-application-api.html.erb)
- Los access tokens **no expiran** hasta ser revocados manualmente ("we do not expire the access_token until it is revoked manually"). [Misma fuente, 2026-11-03]
- Scopes disponibles: `account`, `view_profile`, `edit_profile`, `edit_products`, `edit_emails`, `view_sales`, `view_payouts`, `view_tax_data`, `mark_sales_as_shipped`, `edit_sales`. `edit_products` cubre productos, variantes, offer codes, custom fields y archivos. [Fuente: `ApiDocumentation/Scopes.tsx`, consultado 2026-11-03](https://github.com/antiwork/gumroad/blob/main/app/javascript/components/ApiDocumentation/Scopes.tsx)

**Productos**

- CRUD completo: `GET/POST /v2/products`, `GET/PUT/DELETE /v2/products/:id`. Precio en **centavos** (`price=500` = $5.00). Campo `native_type`: `digital` (default), `course`, `ebook`, `membership`, `bundle`, `coffee`, `call`, `commission`. Guardado como borrador con `draft=true`; se publica luego con `PUT /v2/products/:id/enable`. [Fuente: `ApiDocumentation/Endpoints/Products.tsx` + ejemplo en `Files.tsx`, consultado 2026-11-03](https://github.com/antiwork/gumroad/blob/main/app/javascript/components/ApiDocumentation/Endpoints/Products.tsx)
- Cupones: `GET/POST /v2/products/:id/offer_codes`, `GET/PUT/DELETE /v2/products/:id/offer_codes/:id`. [Fuente: `config/routes.rb` líneas 113-121, 2026-11-03]
- Variantes: `POST /v2/products/:id/variant_categories` y `/variants`. [Misma fuente]
- **Landing HTML propia por producto**: `PUT /v2/products/:id/custom_html` (máx 500,000 caracteres), `POST .../custom_html/edit` y `POST .../preview_custom_html`. El HTML se sanitiza y se sirve en iframe con `sandbox="allow-scripts allow-forms allow-popups allow-popups-to-escape-sandbox"`. Puede cargar JS inline, Tailwind/jsDelivr/unpkg, Google Fonts y Bunny Fonts; **no** puede hacer `fetch`/XHR/WebSocket (`connect-src 'none'`), ni cargar imágenes fuera del CDN de Gumroad, ni enviar formularios a URLs externas. Rate limit: 30 PUT/min y 60 previews/min por token. [Fuente: `Endpoints/Products.tsx`, sección custom HTML, consultado 2026-11-03]

**Archivos**

- Flujo de 4 pasos: `POST /v2/files/presign` (devuelve `upload_id`, `key`, `file_url` y una URL prefirmada por cada parte de 100 MB, válidas 900 s) → `PUT` de cada parte al `presigned_url` capturando el header `ETag` → `POST /v2/files/complete` con la lista de ETags → adjuntar `files[][url]` en `POST/PUT /v2/products`. [Fuente: `app/controllers/api/v2/files_controller.rb` y `Endpoints/Files.tsx`, consultado 2026-11-03](https://github.com/antiwork/gumroad/blob/main/app/controllers/api/v2/files_controller.rb)
- Límite duro: `PART_SIZE = 100.megabytes`, `MAX_FILE_SIZE_GB = 20` ("matching the web uploader limit"). [Mismo controlador, 2026-11-03]
- Límite comercial: productos de pago (> $0.99) hasta **20 GB por archivo**; productos gratuitos o pay-what-you-want con mínimo $0 hasta **250 MB acumulados**. [Fuente: help article 289 "File size limits on Gumroad", repo `main`, 2026-11-03](https://github.com/antiwork/gumroad/blob/main/app/views/help_center/articles/contents/_289-file-size-limits-on-gumroad.html.erb)
- `PUT /v2/products/:id` con `files` es **reemplazo total**: cualquier archivo omitido se borra. `complete` funciona una sola vez por `upload_id`; si se pierde la respuesta hay que reiniciar el upload. [Fuente: `Endpoints/Files.tsx`, 2026-11-03]
- `GET /v2/products/:id` devuelve una URL firmada temporal, **no** la `file_url` canónica: hay que guardarla en nuestra base. [Misma fuente]

**Ventas y webhooks**

- Ventas: `GET /v2/sales`, `GET /v2/sales/:id`, `GET /v2/sales/summary`, `POST /v2/sales/exports`; acciones `PUT /v2/sales/:id/mark_as_shipped`, `/refund`, `/resend_receipt`, `/revoke_access`, `/undo_revoke_access`. [Fuente: `config/routes.rb`, 2026-11-03]
- Webhooks: `PUT /v2/resource_subscriptions` con `resource_name` + `post_url`. Ocho recursos soportados: `sale`, `refund`, `dispute`, `dispute_won`, `cancellation`, `subscription_updated`, `subscription_ended`, `subscription_restarted`. Existe `POST /v2/resource_subscriptions/:id/test_event`, que envía un payload marcado `test: true` sin mover dinero. [Fuente: `Endpoints/ResourceSubscriptions.tsx`, consultado 2026-11-03](https://github.com/antiwork/gumroad/blob/main/app/javascript/components/ApiDocumentation/Endpoints/ResourceSubscriptions.tsx)
- Suscripción a `sale` exige el scope `view_sales`. [Fuente: `Scopes.tsx`, 2026-11-03]

**Rate limits (código, no marketing)**

| Ruta | Límite | Nota |
|---|---|---|
| `POST /v2/products` | 10/min por IP | inicial 10 rpm, techo 50 req/9 h |
| `PUT/PATCH /v2/products/:id` | 30/min por IP y por token | 150/min si la cuenta es "VIP creator" |
| `GET /v2/products/comps` | 30/min | agregación pesada |
| `GET /v2/sales` con `page > 10` | 10/segundo | paginación lenta a propósito |

[Fuente: `config/initializers/rack_attack.rb`, líneas 503-527, consultado 2026-11-03](https://github.com/antiwork/gumroad/blob/main/config/initializers/rack_attack.rb). El throttle usa `throttled_response_retry_after_header = true`, es decir devuelve 429 con `Retry-After`.

**Afiliados**

- Dos programas: "Your Affiliates" (el creador aprueba y fija comisión **entre 1% y 75%**, cookie de **30 días**) y "Gumroad Affiliates" global (comisión fija **10%**, cookie de **7 días**). Ambos opcionales. [Fuente: help article 333 "Affiliates on Gumroad", repo `main`, 2026-11-03](https://github.com/antiwork/gumroad/blob/main/app/views/help_center/articles/contents/_333-affiliates-on-gumroad.html.erb)
- Los productos listados en Discover quedan **auto-inscritos** en Gumroad Affiliates (se puede opt-out). [Fuente: help article 79 "Gumroad Discover", 2026-11-03]
- **No existe API de afiliados**: no hay ninguna ruta `affiliate` dentro de `api_routes`; las rutas de afiliados son solo de la interfaz web (`/affiliates`, `/a/:affiliate_id`). [Fuente: `config/routes.rb`, líneas 716-757 vs. bloque API, 2026-11-03]

**Economía y Discover**

- Comisión: **10% + $0.50** por venta directa; **30%** plano en ventas vía Discover; **5% + $0.50** en ventas directas del mes una vez superados **$20,000** facturados en el mes calendario. [Fuente: help article 66 "Gumroad's fees", repo `main`, 2026-11-03](https://github.com/antiwork/gumroad/blob/main/app/views/help_center/articles/contents/_66-gumroads-fees.html.erb)
- Elegibilidad Discover: payout settings completos + saldo de **$100 USD** en ventas genuinas + revisión de riesgo (promedio **3 semanas**) + al menos 1 venta + categoría asignada + ratings activos. [Fuente: help article 79, 2026-11-03]

**Marketing API v2 (nueva)**

- Endpoints `GET /v2/products/:id/marketing/recommendations`, `POST /v2/marketing_actions`, `.../approve`, `.../execute`, `.../cancel`. Requiere scope `edit_emails` (el scope `account` no se acepta) y la cuenta debe tener `auto_marketing` activo, si no devuelve 404. Preparar no publica: `execute` publica en el canal o deja un borrador de email. No hay programación futura. [Fuente: `docs/marketing-api.md`, repo `main`, consultado 2026-11-03](https://github.com/antiwork/gumroad/blob/main/docs/marketing-api.md)

### Qué podemos automatizar

- **Fábrica de los 52 SKUs de pago (Gumroad)**: por cada producto, `POST /v2/files/presign` → subir partes → `complete` → `POST /v2/products` con `native_type`, `price` en centavos, `description`, `tags`, `files[][url]`, `custom_permalink`. Queda en borrador y se publica con `enable` cuando el resto del sistema lo valide.
- **Puentes y landings**: subir el HTML de cada mini-landing con `PUT /v2/products/:id/custom_html`. Restricción operativa: imágenes solo desde el CDN de Gumroad (hay que subirlas como `covers`/`thumbnail` primero) y cero llamadas a red desde la página. Nuestro backend local **no** puede ser consumido por esa landing.
- **Cupones por SKU** (los 55 con código distinto para atribución de Pinterest/Threads) vía `offer_codes`.
- **Order bump**: Gumroad ya tiene upsells nativos en checkout (`Upsells`, tres tipos: producto adicional, reemplazo o upgrade) además de nuestro bump de $9; conviene usarlos juntos. [Fuente: help article 331 "Creating upsells", 2026-11-03]
- **Radar de ventas**: `GET /v2/sales` paginado + webhook `sale` como fuente de verdad en tiempo real, más `test_event` para probar el pipeline sin estado falso.
- **Emails**: `POST /v2/emails` + `POST /v2/emails/:id/send` y `/schedule` permiten enviar la secuencia de 5 mensajes desde la propia audiencia de Gumroad (scope `edit_emails`). [Fuente: `config/routes.rb`, 2026-11-03]
- **NO automatizable**: alta y comisión de afiliados (solo UI), payouts, verificación de riesgo.

### Riesgos y límites

- **`PUT` de archivos es destructivo** si se envía la lista incompleta: hay que reconstruir siempre desde `GET` y reenviar `id` + `url` de los archivos que se conservan.
- **La `file_url` canónica no se recupera** desde la API; si no la persistimos, hay que volver a subir el archivo.
- Con 52 SKUs y 30 PUT/min, la fábrica debe ir en cola con backoff ante 429 (`Retry-After`), no en paralelo agresivo.
- Token sin expiración = riesgo de seguridad: guardarlo cifrado y nunca en el repo.
- Discover no está disponible el día 1 ($100 + ~3 semanas de revisión): el lanzamiento no puede depender del marketplace.
- Contenido: Gumroad prohíbe reventa de productos ajenos, dropshipping e IPTV. Nuestros blueprints son originales, así que cumplen; los "packs" con material de terceros no. [Fuente: help article 155, 2026-11-03]

---

## 2. Hotmart

### Hechos verificados

**¿Existe API para crear productos?**

- **No para productos digitales.** El índice de ejemplos de código del portal oficial lista, para `v1/product`, solo operaciones de lectura: `product-list`, `product-configuration`, `product-offers`, `product-plans`. La creación de producto (`pp-product-create`) existe únicamente bajo `v1/physical-product` y `v2/physical-product` (productos físicos). [Fuente: índice de `code_examples` embebido en el build de `developers.hotmart.com`, consultado 2026-11-03]
- Lo que sí se puede crear por API: **cupones** (`POST /products/api/v1/product/:product_id/coupon`) y **payment links** (`POST /payments/api/v1/link`, con `value`, `currency`, `checkout_configuration` —PIX, PayPal, boleto, saldo— y `custom_thanks_page` con URLs de retorno). [Fuente: idem, ejemplos `v1/coupon/post-coupon-post-coupon.md` y `v1/payment-link/create-pl-request.md`, 2026-11-03]

**Autenticación**

- OAuth2 `client_credentials`: `POST https://api-sec-vlc.hotmart.com/security/oauth/token?grant_type=client_credentials&client_id=:client_id&client_secret=:client_secret` con cabecera `Authorization: Basic :basic` (Basic con client_id:client_secret en base64). Devuelve `access_token` que se usa como `Bearer` contra `https://developers.hotmart.com/...`. [Fuente: `code_examples/start/app-auth-request.md` en el build oficial, 2026-11-03]
- Las credenciales (client_id / client_secret / basic) se generan en el área de developers de la cuenta. Requiere iniciar sesión en Developers con cuenta Hotmart. [Fuente: changelog oficial "Log into Developers with a Hotmart account for exclusive API and Webhook services", 2026-06-09, indexado en el mismo build]

**Ventas, suscripciones, otros**

- Base `https://developers.hotmart.com/payments/api/v1/`: `sales/history`, `sales/summary`, `sales/users`, `sales/commissions`, `sales/price/details`, `sales/:id/billet`, refunds. [Fuente: índice `v1/sales/*`, 2026-11-03]
- Suscripciones: `subscriptions`, `subscriptions/:id/purchases`, `subscriptions/:id/transactions`, cancelar/reactivar (individual y masivo), cambiar plan, cambiar día de cobro. [Fuente: índice `v1/subscription/*`, 2026-11-03]
- Club (área de miembros): páginas, módulos, lecciones, usuarios. [Fuente: índice `v1/club/*`, 2026-11-03]
- `GET /v1/user/me` para identificar la cuenta. [Fuente: índice `v1/user/*`, 2026-11-03]

**Webhooks**

- Versión 2.0.0 con eventos: `PURCHASE_APPROVED` y familia de compra (`purchase-webhook-v2`), `order-fulfillment`, `cart-abandonment`, `club-first-access`, `club-module-completed`, `cancel-subscription`, `switch-plan`, `update-subscription-charge-date`. Cada payload trae `event`, `version: "2.0.0"`, `id`, `creation_date` y `data.product`/`data.purchase`. [Fuente: `code_examples/2.0.0/webhook/*` del build oficial, consultado 2026-11-03]
- En la versión 1.0.0 el body incluye el campo `hottok` (token del webhook). En los ejemplos de 2.0.0 **no aparece** `hottok`: el mecanismo de validación de firma en v2 no está documentado en los artefactos consultados → **sin confirmar**. [Fuente: `1.0.0/webhook/cart-abandonment-webhook.md` vs `2.0.0/webhook/purchase-webhook-v2.md`, 2026-11-03]

**Afiliados**

- Comisión de hasta **80%** del valor del producto por venta. [Fuente: página oficial `hotmart.com/es/afiliados`, consultada 2026-11-03 vía render]
- La comisión se configura **por producto** en `app.hotmart.com` → Productos → Mis productos → (producto) → afiliados; no hay endpoint público para fijarla. [Fuente: Central de Ayuda, artículo 360016366532 "Cómo definir y configurar la comisión ideal para mis afiliados", consultado 2026-11-03]
- La aprobación de cada solicitud de afiliación la hace el productor; el plazo de auto-aprobación **sin confirmar**.

**Reglas de contenido y verificación**

- **No hay control editorial previo**: "Hotmart no realiza un control editorial previo de los Productos comercializados, así como tampoco evalúa la tecnicidad y experiencia de quienes los producen". [Fuente: `hotmart.com/es/legal/plazo-de-compra`, §1.4, consultado 2026-11-03]
- Pero sí hay verificación de registro: estar "en análisis" solo indica proceso de verificación y **no** implica respaldo ni certificación de Hotmart. [Fuente: `hotmart.com/es/legal/terminos-de-uso`, consultado 2026-11-03]
- **Política General de Uso Responsable, versión 20 de marzo de 2026** (vinculante, puede terminar la cuenta):
  - §3.7 prohíbe "productos que promuevan el enriquecimiento ilícito o irreal, que prometan ganancias garantizadas, beneficios rápidos sin esfuerzo o renta fija derivada de inversiones variables".
  - §3.8 prohíbe "estrategias de marketing basadas en la ostentación de bienes de lujo, dinero en efectivo o estilos de vida irreales con la intención de inducir al Usuario al error sobre la facilidad para obtener resultados financieros".
  - La lista de ejemplos "no es exhaustiva" y la decisión final de aceptar, eliminar o mantener un producto es siempre de Hotmart.
  [Fuente: `hotmart.com/es/legal/politicas-de-uso`, consultado 2026-11-03]

### Qué podemos automatizar

- **Cupones por producto** por API: útil para los códigos únicos de cada una de las 55 rutas puente.
- **Payment links** por API: permite generar checkouts con precio y moneda específicos sin crear producto nuevo (sirve para ofertas y bundles dinámicos K01-K10, M01-M06).
- **Radar**: `sales/history` + `sales/summary` + `sales/commissions` con el mismo token; reconciliación diaria en el Módulo 6.
- **Webhooks 2.0.0** para estado de compra en tiempo real; en v1 usar `hottok` como verificación.
- **Suscripciones**: cancelar/reactivar/cambiar plan por API (útil si algún SKU pasa a membresía).
- **NO automatizable**: alta de producto digital, precios base del producto, comisión de afiliados, aprobación de afiliados, verificación de cuenta.

### Riesgos y límites

- **El catálogo no nace por API**: los 52 SKUs requieren carga manual inicial (o RPA de navegador, que Hotmart no autoriza explícitamente → tratar como riesgo).
- **Riesgo alto de política**: el concepto de la Vía A (capturas de dashboards con cifras, estética "dinero fácil") choca de frente con §3.7/§3.8. Aplica a la promoción, no solo al producto.
- No hay endpoint de creación de producto digital: cualquier promesa de "fábrica 100% automática en Hotmart" es falsa y violaría la regla de estado honesto.
- `hottok` en v2 sin confirmar: el conector no puede reportarse "CONECTADO" hasta verificar un evento real.
- Moneda y medios: PIX/boleto son de Brasil; para LatAm hispana el flujo relevante es tarjeta + efectivo (Nequi/PSE/Efecty) configurado en el checkout, no en la API.

---

## 3. Pinterest

### Hechos verificados

**API v5: requisitos y niveles**

- Para crear una app: cuenta business, email verificado, aceptar Developer Terms, registrar la app en "My apps" y **solicitar Trial access**, que es revisado por Pinterest; luego se obtienen app ID y secret y se configura el Redirect URI (coincidencia exacta). [Fuente: `developers.pinterest.com/docs/getting-started/` (Connect app), consultado 2026-11-03](https://developers.pinterest.com/docs/getting-started/set-up-app/)
- **Trial access**: "all Pins and Boards created with Trial access are only visible to their creator as Sandbox entities". Es decir, la API en Trial **no publica nada visible al público**. [Fuente: `docs/getting-started/access-tiers/`, consultado 2026-11-03](https://developers.pinterest.com/docs/getting-started/access-tiers/)
- **Standard access** exige solicitud de upgrade con **video** demostrando el flujo OAuth (se aceptan grabaciones de terminal o Postman), revisión de política de privacidad y cumplimiento de Developer Guidelines; la decisión llega por email. [Misma fuente]
- Cambio de política reciente: las apps registradas **a partir del 14 de septiembre de 2026** pueden recibir `HTTP 403 PINNER_DATA_ACCESS_DENIED` al pedir boards o Pins sin autorización de Pinterest para usuarios no-business. [Misma fuente]

**Rate limits**

| Categoría | Trial (req/día por app) | Standard (req/min por usuario por app) |
|---|---|---|
| Todas las llamadas | 1,000/día | 100/segundo |
| `org_write` (crear boards, secciones, Pins) | 300/día | 100/min |
| `org_read` | 1,000/día | 1,000/min |
| `trends_read` | 1,000/día | 60/min |

Los headers `x-ratelimit-limit`, `x-ratelimit-remaining` y `x-ratelimit-reset` permiten instrumentar el consumo. [Fuente: `docs/reference/rate-limits/`, consultado 2026-11-03](https://developers.pinterest.com/docs/reference/rate-limits/)

**Qué penaliza el algoritmo (texto oficial, no interpretación)**

Community Guidelines, "última actualización: mayo 2026" (con nueva versión efectiva el **12 de noviembre de 2026**), sección Spam:

- "Don't use automation that hasn't been explicitly approved by Pinterest. This includes unauthorized services that automatically perform actions on your behalf."
- "Don't create or save content that is repetitive, deceptive, or irrelevant in an attempt to make money."
- "Don't link to websites that are unsafe, deceptive, untrustworthy, unoriginal" — los sitios deben tener contenido original.
- "Don't operate multiple accounts or coordinate with other people with the purpose of manipulating the Pinterest platform."
- Prohibido "keyword stuffing" y "redirecting existing Pins to new destinations".
  [Fuente: `policy.pinterest.com/en/community-guidelines`, consultado 2026-11-03](https://policy.pinterest.com/en/community-guidelines)

**Verificación de sitio**

- Cuatro métodos: Google Merchant Center (algunas cuentas), etiqueta HTML, archivo HTML o registro TXT. Requiere poseer el dominio/subdominio/subpath y poder editar el código; un sitio solo puede ser reclamado por una cuenta. [Fuente: `help.pinterest.com/en/business/article/claim-your-website`, consultado 2026-11-03](https://help.pinterest.com/en/business/article/claim-your-website)
- No es obligatoria para publicar por API, pero sin dominio reclamado se pierde la atribución (avatar en el Pin, enlace al perfil, opción de seguir) y las métricas de sitio.
- Pinterest **no publica** un verificador de Rich Pins separado en la documentación consultada → **sin confirmar** el estado actual del validador.

**SEO 2026 con datos**

- Lo único con número oficial es la interfaz de keyword targeting de anuncios: hasta **20,000 keywords** por ad group y recomendación de **mínimo 25** por grupo. [Fuente: `help.pinterest.com/en/business/article/keyword-targeting`, consultado 2026-11-03](https://help.pinterest.com/en/business/article/keyword-targeting)
- **Pinterest no publica volúmenes de búsqueda** para orgánico ni una guía con cifras de CTR por formato. Cualquier "estudio de SEO en Pinterest 2026" con porcentajes es estimación de terceros → **sin confirmar**.
- Consecuencia operativa: la única fuente de verdad de keywords es el autocompletado del buscador de Pinterest y `trends_read` vía API, medido por nosotros.

### Qué podemos automatizar

- **Lectura**: boards, Pins propios, analytics de Pin y de cuenta (`org_analytics`: 60/min en Standard, 1,000/día en Trial), tendencias (`trends_read`).
- **Escritura real**: solo con Standard access aprobado. En Trial los Pins existen pero son invisibles → inservibles para el negocio.
- **Programación**: la API no ofrece scheduler; el calendario lo lleva nuestro backend y publica en el momento (con control de cupo diario).
- **Modo Infiltración (UI)**: pendiente de decisión — ver riesgos.

### Riesgos y límites

- **Trial access no sirve para publicar**: si el Módulo 2 se construye asumiendo que la API publica en Trial, el sistema reportará "publicado" sin que nadie vea el pin. Esto viola directamente la regla de estado honesto.
- **La automatización de UI está prohibida por la política vigente** ("automation that hasn't been explicitly approved"). El "Modo Infiltración" con navegador persistente es exactamente eso: riesgo de suspensión, no solo de bloqueo técnico.
- **Reciclar un Pin hacia otra URL de las 55 rutas** está listado como manipulación ("redirecting existing Pins to new destinations"). El plan de "55 rutas puente reutilizando pines" debe rediseñarse: un Pin nuevo por URL.
- Standard access requiere video de OAuth y revisión humana: no es un trámite instantáneo ni garantizado.
- Límite de escritura en Standard: 100 Pins/min, muy por encima de los 5-15/día del sistema; el cuello de botella no es técnico sino de aprobación y de política.
- Apps nuevas (post 14-sep-2026) pueden recibir 403 al leer datos de usuarios no-business: el dashboard de métricas debe tolerar ese error sin inventar cifras.

---

## 4. Threads (Meta)

### Hechos verificados

**API de publicación**

- Base `https://graph.threads.com/v1.0` (también funciona `graph.threads.net`). Publicación en dos pasos: `POST /{threads-user-id}/threads` (crea contenedor) y `POST /{threads-user-id}/threads_publish` (`creation_id`). Recomendación oficial: esperar ~30 s entre ambos para dar tiempo de procesamiento. [Fuente: `developers.facebook.com/docs/threads/posts`, actualizado 30-oct-2026, consultado 2026-11-03](https://developers.facebook.com/docs/threads/posts)
- Texto: máximo **500 caracteres**; los emojis cuentan como bytes UTF-8. Carrusel: hasta **20** imágenes/videos. [Misma fuente]
- Permisos: `threads_basic` (todo), `threads_content_publish` (publicar), `threads_manage_replies`, `threads_read_replies`, `threads_manage_insights`. [Misma fuente]
- **App Review**: si la app no tiene "advanced access" para `threads_content_publish`, solo puede publicar en nombre de **Threads testers** de la app. Tras publicar la app y aprobar el permiso, puede publicar en nombre de cualquier usuario que lo conceda. [Misma fuente]
- Implicación práctica: agregar **nuestra propia cuenta como tester** permite publicar sin App Review. [Fuente: `docs/threads/get-started` ("Threads testers can grant your app these permissions at any time"), consultado 2026-11-03]
- Tokens: short-lived 1 hora; long-lived **60 días**, refrescable con `GET /refresh_access_token`; la concesión de permisos de perfiles públicos dura **90 días**. Códigos de autorización válidos 1 hora. [Fuente: `docs/threads/get-started`, consultado 2026-11-03]

**Límites**

- **250 posts publicados por API cada 24 h** por perfil (carruseles cuentan como uno). Se consulta con `GET /{threads-user-id}/threads_publishing_limit?fields=quota_usage,config` (`quota_total: 250`, `quota_duration: 86400`). [Fuente: `docs/threads/overview`, consultado 2026-11-03](https://developers.facebook.com/docs/threads/overview)
- **1,000 respuestas cada 24 h** por perfil.
- Cuota de llamadas: `4800 * impresiones` en 24 h (mínimo 10 impresiones), con techos adicionales de CPU y tiempo total.

**Métricas disponibles**

- `views`, `likes`, `replies`, `reposts`, `quotes`, `shares` en `GET /{threads-media-id}/insights`. No incluye métricas de respuestas anidadas. [Fuente: `docs/threads/insights`, actualizado 30-ene-2026, consultado 2026-11-03](https://developers.facebook.com/docs/threads/insights)

**Automatización de UI y reglas**

- Los Términos de Threads prohíben usar "any robot, spider, crawlers, scraper or other automatic device, process, software or queries that intercepts, mines, scrapes, extracts or otherwise accesses the Threads Service". [Fuente: `help.instagram.com/769983657850450` (Threads Terms of Use), consultado 2026-11-03](https://help.instagram.com/769983657850450)
- No hay umbrales de enforcement publicados → **sin confirmar** cuántos posts manuales por hora disparan límites.
- **Ranking**: Meta no publica pesos ni señales de ranking para Threads (a diferencia de Instagram, que sí tiene una explicación pública). Todo lo que circule con porcentajes es especulación → **sin confirmar**. Lo documentado y medible son las seis métricas de insights y ofertas de API para el propio contenido.

### Qué podemos automatizar

- **Publicación completa** de la Vía B (ragebait cínico + 2 auto-respuestas): contenedor de texto → publish → `POST /{threads-user-id}/reply` para las respuestas encadenadas (permiso `threads_manage_replies`). Con 250/24 h hay margen de sobra para 5-15 piezas/día.
- **Radar**: insights por media (views, likes, replies, reposts, quotes, shares) para el criterio de muerte a 14 días.
- **Cola local**: scheduler propio en el backend (la API no programa), respetando 250/24 h y el intervalo de 30 s.
- **Cosecha de comentarios**: `threads_read_replies` para alimentar el clon de Threads del Módulo 1 con datos reales.

### Riesgos y límites

- Publicar con cuenta tester funciona, pero si se **publica la app** sin App Review el permiso caduca a los 90 días y hay que re-autorizar; el sistema debe alertar antes del día 80.
- Tokens de 60 días: sin refresh automático, el conector muere en silencio. Hay que medir y mostrar el estado real (regla anti-estado-falso).
- Contenido con enlaces: solo la **primera URL** del texto genera preview; el resto se pierde. Para 55 productos distintos, un post por URL.
- Automatización de UI (navegador persistente) choca con los Términos: si se usa, debe quedar fuera del camino crítico y marcada como riesgo, nunca como "conector oficial".
- No existe endpoint de trending topics ni de búsqueda de hashtags: el descubrimiento de temas es manual.

---

## 5. Lanzamiento sin audiencia

### Hechos verificados

- **La distribución es el cuello de botella, no el producto**: hilo "Ask HN: Developers — How Did You Get Your First Paying Customers?" (5-ago-2026), donde el autor reporta 1.5 años construyendo y cero usuarios. [Fuente: `news.ycombinator.com/item?id=49187337`, 2026-08-05]
- Tácticas reportadas en ese hilo (evidencia anecdótica de pares, no estudio): listados destacados pagados en directorios de lanzamiento (Product Hunt, "There's An AI For That", PeerPush) para tráfico inmediato sin audiencia; responder 5 hilos por semana en **un** foro donde ya se hacen preguntas de compra, sin vender; círculo cercano; outreach en frío con valor primero. [Misma fuente, comentarios de `ls1911`, `theicreatoriam`, `krm01`, `tommymcglynn`]
- **Gumroad Discover no puede ser el motor inicial**: exige $100 de saldo, 1 venta previa y revisión de riesgo de ~3 semanas. [Fuente: help article 79, 2026-11-03]
- **Los afiliados de Gumroad se auto-inscriben** si el producto está en Discover; comisión fija 10% y cookie 7 días. Es la vía de distribución sin audiencia propia que ya viene "encendida". [Fuente: help article 333 + 79, 2026-11-03]
- **Hotmart permite hasta 80% de comisión** a afiliados: el margen disponible para comprar distribución es enorme comparado con Gumroad. [Fuente: `hotmart.com/es/afiliados`, 2026-11-03]

### Precios de entrada (cálculo propio sobre tarifas verificadas)

Fee de Gumroad = 10% + $0.50 por transacción directa.

| Precio | Fee | Fee efectivo | Sirve como |
|---|---|---|---|
| $9 | $1.40 | **15.6%** | bump / tripwire |
| $19 | $2.40 | 12.6% | entrada recomendada |
| $27 | $3.20 | 11.9% | entrada estándar |
| $47 | $5.20 | 11.1% | core |
| $97 | $10.20 | 10.5% | premium |

Cálculo propio a partir de la estructura de fees oficial. Conclusión ejecutable: **ningún SKU principal a $9**; $9 solo como order bump, donde el fee fijo se diluye en el ticket combinado ($27 + $9 = $36 → fee $4.10, 11.4%).

- Order bump: Gumroad tiene upsells nativos en checkout (producto adicional con descuento, reemplazo de carrito o upgrade) y se configuran por producto; se suman a nuestro bump de $9. [Fuente: help article 331, 2026-11-03]
- Garantía: la política de reembolso es un recurso de la API (`GET/PUT /v2/refund_policy`), es decir se puede fijar y versionar por código. [Fuente: `config/routes.rb`, 2026-11-03]
- Plazo de reembolso en Hotmart: hasta **30 días** por transferencia bancaria y hasta **90 días** con tarjeta, contados desde la solicitud. [Fuente: `hotmart.com/es/legal/plazo-de-compra`, 2026-11-03]

### Secuencia de email de 5 mensajes (ejecutable con `/v2/emails`)

Se crea con `POST /v2/emails` (audiencia propia de Gumroad, scope `edit_emails`), se previsualiza con `POST /v2/emails/:id/preview` y se envía o programa con `send`/`schedule`. Cada mensaje tiene un solo objetivo y un solo CTA.

| # | Momento | Objetivo | Asunto (A/B) | CTA |
|---|---|---|---|---|
| 1 | Inmediato | Entregar y generar confianza | "Tu blueprint está listo (empieza por la página 4)" | Abrir el archivo, no vender |
| 2 | +24 h | Instalar el uso | "El error que comete el 90% en la primera hoja" | Responder con una duda |
| 3 | +72 h | Prueba social y objeción | "Lo que me escribió alguien que lo aplicó en 3 días" | Ver el caso |
| 4 | +5 días | Oferta del SKU siguiente | "Esto es lo que no cabe en el blueprint" | Comprar K0x / M0x |
| 5 | +7 días | Cierre con fecha | "Cierro el bundle el domingo a medianoche" | Checkout con cupón |

Reglas de implementación:
- El mensaje 1 no lleva oferta; el 4 y el 5 sí, y el 5 debe tener fecha real verificable (si la fecha es falsa, es la misma falta que §3.8 de Hotmart).
- Las tasas de apertura/clic de referencia de la industria **no** se citan aquí porque no hay fuente primaria verificable para 2026 → **sin confirmar**. La medición sale de nuestro propio Radar a los 14 días.
- Sin doble opt-in no se envía: la lista se llena con lead magnets L01-L03 y el consentimiento se guarda con fecha.

### Errores comunes documentados

- **Construir 1.5 años sin distribución** (caso del hilo de HN, 2026-08-05).
- **Vender con estética de lujo/dinero**: prohibido por Hotmart §3.8 (mar-2026) y penalizado por Pinterest como contenido engañoso.
- **Reciclar el mismo Pin con URLs distintas**: listado como manipulación por Pinterest (may-2026).
- **Automatizar la UI de una plataforma que exige aprobación**: Pinterest lo prohíbe explícitamente; Threads lo prohíbe en sus Términos.
- **Depender del marketplace el día 1**: Discover requiere $100 y 3 semanas; Hotmart exige registro manual producto por producto.

---

## 6. Hosting gratis

### Cloudflare Pages (plan Free)

Datos de la página oficial de límites, "Last updated Sep 5, 2026":

| Límite | Free |
|---|---|
| Builds concurrentes | 1 |
| Builds por mes | 500 |
| Timeout de build | 20 min |
| Archivos por sitio | 20,000 |
| Tamaño máximo por asset | 25 MiB |
| Dominios personalizados por proyecto | 100 |
| Reglas en `_headers` | 100 (máx 2,000 caracteres por header) |
| Redirecciones en `_redirects` | 2,000 estáticas + 100 dinámicas = 2,100 |
| Preview deployments | ilimitados |
| Proyectos por cuenta | 100 |

[Fuente: `developers.cloudflare.com/pages/platform/limits/`, consultado 2026-11-03](https://developers.cloudflare.com/pages/platform/limits/)

- El subdominio `*.pages.dev` es gratuito y viene por defecto; los dominios propios se añaden aparte (100 por proyecto en Free). [Misma fuente]
- **Aviso oficial de la propia Cloudflare**: "Are you sure you want to use Pages? Workers supports most Pages use cases... Start new projects with Workers." (última actualización 25-ago-2026). [Fuente: `developers.cloudflare.com/pages/`, consultado 2026-11-03](https://developers.cloudflare.com/pages/)
- **Workers Static Assets**: "Requests to static assets are free and unlimited"; solo las invocaciones del Worker script se facturan (límite free tier aplica ahí). [Fuente: `developers.cloudflare.com/workers/static-assets/billing-and-limitations/`, actualizado 3-nov-2026](https://developers.cloudflare.com/workers/static-assets/billing-and-limitations/)
- `_headers` y `_redirects` funcionan igual en Pages; en Workers Static Assets se configuran por `wrangler`/`_headers` según el modo de despliegue.

### Alternativas

| Plataforma | Límites free | ¿Permite uso comercial? |
|---|---|---|
| **GitHub Pages** | 1 GB por sitio, 100 GB/mes de bandwidth (soft), 10 builds/hora, timeout 10 min | **No**: "not intended for or allowed to be used as a free web-hosting service to run your online business, e-commerce site" |
| **Vercel Hobby** | 100 GB de transferencia, 1M invocaciones, 4 h de CPU activa | **No**: "Hobby teams are restricted to non-commercial personal use only" |
| **Netlify Free** | Plan con créditos; límites concretos no verificados en esta investigación | Sí (no encontré restricción equivalente) — cifras **sin confirmar** |

[Fuentes: `docs.github.com/.../github-pages-limits`, consultado 2026-11-03; `vercel.com/docs/limits/fair-use-policy`, consultado 2026-11-03]

### Qué conviene para landings estáticas con backend local

- **Cloudflare Workers Static Assets** (no Pages) para los 55 puentes: tráfico de assets gratis e ilimitado, sin la restricción comercial de Vercel ni la prohibición de GitHub Pages.
- El backend Python en `0.0.0.0:8765` **no puede** servir estas landings: el comprador en móvil no está en la LAN. Las landings deben ser 100% estáticas y el botón de compra apunta a Gumroad/Hotmart (checkout alojado).
- Cada landing puede llevar `_headers` con CSP estricta y `_redirects` para slugs cortos (`/blueprint/e01` → `/e01/index.html`), dentro de los 2,100 redirects: los 55 puentes entran sin problema.
- Imágenes: el límite de 25 MiB por asset es holgado para capturas 2:3, pero **Gumroad custom_html solo acepta imágenes de su CDN**, así que las mismas piezas deben subirse dos veces (Cloudflare para el puente, Gumroad `covers`/`thumbnail` para la página interna).

---

## Recomendación final para este sistema

1. **Gumroad es el motor de la fábrica; Hotmart es el motor de LatAm con costo manual.** Los 52 SKUs se crean por API en Gumroad (producto + archivo + precio + cupón + landing) y se registran a mano una vez en Hotmart para Nequi/PSE/Efecty. El sistema no debe declarar "sincronizado" un SKU de Hotmart hasta que exista su `product_id` real guardado.

2. **Publicar en Pinterest por API no es viable hoy.** Trial crea pines invisibles; Standard exige video y revisión. Mientras no haya Standard aprobado, el Módulo 2 debe operar en modo "lectura + cola de publicación manual", y el estado del conector debe decir `PENDIENTE_DE_APROBACIÓN`, nunca `CONECTADO`.

3. **Threads es el único canal social publicable de punta a punta sin fricción.** Con la cuenta propia como tester: 250 posts/24 h y 60 días de token. Es donde la Vía B debe concentrar el volumen (5-15/día), con refresco de token a los 45 días y alerta al día 80.

4. **Rediseñar la Vía A antes de codificarla.** La estética de dashboards con cifras y lujo está prohibida por Hotmart §3.7/§3.8 (mar-2026) y castigada por Pinterest como contenido engañoso. Sustituir "captura de ingresos" por "captura de proceso" (Gumroad/Hotmart mostrando el producto y el flujo, no el dinero) mantiene el imán visual sin exponer la cuenta.

5. **Un Pin nuevo por URL, siempre.** "Redirecting existing Pins to new destinations" está en la lista de manipulación de Pinterest (may-2026). Las 55 rutas puente necesitan 55 conjuntos de pines propios; el reciclaje queda prohibido por diseño, no por buena práctica.

6. **Precio de entrada $19-$27, bump a $9, garantía configurable por API.** A $9 el fee fijo de Gumroad se lleva 15.6%; el bump solo tiene sentido sumado a un ticket de $27 o más. La `refund_policy` se fija por código y se audita.

7. **Hosting: Cloudflare Workers Static Assets + dominio propio.** GitHub Pages y Vercel Hobby quedan descartados por sus propios términos (comercial). Pages sigue funcionando pero Cloudflare ya recomienda Workers para proyectos nuevos (ago-2026).

8. **Medición honesta desde el día 1.** Webhooks con `test_event` (Gumroad) y eventos v2 (Hotmart) para probar el pipeline; headers `x-ratelimit-*` de Pinterest para el cupo; `threads_publishing_limit` antes de cada lote. Cualquier conector sin evento verificado se muestra como no conectado.

9. **Correo: usar la audiencia de Gumroad, no un SMTP propio.** `POST /v2/emails` + `send`/`schedule` con scope `edit_emails` evita montar infraestructura de deliverability y mantiene el consentimiento dentro de la plataforma que cobra.

10. **El criterio de muerte a 14 días necesita una fuente de verdad por canal**: Gumroad (`sale`), Hotmart (`PURCHASE_APPROVED`), Pinterest (impresiones vía `org_analytics`, solo con Standard) y Threads (`views`). Si un canal no puede entregar su métrica, no entra al veredicto "doblar o matar" — se marca como no medible en lugar de estimarse.
