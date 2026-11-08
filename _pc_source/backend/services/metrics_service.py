import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from backend.config import METRICS_REAL_PATH, ensure_dirs
from backend.models.metrics_models import (
    MetricsRealState,
    MetricsSummaryResponse,
    PerformancePiece,
    PieceMetricRecord,
    SaleRecord,
)
from backend.services.json_store import lock_for, read_json, write_json_atomic


def load_metrics_state() -> MetricsRealState:
    ensure_dirs()
    data, error = read_json(METRICS_REAL_PATH)
    if error is not None or data is None:
        return MetricsRealState(sales=[], manual_piece_metrics=[], last_updated=None)
    try:
        return MetricsRealState(**data)
    except Exception:
        return MetricsRealState(sales=[], manual_piece_metrics=[], last_updated=None)


def save_metrics_state(state: MetricsRealState) -> None:
    ensure_dirs()
    state.last_updated = datetime.now(timezone.utc).isoformat()
    write_json_atomic(METRICS_REAL_PATH, state.model_dump())


def reset_metrics_state() -> MetricsRealState:
    empty_state = MetricsRealState(sales=[], manual_piece_metrics=[], last_updated=datetime.now(timezone.utc).isoformat())
    save_metrics_state(empty_state)
    return empty_state


def add_sales_records(sales: List[SaleRecord]) -> int:
    with lock_for(METRICS_REAL_PATH):
        state = load_metrics_state()
        existing_ids = {sale.id for sale in state.sales}
        added = 0
        for sale in sales:
            if sale.id not in existing_ids:
                state.sales.append(sale)
                existing_ids.add(sale.id)
                added += 1
        if added:
            save_metrics_state(state)
        return added


def add_piece_metric(record: PieceMetricRecord) -> PieceMetricRecord:
    with lock_for(METRICS_REAL_PATH):
        state = load_metrics_state()
        state.manual_piece_metrics.append(record)
        save_metrics_state(state)
    return record


def compute_metrics_summary(is_demo: bool = False) -> MetricsSummaryResponse:
    if is_demo:
        return _build_demo_summary()

    state = load_metrics_state()
    sales = state.sales
    metrics = state.manual_piece_metrics
    product_sales = [sale for sale in sales if not sale.is_order_bump]
    order_bumps = [sale for sale in sales if sale.is_order_bump]
    has_data = len(sales) > 0 or len(metrics) > 0

    if not has_data:
        return MetricsSummaryResponse(
            has_real_data=False,
            is_demo_mode=False,
            total_sales=0,
            product_sales_count=0,
            product_revenue_usd=0.0,
            order_bumps_count=0,
            order_bumps_revenue_usd=0.0,
            total_revenue_usd=0.0,
            gumroad_revenue_usd=0.0,
            hotmart_revenue_usd=0.0,
            hotmart_revenue_cop=0.0,
            aov_usd=None,
            total_impressions=0,
            total_clicks=0,
            total_saves=0,
            ctr_percent=None,
            rpm_usd=None,
            doblar_o_matar_status="SIN DATOS SUFICIENTES: Registra impresiones de piezas o importa ventas reales de Gumroad/Hotmart para calcular el criterio de 14 dias.",
            winning_pieces=[],
            losing_pieces=[],
            funnel_breakdown={"via_a": 0.0, "via_b": 0.0, "via_c": 0.0},
            raw_sales_count=0,
            raw_metrics_count=0,
        )

    gumroad_usd = sum(sale.amount_usd for sale in sales if sale.source == "gumroad")
    hotmart_usd = sum(sale.amount_usd for sale in sales if sale.source == "hotmart")
    hotmart_cop = sum(sale.amount_cop or 0.0 for sale in sales if sale.source == "hotmart")
    product_revenue = sum(sale.amount_usd for sale in product_sales)
    bump_revenue = sum(sale.amount_usd for sale in order_bumps)
    total_rev = round(product_revenue + bump_revenue, 2)
    sales_cnt = len(product_sales)
    # AOV de producto: el order bump no se cuenta como una venta más.
    aov = round(product_revenue / sales_cnt, 2) if sales_cnt > 0 else None

    tot_imp = sum(metric.impressions for metric in metrics)
    tot_clk = sum(metric.clicks for metric in metrics)
    tot_sav = sum(metric.saves for metric in metrics)
    ctr = round((tot_clk / tot_imp) * 100, 2) if tot_imp > 0 else None
    rpm = round((total_rev / tot_imp) * 1000, 2) if tot_imp > 0 else None

    evaluated = [_evaluate_piece(metric) for metric in metrics]
    winners = [piece for piece in evaluated if piece.verdict == "DOBLAR"]
    losers = [piece for piece in evaluated if piece.verdict in ("MATAR", "MUTAR")]

    funnel = _calculate_funnel_breakdown(product_sales)
    doblar_status = f"{len(winners)} piezas ganadoras (Doblar 2x) · {len(losers)} piezas en umbral critico (Mutar/Matar)" if evaluated else "Ventas registradas sin metricas de trafico asociadas."

    return MetricsSummaryResponse(
        has_real_data=True,
        is_demo_mode=False,
        total_sales=sales_cnt,
        product_sales_count=sales_cnt,
        product_revenue_usd=round(product_revenue, 2),
        order_bumps_count=len(order_bumps),
        order_bumps_revenue_usd=round(bump_revenue, 2),
        total_revenue_usd=total_rev,
        gumroad_revenue_usd=round(gumroad_usd, 2),
        hotmart_revenue_usd=round(hotmart_usd, 2),
        hotmart_revenue_cop=round(hotmart_cop, 2),
        aov_usd=aov,
        total_impressions=tot_imp,
        total_clicks=tot_clk,
        total_saves=tot_sav,
        ctr_percent=ctr,
        rpm_usd=rpm,
        doblar_o_matar_status=doblar_status,
        winning_pieces=winners[:5],
        losing_pieces=losers[:5],
        funnel_breakdown=funnel,
        raw_sales_count=len(sales),
        raw_metrics_count=len(metrics),
    )


def _evaluate_piece(m: PieceMetricRecord) -> PerformancePiece:
    ctr = round((m.clicks / m.impressions) * 100, 2) if m.impressions > 0 else 0.0
    if m.impressions >= 100 and ctr >= 2.0:
        verdict = "DOBLAR"
        reason = f"CTR sobresaliente de {ctr}% con {m.impressions} impresiones. Duplicar cadencia de publicacion."
    elif m.impressions >= 300 and ctr < 0.8:
        verdict = "MATAR"
        reason = f"Bajo enganche: CTR {ctr}% (<0.8%) tras {m.impressions} impresiones. Mutar hook a Captura Anzuelo iOS."
    elif m.impressions >= 100 and ctr < 1.2:
        verdict = "MUTAR"
        reason = f"CTR moderado ({ctr}%). Conviene mutar el gancho verbal de la primera linea."
    else:
        verdict = "OBSERVACION"
        reason = f"Datos en recoleccion ({m.impressions} impresiones registradas)."

    return PerformancePiece(
        piece_id=m.piece_id,
        platform=m.platform,
        sku_id=m.sku_id,
        route=m.route,
        impressions=m.impressions,
        clicks=m.clicks,
        saves=m.saves,
        ctr_percent=ctr,
        verdict=verdict,
        reason=reason,
    )


def _calculate_funnel_breakdown(sales: List[SaleRecord]) -> Dict[str, float]:
    if not sales:
        return {"via_a": 0.0, "via_b": 0.0, "via_c": 0.0}
    via_a = sum(1 for s in sales if s.sku_id and s.sku_id.startswith(("E", "A")))
    via_b = sum(1 for s in sales if s.sku_id and s.sku_id.startswith("B"))
    via_c = len(sales) - (via_a + via_b)
    tot = float(len(sales))
    return {
        "via_a": round((via_a / tot) * 100, 1),
        "via_b": round((via_b / tot) * 100, 1),
        "via_c": round((via_c / tot) * 100, 1),
    }


def _build_demo_summary() -> MetricsSummaryResponse:
    return MetricsSummaryResponse(
        has_real_data=True,
        is_demo_mode=True,
        total_sales=12,
        product_sales_count=12,
        product_revenue_usd=348.0,
        order_bumps_count=0,
        order_bumps_revenue_usd=0.0,
        total_revenue_usd=348.0,
        gumroad_revenue_usd=210.0,
        hotmart_revenue_usd=138.0,
        hotmart_revenue_cop=552000.0,
        aov_usd=29.0,
        total_impressions=18450,
        total_clicks=482,
        total_saves=164,
        ctr_percent=2.61,
        rpm_usd=18.86,
        doblar_o_matar_status="[MODO DEMO]: 2 piezas sobrepasan umbral de doblar · 1 pieza candidata a mutar.",
        winning_pieces=[
            PerformancePiece(
                piece_id="demo_th_001",
                platform="threads",
                sku_id="E01",
                route="/blueprint/threads-faceless",
                impressions=8400,
                clicks=240,
                saves=62,
                ctr_percent=2.86,
                verdict="DOBLAR",
                reason="Simulacion demo: CTR alto 2.86%.",
            )
        ],
        losing_pieces=[
            PerformancePiece(
                piece_id="demo_pin_004",
                platform="pinterest",
                sku_id="B02",
                route="/boveda/prompts-ia",
                impressions=2100,
                clicks=12,
                saves=5,
                ctr_percent=0.57,
                verdict="MATAR",
                reason="Simulacion demo: CTR 0.57% inferior a 0.8%.",
            )
        ],
        funnel_breakdown={"via_a": 50.0, "via_b": 33.3, "via_c": 16.7},
        raw_sales_count=12,
        raw_metrics_count=2,
    )
