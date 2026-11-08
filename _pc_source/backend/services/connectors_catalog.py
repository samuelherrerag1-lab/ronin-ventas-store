"""Definición canónica de los conectores del sistema.

Solo metadatos. Ningún estado de conexión vive aquí.
"""

from typing import Any, Dict, List

from backend.config import NANO_BANANA_FALLBACK_MODEL, NANO_BANANA_MODEL, VERTEX_LOCATION, VERTEX_PROJECT_ID

DEFAULT_CONNECTORS: List[Dict[str, Any]] = [
    {
        "connector_id": "google_master",
        "name": "Google Master Session (SSO Vault)",
        "category": "auth_sso",
        "auth_mode": "Chrome Real Persistente (user_data_dir)",
        "account_label": "Cuenta Google Principal",
        "login_url": "https://accounts.google.com/",
        "description": "Chrome Persistente para acceder en 1 clic a Pinterest, Gumroad y Hotmart.",
        "capabilities": ["SSO 1-Clic en Apps", "Huella Residencial Real", "Persistencia de Cookies y WebGL"],
    },
    {
        "connector_id": "threads",
        "name": "Threads (@ronoverthinks)",
        "category": "social_network",
        "auth_mode": "Sesión Nativa en Chrome Vault",
        "account_label": "@ronoverthinks",
        "login_url": "https://www.threads.net/login",
        "description": "Publicación de posts, hilos y anzuelos visuales con auto-comentario en 1ª hora.",
        "capabilities": ["Publicación Hilos/Carruseles", "Auto-Comentario 1ª Hora", "Evasión Anti-Bot liarjs"],
    },
    {
        "connector_id": "pinterest",
        "name": "Pinterest Business (@ronoverthinks)",
        "category": "social_network",
        "auth_mode": "Google OAuth 1-Clic en Chrome Vault",
        "account_label": "@ronoverthinks",
        "login_url": "https://www.pinterest.com/login/",
        "description": "Pines 2:3 hacia las 55 rutas puente semánticas únicas sin repetir URL en <72h.",
        "capabilities": ["Subida 2:3 y 9:16", "Asignación de Tableros SEO", "Rotación de 55 Rutas Puente"],
    },
    {
        "connector_id": "gumroad",
        "name": "Gumroad (Checkout Global USD)",
        "category": "checkout_gateway",
        "auth_mode": "Google OAuth 1-Clic en Chrome Vault",
        "account_label": "Tienda Gumroad USD",
        "login_url": "https://app.gumroad.com/login",
        "description": "Pasarela internacional con cobro en USD, Apple Pay y sincronización de los 52 SKUs.",
        "capabilities": ["Cobro en USD / Apple Pay / PayPal", "Catálogo 52 SKUs", "Sincronización de Links"],
    },
    {
        "connector_id": "hotmart",
        "name": "Hotmart (Checkout Colombia/LatAm)",
        "category": "checkout_gateway",
        "auth_mode": "Google OAuth 1-Clic en Chrome Vault",
        "account_label": "Cuenta Hotmart LatAm",
        "login_url": "https://app-vlc.hotmart.com/login",
        "description": "Pasarela principal LatAm con cobro en COP/Nequi/PSE/Efecty y liquidación directa.",
        "capabilities": ["Nequi / PSE / Efecty", "Extracción de Hotlinks", "Embudo Moneda Local"],
    },
    {
        "connector_id": "vertex_ai",
        "name": f"Vertex AI & Nano Banana 2 ({VERTEX_PROJECT_ID})",
        "category": "ai_cloud",
        "auth_mode": "GCP Application Default Credentials (ADC)",
        "account_label": VERTEX_PROJECT_ID,
        "login_url": "https://console.cloud.google.com/vertex-ai",
        "description": f"Generación de imagen híbrida ({NANO_BANANA_MODEL} en {VERTEX_LOCATION}, fallback {NANO_BANANA_FALLBACK_MODEL}) y Circuit Breaker FinOps.",
        "capabilities": ["Nano Banana 2 Image Gen", "Ron Canónico 2D", "Circuit Breaker FinOps $50"],
    },
    {
        "connector_id": "opencode_v2",
        "name": "OpenCode V2 (SubAgente Fábrica)",
        "category": "ai_cloud",
        "auth_mode": "Daemon Local 127.0.0.1:28894 (service.json)",
        "account_label": "ses_e64c0d9b1ffe56MtJmi0RNNym4",
        "login_url": "http://127.0.0.1:28894",
        "description": "Subagente background con deepseek-v4.1-flash max ($0 cuota) para productos HTML.",
        "capabilities": ["DeepSeek-v4.1-flash Max", "Cost: $0/token", "Sesión Canónica Persistente"],
    },
    {
        "connector_id": "github_pages",
        "name": "GitHub / Cloudflare Deploy (Stan + 55 Landings)",
        "category": "deploy_hosting",
        "auth_mode": "GitHub CLI (gh keyring)",
        "account_label": "samuelherrerag1-lab",
        "login_url": "https://github.com/samuelherrerag1-lab",
        "description": "Despliegue estático para Stan Store Pro y 55 rutas puente semánticas.",
        "capabilities": ["Deploy Estático $0/mes", "55 URLs Semánticas Anti-Spam", "Doble Botón Checkout"],
    },
]
