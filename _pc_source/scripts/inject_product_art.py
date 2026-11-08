"""Inyector idempotente de arte de producto base64 en entregables HTML."""
import argparse
import base64
import re
import sys
from pathlib import Path
from typing import Dict, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

WEB_ART_DIR = BASE_DIR / "data" / "product_art" / "web"
DELIVERABLES_DIR = BASE_DIR / "data" / "deliverables"

START_MARKER = "<!--RONIN-ART-START-->"
END_MARKER = "<!--RONIN-ART-END-->"


def get_base64_data_uri(file_path: Path) -> Optional[str]:
    if not file_path.exists():
        return None
    raw = file_path.read_bytes()
    mime = "image/webp" if file_path.suffix.lower() == ".webp" else "image/png"
    encoded = base64.b64encode(raw).decode("utf-8")
    return f"data:{mime};base64,{encoded}"


def find_cover_image(sku: str) -> Optional[Path]:
    candidates = [
        WEB_ART_DIR / f"{sku}.webp",
        WEB_ART_DIR / "covers" / f"{sku}_v1.webp",
        WEB_ART_DIR / "covers" / f"{sku}_v2.webp",
        WEB_ART_DIR / "covers" / f"{sku}_v3.webp",
    ]
    for c in candidates:
        if c.is_file():
            return c
    return None


def find_divider_image() -> Optional[Path]:
    p = WEB_ART_DIR / "decor" / "decor_divider_01.webp"
    return p if p.is_file() else None


def build_art_header(sku: str, cover_uri: str, format_type: str) -> str:
    is_ebook = format_type.startswith("e") or format_type.startswith("k")
    badge = "EDICIÓN BLUEPRINT CANÓNICA" if is_ebook else "ACTIVO DIGITAL VERIFICADO"
    return (
        f"{START_MARKER}\n"
        f'<div class="ronin-product-art-hero" style="margin:28px 0 38px;display:flex;justify-content:center;align-items:center;">\n'
        f'  <div style="position:relative;max-width:380px;width:100%;border-radius:18px;overflow:hidden;'
        f'border:1px solid rgba(245,158,11,.25);background:#0a0a0f;box-shadow:0 24px 60px rgba(0,0,0,.6),0 0 40px rgba(245,158,11,.08);">\n'
        f'    <div style="position:relative;aspect-ratio:3/4;width:100%;overflow:hidden;background:#050508;">\n'
        f'      <img src="{cover_uri}" alt="{sku} Official Cover" loading="eager" '
        f'style="width:100%;height:100%;object-fit:cover;display:block;" />\n'
        f'      <div style="position:absolute;bottom:0;left:0;right:0;height:70px;background:linear-gradient(to top,#0a0a0f,transparent);"></div>\n'
        f'    </div>\n'
        f'    <div style="padding:14px 18px 16px;background:rgba(14,14,21,.92);backdrop-filter:blur(10px);border-top:1px solid rgba(255,255,255,.06);display:flex;justify-content:space-between;align-items:center;">\n'
        f'      <span style="font-family:ui-monospace,monospace;font-size:10px;letter-spacing:.16em;color:#f59e0b;text-transform:uppercase;font-weight:600;">{badge}</span>\n'
        f'      <span style="font-family:ui-monospace,monospace;font-size:9.5px;letter-spacing:.12em;color:#8b8b99;">SKU {sku}</span>\n'
        f'    </div>\n'
        f'  </div>\n'
        f'</div>\n'
        f"{END_MARKER}"
    )


def inject_into_html(content: str, sku: str, format_type: str) -> str:
    cover_path = find_cover_image(sku)
    if not cover_path:
        return content

    cover_uri = get_base64_data_uri(cover_path)
    if not cover_uri:
        return content

    art_block = build_art_header(sku, cover_uri, format_type)

    if START_MARKER in content and END_MARKER in content:
        pattern = re.compile(rf"{re.escape(START_MARKER)}.*?{re.escape(END_MARKER)}", re.DOTALL)
        content = pattern.sub(art_block, content)
    else:
        # Inserción limpia justo antes del bloque principal o cover
        targets = ['<div class="cover-grid"', '<header class="cover"', '<div class="book"', '<main', '<body>']
        injected = False
        for t in targets:
            if t in content:
                content = content.replace(t, f"{art_block}\n{t}", 1)
                injected = True
                break
        if not injected:
            content = f"{art_block}\n{content}"

    # Si es un ebook, inyectar divisores de capítulo elegantes
    if format_type.startswith("e"):
        div_path = find_divider_image()
        if div_path:
            div_uri = get_base64_data_uri(div_path)
            if div_uri:
                divider_block = (
                    f'\n<div class="ronin-chapter-divider" style="text-align:center;margin:46px 0 32px;opacity:.82;">\n'
                    f'  <img src="{div_uri}" alt="Divider" style="max-width:280px;height:auto;display:inline-block;" />\n'
                    f'</div>\n'
                )
                # Reemplazar h2 que no sean el primero
                parts = content.split('<h2 id="cap-')
                if len(parts) > 1:
                    new_parts = [parts[0]]
                    for p in parts[1:]:
                        if "ronin-chapter-divider" not in new_parts[-1]:
                            new_parts.append(f"{divider_block}<h2 id=\"cap-{p}")
                        else:
                            new_parts.append(f'<h2 id="cap-{p}')
                    content = "".join(new_parts)

    return content


def process_deliverables(target_sku: Optional[str] = None, deliverables_dir: Path = DELIVERABLES_DIR, dry_run: bool = False) -> Dict[str, str]:
    results = {}
    if not deliverables_dir.exists():
        print(f"Directorio {deliverables_dir} no existe.")
        return results

    html_files = sorted(deliverables_dir.glob("*.html"))
    for file_path in html_files:
        name = file_path.name.lower()
        parts = name.split("_")
        sku = parts[0].upper()
        if target_sku and sku != target_sku.upper():
            continue

        orig_html = file_path.read_text(encoding="utf-8")
        updated_html = inject_into_html(orig_html, sku, parts[0])

        if updated_html != orig_html:
            if not dry_run:
                file_path.write_text(updated_html, encoding="utf-8")
            results[sku] = f"{file_path.name} (Modificado: {'Dry-run' if dry_run else 'Escrito'})"
        else:
            results[sku] = f"{file_path.name} (Sin cambios / Ya inyectado)"

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sku", help="Filtrar por SKU específico")
    parser.add_argument("--dir", help="Directorio de entregables personalizado")
    parser.add_argument("--dry-run", action="store_true", help="Solo simular sin escribir")
    args = parser.parse_args()

    target_dir = Path(args.dir) if args.dir else DELIVERABLES_DIR
    res = process_deliverables(args.sku, target_dir, args.dry_run)
    for s, msg in res.items():
        print(f"[{s}] {msg}")
