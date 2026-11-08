# Estrategia de Marketing — @ronOverthinks ("El Insider Cínico")

**Estado:** operativa, lista para ejecutar. Campaña de 30 días ya cargada en el sistema.
**Moneda de trabajo:** USD (cobro) / COP (costo de vida). **Zona horaria:** America/Bogota.
**Fecha de arranque de la campaña:** 2026-11-09 (30 días → 2026-12-08).
**Precios:** todos salen de `data/catalog.json`; no hay precios inventados en este documento.

---

## 0. Resumen ejecutivo

| Hecho | Número / estado |
|---|---|
| Catálogo | 55 SKUs: 12 ebooks, 12 bóvedas, 12 micro-apps, 10 kits, 6 mega-bundles, 3 lead magnets |
| Precios de pago | 15–34 (piezas), 39–49 (kits), 69–149 (bundles) |
| Suma de los 52 productos de pago | **US$1,797** (verificado contra el catálogo) |
| Campaña cargada | **210 piezas**: 150 Threads + 60 Pinterest, 7 piezas/día × 30 días |
| Cobertura de catálogo | **55/55 SKUs** al menos una vez |
| Copy bank | 150 posts de Threads + 60 pines completos, en español, sin promesas de ingresos |
| Restricción cumplida | 0 repeticiones de URL en Pinterest con <72 h de separación |
| Inversión variable de contenido | ~US$4.02 de imágenes para 60 pines (US$0.067/imagen) |
| Lo que este plan NO promete | Ingresos. Se venden mecanismos, no resultados. |

El sistema publica solo: la cola está en `data/social_feeds.json` con `status: "queued"`.
Este documento explica **a quién** le habla esa cola, **a qué precio**, **con qué reglas** y **cuándo se mata**.

---

## 1. ICP y dolores

### 1.1 ICP primario — "El Emprendedor Cínico de LatAm"

| Dimensión | Detalle |
|---|---|
| Edad | 24–38 |
| Geografía | Colombia, México, Argentina, Chile, Perú, Ecuador (pago en Nequi/PSE/Efecty o tarjeta) |
| Ingreso actual | US$400–1,200/mes en moneda local; sueldo fijo o freelance |
| Ocupación | Empleado, diseñador, soporte, estudiante de posgrado, freelance saturado de horas |
| Consumo cultural | Threads, Pinterest, YouTube de negocios, TikTok de IA; desconfía de "gurús" con Lamborghini |
| Herramientas que ya paga | ChatGPT o Gemini (a veces ambos), Canva, alguna suscripción de IA que no usa |
| Experiencia de compra | Ya compró un curso de $9–15 que no terminó. Sabe que el problema fue la ejecución, no el contenido |
| Motivación real | Dejar de cambiar horas por una moneda que se devalúa. No quiere "ser famoso", quiere margen |
| Bloqueo emocional | No quiere mostrar la cara, no quiere venderle a sus amigos, no quiere parecer "vendedor de humo" |
| Nivel de conciencia | Consciente del problema, inconsciente de la solución: cree que necesita audiencia, no **ruta** |

**Día típico del ICP:** abre Threads en el transporte (07:00–08:00), revisa Pinterest en la pausa del almuerzo (12:00–13:00), vuelve a redes entre 19:00 y 22:00 con culpa de no haber ejecutado nada. Compra en el celular si el checkout acepta Nequi.

### 1.2 Dolores ordenados por intensidad (y la pieza que los ataca)

| # | Dolor | Cómo lo dice el ICP | Objeción que aparece | SKUs que lo atacan |
|---|---|---|---|---|
| 1 | No sabe qué vender | "Tengo mil ideas y ninguna publicada" | "¿Y si nadie lo compra?" | B02, E04, E06, A06, M01 |
| 2 | No quiere mostrar la cara | "No voy a grabar videos" | "Sin cara no se puede vender" | E01, E02, E04, K01, K04 |
| 3 | Sabe que le falta distribución | "Publico y nadie lo ve" | "Necesito seguidores primero" | E02, E03, B03, B09, K02, K03 |
| 4 | No entiende el precio | "Vendo barato porque nadie compra" | "$19 es mucho para LatAm" | E08, A09, B10, K08 |
| 5 | Paga IA y no la convierte en activos | "Tengo ChatGPT y sigo igual" | "La IA escribe basura" | E05, E06, B05, B06, A05, M02 |
| 6 | Siente que su moneda le juega en contra | "Trabajo 45 h y no me alcanza" | "Aquí no se puede" | E11, E12, A11, A12, B11, M04 |
| 7 | Escribe y no engancha | "Nadie comenta mis posts" | "No soy bueno escribiendo" | E09, B01, B09, A01, A08, K09 |
| 8 | No tiene autoridad | "¿Por qué me van a comprar a mí?" | "No soy nadie en internet" | E10, B08, A10, K10 |

### 1.3 Anti-ICP (a quién NO se le habla)

- Quien busca cripto, trading, apuestas o "dinero rápido": no hay producto para él y contamina la cuenta.
- Quien quiere mentoría 1:1 o llamadas: no existe esa oferta y no debe insinuarse.
- Quien no va a ejecutar nada: no compra dos veces y arruina la señal de conversión.
- Quien quiere ser "influencer famoso": el posicionamiento es anónimo por diseño.

### 1.4 Jobs to be done

1. **"Dame el mecanismo, no la motivación"** → comprar un blueprint y ejecutarlo esta semana.
2. **"Hazme parecer listo sin exponerme"** → publicar contenido que se comparte sin mostrar la cara.
3. **"Muéstrame la aritmética"** → modelar cuántas ventas de $19 cubren su costo de vida.

### 1.5 Lenguaje del cliente vs. lenguaje prohibido

| El ICP dice | Nosotros decimos | Nunca decimos |
|---|---|---|
| "plata", "dólares", "lucas", "Nequi" | "cobrar en dólares", "checkout con Nequi o PSE" | "libertad financiera total" |
| "me quedé sin ideas" | "página en blanco", "falta de repertorio" | "desbloquea tu potencial infinito" |
| "me da pena vender" | "no quieres parecer vendedor de humo" | "vencer el miedo" |
| "no sé si funciona" | "esto es lo que contiene exactamente" | "método comprobado al 100%" |
| "está caro" | "el precio real es $19; si no te sirve, el anzuelo es gratis" | "descuento solo por hoy" |

---

## 2. Posicionamiento

### 2.1 Declaración

> **Para** el emprendedor latinoamericano de 24–38 años que quiere cobrar en dólares sin mostrar la cara,
> **que** ya probó un curso barato y sabe que el problema es la ejecución,
> **@ronOverthinks** es **el insider que te entrega el mecanismo y la aritmética de una oferta digital**,
> **porque** documenta la estructura exacta (oferta, ruta puente, pin, hook, checkout) en lugar de motivar.

**Promesa:** *te vendo el mecanismo, no la motivación.* El resultado depende de si lo ejecutas; la promesa de ingresos no existe y no se insinúa.

### 2.2 Los tres pilares (y su prueba)

| Pilar | Qué significa | Prueba que ya está en disco |
|---|---|---|
| **Mecanismo** | Cada producto es un procedimiento con pasos, no una colección de consejos | 55 SKUs con `deliverable_spec` y entregables offline en `data/deliverables/` |
| **Aritmética** | Precio, comisión, unidades y punto de equilibrio siempre explícitos | Tabla de §3.2 con precios reales del catálogo |
| **Anonimato** | Todo el sistema está diseñado para operar sin cara ni cámara | 60 pines + 150 posts sin una sola pieza que pida rostro |

### 2.3 Diferenciación (swap test)

| Competidor típico | Su promesa | Lo que nosotros decimos y él no puede decir |
|---|---|---|
| Gurú motivacional | "Cambia tu mentalidad y el dinero llega" | "Así se calcula el margen después de la comisión de pasarela" |
| Curso de Canva a $9 | "150 plantillas editables" | "150 ángulos de pin con overlay, título y descripción listos" |
| Tool de IA al mes | "Escribe 100 posts con IA" | "Un archivo HTML offline que no cobra suscripción y no manda tus datos" |
| Agencia de tráfico | "Te llevamos 10k visitas" | "La ruta puente concreta y el tablero de Pinterest que la alimenta" |

Si una frase de marca puede decirla un competidor sin cambiar nada, no es nuestra frase: se reescribe.

### 2.4 Voz

- **Cínico con el sistema, no con la persona.** El enemigo es la estructura (algoritmo, pasarela, sueldo fijo), nunca el seguidor.
- Frases cortas, primera línea sin contexto, cero emojis, cero signos de exclamación.
- Cifras impares y concretas cuando son ciertas (18 páginas, 500 hooks, 4.8% de conversión de ruta). Cifras inventadas de ventas: prohibidas.
- Humor seco, nunca sarcasmo sobre la situación económica del lector.

### 2.5 Las tres vías de contenido (mapeadas al sistema)

| Vía | Formato | Canal | Lane en el código | Función |
|---|---|---|---|---|
| **A — Captura anzuelo** | iOS lockscreen / nota 3:14 AM / dashboard | Threads (60 piezas) | `via_a_captura_anzuelo` | Detener el scroll y demostrar que existe un artefacto verificable |
| **B — Ragebait cínico** | Hilo de 3–4 láminas | Threads (60 piezas) | `via_b_ragebait_cinico` | Abrir debate, multiplicar respuestas |
| **C — Demo micro-app / caballo de Troya** | Carrusel o pin 2:3 | Threads (30 piezas) + Pinterest (60 pines) | `via_c_demo_microapp`, `caballo_de_troya_curiosidad`, `dinero_ia_directo`, `demo_herramienta_html` | Convertir curiosidad en clic a la ruta |

---

## 3. Arquitectura de oferta y economía unitaria

### 3.1 Escalera (precios reales, sin placeholders)

| Peldaño | Precio | SKUs | Rol en el embudo | CTA |
|---|---|---|---|---|
| 0. Anzuelo | **$0** | L01, L02, L03 | Captura de email y prueba de método | "Descarga sin tarjeta" |
| 1. Entrada | **$15–19** | E01, E02, E03, E06, E09, E10, E11, B01, B03, B08, B09, B11, B12, A07, A11 | Primera compra, valida tarjeta | "Ruta directa" |
| 2. Núcleo | **$21–27** | E04, E05, E08, E12, B02, B04, B05, B06, B10, A02, A04, A09, A10, A12 | Ticket medio, mayor margen | "Sistema completo" |
| 3. Herramienta | **$29–34** | E07, B07, A01, A03, A05, A06, A08 | Atajo percibido (app offline) | "Ábrelo hoy" |
| 4. Kit | **$39–49** | K01–K10 | Consolida 3 activos, sube AOV | "Pack de ejecución" |
| 5. Bundle | **$69–149** | M01 $79 · M02 $89 · M03 $79 · M04 $69 · M05 $99 · M06 $149 | Techo de ticket y ancla de precio | "Vault completo" |
| Bump | **+$9** | (orden bump en checkout) | Sube el ticket sin fricción | "Añadir al pedido" |

Reparto exacto: 15 piezas de entrada + 14 de núcleo + 7 de herramienta = 36; 10 kits + 6 bundles + 3 anzuelos = 55 SKUs.

**Ancla de precio (verificada):** el catálogo completo cuesta **$1,797** comprado por piezas. M06 cuesta **$149**: un 91.7% menos. Ese es el argumento de bundle y es aritmética, no marketing.

**Costo por activo dentro del bundle:** M06 = $2.87/activo (52) · M01 = $6.58 (12) · M04 = $8.63 (8) · M05 = $8.25 (12) · M02 = $7.42 (12). Kits de 3 activos = $13.00–16.33 por activo.

### 3.2 Economía unitaria por precio (pasarelas reales, supuestos declarados)

Supuestos de comisión — **a verificar en el panel antes de escalar**:
Gumroad = 10% + $0.50 por venta. Hotmart LatAm = 9.9% + $1.00 (Nequi/PSE/Efecty).
Reserva de reembolso = 3% del neto. Costo de entrega digital ≈ $0.

| Precio | Neto Gumroad | Neto Hotmart | Neto tras reembolsos (3%) | Ventas para $1,000 netos (Gumroad) |
|---|---|---|---|---|
| $15 | 13.00 | 12.52 | 12.61 | 77 |
| $17 | 14.80 | 14.32 | 14.36 | 68 |
| $19 | 16.60 | 16.12 | 16.10 | **61** |
| $24 | 21.10 | 20.62 | 20.47 | 47 |
| $27 | 23.80 | 23.33 | 23.09 | 42 |
| $34 | 30.10 | 29.63 | 29.20 | 33 |
| $39 | 34.60 | 34.14 | 33.56 | 29 |
| $49 | 43.60 | 43.15 | 42.29 | 23 |
| $69 | 61.60 | 61.17 | 59.75 | 16 |
| $79 | 70.60 | 70.18 | 68.48 | 14 |
| $99 | 88.60 | 88.20 | 85.94 | 11 |
| $149 | 133.60 | 133.25 | 129.59 | **8** |

**Lectura estratégica:** 61 ventas de $19 o 8 ventas de $149 producen el mismo neto. El plan no empuja el precio más alto desde el día 1 (falta confianza), sino que **mezcla**: volumen de $19 para conseguir señal de compra y bundles para el margen.

### 3.3 Costos reales del sistema (no estimados)

| Concepto | Costo | Fuente |
|---|---|---|
| Imagen de pin (Vertex Nano Banana 2) | **$0.067 / imagen** | `backend/config.py` → `IMAGE_COST_USD` |
| 60 pines de la campaña (1 diseño c/u) | **$4.02** | 60 × 0.067 |
| 90 pines (3 diseños por URL, plan de frescura) | **$6.03** | 90 × 0.067 |
| Servidor, app de escritorio, generadores | $0 (local) | sin dependencia de nube |
| Comisión de pasarela | 9.9–10% + fijo | §3.2 |
| Reembolsos | 3% reservado | supuesto, medir en semana 2 |

**Punto de equilibrio del mes:** con 60 pines ($4.02) y 150 posts ($0), **una sola venta de $19** cubre el costo variable de todo el mes de contenido. Todo lo demás es margen de contribución.

### 3.4 Fórmula de LTV por cohorte (para reemplazar supuestos con datos)

```
LTV_90d = (compra_entrada × P(entrada→kit) × precio_kit)
        + (compra_entrada × P(bump)) × 9
        + (compra_entrada × P(recompra))
```

Escenario de trabajo (supuestos, no resultados): 100 leads → 10 compran $19 (10%) → 3 toman bump $9 (30%) → 2 compran un kit de $39 (20%).
Ingreso por 100 leads = 190 + 27 + 78 = **$295** → **$2.95 por lead**. Este número se corrige con datos reales el día 14; hasta entonces es una hipótesis de trabajo, no una promesa.

### 3.5 Reglas de la escalera

1. Nunca se baja el precio de un SKU existente: se crea un kit o se cambia el bundle.
2. El CTA de cada pieza apunta a **una** ruta puente (la de su `sku_id`), no al catálogo.
3. El bump de $9 se ofrece después del pago, nunca antes.
4. Los bundles no se descuentan por temporada: el precio es el precio (la cuenta ya es un 91.7% off frente a la suma).

---

## 4. Canales

### 4.1 Threads — orgánico, *reply-first*

- **Rol:** descubrimiento y conversación. Aquí se gana el interés; la venta ocurre en la ruta puente.
- **Mecánica central:** el algoritmo pesa más las respuestas que los posts, y la **velocidad en la primera hora** es el factor #1. Publicar sin quedarse a responder es regalar el alcance.
- **Regla de oro:** por cada post propio, **al menos 4 respuestas** ajenas ese día. El crecimiento se compone en 60–90 días, no en 7.
- **Formato:** texto + imagen (la imagen sube el alcance), un solo *topic tag*, ≤500 caracteres por bloque.
- **Cadencia del plan:** 5 posts/día (07:10, 12:20, 15:40, 18:50, 21:30 Bogotá), decidida por el dueño. El playbook de §5 dice cómo sostenerla sin quemar la cuenta.

**Tensión documentada:** la guía de plataforma recomienda 3–5 posts/semana, no 5/día. Este plan corre 5/día durante 14 días como **test**, con criterio de corte explícito en §8.4 (si el alcance mediano por post cae >40% frente a la línea base de los días 1–3, se baja a 3/día y se sube el peso de respuestas).

### 4.2 Pinterest — SEO visual

- **Rol:** tráfico compuesto. Un pin sigue trabajando meses; no es una publicación social, es un resultado de búsqueda con enlace.
- **Mecánica:** palabra clave en overlay + título + descripción + tablero + nombre de archivo; 2:3 obligatorio; enlace a página específica (nunca al home); pines **frescos** (diseño nuevo), no repines.
- **Cadencia del plan:** 2 pines/día (11:30 y 20:15), 60 pines en 30 días, 55 URLs distintas + 5 segundas variantes para los SKUs ancla. Separación mínima entre pines de la misma URL: **72 h** (el validador lo impone).
- **Horizonte:** 3–6 meses para tracción real. En 14 días se mide señal, no resultado.

### 4.3 Bio (hub de un solo enlace)

- **Un solo enlace:** `${BASE_URL}/gratis/anatomia-post-418-usd` (L01) — el anzuelo, nunca el catálogo.
- **Bio de 3 líneas:** qué eres (insider cínico), qué resuelves (mecanismo + aritmética), qué haces ahora (anzuelo gratis).
- La bio no menciona precio ni "link en comentarios". El objetivo de la bio es el email, no la venta directa.
- Segundo destino (solo en Pinterest): tablero de marca con las rutas de bundles.

### 4.4 Email (la única audiencia que se posee)

Secuencia de 5 correos desde L01, en 7 días:

| # | Día | Asunto | Objetivo | CTA |
|---|---|---|---|---|
| 1 | 0 | "El desglose que no publiqué" | Entregar L01 y fijar expectativa | Abrir el PDF |
| 2 | 1 | "Por qué tu PDF no vendió" | Agitar dolor #3 (distribución) | Ruta E01 ($19) |
| 3 | 3 | "La aritmética de 4 ventas por semana" | Cuantificar sin prometer | Ruta E12 ($21) |
| 4 | 5 | "El orden importa más que el catálogo" | Presentar la escalera | Kit K01 ($49) |
| 5 | 7 | "Qué contiene el vault completo" | Techo de ticket y cierre suave | M06 ($149) |

Reglas: un solo CTA por correo, sin cuenta regresiva falsa, baja con un clic, y nunca se compra una lista.

### 4.5 Lo que no se hace (todavía)

- **Pauta pagada** hasta tener una ruta con ≥5% de conversión visitas→checkout medida en orgánico.
- Comprar seguidores, loops, pods o "engagement" de intercambio: penalizado y ensucia la señal.
- Engagement bait explícito ("comenta 1 si..." en cada post): el algoritmo lo castiga; solo se usa como pregunta real cuando la pieza ya lo plantea.
- Publicar el mismo texto en Threads y Pinterest: son buscadores distintos.

---

## 5. Playbook de Threads

### 5.1 Anatomía de una pieza

```
Línea 1 (hook, ≤90 caracteres)  ← decide el 80% del resultado
[blanco]
Dolor concreto (2 frases, en 2ª persona)
[blanco]
Mecanismo + dato estructural
[blanco]
Ruta: /blueprint/… · $19 USD
```

**Reglas del hook:** número impar o contradicción de estatus; sin contexto previo; sin "hoy quiero compartir"; sin hashtags; una idea por línea. Si la primera línea sirve para cualquier cuenta de negocios, se reescribe.

### 5.2 Ventana de la primera hora (la parte que casi nadie ejecuta)

| Minuto | Acción |
|---|---|
| 0 | Publicar (horario del calendario) |
| 2–4 | **Auto-respuesta 1:** aclarar la objeción obvia (precio, "no es cripto", "no necesitas audiencia") |
| 6–10 | Responder a todos los comentarios reales, una línea por respuesta, con una pregunta |
| 15–25 | **Auto-respuesta 2:** encadenada a la primera, cierra con la ruta y el precio real |
| 25–60 | 5–10 respuestas a cuentas del nicho (no a tu propio post) |
| 60 | Revisar: si no hay respuestas, el problema es el hook, no el tema |

La auto-respuesta no repite el post: **añade** información (qué contiene, qué no incluye, cuál es el precio real). Nunca simula métricas ni inventa testimonios.

### 5.3 Cadencia diaria (5 publicaciones + respuestas)

| Hora | Formato | Función |
|---|---|---|
| 07:10 | Vía A (imagen/anzuelo) | Capturar el transporte matutino |
| 12:20 | Vía B (hilo) | Almuerzo: discusión |
| 15:40 | Vía A (nota/captura) | Pausa de tarde |
| 18:50 | Vía B (hilo) | Salida del trabajo: ragebait |
| 21:30 | Vía C (carrusel de app) | Pico nocturno: demo de herramienta |

Regla de esfuerzo: **60–70% del tiempo diario en respuestas, 30–40% en publicar**. Un día sin respuestas es un día perdido aunque haya 5 posts.

### 5.4 Checklist antes de publicar (30 segundos)

- [ ] Primera línea con número, contradicción o riesgo de estatus.
- [ ] ≤500 caracteres por bloque y sin emojis.
- [ ] Un solo topic tag.
- [ ] Ruta puente correcta del SKU (no el home).
- [ ] Dos auto-respuestas escritas **antes** de publicar.
- [ ] Sin promesa de ingresos, sin "garantizado", sin cifras de ventas inventadas.
- [ ] Imagen o captura adjunta cuando el formato es Vía A.

### 5.5 Errores que matan la cuenta

1. Publicar y desaparecer (mata la primera hora).
2. Copiar el mismo hook tres días seguidos (el interés se agota).
3. Atacar personas en vez de sistemas (la negatividad se limita).
4. Usar 8 hashtags (no aplica; un topic tag).
5. Mandar al home en vez de a la ruta del SKU (el clic se pierde).

---

## 6. Playbook de Pinterest

### 6.1 Especificación del pin

| Elemento | Regla | Verificación |
|---|---|---|
| Formato | **2:3 · 1000×1500 px** | `aspect_ratio: "2:3"` en el feed |
| Overlay | ≤6 palabras, mayúsculas, legible a 236 px | `overlay_headline` ≤48 caracteres |
| Título SEO | **40–60 caracteres** con la keyword principal al inicio | validador |
| Descripción | **200–350 caracteres**, keyword + beneficio + qué contiene | validador |
| Enlace | Ruta puente del SKU (nunca el home) | `bridge_route` = ruta del catálogo |
| Tablero | Cluster de keyword (11 tableros definidos) | `board_name` |
| Fecha | ≥72 h entre pines de la misma URL | validador |
| Logo | Fuera de la esquina inferior derecha | brief de diseño |
| IA | Declarar imagen generada cuando corresponda | política de plataforma |

### 6.2 Tableros (11 clusters de keyword, ya en uso)

| # | Tablero | Pines en la campaña |
|---|---|---|
| 1 | Psicología Oscura & Mentalidad de Riqueza | 10 |
| 2 | IA Aplicada & Automatización Injusta | 9 |
| 3 | Sistemas Completos Digitales | 7 |
| 4 | Finanzas Cínicas & Libertad en USD | 6 |
| 5 | Pinterest SEO & Tráfico | 5 |
| 6 | Mega-Bundles & Vaults Digitales | 5 |
| 7 | Recursos Gratis de Marketing Digital | 4 |
| 8 | Ingresos Digitales & Sistemas Faceless | 4 |
| 9 | Threads & Crecimiento Orgánico | 4 |
| 10 | Micro-Apps HTML para Creadores | 4 |
| 11 | Bóvedas de Hooks y Plantillas | 2 |

Cada tablero tiene descripción propia con 2–3 keywords y **no** mezcla nichos. El desbalance es deliberado: los primeros tres concentran el 47% de los pines porque son los clusters con más SKUs del catálogo.

### 6.3 Mix de pines (70/30)

- **70% impresión fría:** editorial dark luxury (ajedrez obsidiana/oro, setup OLED, reloj espresso, terminales). Sin producto, sin precio: solo el ángulo y la keyword.
- **30% producto con identidad:** arte canónico de Ron (`pin_ron_3am_blueprint`, `pin_ron_threads_atm`, `pin_ron_escape_matrix`, `pin_ron_dark_psychology`, `pin_ron_puppet_strings`) con la palabra clave del SKU.

En la campaña actual: **42 pines de impresión fría y 18 con arte de Ron** (70/30 exacto). Los 18 slots de identidad priorizan las 11 micro-apps y 7 SKUs de kit/bundle/anzuelo, que son los que necesitan rostro de marca; el resto del catálogo entra con pin editorial.

### 6.4 Frescura: 3–5 diseños por URL

El pin fresco es un **diseño nuevo** para la misma URL, no un repin ni un cambio de color.
Plan de producción: 1 diseño por URL en la campaña (60 pines / 55 URLs), y en cuanto una URL acumule clics por encima de la mediana, se producen 2 variantes más (total 3) con overlay distinto. Cada variante cuesta $0.067 de imagen: la decisión es económica, no creativa.

### 6.5 Keywords semilla por nicho

| Nicho | Semillas |
|---|---|
| Dinero faceless | productos digitales sin cara · vender pdf · ingresos digitales · gumroad españa/latam · trabajar desde casa sin cámara |
| IA injusta | prompts de negocios · automatización sin api · ia para vender · chatgpt para infoproductos |
| Psicología oscura | psicología del precio · anclaje de precios · copywriting persuasivo · ganchos virales |
| Escape 9–5 | cobrar en dólares · salir del 9 a 5 · libertad financiera latam · costo de vida colombia |

Regla: la keyword principal va en overlay **y** en el título; la descripción teje 2–3 variantes semánticas, nunca 8 repeticiones exactas.

### 6.6 Checklist antes de publicar un pin

- [ ] Imagen 1000×1500 (2:3), overlay legible al 25% del tamaño.
- [ ] Título 40–60 caracteres, keyword al inicio.
- [ ] Descripción 200–350 caracteres, con qué contiene y para quién.
- [ ] Enlace a la ruta del SKU correcto.
- [ ] Tablero de keyword correcto.
- [ ] ≥72 h desde el último pin de esa URL.
- [ ] Nombre de archivo descriptivo (`pin_<sku>_<angulo>.png`).

---

## 7. Calendario y operación

- Calendario completo día por día: [`docs/CONTENT_CALENDAR.md`](CONTENT_CALENDAR.md).
- Cola publicable: `data/social_feeds.json` (154 threads, 72 pines; los 4 posts y los 12 pines canónicos se conservan).
- Campaña estructurada: `data/marketing/campaign_30d.json` (210 piezas).
- Copy bank: `data/marketing/copy_bank.json` (150 + 60 piezas completas).
- Export para revisión humana: `data/marketing/campaign_30d.csv`.

Comandos:

```powershell
.\.venv\Scripts\python.exe scripts\campaign_tools.py validate
.\.venv\Scripts\python.exe scripts\campaign_tools.py export-csv
.\.venv\Scripts\python.exe scripts\campaign_tools.py import-feeds --dry-run
.\.venv\Scripts\python.exe scripts\campaign_tools.py import-feeds
```

`${BASE_URL}` es el único placeholder permitido: lo sustituye el publicador por el origen público (LAN `http://<IP>:8765` o el dominio desplegado). No se publica ningún texto con ese token sin resolver.

### 7.1 Qué se importó exactamente (y qué no)

| Concepto | Resultado |
|---|---|
| Piezas canónicas conservadas | 4 posts (`th_001`–`th_004`) y 12 pines (`pin_001`–`pin_010` + 2 benchmarks de competidor que usa el test de honestidad) |
| Piezas de campaña importadas | **150 posts + 60 pines**, `status: "queued"`, ids `th_005`–`th_154` y `pin_101`–`pin_160` |
| Contadores simulados de las piezas nuevas | **0** en likes, respuestas, reposts, guardados y clics: no se midió nada todavía |
| Posts de prueba | Ninguno. No hay piezas con `Custom Bait Studio Injection` ni textos de prueba |
| Benchmarks nuevos | Ninguno. Las dos referencias de competidor son preexistentes y se conservan porque el test de honestidad del repo las exige |
| Re-import | Idempotente: `import-feeds` dos veces seguidas añade 0 piezas |

---

## 8. KPIs, instrumentación y umbrales de muerte (14 días)

### 8.1 Qué se mide y de dónde sale

| KPI | Fuente | Nota de honestidad |
|---|---|---|
| Alcance e impresiones | Analítica nativa de cada plataforma | No se inventa: si no se midió, se reporta vacío |
| Respuestas ÷ alcance | Nativo + hoja de cálculo | Métrica #1 de Threads |
| Clics salientes | Nativo de Pinterest / tracking local | El estado `published` del sistema es solo seguimiento local |
| Visitas a ruta puente | Registro local de la app | `metrics_real.json` |
| Checkout iniciado / compra | Panel de Gumroad y Hotmart | Única fuente de ingresos reales |
| Conversión ruta → checkout | (checkout iniciados) ÷ (visitas) | Objetivo ≥5%, sano 8–12% |
| Checkout → compra | Panel de pasarela | Rango típico 30–60% |
| Opt-in del anzuelo | Captura de email | Objetivo 20–40% |

### 8.2 Objetivos por pieza (los que ya están en la campaña)

| Canal / lane | KPI objetivo |
|---|---|
| Threads Vía A | ≥25 respuestas · respuestas/alcance ≥0.6% · alcance ≥4,000 · ≥12 guardados |
| Threads Vía B | ≥40 respuestas · respuestas/alcance ≥0.8% · alcance ≥6,000 · ≥15 reposts |
| Threads Vía C | ≥15 respuestas · ≥10 guardados · ≥120 visitas al perfil |
| Pinterest | ≥1,500 impresiones · ≥20 clics salientes · ≥25 guardados · CTR ≥1.2% |

### 8.3 Revisión por hitos

| Hito | Qué se mira | Decisión |
|---|---|---|
| Día 3 | Errores de ejecución (¿se publicó a la hora? ¿hubo 2 auto-respuestas?) | Corregir proceso, no contenido |
| Día 7 | Mediana de alcance por lane y CTR de pines | Primer "doblar o matar" |
| **Día 14** | **Umbral de muerte completo (§8.4)** | **Doblar, iterar o matar** |
| Día 21 | Conversión de ruta y AOV | Ajustar oferta, no tráfico |
| Día 30 | LTV de cohorte y costo por venta | Reescribir la escalera si hace falta |

### 8.4 Umbrales de muerte a 14 días ("doblar o matar")

Se evalúa con **muestra mínima**: ≥40 posts de Threads y ≥10 pines publicados. Con menos, no hay veredicto (solo ejecución).

| # | Señal | Umbral de muerte | Acción si se cumple | Acción si se supera |
|---|---|---|---|---|
| 1 | Mediana de alcance por post (Threads) | <700 con ≥40 posts | Matar el lane y reescribir hooks con la bóveda B01 | Doblar el formato ganador |
| 2 | Respuestas ÷ alcance (Threads) | <0.25% mediana | Cambiar la pregunta de cierre; publicar 3/día y responder el doble | Subir a 2 posts del mismo ángulo |
| 3 | Crecimiento de seguidores | 0% en 14 días | Revisar nicho y topic tag; el interés no está claro | Mantener y acelerar respuestas |
| 4 | Impresiones medianas por pin | <500 | Reescribir keywords y tableros | Producir 2 variantes frescas de las top |
| 5 | CTR de pin (clics/impresiones) | <0.3% | El overlay no promete nada: rediseñar | Escalar a 3–5 diseños por URL |
| 6 | Clics salientes totales (Pinterest) | 0 con ≥10 pines | El enlace o la ruta están mal: auditar 55 rutas | Duplicar producción de pines |
| 7 | Visitas a ruta sin compra | 250 visitas y 0 compras | Reescribir la página puente (precio, prueba, CTA) antes de traer más tráfico | Mantener y subir precio del kit |
| 8 | Conversión ruta → checkout | <2% | Problema de oferta (precio o promesa), no de tráfico | Optimizar checkout y bump |

**Regla de oro:** el tráfico nunca se escala sobre una ruta que no convierte. Primero se arregla la ruta, después se compra o se publica más.

### 8.5 Lo que no cuenta como KPI

- Likes sueltos, impresiones sin clic, "engagement" de cuentas que nunca compran.
- Métricas simuladas del feed local: los contadores nuevos se importaron **en cero** porque no se han medido.

---

## 9. Plan de lanzamiento de 7 días

| Día | Objetivo | Acciones concretas | Criterio de éxito |
|---|---|---|---|
| **-1 (prep)** | Cerrar el circuito de venta | Verificar las 55 rutas puente · confirmar checkout Gumroad/Hotmart por SKU · bio con L01 · captura de email activa · `campaign_tools.py validate` en verde | 0 rutas rotas, 0 SKUs de pago sin pasarela |
| **1** | Sembrar el anzuelo | Publicar L01 (07:10) + E01 (12:20) + E03 (15:40) + E11 (18:50) + A01 (21:30) · pins L01 y E01 (11:30 / 20:15) · 20 respuestas ajenas | ≥2 auto-respuestas por post, 0 errores de ruta |
| **2** | Abrir la conversación | 5 posts (E02, E11, E01, E10, A02) · pins E02 y K01 · responder todo comentario en <30 min | ≥10 respuestas totales |
| **3** | Medir ejecución | 5 posts · 2 pines · revisar si se cumplieron horarios y auto-respuestas | Checklist de §5.4 al 100% |
| **4** | Primer test de oferta | Empujar kit K03 y bundle M01 en los CTAs · revisar clics a ruta | ≥50 visitas a ruta en el día |
| **5** | Email | Enviar correo 2 de la secuencia a los opt-in de L01 | ≥25% de apertura (referencia, no promesa) |
| **6** | Revisión de pines | Ver impresiones por pin; reescribir los 3 peores títulos | 0 títulos fuera de 40–60 caracteres |
| **7** | Primer "doblar o matar" | Tabla de §8.4 con datos de 7 días · duplicar el lane con mejor mediana · pausar el peor | Decisión escrita, una sola: doblar o matar |

**Después del día 7:** se mantiene el calendario de 30 días sin cambios hasta el día 14. Cambiar el plan cada 48 horas es la forma más rápida de no aprender nada.

---

## 10. Riesgos, ética y límites

| Riesgo | Mitigación |
|---|---|
| Promesa implícita de ingresos | Cero "garantizado", cero cifras de ventas inventadas; el validador bloquea claims prohibidos |
| Cadencia alta vs. límite de la plataforma | Test de 14 días con corte explícito (§4.1) y peso en respuestas |
| Saturación de pines de la misma URL | Regla de 72 h impuesta por el validador |
| Imágenes generadas con IA | Se declara cuando la plataforma lo permita; el arte de Ron es canónico y consistente |
| Afiliados / terceros | Se declara cualquier enlace de afiliado (FTC) |
| Estado falso en el sistema | Los contadores simulados de las piezas nuevas quedaron en 0; `published` es seguimiento local, no publicación en red |
| Dependencia de una sola cuenta | El email es el activo propio; todo el tráfico de Pinterest y Threads apunta al anzuelo |

---

## 11. Anexo — mapa de archivos

| Archivo | Qué contiene |
|---|---|
| `data/marketing/campaign_30d.json` | 210 piezas con día, hora, plataforma, SKU, ruta, copy, imagen, tablero, keywords, CTA y KPI |
| `data/marketing/copy_bank.json` | 150 posts de Threads + 60 pines completos (fuente de copy) |
| `data/marketing/campaign_30d.csv` | Export legible para revisión y edición |
| `data/social_feeds.json` | Cola publicable con modelos Pydantic (`ThreadsPostItem` / `PinterestPinItem`) |
| `scripts/campaign_tools.py` | `validate`, `export-csv`, `import-feeds` (idempotente) |
| `docs/CONTENT_CALENDAR.md` | Calendario de 30 días y checklist de estreno |
