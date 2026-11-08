from typing import List, Literal, Optional
from pydantic import BaseModel, Field

ProductFormat = Literal[
    "ebook_blueprint",
    "boveda_arsenal",
    "micro_app_html",
    "kit_sistema",
    "mega_bundle",
    "lead_magnet",
]

NicheCategory = Literal[
    "dinero_digital_faceless",
    "ia_automatizacion_injusta",
    "psicologia_oscura_persuasion",
    "escape_9a5_finanzas_cinicas",
]


class ProductSKU(BaseModel):
    sku_id: str
    slug: str
    title: str
    subtitle: str
    format: ProductFormat
    niche: NicheCategory
    price_usd: float
    price_cop: int
    bridge_route: str
    hook_angle: str
    deliverable_spec: str
    gumroad_url: str = ""
    hotmart_url: str = ""
    status: Literal["ready_spec", "generated", "published"] = "ready_spec"
    featured_on_stan: bool = False

    @property
    def checkout_ready(self) -> bool:
        """Verdadero solo si hay una pasarela real configurada (URL https)."""
        return bool(self.gumroad_url or self.hotmart_url)


class BaitWidgetConfig(BaseModel):
    widget_type: Literal["ios_lockscreen", "stripe_gumroad_dashboard", "iphone_note_3am", "micro_app_mockup"]
    headline_metric: str
    sub_metric: str
    notifications: List[str] = Field(default_factory=list)
    timestamp_label: str = "03:14 AM"
    date_label: str = "domingo, 2 de noviembre"


class ThreadsPostItem(BaseModel):
    post_id: str
    strategy_lane: Literal["via_a_captura_anzuelo", "via_b_ragebait_cinico", "via_c_demo_microapp"]
    format: Literal["single_text", "thread_chain", "image_bait", "carousel_dark"]
    hook_pattern: str
    body_slides: List[str]
    suggested_self_replies: List[str]
    target_sku_id: str
    topic_tag: str
    status: Literal["queued", "published"] = "queued"
    bait_widget: Optional[BaitWidgetConfig] = None
    simulated_likes: int = 412
    simulated_replies: int = 89
    simulated_reposts: int = 34


class PinterestPinItem(BaseModel):
    pin_id: str
    strategy_lane: Literal["dinero_ia_directo", "caballo_de_troya_curiosidad", "demo_herramienta_html"]
    overlay_headline: str
    overlay_badge: str
    seo_title: str
    seo_description: str
    board_name: str
    bridge_route: str
    target_sku_id: str
    visual_engine: Literal["playwright_html", "vertex_nano_banana_hybrid"]
    visual_theme: str
    aspect_ratio: Literal["2:3", "9:16"] = "2:3"
    status: Literal["queued", "published"] = "queued"
    simulated_saves: int = 640
    simulated_outbound_clicks: int = 195
    is_competitor_benchmark: bool = False
    competitor_source: str = ""
    image_url: Optional[str] = None


class ConnectorCard(BaseModel):
    connector_id: str
    name: str
    category: str
    status: str = "SIN_VERIFICAR"
    auth_mode: str
    account_label: str
    login_url: str
    description: str
    capabilities: List[str]
    latency_ms: Optional[float] = None
    detail: Optional[str] = None
    checked_at: Optional[str] = None


class SkillCustomizationItem(BaseModel):
    skill_id: str
    name: str
    category: str
    enabled: bool
    installed_on_disk: bool
    power_rule: str
