import re
from typing import Any, Dict, List
from backend.config import GLOBAL_SKILLS_DIR
from backend.models.catalog_models import SkillCustomizationItem

CATEGORY_KEYWORDS = {
    "viral_hooks": ["hook", "viral", "headline", "title", "attention"],
    "funnel_conversion": ["funnel", "sales", "landing", "conversion", "copywriting", "pricing"],
    "stealth_antibot": ["stealth", "playwright", "browser", "fingerprint", "bot", "captcha"],
    "reverse_engineering": ["reverse", "competitor", "teardown", "protocol", "audit"],
    "ron_mode": ["ron_mode", "ragebait", "anzuelo", "trojan"],
}


def _infer_category(skill_id: str, desc: str) -> str:
    combined = f"{skill_id} {desc}".lower()
    if skill_id.startswith("ron_mode_"):
        return "ron_mode"
    for cat, words in CATEGORY_KEYWORDS.items():
        if any(w in combined for w in words):
            return cat
    return "tools_engineering"


def load_all_skills(default_skills: List[Dict[str, Any]], toggles: Dict[str, bool]) -> List[SkillCustomizationItem]:
    skills_map: Dict[str, SkillCustomizationItem] = {}

    for sk in default_skills:
        sid = sk["skill_id"]
        # `installed_on_disk` significa EXACTAMENTE eso. Los skills MODO RON son
        # reglas internas del producto, no carpetas en ~/.agents/skills: antes se
        # marcaban instaladas sin estarlo (estado falso).
        installed = (GLOBAL_SKILLS_DIR / sid).is_dir()
        enabled = toggles.get(sid, sk["enabled"])
        skills_map[sid] = SkillCustomizationItem(
            skill_id=sid,
            name=sk["name"],
            category=sk["category"],
            enabled=bool(enabled),
            installed_on_disk=installed,
            power_rule=sk["power_rule"],
        )

    if GLOBAL_SKILLS_DIR.exists():
        for skill_dir in sorted(GLOBAL_SKILLS_DIR.iterdir()):
            if not skill_dir.is_dir():
                continue
            sid = skill_dir.name
            if sid in skills_map:
                continue
            skill_md = skill_dir / "SKILL.md"
            power_rule = "Regla de automatización para agente Antigravity."
            display_name = sid.replace("-", " ").replace("_", " ").title()
            if skill_md.exists():
                try:
                    txt = skill_md.read_text(encoding="utf-8", errors="ignore")[:600]
                    desc_match = re.search(r"description:\s*(?:>-\s*|\"|')?([^\n\r\"']+)", txt)
                    if desc_match:
                        power_rule = desc_match.group(1).strip()
                except Exception:
                    pass
            cat = _infer_category(sid, power_rule)
            enabled = toggles.get(sid, True)
            skills_map[sid] = SkillCustomizationItem(
                skill_id=sid,
                name=display_name,
                category=cat,
                enabled=bool(enabled),
                installed_on_disk=True,
                power_rule=power_rule,
            )

    return list(skills_map.values())
