import random
from typing import Dict, List, Optional
from backend.config import FEEDS_JSON_PATH, ensure_dirs
from backend.models.catalog_models import BaitWidgetConfig, PinterestPinItem, ThreadsPostItem
from backend.services.json_store import (
    lock_for,
    quarantine_corrupt,
    read_json,
    write_json_atomic,
)
from backend.services.pinterest_seed_data import build_default_pinterest_pins

MUTATION_NOTE = (
    "Variante generada con una plantilla local aleatoria. No se usó ningún modelo "
    "de IA y no hay métricas medidas: los contadores del feed siguen siendo simulados."
)

HOOK_MUTATION_TEMPLATES = [
    "Opinión impopular: si tienes IA gratis y sigues ganando menos de $1,800/mes, tu problema no es el país, es cómo usas el cerebro. ({angle})",
    "Hice esta prueba silenciosa a las 3:14 AM con un archivo de 18 páginas y el algoritmo hizo el resto: {angle}",
    "El 97% de la gente pierde 5 años estudiando lo que un sistema automatizado resuelve en 48 horas. {angle}",
    "Nadie te lo va a admitir en público, pero así es como realmente se mueve el dinero digital hoy: {angle}",
    "¿Prefieres ganar $4,500/mes siendo un fantasma en internet o $8,000 teniendo que poner tu cara todos los días? ({angle})",
]


def build_default_threads_posts() -> List[ThreadsPostItem]:
    return [
        ThreadsPostItem(
            post_id="th_001",
            strategy_lane="via_a_captura_anzuelo",
            format="image_bait",
            hook_pattern="Insider Experiment + Odd Number Proof",
            body_slides=[
                "Subí un documento oscuro de 18 páginas un martes a las 11 PM sin mostrar la cara ni grabar un solo Reel.\n\nDesperté a las 7:12 AM con la pantalla así ($418.50 acumulados entre Gumroad y Hotmart).\n\nLa gente sigue creyendo que necesita 50.000 seguidores para facturar. No necesitas audiencia, necesitas un puente donde la gente ya tiene la tarjeta en la mano."
            ],
            suggested_self_replies=[
                "Antes de que pregunten en DM: no es dropshipping ni cripto. Dejé el desglose exacto del experimento arriba en mi perfil antes de pasarlo a privado.",
                "Pregunta honesta: ¿cuántos de aquí tienen al menos 1 producto digital de $19 cobrando mientras duermen? Los leo 👇",
            ],
            target_sku_id="E01",
            topic_tag="Negocios Digitales",
            bait_widget=BaitWidgetConfig(
                widget_type="ios_lockscreen",
                headline_metric="$418.50 USD",
                sub_metric="9 notificaciones durante la noche",
                notifications=[
                    "Gumroad • Hace 14 min — You made a sale! ($29.00) - Sistema Completo #1",
                    "Hotmart • Hace 41 min — ¡Venta realizada! Tu comisión: $19.40 USD (Nequi/PSE)",
                    "Gumroad • Hace 2 h — You made a sale! ($27.00) - Ingeniería Inversa IA",
                    "Gumroad • Hace 4 h — You made a sale! ($19.00) - Máquina Silenciosa PDF",
                ],
                timestamp_label="07:12",
            ),
            simulated_likes=842,
            simulated_replies=194,
            simulated_reposts=67,
        ),
        ThreadsPostItem(
            post_id="th_002",
            strategy_lane="via_b_ragebait_cinico",
            format="thread_chain",
            hook_pattern="Ego Attack + Contrarian Math",
            body_slides=[
                "1/4 Opinión que va a molestar a varios:\n\nSi tienes acceso a Gemini, Claude y ChatGPT y sigues cambiando 45 horas de tu semana por un sueldo en moneda local devaluada, ya no es falta de oportunidades. Es pereza mental.",
                "2/4 A tu jefe no le pagan más porque sea 10 veces más inteligente que tú.\n\nLe pagan más porque él entiende el apalancamiento (comprar horas ajenas o construir activos que se venden 1.000 veces) y a ti te entrenaron para pedir permiso.",
                "3/4 Un solo activo digital de $19 vendido a 4 personas al día son $2,280 dólares al mes.\n\nConseguir 4 clics de compra al día en un buscador de 500 millones de usuarios como Pinterest no requiere talento. Requiere un sistema.",
                "4/4 Armé un simulador en HTML (1 solo archivo) donde mueves dos barras y ves cuántos días de tu sueldo reemplaza cada venta.\n\nEstá en el link de mi bio junto con la bóveda completa.",
            ],
            suggested_self_replies=[
                "El que se ofendió en el primer post acaba de confirmar exactamente el punto 2.",
                "¿Prefieres $3,000/mes con una cuenta anónima o $10,000/mes siendo influencer famoso? El 90% responde desde el ego.",
            ],
            target_sku_id="A11",
            topic_tag="Psicología del Dinero",
            bait_widget=BaitWidgetConfig(
                widget_type="iphone_note_3am",
                headline_metric="Regla de las 3:00 AM",
                sub_metric="Notas de Ron Overthinks",
                notifications=[
                    "1. El sueldo fijo es el soborno que te dan para olvidar tus propios activos.",
                    "2. 4 ventas de $19 al día = $2,280/mes.",
                    "3. Quien controla el embudo controla el margen.",
                ],
                timestamp_label="03:04 AM",
            ),
            simulated_likes=1290,
            simulated_replies=348,
            simulated_reposts=112,
        ),
        ThreadsPostItem(
            post_id="th_003",
            strategy_lane="via_c_demo_microapp",
            format="carousel_dark",
            hook_pattern="Unfair Tool Reveal + Swipe Breakdown",
            body_slides=[
                "LÁMINA 1: Me cansé de ver a la gente escribir posts tibios que nadie lee. Así que programé este generador en 1 solo archivo HTML (HookForge Pro).",
                "LÁMINA 2: El problema del 99% en Threads: abren con 'Hoy quiero compartir 3 consejos...'. Tu cerebro ignora eso en 0.4 segundos.",
                "LÁMINA 3: Cómo funciona el secuestro de atención: número impar + contradicción al estatus + brecha de curiosidad abierta.",
                "LÁMINA 4: En lugar de pensar media hora, seleccionas el gatillo (Envidia, Insider, Miedo) y la Micro-App te escupe 30 ganchos listos.",
                "LÁMINA 5: Puedes descargar el archivo .html completo hoy mismo en mi perfil y correrlo offline en tu PC o teléfono.",
            ],
            suggested_self_replies=[
                "No requiere suscripción mensual ni servidor. Abres el archivo .html en tu navegador y es tuyo para siempre.",
            ],
            target_sku_id="A01",
            topic_tag="Inteligencia Artificial",
            bait_widget=BaitWidgetConfig(
                widget_type="micro_app_mockup",
                headline_metric="HookForge Pro v2.4 (Offline .HTML)",
                sub_metric="Score de Voltaje Emocional: 96/100",
                notifications=[
                    "[PATRÓN INSIDER] → Generados 18 hooks en 0.2s",
                    "[PATRÓN CONTRARIAN] → CTR estimado +340%",
                ],
                timestamp_label="LIVE APP",
            ),
            simulated_likes=615,
            simulated_replies=127,
            simulated_reposts=59,
        ),
        ThreadsPostItem(
            post_id="th_004",
            strategy_lane="via_a_captura_anzuelo",
            format="image_bait",
            hook_pattern="Reverse Engineering Teardown",
            body_slides=[
                "Desmonté 14 cuentas gringas que dicen ganar $20,000/mes en Threads.\n\n¿El secreto sucio? La mitad de sus métricas son anzuelos visuales, pero su embudo por detrás SÍ factura miles vendiendo guías de $27.\n\nNo odies al jugador: hazle ingeniería inversa a su embudo. Aquí está el mapa completo."
            ],
            suggested_self_replies=[
                "Metí los 120 prompts que uso para destripar cualquier cuenta y clonar su oferta en la Bóveda B05 de mi bio.",
            ],
            target_sku_id="B05",
            topic_tag="Marketing Digital",
            bait_widget=BaitWidgetConfig(
                widget_type="stripe_gumroad_dashboard",
                headline_metric="$3,842.10 últimos 14 días",
                sub_metric="Conversión de rutas puente: 4.8%",
                notifications=[
                    "Ruta top: /boveda/boveda-prompts-ingenieria-inversa ($1,431.00)",
                    "Ruta #2: /blueprint/maquina-silenciosa-pdf ($1,121.00)",
                ],
                timestamp_label="14D PANEL",
            ),
            simulated_likes=934,
            simulated_replies=211,
            simulated_reposts=88,
        ),
    ]


_LAST_LOAD_ERROR: Optional[str] = None


def get_last_load_error() -> Optional[str]:
    return _LAST_LOAD_ERROR


def _normalize_feed_status(feeds: Dict[str, list]) -> Dict[str, list]:
    """Un `published` persistido sin URL ni timestamp de la plataforma es falso.

    El estado real de publicación vive en `publish_state` (seguimiento local).
    El campo legacy del feed se fuerza a `queued` al leer.
    """
    for post in feeds["threads"]:
        post.status = "queued"
    for pin in feeds["pinterest"]:
        pin.status = "queued"
    return feeds


def load_or_init_feeds() -> Dict[str, list]:
    global _LAST_LOAD_ERROR
    ensure_dirs()
    with lock_for(FEEDS_JSON_PATH):
        raw, error = read_json(FEEDS_JSON_PATH)
        if error is not None:
            backup = quarantine_corrupt(FEEDS_JSON_PATH)
            threads = build_default_threads_posts()
            pinterest = build_default_pinterest_pins()
            save_feeds(threads, pinterest)
            _LAST_LOAD_ERROR = (
                f"social_feeds.json ilegible ({error}). Se movió a {backup or 'sin backup'} "
                "y se regeneró la cola por defecto."
            )
            return {"threads": threads, "pinterest": pinterest}
        if raw is None:
            threads = build_default_threads_posts()
            pinterest = build_default_pinterest_pins()
            save_feeds(threads, pinterest)
            _LAST_LOAD_ERROR = None
            return {"threads": threads, "pinterest": pinterest}

    try:
        feeds = {
            "threads": [ThreadsPostItem(**item) for item in raw.get("threads", [])],
            "pinterest": [PinterestPinItem(**item) for item in raw.get("pinterest", [])],
        }
    except Exception as exc:  # estructura inválida en disco
        backup = quarantine_corrupt(FEEDS_JSON_PATH)
        threads = build_default_threads_posts()
        pinterest = build_default_pinterest_pins()
        save_feeds(threads, pinterest)
        _LAST_LOAD_ERROR = (
            f"social_feeds.json inválido ({type(exc).__name__}: {exc}). "
            f"Se movió a {backup or 'sin backup'} y se regeneró la cola por defecto."
        )
        return {"threads": threads, "pinterest": pinterest}
    _LAST_LOAD_ERROR = None
    return _normalize_feed_status(feeds)


def save_feeds(threads: List[ThreadsPostItem], pinterest: List[PinterestPinItem]) -> None:
    ensure_dirs()
    payload = {
        "threads": [post.model_dump() for post in threads],
        "pinterest": [pin.model_dump() for pin in pinterest],
    }
    write_json_atomic(FEEDS_JSON_PATH, payload)


def next_thread_id(threads: List[ThreadsPostItem]) -> str:
    """Id correlativo sin colisiones (el conteo simple fallaba si se borraba uno)."""
    highest = 0
    for post in threads:
        suffix = post.post_id.rsplit("_", 1)[-1]
        if suffix.isdigit():
            highest = max(highest, int(suffix))
    return f"th_{highest + 1:03d}"


def mutate_thread_hook(post: ThreadsPostItem) -> ThreadsPostItem:
    """Sustituye la primera línea por una variante de plantilla (no es IA).

    Antes además inflaba `simulated_likes` con un random: eso era un estado
    falso (mutar un hook no produce likes). Ahora los contadores se quedan como
    estaban y la respuesta lo declara como variante de plantilla.
    """
    base_angle = post.body_slides[0].split("\n")[0][:90]
    template = random.choice(HOOK_MUTATION_TEMPLATES)
    new_first = template.format(angle=base_angle)
    rest = "\n\n".join(post.body_slides[0].split("\n\n")[1:])
    post.body_slides[0] = f"{new_first}\n\n{rest}".strip() if rest else new_first
    return post
