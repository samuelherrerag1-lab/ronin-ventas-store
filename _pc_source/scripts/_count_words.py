import json
import pathlib
import re

cat = json.load(open("data/catalog.json", encoding="utf-8"))
rows = []
for sku in cat:
    f = pathlib.Path("data/deliverables") / f"{sku['sku_id'].lower()}_{sku['slug']}.html"
    if not f.exists():
        rows.append((0, sku["sku_id"], sku["title"]))
        continue
    txt = f.read_text(encoding="utf-8", errors="ignore")
    txt = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", txt, flags=re.S | re.I)
    txt = re.sub(r"<[^>]+>", " ", txt)
    words = len(re.findall(r"[A-Za-zÁÉÍÓÚñÑ]{3,}", txt))
    rows.append((words, sku["sku_id"], sku["title"][:70]))
rows.sort()
for words, sku_id, title in rows:
    print(f"{words:>7}  {sku_id}  {title}")
print("---")
print("min", rows[0][0], "median", rows[len(rows) // 2][0], "max", rows[-1][0])
