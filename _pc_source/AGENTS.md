# Reglas Oficiales de Arquitectura y Operación — Ronin Ventas OS (@ronOverthinks)

## 1. Foco del Negocio y Decisiones de los Grills Iniciales (#1 a #7)
- **Marca y Personaje Único**: `@ronOverthinks` — Híbrido *"El Insider Cínico"* (El Analista Cínico del Dinero + El Insider de Sistemas IA).
  - **Arte Canónico (`ronin_studio`)**: Exclusivamente **Ron** (cabeza blanca ovoide, ojos grandes con pupila negra, cejas tristes, **ojeras rosa-marrón marcadas**, mechón castaño despeinado, **hoodie terracota `#E07A5F`**, piernas delgadas negras, estilo `cinematic-2d-v2` con semilla `ron_canonical_seed.png`). **Prohibido usar a Mara o cualquier otro personaje secundario**.
- **Las 3 Vías de Contenido Agresivo (5–15 piezas/día en Español)**:
  - **Vía A — Capturas "Anzuelo" (El Imán Visual)**: Pantallas de bloqueo iOS 17.5 con notificaciones de Gumroad (`#FF90E8`) y Hotmart (`#F04E23` en COP/Nequi/PSE), Dashboards de Stripe Express con cifras impares (`$418.50`, `$1,940.20`) y Notas de iPhone a las 3:14 AM sin hacer promesas directas de ingresos.
  - **Vía B — Ragebait Cínico & Preguntas Trampa (Threads)**: Ataques al ego, falsos dilemas y verdades incómodas con 2 auto-respuestas encadenadas en la 1ª hora para multiplicar el alcance algorítmico.
  - **Vía C — Pines "Caballo de Troya" 2:3 + Pines de Producto con Identidad (Pinterest Mix 70% / 30%)**:
    - **70% Pines de Impresión Fría (Dark Luxury & Capturas)**: Fotografía editorial *Dark Luxury* (Ficha de Ajedrez Obsidiana/Oro, Setup de Lujo OLED, Reloj Negro/Espresso, Terminales y Capturas iOS) con tipografía de póster legible a 236px para maximizar impresiones en frío.
    - **30% Pines de Llamado Directo a Producto con Identidad de Ron (`ronin_studio`)**: Pines enfocados en presentar los productos del catálogo (Blueprints, Bóvedas, Micro-Apps) que **SÍ utilizan el arte canónico 2D de Ron** (`pin_ron_3am_blueprint.png`, `pin_ron_threads_atm.png`, `pin_ron_escape_matrix.png`, `pin_ron_dark_psychology.png`) para inyectar identidad de marca (`@ronOverthinks`) y conversión directa hacia las 55 rutas puente únicas sin repetir URL en <72h.
- **Catálogo de 55 SKUs (52 de Pago + 3 Lead Magnets — Grill #1 y #2)**:
  - Concentrado en 4 nichos de alta conversión (Dinero Digital Faceless 35%, IA & Automatización Injusta 30%, Psicología Oscura del Dinero/Atención 20%, Escape 9-a-5 & Finanzas Cínicas 15%):
  - 12 Ebooks Blueprint (`E01`–`E12`), 12 Bóvedas/Arsenales (`B01`–`B12`), 12 Micro-Apps Interactivas HTML (`A01`–`A12`), 10 Kits Combinados (`K01`–`K10`), 6 Mega-Bundles (`M01`–`M06`) y 3 Lead Magnets (`L01`–`L03`).
- **Puente de Conversión (Grill #3)**: Clon propio de Stan Store Pro + 55 rutas puente semánticas únicas (`/blueprint/...`, `/boveda/...`, `/app/...`, `/sistema/...`, `/vault/...`) con doble checkout (**Hotmart LatAm** Nequi/PSE/Efecty + **Gumroad Global** USD/Apple Pay) y Order Bump interactivo (`+$9 USD`).
- **Los 7 Módulos Oficiales del Aplicativo Escritorio + Móvil LAN (Grill #5, #6A, #6B, #7)**:
  1. Clon Visual de Threads (Dark Mode `#0a0a0a` 1:1)
  2. Clon Visual de Pinterest (Masonry Grid 236px + Modo Infiltración)
  3. Laboratorio de Capturas Anzuelo iPhone 15 Pro + Vertex AI Nano Banana 2 (`example-project-id`, `global`, `gemini-3.1-flash-image` con fallback `gemini-3.1-flash-lite-image`)
  4. Fábrica & Bóveda de los 55 Productos (con visor `.HTML` integrado)
  5. Constructor Stan Store Pro + 55 Mini-Landings & Centro Stealth (`liarjs` + Chrome Persistente)
  6. Radar de Métricas, Ventas y Criterio de Muerte 14 Días ("Doblar o Matar")
  7. Customizations & Connectors Hub (SSO 1-Clic en Chrome Persistente + 112 Skills Globales)
- **Servidor Dual Escritorio + Móvil en Misma Red (LAN `0.0.0.0:8765`)**:
  - Escucha en `0.0.0.0:8765` con diseño 100% responsive (Sidebar en PC + Barra Inferior iOS Glass en Móvil) accesible desde cualquier celular en el mismo Wi-Fi (`http://<LAN_IP>:8765`).

## 2. Límite Atómico de Código y Verificación Real
- **Límite Estricto de 250 Líneas**: Ningún archivo `.py`, `.ts` o `.tsx` fuera de `data/` puede superar las **250 líneas** (`test_strict_atomic_file_line_limit` en `tests/test_bloque1.py`).
- **Entorno Python Oficial**: el proyecto usa su **propio entorno aislado** en `C:\Users\EXAMPLE\Documents\ronin_ventas\.venv`. Nunca se usa el venv de otro proyecto. Backend y `pytest` se ejecutan siempre con `".\.venv\Scripts\python.exe"`.
- **Cero Placeholders en Productos**: Todo entregable en `data/deliverables/*.html` debe ser 100% funcional offline, con CSS/JS real y protegido contra sobrescritura accidental.
- **Prohibido el estado falso**: ningún conector puede reportarse `CONECTADO` sin evidencia medida. Ningún diagnóstico se siembra a mano. `tests/test_honesty.py` lo impone.

## 2.1 Entorno de Verificación Mínimo
```powershell
cd C:\Users\EXAMPLE\Documents\ronin_ventas
.\.venv\Scripts\python.exe -m pytest tests -q
cd frontend; npm run build; npx tsc --noEmit
```

## 3. Gobernanza de Subagentes y Modelos
- **Crítico Cínico (`cynical-critic`)**: Único subagente autorizado para usar `Model="inherit"` (Gemini 4 Argon). Audita sin piedad la estética 1:1 y los entregables.
- **Subagentes Constructores de UI**: Invocar siempre con `Model="flash"` (Gemini 3.8 Flash) para tareas paralelas de frontend/componentes.
- **Fábrica de Productos en OpenCode V2**: Usar `http://127.0.0.1:28894` con `opencode-go/deepseek-v4.1-flash` en variante `max` (`cost: 0`), reutilizando la sesión `ses_e64c0d9b1ffe56MtJmi0RNNym4`.

## 4. Estándar Visual 1:1 (Cero Emojis en Réplicas)
- Prohibido usar emojis del sistema en toda la UI. Usar exclusivamente vectores SVG oficiales, arte canónico de Ron (`ronin_studio`), fondos fotográficos reales de Vertex AI Nano Banana 2 y sombras ópticas de hardware real.
