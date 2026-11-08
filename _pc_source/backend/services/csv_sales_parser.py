"""Parser de CSVs reales de Gumroad y Hotmart.

- Una sola tabla de FX con fecha (USD base) y normalización de miles ("79.800").
- Fecha normalizada a ISO; no se inventan fechas ni ids de orden.
- El order bump se marca (`is_order_bump`) para no contarlo como venta.
"""

import csv
import datetime
import hashlib
import io
import re
from typing import Any, Dict, List, Optional, Tuple

from backend.models.metrics_models import CsvImportResult, SaleRecord

FX_AS_OF = "2026-11-04"
COP_RATE = 4200.0
FX_RATES_TO_USD: Dict[str, float] = {"USD": 1.0, "COP": 1.0 / COP_RATE, "BRL": 0.18, "EUR": 1.08}
FX_NOTE = f"Tasas fijas de referencia al {FX_AS_OF}; no son cotización en vivo."
SUPPORTED_CURRENCIES = tuple(FX_RATES_TO_USD)


def _detect_delimiter(text_sample: str) -> str:
    counts = {delim: text_sample.count(delim) for delim in (",", ";", "\t")}
    return max(counts, key=counts.get)


def _clean_header(header: str) -> str:
    cleaned = header.strip().lower()
    for accented, plain in (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u")):
        cleaned = cleaned.replace(accented, plain)
    cleaned = cleaned.replace("ã", "a").replace("ç", "c").replace(" ", "_")
    return re.sub(r"[^a-z0-9_]", "", cleaned)


def _parse_amount(raw: Any) -> Tuple[float, str]:
    if raw is None:
        return 0.0, "USD"
    text = str(raw).strip()
    lowered = text.lower()
    currency = "COP" if "cop" in lowered else "BRL" if ("r$" in lowered or "brl" in lowered) else "EUR" if ("eur" in lowered or "€" in text) else "USD"

    cleaned = re.sub(r"[^\d.,\-]", "", text)
    if not cleaned:
        return 0.0, currency
    if "," in cleaned and "." in cleaned:
        if cleaned.rfind(",") > cleaned.rfind("."):
            cleaned = cleaned.replace(".", "").replace(",", ".")
        else:
            cleaned = cleaned.replace(",", "")
    elif re.fullmatch(r"\d{1,3}(\.\d{3})+", cleaned):
        # "79.800" o "1.234.567" son COP con punto de miles, no 79.8.
        cleaned = cleaned.replace(".", "")
    elif "," in cleaned:
        if len(cleaned.split(",")[-1]) == 2:
            cleaned = cleaned.replace(",", ".")
        else:
            cleaned = cleaned.replace(",", "")
    try:
        return float(cleaned), currency
    except ValueError:
        return 0.0, currency


def _normalize_date(raw: Optional[str], row_number: int, errors: List[str]) -> Optional[str]:
    """Devuelve 'YYYY-MM-DD', '' si no hay fecha o None si es inválida (se omite)."""
    if not raw:
        errors.append(f"Fila {row_number}: sin fecha (la venta se guarda sin fecha ISO).")
        return ""
    text = str(raw).strip()
    match = re.match(r"^(\d{4}-\d{2}-\d{2})(?:[ T].*)?$", text)
    if match:
        try:
            datetime.date.fromisoformat(match.group(1))
            return match.group(1)
        except ValueError:
            pass
    errors.append(f"Fila {row_number}: fecha no ISO ('{text[:24]}'). Fila omitida.")
    return None


def _infer_sku(product_name: str) -> Optional[str]:
    match = re.search(r"\b([EBAKM][0-1][0-9]|L0[1-3])\b", product_name, re.IGNORECASE)
    return match.group(1).upper() if match else None


def _find_field(data: Dict[str, str], candidates: List[str]) -> Optional[str]:
    """Coincidencia exacta primero; la difusa exige claves de 4+ letras.

    Antes el candidato `id` hacía match con `product_id` y guardaba el id de
    producto como id de orden.
    """
    for candidate in candidates:
        if data.get(candidate):
            return data[candidate]
    for candidate in candidates:
        if len(candidate) < 4:
            continue
        for key, value in data.items():
            if candidate in key and value:
                return value
    return None


def parse_sales_csv(content: str, source: str) -> CsvImportResult:
    lines = [line for line in content.splitlines() if line.strip()]
    if not lines:
        return CsvImportResult(
            source=source,
            total_rows=0,
            imported_count=0,
            skipped_count=0,
            total_amount_usd=0.0,
            errors=["El archivo CSV esta vacio."],
        )

    delimiter = _detect_delimiter("\n".join(lines[:10]))
    reader = csv.reader(io.StringIO("\n".join(lines)), delimiter=delimiter)
    try:
        raw_headers = next(reader)
    except StopIteration:
        return CsvImportResult(
            source=source,
            total_rows=0,
            imported_count=0,
            skipped_count=0,
            total_amount_usd=0.0,
            errors=["No se encontro fila de cabecera en el CSV."],
        )

    headers = [_clean_header(header) for header in raw_headers]
    sales: List[SaleRecord] = []
    errors: List[str] = []
    data_rows = 0
    skipped = 0
    missing_order_ids = 0

    for row in reader:
        if not row or all(not cell.strip() for cell in row):
            continue
        data_rows += 1
        row_number = data_rows + 1
        data: Dict[str, str] = {
            headers[index]: row[index].strip() for index in range(min(len(headers), len(row)))
        }

        order_id = _find_field(
            data,
            [
                "order_id",
                "order_number",
                "codigo_de_transaccion",
                "codigo_de_la_transaccion",
                "codigo_da_transacao",
                "transaction_code",
                "id",
            ],
        )
        product_name = _find_field(
            data,
            ["product_name", "product", "item_name", "producto", "produto", "nombre_del_producto", "item"],
        )
        raw_date = _find_field(
            data,
            ["date", "order_date", "created_at", "fecha", "data_da_venda", "purchase_date", "fecha_de_compra"],
        )
        amount_raw = _find_field(
            data, ["price", "item_price", "amount", "total", "precio", "valor", "preco", "preco_do_produto"]
        )
        currency_raw = _find_field(data, ["currency", "moneda", "moeda"])
        refund_status = _find_field(data, ["refunded", "status", "estado"])

        if refund_status and refund_status.lower() in (
            "true",
            "1",
            "refunded",
            "reembolsada",
            "cancelada",
        ):
            skipped += 1
            continue
        if not product_name and not amount_raw:
            errors.append(f"Fila {row_number}: no se encontro nombre de producto ni precio.")
            skipped += 1
            continue

        date_value = _normalize_date(raw_date, row_number, errors)
        if date_value is None:
            skipped += 1
            continue

        amount, detected_currency = _parse_amount(amount_raw)
        currency = (currency_raw or detected_currency).upper().strip()
        rate = FX_RATES_TO_USD.get(currency)
        if rate is None:
            errors.append(
                f"Fila {row_number}: moneda no soportada '{currency}'. "
                f"Usa {', '.join(SUPPORTED_CURRENCIES)}."
            )
            skipped += 1
            continue

        amount_usd = round(amount * rate, 2)
        amount_cop = round(amount, 2) if currency == "COP" else round(amount_usd * COP_RATE, 2)
        bump_text = (product_name or "").lower()
        order_id = (order_id or "").strip()
        if not order_id:
            missing_order_ids += 1
            fingerprint = hashlib.sha1(
                f"{source}|{date_value}|{product_name}|{amount_raw}".encode("utf-8")
            ).hexdigest()[:12]
            record_id = f"{source}_row_{fingerprint}"
        else:
            record_id = f"{source}_{order_id}"
        sales.append(
            SaleRecord(
                id=record_id,
                source="gumroad" if source.lower() == "gumroad" else "hotmart",
                order_id=order_id,
                date=date_value,
                product_name=product_name or "Producto Ronin",
                sku_id=_infer_sku(product_name or ""),
                amount_usd=amount_usd,
                amount_cop=amount_cop,
                currency=currency,
                is_order_bump=("bump" in bump_text or "+$9" in bump_text),
                customer_email=_find_field(data, ["customer_email", "email", "comprador_email"]),
            )
        )

    if missing_order_ids:
        errors.append(
            f"{missing_order_ids} filas sin Order ID: se deduplican por hash de contenido "
            "(no se inventa un identificador de orden)."
        )
    return CsvImportResult(
        source=source,
        total_rows=data_rows,
        imported_count=len(sales),
        skipped_count=skipped,
        total_amount_usd=round(sum(sale.amount_usd for sale in sales), 2),
        errors=errors[:10],
        sales_sample=sales[:5],
        all_sales=sales,
    )
