from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class SaleRecord(BaseModel):
    id: str
    source: Literal["gumroad", "hotmart"]
    order_id: str
    date: str
    product_name: str
    sku_id: Optional[str] = None
    amount_usd: float = 0.0
    amount_cop: Optional[float] = None
    currency: str = "USD"
    is_order_bump: bool = False
    customer_email: Optional[str] = None


class PieceMetricRecord(BaseModel):
    id: str
    date: str
    platform: Literal["threads", "pinterest"]
    piece_id: str
    sku_id: Optional[str] = None
    route: Optional[str] = None
    impressions: int = 0
    clicks: int = 0
    saves: int = 0
    notes: Optional[str] = None


class MetricsRealState(BaseModel):
    sales: List[SaleRecord] = Field(default_factory=list)
    manual_piece_metrics: List[PieceMetricRecord] = Field(default_factory=list)
    last_updated: Optional[str] = None


class CsvImportResult(BaseModel):
    source: str
    total_rows: int
    imported_count: int
    skipped_count: int
    total_amount_usd: float
    errors: List[str] = Field(default_factory=list)
    sales_sample: List[SaleRecord] = Field(default_factory=list)
    all_sales: List[SaleRecord] = Field(default_factory=list)


class PerformancePiece(BaseModel):
    piece_id: str
    platform: str
    sku_id: Optional[str]
    route: Optional[str]
    impressions: int
    clicks: int
    saves: int
    ctr_percent: float
    verdict: Literal["DOBLAR", "MATAR", "MUTAR", "OBSERVACION"]
    reason: str


class MetricsSummaryResponse(BaseModel):
    has_real_data: bool
    is_demo_mode: bool = False
    total_sales: int = 0
    product_sales_count: int = 0
    product_revenue_usd: float = 0.0
    order_bumps_count: int = 0
    order_bumps_revenue_usd: float = 0.0
    total_revenue_usd: float = 0.0
    gumroad_revenue_usd: float = 0.0
    hotmart_revenue_usd: float = 0.0
    hotmart_revenue_cop: float = 0.0
    aov_usd: Optional[float] = None
    total_impressions: int = 0
    total_clicks: int = 0
    total_saves: int = 0
    ctr_percent: Optional[float] = None
    rpm_usd: Optional[float] = None
    doblar_o_matar_status: str
    winning_pieces: List[PerformancePiece] = Field(default_factory=list)
    losing_pieces: List[PerformancePiece] = Field(default_factory=list)
    funnel_breakdown: Dict[str, float] = Field(default_factory=dict)
    attribution_note: str = (
        "Atribución aproximada por prefijo de SKU (E/A/B/K/M). No es UTM ni una "
        "medición real de la vía de contenido que produjo la venta."
    )
    raw_sales_count: int = 0
    raw_metrics_count: int = 0
