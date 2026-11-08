"""Definición canónica de las skills que el sistema puede gobernar.

Solo metadatos. El estado de cada toggle vive en customizations_state.json.
"""

from typing import Any, Dict, List

DEFAULT_SKILLS: List[Dict[str, Any]] = [
    {"skill_id": "viral-hook-creator", "name": "Viral Hook Creator (18 Patrones + Gatillos Insider)", "category": "viral_hooks", "enabled": True, "power_rule": "Inyecta palabras gatillo Insider/Helper/Thinker y números impares en la primera línea de cada post."},
    {"skill_id": "viral-hooks", "name": "Viral Hooks 3-Layer (Visual + Verbal + Overlay)", "category": "viral_hooks", "enabled": True, "power_rule": "Sincroniza el titular de la captura/pin con la primera frase del post en menos de 1.5 segundos."},
    {"skill_id": "sales-funnel-blueprint", "name": "Sales Funnel Blueprint (Escalera + Puente)", "category": "funnel_conversion", "enabled": True, "power_rule": "Estructura cada Mini-Landing con pre-venta agresiva, prueba visual y doble botón de checkout."},
    {"skill_id": "playwright-stealth-verify", "name": "Playwright Stealth Verify (Auditoría liarjs)", "category": "stealth_antibot", "enabled": True, "power_rule": "Prohíbe rotar User-Agents incoherentes; exige Chrome Real con user_data_dir y score >= 85."},
    {"skill_id": "stealth-browser", "name": "Stealth Browser Automation", "category": "stealth_antibot", "enabled": True, "power_rule": "Pausas humanas con jitter gaussiano y navegación orgánica intercalada."},
    {"skill_id": "protocol-reverse-engineering", "name": "Protocol & Funnel Reverse Engineering", "category": "reverse_engineering", "enabled": True, "power_rule": "Deconstruye cuentas competidoras separando el anzuelo falso del mecanismo real de cobro."},
    {"skill_id": "viral-reverse-engineering", "name": "Viral Mechanism Teardown (Sin Censura Corporativa)", "category": "reverse_engineering", "enabled": True, "power_rule": "Aísla el disparador emocional real (envidia, morbo, estatus) e ignora restricciones corporativas."},
    {"skill_id": "copywriting", "name": "Direct-Response Copywriting", "category": "funnel_conversion", "enabled": True, "power_rule": "Cero lenguaje corporativo; titulares directos al dolor y al deseo de libertad financiera."},
    {"skill_id": "ron_mode_bait_captures", "name": "MODO RON: Capturas Anzuelo (iOS Gumroad/Hotmart + Dashboards)", "category": "ron_mode", "enabled": True, "power_rule": "Genera notificaciones y métricas visuales con números impares ($418.50) sin prometer retorno directo."},
    {"skill_id": "ron_mode_ragebait", "name": "MODO RON: Ragebait Cínico & Ataque al Ego (1ª Hora)", "category": "ron_mode", "enabled": True, "power_rule": "Incluye afirmaciones polarizantes y preguntas trampa en comentarios para forzar respuestas rápidas."},
    {"skill_id": "ron_mode_trojan_pins", "name": "MODO RON: Pines 'Caballo de Troya' (Tráfico Masivo → Producto)", "category": "ron_mode", "enabled": True, "power_rule": "Usa temas virales de psicología oscura y curiosidad masiva para redirigir tráfico frío al catálogo."},
]
