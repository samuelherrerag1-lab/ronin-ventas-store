import json
import re
from collections import Counter

cat = {s["sku_id"]: s for s in json.load(open("data/catalog.json", encoding="utf-8"))}
campaign = json.load(open("data/marketing/campaign_30d.json", encoding="utf-8"))
print("campaign type:", type(campaign).__name__)
if isinstance(campaign, dict):
    print("keys:", list(campaign)[:10])
    items = campaign.get("items") or campaign.get("pieces") or campaign.get("days")
else:
    items = campaign
if isinstance(items, list):
    print("pieces:", len(items))
    platforms = Counter(str(i.get("platform")) for i in items if isinstance(i, dict))
    print("platforms:", dict(platforms))
    skus = {i.get("sku_id") for i in items if isinstance(i, dict)}
    print("skus covered:", len(skus & set(cat)), "/", len(cat))
    print("missing:", sorted(set(cat) - skus))
    days = {i.get("day") for i in items if isinstance(i, dict)}
    print("days:", len(days), "min/max:", min(days) if days else None, max(days) if days else None)

bank = json.load(open("data/marketing/copy_bank.json", encoding="utf-8"))
print("copy_bank keys:", list(bank)[:10] if isinstance(bank, dict) else type(bank).__name__)
if isinstance(bank, dict):
    for k, v in bank.items():
        if isinstance(v, list):
            print(k, len(v))

feeds = json.load(open("data/social_feeds.json", encoding="utf-8"))
print("feeds threads:", len(feeds.get("threads", [])), "pins:", len(feeds.get("pinterest", [])))
bad = [t.get("post_id") for t in feeds.get("threads", []) if "Prueba de inyecci" in str(t)]
print("test posts:", bad[:5], "count", len(bad))
text = json.dumps(feeds, ensure_ascii=False).lower()
for pattern in ("garantizado", "garantizada", "ingresos garantizados", "resultados garantizados"):
    print(pattern, text.count(pattern))
print("placeholders:", len(re.findall(r"\{\{", text)))
