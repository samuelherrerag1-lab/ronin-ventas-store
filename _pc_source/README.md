# Ronin Ventas OS — `@ronOverthinks`

Aplicativo de escritorio + móvil LAN (FastAPI + React) para operar el negocio de
productos digitales: 55 SKUs, 55 rutas puente de conversión, fábrica de capturas
"anzuelo", clones visuales de Threads/Pinterest, radar de métricas y hub de
conectores con diagnóstico honesto.

## Arranque rápido

```powershell
cd C:\Users\EXAMPLE\Documents\ronin_ventas
start_ronin_os.bat
# PC:  http://127.0.0.1:8765
# Móvil (misma Wi-Fi): http://<LAN_IP>:8765
```

Si el entorno no existe:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
cd frontend; npm install; npm run build; cd ..
```

## Verificación obligatoria

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
.\.venv\Scripts\python.exe scripts\validate_deliverables.py
.\.venv\Scripts\python.exe scripts\probe_vertex.py
cd frontend; npx tsc --noEmit; npm run build
```

## Vertex AI (Nano Banana 2)

- Proyecto: `REDACTED_EXAMPLE_PROJECT` (override: `GOOGLE_CLOUD_PROJECT`).
- Región: `global`. Modelo: `gemini-3.1-flash-image`, fallback `gemini-3.1-flash-lite-image`.
- Auth: ADC de gcloud (`gcloud auth application-default login`). No se usa API key.
- Coste real registrado en `data/finops-ledger.json`; corte duro en `FINOPS_CIRCUIT_BREAKER_USD`.
- Sonda sin gasto de UI: `scripts\probe_vertex.py` (genera 1 imagen de prueba real).

## Publicar (orden recomendado)

1. `POST /api/catalog/{sku_id}/checkout` o el formulario del Publish Center para
   pegar la URL de Gumroad/Hotmart de cada SKU. Sin URL, la landing dice la
   verdad ("checkout aún no configurado") y no muestra un botón falso.
2. Generar el sitio estático: `.\.venv\Scripts\python.exe scripts\build_publish_pack.py --base-url https://tu-dominio`.
   Salida: `data/publish_site/` con la tienda, las 55 rutas puente, portadas,
   sitemap, robots y la cola de contenido (`content/threads.json`, `content/pinterest.json`).
3. Revisar la cola de contenido y publicar manualmente en Threads/Pinterest
   (el sistema marca el estado local, no publica en la red por ti).
4. Desplegar el sitio: `scripts\deploy_store.ps1 -Confirm` (GitHub Pages, `gh`
   ya autenticado). Sin `-Confirm` solo imprime el plan.

## Estructura

```
backend/            FastAPI: routers, servicios, modelos
frontend/           React 18 + Vite + Tailwind (dist se sirve desde FastAPI)
data/               catálogo, feeds, métricas, entregables, arte, ledger
scripts/            sondas y generadores (Vertex, arte, validación, sitio)
tests/              pytest (honestidad, rutas, entrega, métricas, publicar)
docs/               plan, research, auditorías y reportes
```

## Seguridad de la red local

El servidor escucha en `0.0.0.0:8765` para que el móvil pueda usarlo, y por
diseño la API no pide login. Si no confías en todos los dispositivos del Wi-Fi:

```powershell
$env:RONIN_API_TOKEN = "REDACTED_EXAMPLE_CREDENTIAL"
start_ronin_os.bat
```

Con `RONIN_API_TOKEN` definida, toda escritura (`POST/PUT/PATCH/DELETE`) exige
`X-Ronin-Token` o `?token=...`. Ojo: la UI del Publish Center no envía el token
todavía, así que si lo activas úsalo desde `curl`/scripts o añade el header a
mano. Los endpoints caros (`test-all`, `vertex-generate`) tienen además
rate-limit de 1 llamada cada 20 s por cliente.

Los entregables de pago solo se sirven a `localhost` (equipo del operador);
desde cualquier otra IP devuelven 403. Los 3 lead magnets son públicos. El sitio
estático (`/store`) solo contiene landings y los lead magnets.

## Datos que no se versionan

`data/chrome_vault/`, `data/generated_images/`, `data/product_art/`,
`data/publish_site/`, `.venv/`, `frontend/node_modules/`, `frontend/dist/`
(ver `.gitignore`).

## Reglas del proyecto

Ver [`AGENTS.md`](AGENTS.md): 250 líneas por archivo, cero placeholders, cero
emojis en UI, cero estados falsos, entorno Python aislado.
