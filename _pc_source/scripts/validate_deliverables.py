"""Valida los 55 entregables reales de `data/deliverables/`.

Por SKU comprueba: existe, >20 KB, HTML parseable, `<title>`, sin recursos
http(s) externos (src/link/@import/url()/poster/action), sin lorem ipsum y con
texto visible real. Mide palabras visibles y avisa de credibilidad: `TODO` de
desarrollo, placeholders, `{{ }}` declaradas, `(cifra ilustrativa`, garantías,
claims de ingresos, enlaces externos y hooks duplicados exactos en B01.
Los HTML son productos reales: NO se reescriben.

Uso:
    .\\.venv\\Scripts\\python.exe scripts\\validate_deliverables.py
    .\\.venv\\Scripts\\python.exe scripts\\validate_deliverables.py --report docs\\GENERADORES_VALIDACION.md

Exit code 1 si hay fallos duros; 0 si solo hay avisos.
"""

import argparse
import html as html_lib
import json
import re
import sys
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CATALOG_PATH = BASE_DIR / "data" / "catalog.json"
DELIVERABLES_DIR = BASE_DIR / "data" / "deliverables"
MIN_BYTES, MIN_WORDS, WARN_WORDS = 20_000, 50, 300

# Solo cuenta como fallo lo que CARGA recursos de red. Un <a href="https://...">
# es un enlace de salida, no una dependencia: se reporta como aviso. Los data URI
# con `xmlns='http://...'` no son red.
EXTERNAL_RESOURCE_RE = re.compile(
    r"""(?isx)
    (?:src|poster)\s*=\s*["']https?://
    | <link\b[^>]*\bhref\s*=\s*["']https?://
    | @import\s+(?:url\()?["']?https?://
    | url\(\s*["']?https?://
    | (?:action)\s*=\s*["']https?://
    """
)
EXTERNAL_LINK_RE = re.compile(r"""(?is)<a\b[^>]*\bhref\s*=\s*["']https?://""")
TODO_RE = re.compile(r"(?<!\w)TODO(?!\w)")  # \w Unicode: no marca "MÉTODO"/"método"
PLACEHOLDER_RE = re.compile(r"placeholder", re.IGNORECASE)
LOREM_RE = re.compile(r"lorem\s+ipsum", re.IGNORECASE)
TEMPLATE_RE = re.compile(r"\{\{")
DECLARED_TEMPLATE_SKUS = {"L03"}  # meta-prompt con variables que rellena el comprador
CLAIM_RE = re.compile(
    r"(?:ingresos?|ganancias?|beneficios?|resultados?|ventas?)\s+(?:est[aá]n\s+)?garantizad",
    re.IGNORECASE,
)
# Marcas de cita, negación o prohibición alrededor del claim: no es una promesa propia.
CLAIM_CONTEXT_RE = re.compile(
    r"(?i)\b(?:sin|no|ni|nunca|jamás|ningún|ninguna|prohíbe|prohibir|prohibido|evita|"
    r"evitar|prometer|promesa|promesas|mito|objeción|exigencia|reportes|rojo|alerta|bandera)\b"
)
GUARANTEE_RE = re.compile(r"garantizad", re.IGNORECASE)
ILLUSTRATIVE_RE = re.compile(r"\(cifra ilustrativa", re.IGNORECASE)


def classify_claims(text: str) -> dict:
    """Separa promesas propias de menciones citadas, negadas o prohibidas."""
    positivos = citados = 0
    for match in CLAIM_RE.finditer(text):
        window = text[max(0, match.start() - 140) : match.end() + 140]
        if CLAIM_CONTEXT_RE.search(window):
            citados += 1
        else:
            positivos += 1
    return {"positivos": positivos, "citados": citados}


class _TitleParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_parts: list[str] = []
        self._in_title = False

    def handle_starttag(self, tag, attrs) -> None:
        self._in_title = tag.lower() == "title"

    def handle_endtag(self, tag) -> None:
        if tag.lower() == "title":
            self._in_title = False

    def handle_data(self, data) -> None:
        if self._in_title:
            self.title_parts.append(data)

    @property
    def title(self) -> str:
        return " ".join(part.strip() for part in self.title_parts).strip()


def visible_text(raw: str) -> str:
    text = re.sub(r"(?is)<script.*?</script>", " ", raw)
    text = re.sub(r"(?is)<style.*?</style>", " ", text)
    text = re.sub(r"(?s)<!--.*?-->", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", html_lib.unescape(text)).strip()


def check_sku(item: dict) -> dict:
    sku_id = item["sku_id"]
    filename = f"{sku_id.lower()}_{item['slug']}.html"
    path = DELIVERABLES_DIR / filename
    row = {"sku_id": sku_id, "format": item["format"], "filename": filename,
           "bytes": 0, "words": 0, "title": "", "failures": [], "warnings": []}
    if not path.is_file():
        row["failures"].append("archivo_ausente")
        return row
    size, failures, warnings = path.stat().st_size, row["failures"], row["warnings"]
    raw = path.read_text(encoding="utf-8", errors="ignore")
    row["bytes"] = size
    if size <= MIN_BYTES:
        failures.append(f"tamano_{size}B")
    parser = _TitleParser()
    try:
        parser.feed(raw)
        parser.close()
    except Exception as exc:  # noqa: BLE001 - se reporta, no se silencia
        failures.append(f"html_no_parseable_{type(exc).__name__}")
    row["title"] = parser.title
    if not parser.title:
        failures.append("sin_title")
    if not raw.rstrip().lower().endswith("</html>"):
        failures.append("sin_cierre_html")
    if EXTERNAL_RESOURCE_RE.search(raw):
        failures.append("recurso_externo")
    if EXTERNAL_LINK_RE.search(raw):
        warnings.append(f"enlaces_salida_{len(EXTERNAL_LINK_RE.findall(raw))}")
    text = visible_text(raw)
    row["words"] = len(text.split())
    if row["words"] < MIN_WORDS:
        failures.append(f"vacio_{row['words']}palabras")
    elif row["words"] < WARN_WORDS:
        warnings.append(f"pocas_palabras_{row['words']}")
    if LOREM_RE.search(text):
        failures.append("lorem_ipsum")
    if TODO_RE.search(text):
        warnings.append("marcador_TODO_desarrollo")
    placeholders = len(PLACEHOLDER_RE.findall(text))
    if placeholders:
        warnings.append(f"menciona_placeholder_{placeholders}")
    templates = len(TEMPLATE_RE.findall(text))
    if templates:
        suffix = "esperado" if sku_id in DECLARED_TEMPLATE_SKUS else "revisar"
        warnings.append(f"variables_plantilla_{templates}_{suffix}")
    illustrative = len(ILLUSTRATIVE_RE.findall(raw))
    if illustrative:
        warnings.append(f"cifra_ilustrativa_{illustrative}")
    claims = classify_claims(text)
    if claims["positivos"]:
        warnings.append(f"claim_ingresos_positivo_{claims['positivos']}")
    if claims["citados"]:
        warnings.append(f"garantia_negada_o_citada_{claims['citados']}")
    guarantee = len(GUARANTEE_RE.findall(text))
    if guarantee:
        warnings.append(f"menciona_garantizado_{guarantee}")
    return row


def check_b01_hooks() -> dict:
    path = DELIVERABLES_DIR / "b01_boveda-500-hooks-cinicos.html"
    out = {"checked": False, "hooks": 0, "unique": 0, "exact_duplicates": 0, "examples": []}
    if not path.is_file():
        return out
    raw = path.read_text(encoding="utf-8", errors="ignore")
    start, end = raw.find("const HOOKS = ["), raw.find("const NICHE_LIST")
    block = raw[start:end] if start >= 0 and end > start else raw
    texts = [value[1] for value in re.findall(r"""texto\s*:\s*(["'])(.*?)\1""", block, re.S)]
    seen: dict[str, int] = {}
    for text in texts:
        seen[text] = seen.get(text, 0) + 1
    duplicates = [(text, count) for text, count in seen.items() if count > 1]
    out.update(checked=True, hooks=len(texts), unique=len(seen),
               exact_duplicates=len(duplicates), examples=[t[:100] for t, _ in duplicates[:5]])
    return out


def render_markdown(rows: list[dict], hooks: dict, generated_at: str) -> str:
    valid = sum(1 for row in rows if not row["failures"])
    warn = sum(1 for row in rows if row["warnings"])
    lines = [
        "# Validación de los entregables reales", "",
        f"Generado: {generated_at}",
        "Directorio: `data/deliverables/` · Catálogo: `data/catalog.json`", "",
        f"**Resultado: {valid}/{len(rows)} entregables válidos** "
        f"({len(rows) - valid} con fallo duro, {warn} con avisos de credibilidad).", "",
        "Fallos duros: archivo ausente, <=20 KB, HTML no parseable, sin `<title>`, "
        "sin `</html>`, recurso http(s) externo, lorem ipsum o texto visible vacío.  ",
        "Avisos: pocas palabras, `TODO` de desarrollo (regex `(?<!\\w)TODO(?!\\w)`: "
        "no marca `MÉTODO`), menciones de `placeholder`, variables `{{ }}` "
        "(`L03` es esperado: meta-prompt que el comprador rellena), "
        "`(cifra ilustrativa`, garantías, claims de ingresos, enlaces de salida y "
        "hooks duplicados exactos en B01. No se reescribe ningún HTML.", "",
        "`claim_ingresos_positivo` cuenta promesas propias; "
        "`garantia_negada_o_citada` cuenta menciones que el propio producto niega, cita o prohíbe.", "",
        "## Tabla por SKU", "",
        "| SKU | Formato | KB | Palabras | Estado | Detalle |", "| --- | --- | ---: | ---: | --- | --- |",
    ]
    for row in rows:
        state = "FALLO" if row["failures"] else ("AVISO" if row["warnings"] else "OK")
        detail = ", ".join(row["failures"] + row["warnings"]) or "—"
        lines.append(f"| {row['sku_id']} | {row['format']} | {row['bytes'] / 1024:.1f} | "
                     f"{row['words']} | {state} | {detail} |")
    lines += ["", "## B01 · hooks duplicados exactos", ""]
    if hooks["checked"]:
        lines.append(f"- Hooks parseados: **{hooks['hooks']}** · únicos: "
                     f"**{hooks['unique']}** · duplicados exactos: "
                     f"**{hooks['exact_duplicates']}**.")
        lines += [f"- Ejemplo duplicado: `{example}`" for example in hooks["examples"]]
    else:
        lines.append("- B01 no encontrado en disco: comprobación omitida.")
    lines += ["", "## Cómo reproducir", "", "```powershell",
              "cd C:\\Users\\USER\\Documents\\ronin_ventas",
              ".\\\\.venv\\\\Scripts\\\\python.exe scripts\\\\validate_deliverables.py --report docs\\\\GENERADORES_VALIDACION.md",
              "```", "", "Exit code 1 si hay fallos duros; 0 si solo hay avisos.", ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida los 55 entregables reales")
    parser.add_argument("--catalog", default=str(CATALOG_PATH))
    parser.add_argument("--report", default="", help="Ruta Markdown opcional")
    args = parser.parse_args()
    catalog = json.loads(Path(args.catalog).read_text(encoding="utf-8"))
    rows = [check_sku(item) for item in catalog]
    hooks = check_b01_hooks()
    for row in rows:
        state = "FAIL" if row["failures"] else ("WARN" if row["warnings"] else "OK")
        detail = ", ".join(row["failures"] + row["warnings"])
        print(f"{row['sku_id']:4} {state:4} {row['bytes'] / 1024:6.1f} KB "
              f"{row['words']:6} palabras  {detail}")
    valid = sum(1 for row in rows if not row["failures"])
    print(f"\nValidos: {valid}/{len(rows)} · con avisos: "
          f"{sum(1 for row in rows if row['warnings'])}")
    print(f"B01 hooks: {hooks['hooks']} parseados, {hooks['exact_duplicates']} duplicados exactos")
    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report_path.write_text(render_markdown(rows, hooks, stamp), encoding="utf-8")
        print(f"Reporte: {report_path}")
    return 0 if valid == len(rows) else 1


if __name__ == "__main__":
    sys.exit(main())
