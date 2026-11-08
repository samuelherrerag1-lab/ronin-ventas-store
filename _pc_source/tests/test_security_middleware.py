"""Middleware de seguridad opcional: token por env, rate-limit y guard de Vertex."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.security_middleware import (
    SecurityMiddleware,
    image_job_guard,
    reset_rate_limits,
)


def _security_client() -> TestClient:
    security_app = FastAPI()
    security_app.add_middleware(SecurityMiddleware)

    @security_app.post("/api/customizations/vertex-generate")
    def _vertex():
        return {"ok": True}

    @security_app.post("/api/customizations/test-all")
    def _test_all():
        return {"ok": True}

    @security_app.get("/api/health")
    def _health():
        return {"ok": True}

    return TestClient(security_app)


def test_optional_token_auth(monkeypatch):
    monkeypatch.delenv("RONIN_API_TOKEN", raising=False)
    reset_rate_limits()
    open_client = _security_client()
    assert open_client.post("/api/customizations/vertex-generate").status_code == 200

    monkeypatch.setenv("RONIN_API_TOKEN", "s3cret")
    reset_rate_limits()
    guarded = _security_client()
    assert guarded.post("/api/customizations/vertex-generate").status_code == 401
    assert guarded.post(
        "/api/customizations/vertex-generate", headers={"X-Ronin-Token": "s3cret"}
    ).status_code == 200
    # También se acepta por query string.
    reset_rate_limits()
    assert guarded.post(
        "/api/customizations/vertex-generate", params={"token": "s3cret"}
    ).status_code == 200
    assert guarded.get("/api/health").status_code == 200  # GET no exige token


def test_rate_limit_and_image_job_guard(monkeypatch):
    monkeypatch.delenv("RONIN_API_TOKEN", raising=False)
    reset_rate_limits()
    rate_client = _security_client()
    assert rate_client.post("/api/customizations/vertex-generate").status_code == 200
    blocked = rate_client.post("/api/customizations/vertex-generate")
    assert blocked.status_code == 429
    assert blocked.json()["retry_after_sec"] > 0

    reset_rate_limits()
    with image_job_guard():
        conflict = rate_client.post("/api/customizations/test-all")
        assert conflict.status_code == 409
        assert "Vertex" in conflict.json()["detail"]
    reset_rate_limits()
    assert rate_client.post("/api/customizations/test-all").status_code == 200


def test_install_security_registers_middleware():
    from backend.security_middleware import install_security

    fresh = FastAPI()
    install_security(fresh)
    assert any(middleware.cls is SecurityMiddleware for middleware in fresh.user_middleware)
