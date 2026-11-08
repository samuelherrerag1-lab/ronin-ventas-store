"""Generador programático del catálogo de prompts de arte para Ronin Ventas OS."""
import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
DATA_DIR = BASE_DIR / "data"
OUTPUT_FILE = DATA_DIR / "product_art_prompts.json"

RON_SEED = "data/generated_images/ron_canonical_seed.png"

# Reglas estrictas: Cero texto, alta fidelidad visual
NO_TXT = "No text, no letters, no typography, clean composition."


def build_prompts():
    from backend.services.catalog_data import BOVEDA_SPECS, EBOOK_SPECS, MICRO_APP_SPECS

    data = {
        "covers": {},
        "ebook_interiors": {},
        "interfaces": {},
        "wallpapers_ios": {},
        "dark_luxury_pins": {},
        "ron_scenes": {},
        "banners": {},
        "stan_store_profile": {},
        "decor": {},
    }

    # 1. Portadas (E01-E12: 3 variantes; resto: 2 variantes)
    for eb in EBOOK_SPECS:
        sku = eb[0]
        title = eb[2]
        data["covers"][f"{sku}_v1"] = {"sku": sku, "aspect": "3:4", "ron": True, "prompt": f"Ron in terracotta hoodie holding minimalist tablet showing {title}, dramatic night shadows, halftone grain. {NO_TXT}"}
        data["covers"][f"{sku}_v2"] = {"sku": sku, "aspect": "3:4", "ron": True, "prompt": f"Ron in terracotta hoodie seated at midnight desk with coffee mug, contemplative expression, dark studio glow. {NO_TXT}"}
        data["covers"][f"{sku}_v3"] = {"sku": sku, "aspect": "3:4", "ron": False, "prompt": f"Dark luxury editorial book mockup on black slate, subtle gold foil embossed lines, soft cinematic lighting. {NO_TXT}"}

    for bv in BOVEDA_SPECS:
        sku = bv[0]
        desc = bv[2]
        data["covers"][f"{sku}_v1"] = {"sku": sku, "aspect": "3:4", "ron": False, "prompt": f"Heavy obsidian vault door slightly ajar, warm gold interior light spilling onto dark marble, luxury editorial. {NO_TXT}"}
        data["covers"][f"{sku}_v2"] = {"sku": sku, "aspect": "3:4", "ron": False, "prompt": f"Dark titanium security briefcase open on espresso wood table, showing classified brass modules, 35mm lens. {NO_TXT}"}

    for ap in MICRO_APP_SPECS:
        sku = ap[0]
        title = ap[2]
        data["covers"][f"{sku}_v1"] = {"sku": sku, "aspect": "3:4", "ron": False, "prompt": f"Ultra-thin dark OLED tablet floating over black desk showing illuminated sliders and tactile dials, emerald glow. {NO_TXT}"}
        data["covers"][f"{sku}_v2"] = {"sku": sku, "aspect": "3:4", "ron": False, "prompt": f"Sleek minimalist hardware synthesizer console in obsidian and gold, macro angle, high tech dark luxury. {NO_TXT}"}

    for i in range(1, 11):
        sku = f"K{i:02d}"
        data["covers"][f"{sku}_v1"] = {"sku": sku, "aspect": "3:4", "ron": True, "prompt": f"Ron in terracotta hoodie assembling dark mechanical system gears and glowing wireframe modules at night. {NO_TXT}"}
        data["covers"][f"{sku}_v2"] = {"sku": sku, "aspect": "3:4", "ron": True, "prompt": f"Ron in terracotta hoodie holding a dark obsidian master box with golden light emanating from within. {NO_TXT}"}

    mega_prompts = [
        ("M01", "Ron standing before towering obsidian archive lockers"),
        ("M02", "Colossal obsidian monolith in brutalist hall with emerald circuit lines"),
        ("M03", "Ron seated in high-backed dark leather armchair contemplating a golden chess queen"),
        ("M04", "Ron walking through open vault door towards morning city horizon"),
        ("M05", "Grid of 12 glowing dark glass cards on black velvet"),
        ("M06", "Ron holding glowing master key in front of colossal Insider Vault entrance"),
    ]
    for sku, p in mega_prompts:
        data["covers"][f"{sku}_v1"] = {"sku": sku, "aspect": "3:4", "ron": "Ron" in p, "prompt": f"{p}, dark luxury lighting. {NO_TXT}"}
        data["covers"][f"{sku}_v2"] = {"sku": sku, "aspect": "3:4", "ron": "Ron" in p, "prompt": f"{p}, alternate dramatic wide angle view. {NO_TXT}"}

    lead_prompts = [
        ("L01", "Ron holding a small glowing document with a curious surprised expression"),
        ("L02", "Ron with finger over lips whispering a secret in dark atmospheric shadows"),
        ("L03", "Ron using brass magnifying glass to inspect tiny glowing wireframe engine"),
    ]
    for sku, p in lead_prompts:
        data["covers"][f"{sku}_v1"] = {"sku": sku, "aspect": "3:4", "ron": True, "prompt": f"{p}, cinematic 2D comic frame. {NO_TXT}"}
        data["covers"][f"{sku}_v2"] = {"sku": sku, "aspect": "3:4", "ron": True, "prompt": f"{p}, intense night rim lighting. {NO_TXT}"}

    # 2. Ilustraciones interiores (6 por ebook E01-E12)
    ebook_concepts = [
        ("E01", ["midnight desk with iPad and cold coffee", "flow of digital files across dark networks", "silent printing press in dark room", "stack of black minimalist paper folios", "Ron examining file metadata at 3 AM", "clean obsidian stamp on parchment"]),
        ("E02", ["red and gold bridge pins connecting on dark map", "magnifying glass over search query", "Ron pinning cards onto dark corkboard", "stream of visitors funneling into vault", "golden compass on black slate", "bridge extending into dark horizon"]),
        ("E03", ["lightning striking dark calm ocean water", "split shadow mask over dramatic face", "Ron observing chaotic notifications on curved screen", "hourglass running backwards on marble", "flock of dark birds swirling upward", "chessboard with single overturned white pawn"]),
        ("E04", ["silhouette behind translucent glass panel", "constellation of 10 glowing nodes", "Ron working quietly in dark minimalist room", "automated assembly line of black cards", "clock hands frozen at 12:00", "dark horizon with glowing dawn line"]),
        ("E05", ["wireframe teardown of complex mechanism", "laser scanning intricate watch movement", "Ron dissecting holographic blueprint", "circuit board etched in brushed copper", "microscope focusing on golden microchip", "gears separating cleanly into components"]),
        ("E06", ["precision printing press with black ink", "stack of luxury guides tied with black ribbon", "Ron tuning dials on dark console", "assembly line under warm spot lighting", "obsidian ruler and gold fountain pen", "clean minimal workspace at midnight"]),
        ("E07", ["three monitors glowing in dark empty office", "phantom lines of code floating in air", "Ron walking through corridor of servers", "automated mechanical clock ticking alone", "shadow typing on invisible keyboard", "emerald matrix light spilling under door"]),
        ("E08", ["obsidian chess knight casting long shadow", "balance scale tilting with single gold coin", "Ron studying psychological portrait", "dark velvet curtain pulled slightly back", "pair of antique brass calipers", "golden key resting on black cushion"]),
        ("E09", ["single spotlight in pitch black auditorium", "soundwave spike glowing amber on oscilloscope", "Ron staring forward with high contrast lighting", "prism refracting golden light beam", "target bullseye made of obsidian rings", "stopwatch frozen at three seconds"]),
        ("E10", ["golden halo ring glowing behind dark silhouette", "throne-like high-back chair in dark hall", "Ron standing tall in terracotta hoodie with authority", "pedestal made of black marble with spotlight", "crown forged in dark gunmetal and gold", "clean architectural symmetry in dark hall"]),
        ("E11", ["iron chains breaking against dark slate", "open window looking out at early morning sky", "Ron packing single black bag at midnight", "cracked concrete with flower blooming in gold", "empty office cubicle with glowing monitor", "deserted highway under starlit night"]),
        ("E12", ["two coins balancing on knife edge: peso and dollar", "global timezone clock wall in dark wood", "Ron overlooking illuminated harbor at night", "airplane wing passing over dark sea", "telegraph wire carrying golden sparks", "sunrise over mountain ridge in deep indigo"]),
    ]
    for sku, concepts in ebook_concepts:
        for idx, c in enumerate(concepts, 1):
            key = f"{sku}_ill_{idx:02d}"
            is_ron = "Ron" in c
            data["ebook_interiors"][key] = {"sku": sku, "aspect": "16:9", "ron": is_ron, "prompt": f"Editorial cinematic illustration: {c}, dark luxury style, deep shadows. {NO_TXT}"}

    # 3. Arte de interfaz (A01-A12 y B01-B12)
    for i in range(1, 13):
        data["interfaces"][f"A{i:02d}_ui"] = {"aspect": "16:9", "ron": False, "prompt": f"Dark mode software panel interface header, glowing emerald and amber telemetry dials, obsidian glass texture, sleek HUD. {NO_TXT}"}
        data["interfaces"][f"B{i:02d}_ui"] = {"aspect": "16:9", "ron": False, "prompt": f"Subterranean vault archive panel, heavy dark titanium rivets, glowing brass status lamps, luxury security aesthetic. {NO_TXT}"}

    # 4. 20 Wallpapers iOS 17
    wallpapers = [
        "Deep titanium mesh with subtle gold refraction", "OLED abstract smoke swirls in charcoal and amber", "Midnight cityscape bokeh through rain-streaked glass",
        "Minimalist black marble with single thin gold vein", "Brushed dark graphite with diagonal precision milled grooves", "Dark espresso leather macro texture with fine stitching",
        "Ethereal northern lights in deep emerald over obsidian ice", "Architectural brutalist staircase at dusk with amber light", "Macro of complex tourbillon watch movement in dark ruthenium",
        "Liquid obsidian ripples with metallic gold reflections", "Dark room single shaft of warm sunlight through slit", "Subtle topographic contour lines in dark gray on black",
        "Moody forest fog in deep twilight with pine silhouettes", "Obsidian geometric prism catching rim light", "Black sand dunes under starlit night sky",
        "Macro water droplets on matte black carbon fiber", "Abstract dark waves of flowing satin silk", "Minimalist concrete wall with warm raking shadow",
        "Dark circuit traces glowing faintly in deep copper", "Clean OLED pure black with subtle micro-starfield",
    ]
    for idx, w in enumerate(wallpapers, 1):
        data["wallpapers_ios"][f"ios17_wp_{idx:02d}"] = {"aspect": "3:4", "ron": False, "prompt": f"Photorealistic luxury iPhone wallpaper: {w}, shot on 35mm f/1.4, clean composition. {NO_TXT}"}

    # 5. 12 Dark Luxury Pines 70%
    pins = [
        "Black obsidian chess knight with fine gold inlay on marble", "Luxury dark chronograph watch with leather strap on espresso wood", "Minimalist workstation at night with ultrawide OLED and warm desk lamp",
        "Penthouse terrace at 3 AM overlooking rainy metropolis", "Vintage brass telescope pointing out floor-to-ceiling dark glass", "Dark leather ledger open with fountain pen and brass weights",
        "Obsidian signet ring resting on black velvet tray", "Monolithic black coffee machine pulling rich espresso with crema", "Clean terminal screen on dark glass desk showing matrix graphs",
        "Black titanium sunglasses on architectural slate stone", "Heavy bank vault dial mechanism with glowing brass numbers", "Minimalist luxury staircase of floating black granite steps",
    ]
    for idx, p in enumerate(pins, 1):
        data["dark_luxury_pins"][f"pin_dark_{idx:02d}"] = {"aspect": "3:4", "ron": False, "prompt": f"Dark luxury editorial photography: {p}, dramatic museum raking light, authentic film grain. {NO_TXT}"}

    # 6. 10 Ron Canonical Scenes
    ron_scenes = [
        "Ron sitting cross-legged on dark floor reviewing blueprints", "Ron leaning on balcony railing looking at night sky", "Ron holding glowing lightbulb with puzzled thoughtful expression",
        "Ron examining complex mechanical watch with tweezers", "Ron walking through dark rain with black umbrella", "Ron pointing at glowing chart showing sudden vertical spike",
        "Ron typing furiously on laptop with coffee steam rising", "Ron standing victorious in front of opened massive vault", "Ron sketching on digital drafting pad at 3:14 AM",
        "Ron holding small golden key up to the moonlight",
    ]
    for idx, r in enumerate(ron_scenes, 1):
        data["ron_scenes"][f"ron_scene_{idx:02d}"] = {"aspect": "3:4", "ron": True, "prompt": f"{r}, cinematic 2D comic frame, dramatic lighting, halftone shadows. {NO_TXT}"}

    # 7. 12 Reusable Banners (16:9)
    banners = [
        ("banner_niche_faceless", "Wide panorama of dark luxury trading and creator desk at night with multiple OLED monitors, espresso"),
        ("banner_niche_ai", "Wide dark panoramic server room with sleek black blades and subtle emerald phosphor lights"),
        ("banner_niche_psychology", "Wide dramatic chess board with obsidian and gold pieces illuminated by soft raking light"),
        ("banner_niche_escape", "Wide panoramic empty modern corporate floor at 3 AM looking through glass at dark skyline"),
        ("banner_fmt_blueprint", "Wide view of dark editorial drafting desk with black notebooks, brass instruments, and blueprints"),
        ("banner_fmt_vault", "Wide view of dark subterranean bank vault with rows of obsidian safety deposit boxes"),
        ("banner_fmt_apps", "Wide view of clean dark minimalist hardware lab with glass screens and tactile interfaces"),
        ("banner_fmt_system", "Wide view of interconnected glowing golden mechanical gears and data pipelines on dark slate"),
        ("banner_ron_3am", "Ron in terracotta hoodie working at dark desk with dual monitors at 3:14 AM with coffee mug"),
        ("banner_ron_city", "Ron in terracotta hoodie standing on a dark balcony looking over vast illuminated city at night"),
        ("banner_ron_lab", "Ron in terracotta hoodie dissecting algorithms on a glowing dark glass workbench"),
        ("banner_ron_vault", "Ron in terracotta hoodie standing inside a massive circular vault opening, golden light behind"),
    ]
    for b_id, b_p in banners:
        is_ron = "Ron" in b_p
        data["banners"][b_id] = {"aspect": "16:9", "ron": is_ron, "prompt": f"{b_p}, dark luxury panoramic composition. {NO_TXT}"}

    # 8. Stan Store Campaign & Profile
    stan = [
        ("stan_hero_faceless", "16:9", False, "Panoramic luxury hero banner for digital products store, dark obsidian and gold cards floating"),
        ("stan_hero_ai", "16:9", False, "Panoramic cyberpunk luxury hero banner, glowing neural networks and dark minimalist hardware"),
        ("stan_hero_psychology", "16:9", False, "Panoramic editorial hero banner, dark marble chess board with warm directional light"),
        ("stan_hero_escape", "16:9", False, "Panoramic hero banner, modern minimalist penthouse office looking at night horizon"),
        ("profile_avatar_ron", "1:1", True, "Ron canonical portrait looking directly at viewer with slight cynical smirk, terracotta hoodie, circular crop friendly"),
        ("profile_banner_ron", "16:9", True, "Wide profile banner showing Ron working late at his minimalist command center surrounded by glowing screens"),
    ]
    for s_id, asp, is_ron, s_p in stan:
        data["stan_store_profile"][s_id] = {"aspect": asp, "ron": is_ron, "prompt": f"{s_p}. {NO_TXT}"}

    # 9. 24 Decor items (dividers, seals, textures, frames)
    decors = [
        ("decor_divider_01", "16:9", False, "Minimalist horizontal divider bar with brushed gold center knot on black background"),
        ("decor_divider_02", "16:9", False, "Dark horizontal divider line with glowing emerald micro-circuit traces in center"),
        ("decor_divider_03", "16:9", False, "Dark line with polished obsidian diamond emblem in middle on black slate"),
        ("decor_divider_04", "16:9", False, "Horizontal decorative rule featuring tiny gold mechanical gears in center"),
        ("decor_divider_05", "16:9", False, "Dark horizontal divider bar with minimalist terracotta accent stroke in center"),
        ("decor_divider_06", "16:9", False, "Five tiny polished gold dots in a horizontal row on deep black background"),
        ("decor_seal_01", "1:1", False, "Dark circular wax seal made of black obsidian with embossed gold monogram crown"),
        ("decor_seal_02", "1:1", False, "Dark octagonal titanium security badge with gold beveled edge and center keyhole icon"),
        ("decor_seal_03", "1:1", True, "Dark round crest featuring minimalist stylized Ron hoodie silhouette embossed in gold"),
        ("decor_seal_04", "1:1", False, "Circular heavy bronze stamp emblem with vault lock dial motif on dark background"),
        ("decor_seal_05", "1:1", False, "Dark metal medallion with intricate interlocking watch gears embossed in gold foil"),
        ("decor_seal_06", "1:1", False, "Dark square emblem with gold broken chain motif on black granite"),
        ("decor_texture_01", "1:1", False, "Ultra-fine weave matte black carbon fiber seamless texture"),
        ("decor_texture_02", "1:1", False, "Subtle 35mm film grain on pure OLED black background"),
        ("decor_texture_03", "1:1", False, "Black imperial marble texture with subtle deep charcoal and gold veins"),
        ("decor_texture_04", "1:1", False, "Dark espresso brown leather grain surface under soft raking light"),
        ("decor_texture_05", "1:1", False, "Dark brushed titanium metal surface with horizontal micro-scratches"),
        ("decor_texture_06", "1:1", False, "Dark slate surface with faint etched copper circuit lines glowing dimly"),
        ("decor_frame_01", "1:1", False, "Dark card frame with delicate brushed gold geometric corner brackets on black"),
        ("decor_frame_02", "1:1", False, "Tech frame with glowing green terminal corner accents on pitch black background"),
        ("decor_frame_03", "1:1", False, "Industrial luxury frame with matte black metal border and tiny gold corner rivets"),
        ("decor_frame_04", "1:1", False, "Thin single-pixel-style gold border framing a dark card area, minimalist luxury"),
        ("decor_frame_05", "1:1", False, "Subtle dark diagonal micro-stripes accent border in terracotta and black"),
        ("decor_frame_06", "1:1", False, "Dark smoked glass card holder with gold clip at top on dark background"),
    ]
    for d_id, asp, is_ron, d_p in decors:
        data["decor"][d_id] = {"aspect": asp, "ron": is_ron, "prompt": f"{d_p}. {NO_TXT}"}

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    total = sum(len(v) for v in data.values())
    print(f"Catálogo de prompts generado con éxito: {total} prompts en {OUTPUT_FILE}")


if __name__ == "__main__":
    build_prompts()
