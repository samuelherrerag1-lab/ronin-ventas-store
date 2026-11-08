# Validación de los entregables reales

Generado: 2026-11-04 21:57:18
Directorio: `data/deliverables/` · Catálogo: `data/catalog.json`

**Resultado: 55/55 entregables válidos** (0 con fallo duro, 34 con avisos de credibilidad).

Fallos duros: archivo ausente, <=20 KB, HTML no parseable, sin `<title>`, sin `</html>`, recurso http(s) externo, lorem ipsum o texto visible vacío.  
Avisos: pocas palabras, `TODO` de desarrollo (regex `(?<!\w)TODO(?!\w)`: no marca `MÉTODO`), menciones de `placeholder`, variables `{{ }}` (`L03` es esperado: meta-prompt que el comprador rellena), `(cifra ilustrativa`, garantías, claims de ingresos, enlaces de salida y hooks duplicados exactos en B01. No se reescribe ningún HTML.

`claim_ingresos_positivo` cuenta promesas propias; `garantia_negada_o_citada` cuenta menciones que el propio producto niega, cita o prohíbe.

## Tabla por SKU

| SKU | Formato | KB | Palabras | Estado | Detalle |
| --- | --- | ---: | ---: | --- | --- |
| E01 | ebook_blueprint | 138.2 | 11429 | AVISO | garantia_negada_o_citada_1, menciona_garantizado_2 |
| E02 | ebook_blueprint | 305.6 | 31894 | AVISO | garantia_negada_o_citada_2, menciona_garantizado_3 |
| E03 | ebook_blueprint | 322.3 | 32842 | AVISO | menciona_placeholder_1, garantia_negada_o_citada_2, menciona_garantizado_2 |
| E04 | ebook_blueprint | 126.7 | 11502 | AVISO | garantia_negada_o_citada_2, menciona_garantizado_2 |
| E05 | ebook_blueprint | 172.4 | 14081 | AVISO | garantia_negada_o_citada_1, menciona_garantizado_2 |
| E06 | ebook_blueprint | 154.1 | 14207 | AVISO | garantia_negada_o_citada_1, menciona_garantizado_1 |
| E07 | ebook_blueprint | 169.8 | 14533 | OK | — |
| E08 | ebook_blueprint | 158.7 | 13450 | AVISO | garantia_negada_o_citada_2, menciona_garantizado_3 |
| E09 | ebook_blueprint | 173.1 | 17365 | OK | — |
| E10 | ebook_blueprint | 136.2 | 12685 | AVISO | garantia_negada_o_citada_1, menciona_garantizado_1 |
| E11 | ebook_blueprint | 138.5 | 12082 | OK | — |
| E12 | ebook_blueprint | 164.4 | 13155 | OK | — |
| B01 | boveda_arsenal | 324.9 | 7039 | OK | — |
| B02 | boveda_arsenal | 83.7 | 118 | AVISO | pocas_palabras_118, menciona_placeholder_1 |
| B03 | boveda_arsenal | 127.2 | 136 | AVISO | pocas_palabras_136, menciona_placeholder_1 |
| B04 | boveda_arsenal | 121.8 | 217 | AVISO | pocas_palabras_217 |
| B05 | boveda_arsenal | 285.3 | 1705 | OK | — |
| B06 | boveda_arsenal | 66.6 | 1882 | OK | — |
| B07 | boveda_arsenal | 71.4 | 2605 | OK | — |
| B08 | boveda_arsenal | 157.0 | 298 | AVISO | pocas_palabras_298 |
| B09 | boveda_arsenal | 533.6 | 32279 | AVISO | garantia_negada_o_citada_2, menciona_garantizado_2 |
| B10 | boveda_arsenal | 241.0 | 11442 | AVISO | menciona_garantizado_1 |
| B11 | boveda_arsenal | 225.3 | 11446 | OK | — |
| B12 | boveda_arsenal | 142.3 | 4685 | OK | — |
| A01 | micro_app_html | 167.9 | 1894 | OK | — |
| A02 | micro_app_html | 114.1 | 1295 | OK | — |
| A03 | micro_app_html | 68.9 | 2544 | AVISO | menciona_placeholder_1 |
| A04 | micro_app_html | 65.1 | 2836 | AVISO | menciona_placeholder_1 |
| A05 | micro_app_html | 105.6 | 1593 | OK | — |
| A06 | micro_app_html | 65.1 | 2364 | AVISO | menciona_placeholder_1 |
| A07 | micro_app_html | 65.1 | 3109 | OK | — |
| A08 | micro_app_html | 128.2 | 1812 | OK | — |
| A09 | micro_app_html | 67.3 | 2422 | OK | — |
| A10 | micro_app_html | 65.1 | 2404 | OK | — |
| A11 | micro_app_html | 134.6 | 1862 | AVISO | menciona_garantizado_1 |
| A12 | micro_app_html | 110.7 | 1490 | OK | — |
| K01 | kit_sistema | 484.4 | 15040 | AVISO | garantia_negada_o_citada_1, menciona_garantizado_2 |
| K02 | kit_sistema | 306.8 | 16834 | AVISO | menciona_placeholder_1, garantia_negada_o_citada_2, menciona_garantizado_2 |
| K03 | kit_sistema | 406.1 | 26296 | AVISO | menciona_placeholder_2, garantia_negada_o_citada_2, menciona_garantizado_2 |
| K04 | kit_sistema | 284.3 | 14840 | AVISO | menciona_placeholder_1, garantia_negada_o_citada_2, menciona_garantizado_2 |
| K05 | kit_sistema | 486.4 | 17661 | AVISO | garantia_negada_o_citada_1, menciona_garantizado_2 |
| K06 | kit_sistema | 244.6 | 18750 | AVISO | menciona_placeholder_1, garantia_negada_o_citada_1, menciona_garantizado_1 |
| K07 | kit_sistema | 275.1 | 20528 | OK | — |
| K08 | kit_sistema | 386.4 | 15846 | AVISO | garantia_negada_o_citada_2, menciona_garantizado_3 |
| K09 | kit_sistema | 730.2 | 52346 | AVISO | garantia_negada_o_citada_2, menciona_garantizado_2 |
| K10 | kit_sistema | 333.8 | 26811 | AVISO | garantia_negada_o_citada_1, menciona_garantizado_2 |
| M01 | mega_bundle | 749.8 | 72452 | AVISO | menciona_placeholder_4, garantia_negada_o_citada_7, menciona_garantizado_8 |
| M02 | mega_bundle | 587.1 | 56548 | AVISO | menciona_placeholder_1, garantia_negada_o_citada_2, menciona_garantizado_3 |
| M03 | mega_bundle | 696.9 | 65178 | AVISO | garantia_negada_o_citada_3, menciona_garantizado_7 |
| M04 | mega_bundle | 517.5 | 45014 | AVISO | menciona_garantizado_1 |
| M05 | mega_bundle | 449.8 | 26215 | AVISO | menciona_placeholder_3, menciona_garantizado_1 |
| M06 | mega_bundle | 85.8 | 4955 | OK | — |
| L01 | lead_magnet | 286.9 | 31650 | AVISO | garantia_negada_o_citada_1, menciona_garantizado_1 |
| L02 | lead_magnet | 57.9 | 3202 | OK | — |
| L03 | lead_magnet | 55.9 | 4115 | AVISO | variables_plantilla_5_esperado |

## B01 · hooks duplicados exactos

- Hooks parseados: **500** · únicos: **500** · duplicados exactos: **0**.

## Cómo reproducir

```powershell
cd C:\Users\EXAMPLE\Documents\ronin_ventas
.\\.venv\\Scripts\\python.exe scripts\\validate_deliverables.py --report docs\\GENERADORES_VALIDACION.md
```

Exit code 1 si hay fallos duros; 0 si solo hay avisos.
