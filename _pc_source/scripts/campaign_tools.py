"""Campaña de 30 días (@ronOverthinks): validate, export-csv e import-feeds.

`validate` solo lee. `import-feeds` es idempotente: identifica cada pieza por
post_id/pin_id y por firma (plataforma+SKU+cuerpo completo), conserva los 4
posts y los 12 pines canónicos, y no duplica nada al repetirse.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.config import FEEDS_JSON_PATH  # noqa: E402
from backend.models.catalog_models import BaitWidgetConfig, PinterestPinItem, ThreadsPostItem  # noqa: E402
from backend.services.social_feed_seed import load_or_init_feeds, save_feeds  # noqa: E402

MARKETING_DIR = BASE_DIR / "data" / "marketing"
CAMPAIGN_PATH = MARKETING_DIR / "campaign_30d.json"
COPY_BANK_PATH = MARKETING_DIR / "copy_bank.json"
CATALOG_PATH = BASE_DIR / "data" / "catalog.json"
REQUIRED = ("day", "platform", "time_local", "format", "sku_id", "route", "title", "hook",
            "body", "self_replies", "image", "board", "keywords", "cta", "kpi_target")
BANNED = ("garantiz", "ganarás", "te harás rico", "hazte rico", "ingresos asegurados",
          "dinero fácil", "sin riesgo", "100% seguro", "retorno garantizado")
PLACEHOLDER = re.compile(r"\$\{[^}]+\}")
THREAD_FORMATS = {"single_text", "thread_chain", "image_bait", "carousel_dark"}
PIN_LANES = {"dinero_ia_directo", "caballo_de_troya_curiosidad", "demo_herramienta_html"}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def signature(platform: str, sku_id: str, body: str) -> str:
    return hashlib.sha256(f"{platform}|{sku_id}|{body}".encode("utf-8")).hexdigest()[:16]


def piece_dt(meta: dict, piece: dict) -> dt.datetime:
    start = dt.date.fromisoformat(meta["start_date"])
    return dt.datetime.combine(start + dt.timedelta(days=piece["day"] - 1),
                               dt.time.fromisoformat(piece["time_local"]))


def check_campaign(campaign: dict, copy_bank: dict, catalog: list) -> list[str]:
    errors: list[str] = []
    meta, pieces = campaign.get("meta", {}), campaign.get("pieces", [])
    by_sku = {item["sku_id"]: item for item in catalog}
    routes = {item["bridge_route"] for item in catalog}
    if not pieces:
        return ["campaign_30d.json sin piezas"]
    for i, piece in enumerate(pieces):
        missing = [key for key in REQUIRED if key not in piece]
        if missing:
            errors.append(f"pieza {i}: faltan campos {missing}")
            continue
        if piece["platform"] not in ("threads", "pinterest"):
            errors.append(f"pieza {i}: plataforma inválida {piece['platform']}")
        if piece["sku_id"] not in by_sku:
            errors.append(f"pieza {i}: SKU inexistente {piece['sku_id']}")
        elif piece["route"] != by_sku[piece["sku_id"]]["bridge_route"] or piece["route"] not in routes:
            errors.append(f"pieza {i}: ruta {piece['route']} no es la del SKU {piece['sku_id']}")
        if not isinstance(piece["self_replies"], list) or not isinstance(piece["keywords"], list):
            errors.append(f"pieza {i}: self_replies/keywords deben ser listas")
        text = " ".join([piece["body"], *piece["self_replies"], piece["cta"], piece["title"]])
        if any(word in text.lower() for word in BANNED):
            errors.append(f"pieza {i}: claim prohibido en el texto")
        bad = [tok for tok in PLACEHOLDER.findall(text) if tok != "${BASE_URL}"]
        if bad:
            errors.append(f"pieza {i}: placeholder no permitido {bad}")
        if piece["platform"] == "threads":
            if piece["format"] not in THREAD_FORMATS:
                errors.append(f"pieza {i}: formato Threads inválido")
            if len(piece["self_replies"]) < 2:
                errors.append(f"pieza {i}: menos de 2 auto-respuestas encadenadas")
            if len(piece["keywords"]) != 1:
                errors.append(f"pieza {i}: Threads lleva un solo topic tag")
            if any(len(slide) > 500 for slide in piece["body"].split("\n\n")):
                errors.append(f"pieza {i}: slide de Threads > 500 caracteres")
        else:
            if piece["format"] != "static_pin_2x3":
                errors.append(f"pieza {i}: formato de pin inválido")
            if not 40 <= len(piece["title"]) <= 60:
                errors.append(f"pieza {i}: título de pin fuera de 40-60 ({len(piece['title'])})")
            if not 200 <= len(piece["body"]) <= 350:
                errors.append(f"pieza {i}: descripción fuera de 200-350 ({len(piece['body'])})")
            if not 5 <= len(piece["keywords"]) <= 8:
                errors.append(f"pieza {i}: keywords de pin fuera de 5-8")
            if not piece["board"]:
                errors.append(f"pieza {i}: pin sin tablero")
            if "${BASE_URL}" not in piece["cta"]:
                errors.append(f"pieza {i}: CTA de pin sin ${{BASE_URL}}")
    per_day = Counter(piece["day"] for piece in pieces)
    for day in range(1, meta.get("days", 30) + 1):
        if not 5 <= per_day.get(day, 0) <= 8:
            errors.append(f"día {day}: {per_day.get(day, 0)} piezas (rango 5-8)")
    if max(per_day) > meta.get("days", 30):
        errors.append("hay piezas fuera de la ventana de 30 días")
    if len(pieces) < 150:
        errors.append(f"solo {len(pieces)} piezas (mínimo 150)")
    missing_skus = sorted(set(by_sku) - {piece.get("sku_id") for piece in pieces})
    if missing_skus:
        errors.append(f"SKUs sin cobertura: {missing_skus}")
    last_seen: dict[str, dt.datetime] = {}
    for piece in sorted((p for p in pieces if p["platform"] == "pinterest"),
                        key=lambda p: (p["day"], p["time_local"])):
        stamp, previous = piece_dt(meta, piece), last_seen.get(piece["route"])
        if previous and (stamp - previous).total_seconds() < 72 * 3600:
            errors.append(f"pin repetido <72h en {piece['route']}")
        last_seen[piece["route"]] = stamp
    threads_bank, pins_bank = copy_bank.get("threads", []), copy_bank.get("pinterest", [])
    if len(threads_bank) < 60:
        errors.append(f"copy_bank con {len(threads_bank)} posts Threads (mínimo 60)")
    if len(pins_bank) < 40:
        errors.append(f"copy_bank con {len(pins_bank)} pines (mínimo 40)")
    errors += [f"copy_bank: lane de pin inválido {pin.get('copy_id')}"
               for pin in pins_bank if pin.get("lane") not in PIN_LANES]
    return errors


def cmd_validate(_args) -> int:
    campaign, copy_bank, catalog = (load_json(CAMPAIGN_PATH), load_json(COPY_BANK_PATH),
                                    load_json(CATALOG_PATH))
    errors = check_campaign(campaign, copy_bank, catalog)
    pieces = campaign["pieces"]
    threads = [p for p in pieces if p["platform"] == "threads"]
    pins = [p for p in pieces if p["platform"] == "pinterest"]
    print(f"piezas={len(pieces)} threads={len(threads)} pins={len(pins)} "
          f"skus={len({p['sku_id'] for p in pieces})}/{len(catalog)}")
    print(f"copy_bank: {len(copy_bank['threads'])} threads / {len(copy_bank['pinterest'])} pines")
    print("días:", dict(sorted(Counter(p['day'] for p in pieces).items())))
    if errors:
        print(f"FALLÓ con {len(errors)} errores:")
        for error in errors[:40]:
            print(" -", error)
        return 1
    print("OK: estructura, cobertura 55 SKUs, rutas, ventana 72h y claims")
    return 0


def cmd_export_csv(args) -> int:
    campaign = load_json(CAMPAIGN_PATH)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    fields = ["day", "date", "platform", "time_local", "format", "sku_id", "route", "title",
              "hook", "body", "self_replies", "image", "board", "keywords", "cta", "kpi_target"]
    start = dt.date.fromisoformat(campaign["meta"]["start_date"])
    with out.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for piece in campaign["pieces"]:
            row = {key: piece.get(key, "") for key in fields}
            row["date"] = (start + dt.timedelta(days=piece["day"] - 1)).isoformat()
            row["self_replies"] = " || ".join(piece["self_replies"])
            row["keywords"] = ", ".join(piece["keywords"])
            writer.writerow(row)
    print(f"CSV: {out} ({len(campaign['pieces'])} filas)")
    return 0


def cmd_import_feeds(args) -> int:
    campaign, copy_bank = load_json(CAMPAIGN_PATH), load_json(COPY_BANK_PATH)
    threads_meta = {(t["sku_id"], t["plan_day"], t["plan_time"]): t for t in copy_bank["threads"]}
    pins_meta = {(p["sku_id"], p["plan_day"], p["plan_time"]): p for p in copy_bank["pinterest"]}
    feeds = load_or_init_feeds()
    ids = {post.post_id for post in feeds["threads"]} | {pin.pin_id for pin in feeds["pinterest"]}
    known = {signature("threads", p.target_sku_id, "\n\n".join(p.body_slides)) for p in feeds["threads"]}
    known |= {signature("pinterest", p.target_sku_id, p.seo_description) for p in feeds["pinterest"]}
    added_threads = added_pins = 0
    nums = {name: [int(i.rsplit("_", 1)[-1]) for i in ids
                   if i.startswith(name) and i.rsplit("_", 1)[-1].isdigit()] for name in ("th_", "pin_")}
    next_thread = max(nums["th_"] or [4]) + 1
    next_pin = max([n for n in nums["pin_"] if n >= 100] or [100]) + 1
    for piece in campaign["pieces"]:
        key = (piece["sku_id"], piece["day"], piece["time_local"])
        if piece["platform"] == "threads":
            sig = signature("threads", piece["sku_id"], piece["body"])
            if sig in known:
                continue
            extra = threads_meta.get(key, {})
            item = ThreadsPostItem(
                post_id=f"th_{next_thread:03d}", strategy_lane=extra.get("lane", "via_a_captura_anzuelo"),
                format=piece["format"], hook_pattern=f"Campaña 30d · día {piece['day']} · {piece['format']}",
                body_slides=(piece["body"].split("\n\n") if piece["format"] in
                             ("thread_chain", "carousel_dark") else [piece["body"]]),
                suggested_self_replies=piece["self_replies"],
                target_sku_id=piece["sku_id"], topic_tag=piece["keywords"][0], status="queued",
                bait_widget=BaitWidgetConfig(**extra["bait_widget"]) if extra.get("bait_widget") else None,
                simulated_likes=0, simulated_replies=0, simulated_reposts=0)
            if item.post_id in ids:
                continue
            feeds["threads"].append(item)
            ids.add(item.post_id)
            known.add(sig)
            next_thread += 1
            added_threads += 1
        else:
            sig = signature("pinterest", piece["sku_id"], piece["body"])
            if sig in known:
                continue
            extra = pins_meta.get(key, {})
            feed_pin = PinterestPinItem(
                pin_id=f"pin_{next_pin:03d}", strategy_lane=extra.get("lane", "caballo_de_troya_curiosidad"),
                overlay_headline=piece["hook"], overlay_badge=extra.get("overlay_badge", "GUÍA PRÁCTICA"),
                seo_title=piece["title"], seo_description=piece["body"], board_name=piece["board"],
                bridge_route=piece["route"], target_sku_id=piece["sku_id"],
                visual_engine=extra.get("visual_engine", "vertex_nano_banana_hybrid"),
                visual_theme=extra.get("visual_theme", "dark_luxury_setup_oled"), aspect_ratio="2:3",
                status="queued", simulated_saves=0, simulated_outbound_clicks=0,
                is_competitor_benchmark=False, competitor_source="", image_url=piece["image"])
            feeds["pinterest"].append(feed_pin)
            ids.add(feed_pin.pin_id)
            known.add(sig)
            next_pin += 1
            added_pins += 1

    if args.dry_run:
        print(f"[dry-run] añadiría {added_threads} threads y {added_pins} pines")
        return 0
    if added_threads or added_pins: save_feeds(feeds["threads"], feeds["pinterest"])
    print(f"import: +{added_threads} threads, +{added_pins} pines · total "
          f"{len(feeds['threads'])} threads / {len(feeds['pinterest'])} pines")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Campaña 30 días de @ronOverthinks")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate").set_defaults(func=cmd_validate)
    export = sub.add_parser("export-csv")
    export.add_argument("--out", default=str(MARKETING_DIR / "campaign_30d.csv"))
    export.set_defaults(func=cmd_export_csv)
    importer = sub.add_parser("import-feeds")
    importer.add_argument("--dry-run", action="store_true")
    importer.set_defaults(func=cmd_import_feeds)
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
