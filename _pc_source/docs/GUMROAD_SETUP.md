# Gumroad REAL — alta de los 52 productos (estado 2026-11-04/05)

Documento operativo del conector **Gumroad v2** de Ronin Ventas OS: cómo se obtuvo
el token, cómo se crean los productos con entrega y portada, qué se ejecutó de
verdad, qué bloqueos externos aparecieron y cómo terminar el trabajo.

## 1. Cuenta y token (verificado, no simulado)

| Campo | Valor real |
| --- | --- |
| Email | `example@example.invalid` |
| Nombre | ron Broken |
| user_id | `EXAMPLE_ACCOUNT_ID` |
| Token | `data/secrets.json` (masked `EXAMPLE_MASKED_CREDENTIAL`), nunca se imprime completo |
| Validación | `GET https://api.gumroad.com/v2/user` → 200 + `success:true` |
| Cómo se obtuvo | Login humano una vez en Chrome persistente (`data/chrome_vault`, `channel="chrome"`); después Settings → Advanced → aplicación de API → *Generate access token* automatizado con Playwright |

La cookie `_gumroad_app_session` que ya estaba en el perfil **no era válida**
(Gumroad redirigía a `/login`): el login humano era imprescindible. Una vez
extraído, el token sirve para todas las llamadas siguientes sin navegador.

## 2. Qué se creó de verdad (evidencia de API)

`data/gumroad_products.json` es el mapa auditable:
`{sku_id: product_id, gumroad_url, published, file_attached, cover_attached, price_cents, warnings}`.

| Métrica | Valor |
| --- | --- |
| SKUs de pago en catálogo | 52 |
| Productos creados en Gumroad | **10** (E01–E10) |
| Con archivo adjunto | **10/10** |
| Con portada adjunta | **10/10** |
| Publicados | **0** (bloqueo externo §4.2) |
| Bloqueados por cupo diario | 42 |
| URLs en `data/catalog.json` | **10** (decisión del Lead: persistir las 10; son reales pero los borradores no son comprables) |
| Readiness `checkouts_gumroad` | **0 → 10** |

Productos reales (id → URL de checkout):

- E01 `b2Q_yHRRl5p-u5GAntbGqA==` → https://ronbroke.gumroad.com/l/maquina-silenciosa-pdf
- E02 `Chq8pigjIVeg9801nnSGgQ==` → https://ronbroke.gumroad.com/l/pinterest-cajero-oculto
- E03 `3pM22hjy4P1hpIOZXU0Uyg==` → https://ronbroke.gumroad.com/l/threads-algoritmo-polarizacion
- E04 `gIKWLAj6hYmYm_-jb5fVTg==` → https://ronbroke.gumroad.com/l/imperio-faceless-48h
- E05 `dRfWGlG9S7fMr4KE5DhB1A==` → https://ronbroke.gumroad.com/l/arquitectura-clonacion-ia
- E06 `aVTJFwKqqLFlkaKxNk0VZg==` → https://ronbroke.gumroad.com/l/fabrica-productos-1-hora
- E07 `b-2unCXuyPfSceP-nKPnoQ==` → https://ronbroke.gumroad.com/l/empleados-fantasma-ia
- E08 `8Mngev25DBtpiWsNizCK-A==` → https://ronbroke.gumroad.com/l/psicologia-oscura-precio
- E09 `f_TCvF4OseR76e-sCBjttQ==` → https://ronbroke.gumroad.com/l/secuestro-atencion-3-segundos
- E10 `l0LOaiCbx31emLhXgcEaig==` → https://ronbroke.gumroad.com/l/efecto-halo-autoridad

Verificación pública real de E01 (GET sin token):
`HTTP 200 · title="La Máquina Silenciosa de Archivos PDF" · precio="19.0" ·
archivo 141.484 bytes · 1 cover`. La página existe y muestra título/precio, pero
**no es comprable**: el producto es borrador y no hay botón de compra. Las URLs
se persistieron en el catálogo por instrucción del Lead para que readiness
cuente 10 checkouts; **no hay que tratarlas como venta activa** hasta publicar.

## 3. Contrato real de la API v2 usado

Base: `https://api.gumroad.com/v2` · auth `Authorization: Bearer <token>`.

1. **Crear producto**: `POST /products` con `name`, `price` (céntimos),
   `price_currency_type=usd`, `custom_permalink=<slug>`, `description` (HTML),
   `draft=true`, `published=false`, `tags[]`, `files[][url]=<file_url>`.
2. **Subir archivo** (3 pasos): `POST /files/presign` (`filename`, `file_size`)
   → `PUT` de los bytes a cada `part.presigned_url` capturando el header `ETag`
   → `POST /files/complete` con `upload_id`, `key` y los pares
   `parts[][part_number]` + `parts[][etag]` **intercalados** (enviarlos como
   JSON string da HTTP 400 "each part must have scalar part_number and etag
   values").
3. **Portada/miniatura**: `POST /direct_uploads` con `blob[filename]`,
   `blob[byte_size]`, `blob[checksum]` (MD5 base64), `blob[content_type]`
   (solo `image/jpeg|png|gif`) → `PUT` a `direct_upload.url` → `POST
   /products/:id/covers` con `signed_blob_id`. Ojo: `/direct_uploads` responde
   200 **sin** campo `success`.
4. **Publicar / despublicar**: `PUT /products/:id/enable` · `PUT
   /products/:id/disable` · `DELETE /products/:id`.
5. **Verificación**: `GET /user`, `GET /products`, `GET /products/:id`
   (devuelve `files` y `covers`; la lista no devuelve `files`).

## 4. Bloqueos externos reales (no son bugs del código)

### 4.1 Límite diario de creación: 10 productos/día

Al crear el producto 11 la API responde HTTP 200 con
`{"success": false, "message": "Sorry, you can only create 10 products per day."}`.

Causa en el código de Gumroad (`app/modules/product/creation_limit.rb`): cuentan
los productos **vivos** creados en las últimas 24 h y el límite es
`compliant? ? 100 : 10`. Esta cuenta tiene `user_risk_state` distinto de
`compliant` (vendedor nuevo sin método de pago/KYC), así que el tope es 10 cada
24 h rodantes. Es una validación del modelo `Product`, por lo que **también
bloquea la UI web**: no se puede saltar con navegador. Borrar un producto libera
cupo.

Desbloqueo: `Settings → Payments` (conectar payout) + verificación/KYC. Cuando
la cuenta pase a `compliant`, el cupo sube a 100/día y los 42 restantes se crean
en una sola ejecución.

### 4.2 No se puede publicar sin método de pago

`PUT /products/<id>/enable` → HTTP 200 con
`{"success": false, "message": "You must connect at least one payment method before you can publish this product for sale."}`.

Se intentó publicar 5 productos reales (E01, E02, E03, E04, E05): **0 publicados**,
los 5 devolvieron ese mensaje. El script lo reporta como fallo honesto
(`published: false`), nunca como éxito. Hasta que el dueño conecte un método de
pago en Gumroad no se puede vender ningún producto.

## 5. Comandos (idempotentes)

```powershell
# 1) Login humano UNA vez (solo si no hay token guardado)
.\.venv\Scripts\python.exe scripts\gumroad_setup.py login --wait 3600

# 2) Validar token guardado
.\.venv\Scripts\python.exe scripts\gumroad_setup.py token

# 3) Crear/actualizar borradores. Idempotente: busca por custom_permalink y no
#    sube archivo ni portada si ya existen. Se detiene solo al agotar el cupo.
.\.venv\Scripts\python.exe scripts\gumroad_setup.py create
.\.venv\Scripts\python.exe scripts\gumroad_setup.py create --only E01 --limit 1

# 4) Reintentar SOLO los bloqueados por cupo (los 42), opcionalmente en tanda
.\.venv\Scripts\python.exe scripts\gumroad_setup.py retry-blocked --max 10

# 5) Publicar flagship (exige archivo adjunto + método de pago de la cuenta)
.\.venv\Scripts\python.exe scripts\gumroad_setup.py publish --skus E01,B01,A01,K01,M06

# 6) Persistir en catálogo: por defecto solo publicados; --all incluye borradores
.\.venv\Scripts\python.exe scripts\gumroad_setup.py apply-catalog
.\.venv\Scripts\python.exe scripts\gumroad_setup.py apply-catalog --all

# 7) Verificar URLs publicadas con GET público y ver el reporte completo
.\.venv\Scripts\python.exe scripts\gumroad_setup.py verify
.\.venv\Scripts\python.exe scripts\gumroad_setup.py report

# 8) Todo en uno: token + crear + publicar + catálogo + verificar
.\.venv\Scripts\python.exe scripts\gumroad_setup.py sync
```

### 5.1 Plan de 5 días (cupo 10/día) y scheduler diario

Orden exacto para terminar los 42 restantes sin tocar nada a mano:

1. **Día 1 (hoy)**: 10 creados (E01–E10). Nada más que hacer.
2. **Día 2–5**: una vez cada 24 h, ejecutar
   `.\.venv\Scripts\python.exe scripts\gumroad_setup.py retry-blocked --max 10`
   (crea hasta 10 y deja el resto en `blocked_quota`). Repetir hasta que
   `created` llegue a 52.
3. **Cuando el dueño conecte método de pago**:
   `publish --skus E01,B01,A01,K01,M06` (publica los flagship que existan) y
   `apply-catalog` (persiste solo los comprables). `verify` confirma título/precio.
4. Si la cuenta pasa a `compliant` (KYC/payout), `retry-blocked` crea los 42 de
   golpe porque el cupo sube a 100/día.

Scheduler diario con Windows Task Scheduler (recomendado, documentado; no se
creó la tarea automáticamente porque es un cambio de sistema):

```powershell
# Ejecutar cada día a las 09:00 (ajustar la ruta al repo real)
schtasks /Create /TN "Ronin Gumroad retry" /SC DAILY /ST 09:00 /F `
  /TR "cmd /c cd /d C:\Users\EXAMPLE\Documents\ronin_ventas && .venv\Scripts\python.exe scripts\gumroad_setup.py retry-blocked --max 10 >> data\_locks\gumroad_retry.log 2>&1"
# Comprobar / borrar la tarea
schtasks /Query /TN "Ronin Gumroad retry"
schtasks /Delete /TN "Ronin Gumroad retry" /F
```

Alternativa sin Task Scheduler: un job de PowerShell con `Start-Sleep` diario o
el `sync` al final del día (idempotente, no duplica y se detiene solo en el
tope). El estado queda siempre en `data/gumroad_products.json`; el log en
`data/_locks/gumroad_retry.log`.

## 6. Tests y honestidad

- `tests/test_gumroad_products.py` (cliente) + `tests/test_gumroad_catalog_sync.py`
  (motor): **16 tests con HTTP mockeado**. Ningún test llama a Gumroad; cualquier
  URL no registrada en el mock hace fallar el test (`AssertionError`), lo que
  garantiza cero red. Los fakes viven en `tests/gumroad_fakes.py`.
- Cubre: Bearer + `/user`, error 401, presign/PUT/complete con ETag intercalado,
  direct upload con checksum, creación con `draft`+archivo+cover, idempotencia
  por permalink, entregable ausente (no crea), cupo diario (detiene y no sube el
  resto), publicación solo con archivo, persistencia de catálogo (publicados sí
  / borradores no por defecto), descripción sin promesas de ingresos y
  conversión webp→JPEG.
- Límite de 250 líneas respetado en todos los módulos y tests nuevos (se dividió
  en `gumroad_browser.py`, `gumroad_media.py` y dos archivos de test).

## 7. Rollback / limpieza

- Despublicar: `PUT /products/:id/disable`.
- Borrar un producto: `DELETE /products/:id` con el token (irreversible; libera
  cupo según el comentario del código de Gumroad).
- Estado local: `data/gumroad_products.json` (mapa) y `data/secrets.json`
  (token). Borrar el token de `secrets.json` invalida el conector local sin
  tocar la cuenta.
- Los archivos subidos a S3 de productos que fallaron al crearse quedan
  huérfanos; no afectan a la cuenta ni se facturan.

## 8. Riesgos conocidos

- `custom_permalink` debe ser único en la cuenta; si ya existe, Gumroad
  devuelve error y el SKU queda en `failed` (el script no lo renombra solo).
- En catálogo hay 10 URLs de borradores (decisión del Lead): readiness las
  cuenta como checkout, pero no son comprables hasta publicar. `apply-catalog`
  sin `--all` evita ese estado falso.
- Un precio USD se envía en céntimos; `price_currency_type=usd`.
- 429 esporádicos de la API: el cliente reintenta 2 veces con espera corta; una
  nueva ejecución de `create`/`retry-blocked` retoma donde quedó.
