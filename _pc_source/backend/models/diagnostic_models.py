from typing import Dict, Literal, Optional
from pydantic import BaseModel, Field

DiagnosticStatus = Literal["CONECTADO", "FALLA", "SIN_VERIFICAR"]


class ConnectorTestResult(BaseModel):
    connector_id: str
    name: str
    status: DiagnosticStatus
    latency_ms: float = 0.0
    detail: str = ""
    checked_at: str = ""
    error_literal: Optional[str] = None


class TestAllResponse(BaseModel):
    total: int
    connected_count: int
    falla_count: int
    sin_verificar_count: int
    results: Dict[str, ConnectorTestResult]
    tested_at: str
