from fastapi.testclient import TestClient
from backend.main import app
from backend.services.csv_sales_parser import parse_sales_csv

client = TestClient(app)

SAMPLE_GUMROAD_CSV = """Order ID,Date,Product Name,Price,Currency,Refunded,Customer Email
GR-9001,2026-11-01 10:14:00,E01 Manual Faceless Threads,$19.00,USD,false,example@example.invalid
GR-9002,2026-11-01 14:22:00,B01 Boveda 100 Prompts,$27.00,USD,false,example@example.invalid
GR-9003,2026-11-01 18:05:00,Order Bump +$9 Hooks,$9.00,USD,false,example@example.invalid
GR-9004,2026-11-01 20:00:00,E02 Reembolsado,$19.00,USD,true,example@example.invalid
"""

SAMPLE_HOTMART_CSV = """Codigo de transaccion;Fecha;Producto;Precio;Moneda;Status
HP-7701;2026-11-02;E01 Manual Faceless Threads;79800;COP;Aprobada
HP-7702;2026-11-02;B02 Arsenal Automatizacion;114000;COP;Aprobada
HP-7703;2026-11-02;E03 Cancelada;79800;COP;Cancelada
"""


def test_metrics_empty_state_honest():
    res_reset = client.delete("/api/metrics/reset")
    assert res_reset.status_code == 200

    res = client.get("/api/metrics")
    assert res.status_code == 200
    data = res.json()
    assert data["has_real_data"] is False
    assert data["is_demo_mode"] is False
    assert data["total_sales"] == 0
    assert data["total_revenue_usd"] == 0.0
    assert data["total_impressions"] == 0
    assert data["aov_usd"] is None
    assert data["ctr_percent"] is None
    assert "SIN DATOS SUFICIENTES" in data["doblar_o_matar_status"]
    assert len(data["winning_pieces"]) == 0
    assert len(data["losing_pieces"]) == 0


def test_gumroad_csv_parser_and_import():
    parsed = parse_sales_csv(SAMPLE_GUMROAD_CSV, "gumroad")
    assert parsed.imported_count == 3
    assert parsed.total_amount_usd == 55.0
    assert parsed.sales_sample[0].sku_id == "E01"
    assert parsed.sales_sample[2].is_order_bump is True
    assert parsed.sales_sample[0].date == "2026-11-01"  # normalizada a ISO

    res = client.post("/api/metrics/import-csv", json={"source": "gumroad", "csv_content": SAMPLE_GUMROAD_CSV})
    assert res.status_code == 200
    assert res.json()["imported_count"] == 3
    assert "example@example.invalid" not in res.text  # la fila reembolsada se omite
    assert all(sale["customer_email"] is None for sale in res.json()["sales_sample"])

    res_summary = client.get("/api/metrics")
    summary = res_summary.json()
    assert summary["has_real_data"] is True
    # El order bump NO cuenta como venta de producto.
    assert summary["product_sales_count"] == 2
    assert summary["total_sales"] == 2
    assert summary["order_bumps_count"] == 1
    assert summary["order_bumps_revenue_usd"] == 9.0
    assert summary["product_revenue_usd"] == 46.0
    assert summary["total_revenue_usd"] == 55.0
    assert summary["aov_usd"] == 23.0


def test_hotmart_csv_parser_and_cop_conversion():
    parsed = parse_sales_csv(SAMPLE_HOTMART_CSV, "hotmart")
    assert parsed.imported_count == 2
    assert parsed.sales_sample[0].sku_id == "E01"
    assert parsed.sales_sample[0].amount_cop == 79800.0
    # TRM única del sistema: 4200 COP por USD (antes 4000 en el parser).
    assert parsed.sales_sample[0].amount_usd == 19.0

    res = client.post("/api/metrics/import-csv", json={"source": "hotmart", "csv_content": SAMPLE_HOTMART_CSV})
    assert res.status_code == 200


def test_manual_metrics_and_doblar_o_matar_logic():
    res_winner = client.post(
        "/api/metrics/manual-entry",
        json={
            "date": "2026-11-02",
            "platform": "threads",
            "piece_id": "th_winner_01",
            "sku_id": "E01",
            "impressions": 1000,
            "clicks": 35,
            "saves": 12,
        },
    )
    assert res_winner.status_code == 200

    res_loser = client.post(
        "/api/metrics/manual-entry",
        json={
            "date": "2026-11-02",
            "platform": "threads",
            "piece_id": "th_loser_02",
            "sku_id": "B01",
            "impressions": 500,
            "clicks": 2,
            "saves": 0,
        },
    )
    assert res_loser.status_code == 200

    res = client.get("/api/metrics")
    data = res.json()
    assert data["has_real_data"] is True
    assert data["total_impressions"] >= 1500
    assert any(p["verdict"] == "DOBLAR" for p in data["winning_pieces"])
    assert any(p["verdict"] == "MATAR" for p in data["losing_pieces"])


def test_demo_mode_isolated():
    res = client.get("/api/metrics?demo=true")
    assert res.status_code == 200
    data = res.json()
    assert data["is_demo_mode"] is True
    assert data["has_real_data"] is True
    assert data["total_sales"] == 12
