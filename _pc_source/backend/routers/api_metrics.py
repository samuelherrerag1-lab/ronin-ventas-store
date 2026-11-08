"""Radar de métricas: ventas reales importadas y métricas manuales.

Endurecido contra entradas basura y contra PII:
- límite de 2 MB para cualquier CSV (el anterior leía archivos de cualquier
  tamaño en memoria),
- fecha ISO obligatoria y plataforma válida (antes 'instagram' se guardaba como
  pinterest en silencio),
- la respuesta nunca devuelve emails de clientes.
"""

import uuid
from datetime import date as date_cls
from typing import Literal, Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field, field_validator

from backend.models.metrics_models import (
    CsvImportResult,
    MetricsRealState,
    MetricsSummaryResponse,
    PieceMetricRecord,
)
from backend.services.csv_sales_parser import (
    FX_AS_OF,
    FX_NOTE,
    FX_RATES_TO_USD,
    parse_sales_csv,
)
from backend.services.metrics_service import (
    add_piece_metric,
    add_sales_records,
    compute_metrics_summary,
    load_metrics_state,
    reset_metrics_state,
)

router = APIRouter(prefix="/api/metrics", tags=["metrics"])

MAX_CSV_BYTES = 2_000_000
MAX_COUNTER = 1_000_000_000


class ManualMetricPayload(BaseModel):
    date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    platform: Literal["threads", "pinterest"]
    piece_id: str = Field(min_length=1, max_length=80)
    sku_id: Optional[str] = Field(default=None, max_length=10)
    route: Optional[str] = Field(default=None, max_length=200)
    impressions: int = Field(default=0, ge=0, le=MAX_COUNTER)
    clicks: int = Field(default=0, ge=0, le=MAX_COUNTER)
    saves: int = Field(default=0, ge=0, le=MAX_COUNTER)
    notes: Optional[str] = Field(default=None, max_length=500)

    @field_validator("date")
    @classmethod
    def _valid_iso_date(cls, value: str) -> str:
        try:
            date_cls.fromisoformat(value)
        except ValueError as exc:
            raise ValueError("La fecha debe ser una fecha ISO válida (YYYY-MM-DD)") from exc
        return value


class CsvImportPayload(BaseModel):
    source: str = Field(min_length=1, max_length=20)
    csv_content: str = Field(min_length=1, max_length=MAX_CSV_BYTES)

    @field_validator("source")
    @classmethod
    def _valid_source(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in ("gumroad", "hotmart"):
            raise ValueError("El source debe ser 'gumroad' o 'hotmart'")
        return normalized


def _public_result(result: CsvImportResult) -> CsvImportResult:
    """Quita PII y el volcado completo antes de responder al cliente."""
    sample = [sale.model_copy(update={"customer_email": None}) for sale in result.sales_sample]
    return result.model_copy(update={"sales_sample": sample, "all_sales": []})


@router.get("", response_model=MetricsSummaryResponse)
def get_metrics_summary(demo: bool = False):
    return compute_metrics_summary(is_demo=demo)


@router.get("/raw", response_model=MetricsRealState)
def get_raw_metrics():
    return load_metrics_state()


@router.post("/manual-entry", response_model=PieceMetricRecord)
def create_manual_entry(payload: ManualMetricPayload):
    record = PieceMetricRecord(
        id=f"pm_{uuid.uuid4().hex[:8]}",
        date=payload.date,
        platform=payload.platform,
        piece_id=payload.piece_id,
        sku_id=payload.sku_id,
        route=payload.route,
        impressions=payload.impressions,
        clicks=payload.clicks,
        saves=payload.saves,
        notes=payload.notes,
    )
    return add_piece_metric(record)


@router.post("/import-csv", response_model=CsvImportResult)
def import_sales_csv(payload: CsvImportPayload):
    result = parse_sales_csv(payload.csv_content, payload.source)
    if result.all_sales:
        add_sales_records(result.all_sales)
    return _public_result(result)


@router.post("/upload-csv", response_model=CsvImportResult)
async def upload_csv_file(source: str = Form(...), file: UploadFile = File(...)):
    normalized = source.strip().lower()
    if normalized not in ("gumroad", "hotmart"):
        raise HTTPException(status_code=400, detail="El source debe ser 'gumroad' o 'hotmart'")
    content_bytes = await file.read(MAX_CSV_BYTES + 1)
    if len(content_bytes) > MAX_CSV_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"El CSV supera el límite de {MAX_CSV_BYTES // 1_000_000} MB.",
        )
    try:
        content_str = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        content_str = content_bytes.decode("latin-1", errors="ignore")
    result = parse_sales_csv(content_str, normalized)
    if result.all_sales:
        add_sales_records(result.all_sales)
    return _public_result(result)


@router.delete("/reset", response_model=MetricsRealState)
def clear_all_metrics():
    return reset_metrics_state()


@router.get("/templates")
def get_csv_templates():
    return {
        "gumroad": {
            "required_columns": ["Order ID", "Date", "Product Name", "Price"],
            "optional_columns": ["Currency", "Refunded", "Customer Email"],
            "example_csv": "Order ID,Date,Product Name,Price,Currency\nGR-1001,2026-11-01 10:30:00,E01 Manual Faceless Threads,$19.00,USD\nGR-1002,2026-11-01 12:45:00,B01 Boveda 100 Prompts,$27.00,USD",
        },
        "hotmart": {
            "required_columns": ["Codigo de transaccion", "Fecha", "Producto", "Precio"],
            "optional_columns": ["Moneda", "Status", "Email"],
            "example_csv": "Codigo de transaccion;Fecha;Producto;Precio;Moneda\nHP0981273;2026-11-01;E01 Manual Faceless Threads;79800;COP\nHP0981274;2026-11-02;B01 Boveda 100 Prompts;114000;COP",
        },
        "fx_reference": {
            "as_of": FX_AS_OF,
            "rates_to_usd": FX_RATES_TO_USD,
            "note": FX_NOTE,
        },
    }
