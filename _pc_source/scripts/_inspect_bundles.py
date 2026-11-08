import re
from pathlib import Path

D = Path("data/deliverables")
for name in ["b06_arsenal-prompts-creacion-ebooks.html", "b05_boveda-prompts-ingenieria-inversa.html"]:
    raw = (D / name).read_text(encoding="utf-8")
    print("==", name, "bytes", len(raw))
    print("  id=p", len(re.findall(r"id=.(?:p|prompt)[-_]?\d+", raw)))
    print("  prompt-card", raw.count("prompt-card"), "const PROMPTS", raw.count("const PROMPTS"))
    for token in ["24 prompts", "24 PROMPTS", "14 prompts", "14 PROMPTS", "120 prompts", "40 prompts", "40 META"]:
        print("  ", token, raw.count(token))
    for m in re.finditer(r"(?i)(?:24|14|120|40)\s*(?:meta-)?prompts", raw):
        a = max(0, m.start() - 60); b = min(len(raw), m.end() + 60)
        print("   ...", re.sub(r"\s+", " ", raw[a:b]))
