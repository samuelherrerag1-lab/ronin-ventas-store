# Ronin Ventas OS — Sistema de diseño “Obsidian Ledger”

Rediseño de la shell y las superficies operativas. La regla del producto: **una persona, 55 rutas puente,
una máquina de dinero que se juzga cada 14 días**. La interfaz se comporta como un libro contable privado:
superficie obsidiana plana, cifras tabulares alineadas a la derecha, un solo acento cálido sobre el dato,
y la regla “Doblar o Matar” siempre a la vista.

## Dirección

| Decisión | Valor |
| --- | --- |
| Modo | Operate (pantallas de trabajo, sesiones densas en escritorio, vistazos en el móvil) |
| Estilo | `true-black-flat` con la lógica editorial de `achromatic-ledger`: elevación por tono, color solo sobre datos/estado/acción |
| Cara del producto | Bricolage Grotesque en títulos y en el wordmark; Geist en la UI; mono **solo** para identificadores reales (SKU, ruta, id de pieza) |
| Elemento firma | El panel “Doblar o Matar”: veredicto + horizonte de 14 días + la pieza que lo dispara |
| Segundo firma | El embudo como escalera de tres peldaños (impresiones → clics → ventas) con la tasa entre peldaños |

## Tokens

```
--bg        #0A0A0C   fondo de página
--panel     #101013   tarjeta
--panel-2   #15151A   fila / control elevado
--line      #212128   hairline
--line-2    #2C2C36   hairline fuerte / hover
--ink       #ECE8E3   texto principal (cálido, no gris de kit)
--ink-2     #A6A099   texto secundario (6.4:1 sobre --bg)
--ink-3     #6F6B66   terciario / labels (solo ≥11px)
--accent    #E07A5F   terracota del hoodie: dato principal + acción primaria
--pos       #7FAF8C   señal buena
--neg       #DE6A62   señal mala
--warn      #DDAE63   pendiente / demo
radio       tarjeta 12 · control 8 · chip 6 · pill 999
motion      140 / 180 / 220 ms · ease-out (0.23,1,0.32,1) · drawer (0.32,0.72,0,1)
```

Reglas duras: sin degradados, sin glows, sin sombras en reposo (solo menú/paleta/drawer), sin emojis,
un solo botón relleno por pantalla, sin etiquetas en mayúsculas con tracking, cero morado/índigo.

## Navegación

Sidebar de 236 px con etiqueta + icono de 16 px (34 px de pitch, pill neutra activa), colapsable a riel de
64 px con tooltip y `aria-label`. Móvil: dock inferior glass de 5 destinos + hoja “Más”. El header lleva
tres KPIs en vivo, buscador/paleta (`Ctrl/Cmd+K`), LAN y refresco.

## Datos honestos

- Sin datos reales: cifras en 0 o `—`, panel de “sin datos” con CTA de importar CSV, nunca cifras inventadas.
- El **modo demo** se etiqueta como ficticio en cada bloque que lo usa (la serie de los sparklines se
  reparte para sumar exactamente los totales demo).
- Toda cifra que aparece dos veces sale de la misma variable; los deltas nombran su base (“vs. periodo
  anterior”) o se muestran como `—` si no existe base.
- Lo que falta en el backend se rotula “Pendiente en backend”, no se simula.
