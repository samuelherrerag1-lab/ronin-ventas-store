"""Auth opcional por token + rate-limit en memoria + guard de job de imagen.

`install_security(app)` se llama una vez desde `main.py`. Si la variable
`RONIN_API_TOKEN` NO está definida, el comportamiento es el actual (la LAN queda
abierta): el token es una capa opcional, no un requisito de arranque. Si está
definida, toda escritura (POST/PUT/PATCH/DELETE) exige `X-Ronin-Token` o
`?token=`.

Los endpoints caros (`test-all`, `vertex-generate`) aceptan 1 llamada cada 20 s
por cliente, y `test-all` se bloquea si ya hay una generación de imagen Vertex en
curso (evita dos jobs de Vertex compitiendo por el mismo ledger).
"""

import hmac
import math
import os
import threading
import time
from contextlib import contextmanager
from typing import Dict, Iterator, Tuple

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

TOKEN_ENV = "RONIN_API_TOKEN"
TOKEN_HEADER = "x-ronin-token"
WRITE_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})
RATE_LIMITED_POSTS: Dict[str, float] = {
    "/api/customizations/test-all": 20.0,
    "/api/customizations/vertex-generate": 20.0,
}
TEST_ALL_PATH = "/api/customizations/test-all"

_RATE_LOCK = threading.Lock()
_LAST_CALL: Dict[Tuple[str, str], float] = {}
_IMAGE_LOCK = threading.Lock()
_IMAGE_JOBS = 0


def _client_key(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def reset_rate_limits() -> None:
    with _RATE_LOCK:
        _LAST_CALL.clear()


def rate_limit_wait(path: str, client: str) -> float:
    """Segundos que faltan para poder repetir la llamada (0 si se puede ya)."""
    interval = RATE_LIMITED_POSTS.get(path, 0.0)
    if interval <= 0:
        return 0.0
    with _RATE_LOCK:
        last = _LAST_CALL.get((path, client))
        if last is None:
            return 0.0
        return max(0.0, interval - (time.time() - last))


def image_job_active() -> bool:
    with _IMAGE_LOCK:
        return _IMAGE_JOBS > 0


@contextmanager
def image_job_guard() -> Iterator[None]:
    """Marca que hay una generación Vertex en curso mientras dure el bloque."""
    global _IMAGE_JOBS
    with _IMAGE_LOCK:
        _IMAGE_JOBS += 1
    try:
        yield
    finally:
        with _IMAGE_LOCK:
            _IMAGE_JOBS = max(0, _IMAGE_JOBS - 1)


def _token_matches(supplied: str, expected: str) -> bool:
    return bool(supplied) and hmac.compare_digest(str(supplied), expected)


class SecurityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        expected_token = os.environ.get(TOKEN_ENV, "").strip()
        if expected_token and request.method in WRITE_METHODS:
            supplied = request.headers.get(TOKEN_HEADER) or request.query_params.get("token", "")
            if not _token_matches(supplied, expected_token):
                return JSONResponse(
                    status_code=401,
                    content={
                        "detail": (
                            "Auth opcional activa (RONIN_API_TOKEN): envía el header "
                            "X-Ronin-Token o el parámetro token."
                        )
                    },
                )

        if request.method == "POST" and path == TEST_ALL_PATH and image_job_active():
            return JSONResponse(
                status_code=409,
                content={
                    "detail": (
                        "Hay una generación de imagen Vertex en curso. Espera a que "
                        "termine antes de lanzar test-all."
                    )
                },
            )

        if request.method == "POST" and path in RATE_LIMITED_POSTS:
            client = _client_key(request)
            wait = rate_limit_wait(path, client)
            if wait > 0:
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": (
                            f"Rate limit: {path} acepta 1 llamada cada "
                            f"{int(RATE_LIMITED_POSTS[path])}s. Reintenta en {math.ceil(wait)}s."
                        ),
                        "retry_after_sec": round(wait, 1),
                    },
                )
            with _RATE_LOCK:
                _LAST_CALL[(path, client)] = time.time()
        return await call_next(request)


def install_security(app) -> None:
    """Registra el middleware. Llamar una sola vez tras crear `app` en main.py."""
    app.add_middleware(SecurityMiddleware)
