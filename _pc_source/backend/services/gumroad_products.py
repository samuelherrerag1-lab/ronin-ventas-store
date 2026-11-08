"""Cliente real de la API v2 de Gumroad.

Documentación oficial (repo open source de Gumroad, `antiwork/gumroad`):
- Auth: `Authorization: Bearer <token>` (también `access_token` como parámetro).
- Productos: POST/PUT/GET/DELETE `/v2/products`; `PUT /v2/products/:id/enable|disable`.
- Archivos: `POST /v2/files/presign` -> PUT a la URL firmada -> `POST /v2/files/complete`
  (`parts=[{"part_number":1,"etag":"..."}]`) -> `file_url` -> `files[][url]` del producto.
- Imágenes (portada/miniatura): `POST /v2/direct_uploads` (JPEG/PNG/GIF) -> PUT a
  `direct_upload.url` -> `signed_blob_id` -> `POST /v2/products/:id/covers|thumbnail`.
"""

import base64
import datetime
import hashlib
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import quote, urlencode

import requests

API_BASE = "https://api.gumroad.com/v2"
USER_AGENT = "RoninVentasOS/2.0 (+gumroad-products)"


def utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


class GumroadError(RuntimeError):
    def __init__(self, message: str, status: Optional[int] = None, payload: Any = None):
        super().__init__(message)
        self.status = status
        self.payload = payload


class GumroadClient:
    """Envoltorio fino de la API v2. La sesión HTTP se inyecta en los tests."""

    def __init__(self, token: str, session: Optional[Any] = None, timeout: float = 90.0):
        if not token:
            raise GumroadError("Falta el access token de Gumroad")
        self.token = token
        self.session = session or requests.Session()
        self.timeout = timeout
        self.calls: List[Dict[str, Any]] = []

    # -- transporte ---------------------------------------------------------
    def _request(
        self, method: str, path: str, data: Optional[Dict[str, Any]] = None, form_body: Optional[str] = None
    ) -> Dict[str, Any]:
        url = path if path.startswith("http") else f"{API_BASE}{path}"
        headers = {"Authorization": f"Bearer {self.token}", "User-Agent": USER_AGENT}
        if form_body is not None:
            encoded = form_body + "&access_token=" + quote(self.token, safe="")
            headers["Content-Type"] = "application/x-www-form-urlencoded"
            response = self.session.request(method, url, data=encoded, headers=headers, timeout=self.timeout)
        else:
            payload = dict(data or {})
            payload.setdefault("access_token", self.token)
            response = self.session.request(method, url, data=payload, headers=headers, timeout=self.timeout)
        # Rate limit: se reintenta con espera corta (Gumroad devuelve 429 sin cuerpo útil).
        for attempt in range(2):
            if response.status_code != 429:
                break
            time.sleep(3 * (attempt + 1))
            if form_body is not None:
                response = self.session.request(method, url, data=encoded, headers=headers, timeout=self.timeout)
            else:
                response = self.session.request(method, url, data=payload, headers=headers, timeout=self.timeout)
        self.calls.append({"method": method, "path": path, "status": response.status_code})
        try:
            body: Any = response.json()
        except Exception:
            body = {"raw": (response.text or "")[:400]}
        if response.status_code >= 400 or (isinstance(body, dict) and body.get("success") is False):
            message = ""
            if isinstance(body, dict):
                message = str(body.get("error") or body.get("message") or "")
            raise GumroadError(
                f"{method} {path} -> HTTP {response.status_code}: {message or 'respuesta inválida'}",
                status=response.status_code,
                payload=body,
            )
        return body

    # -- cuenta y productos -------------------------------------------------
    def get_user(self) -> Dict[str, Any]:
        return self._request("GET", "/user").get("user") or {}

    def list_products(self) -> List[Dict[str, Any]]:
        products: List[Dict[str, Any]] = []
        page_key: Optional[str] = None
        for _ in range(50):
            data = {"page_key": page_key} if page_key else {}
            body = self._request("GET", "/products", data)
            products.extend(body.get("products") or [])
            page_key = body.get("next_page_key")
            if not page_key:
                break
        return products

    def get_product(self, product_id: str) -> Dict[str, Any]:
        return self._request("GET", f"/products/{product_id}").get("product") or {}

    def create_product(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        body = self._request("POST", "/products", payload)
        return {"product": body.get("product") or {}, "warning": body.get("warning")}

    def update_product(self, product_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        body = self._request("PUT", f"/products/{product_id}", payload)
        return {"product": body.get("product") or {}, "warning": body.get("warning")}

    def enable_product(self, product_id: str) -> Dict[str, Any]:
        return self._request("PUT", f"/products/{product_id}/enable").get("product") or {}

    def disable_product(self, product_id: str) -> Dict[str, Any]:
        return self._request("PUT", f"/products/{product_id}/disable").get("product") or {}

    def delete_product(self, product_id: str) -> Dict[str, Any]:
        return self._request("DELETE", f"/products/{product_id}")

    # -- archivos del producto ----------------------------------------------
    def upload_file(self, path: Path) -> str:
        size = path.stat().st_size
        presign = self._request("POST", "/files/presign", {"filename": path.name, "file_size": str(size)})
        chunk = path.read_bytes()
        parts: List[Dict[str, Any]] = []
        for part in presign.get("parts") or []:
            uploaded = self.session.request(
                "PUT",
                part["presigned_url"],
                data=chunk,
                headers={"Content-Type": "application/octet-stream", "User-Agent": USER_AGENT},
                timeout=self.timeout,
            )
            if uploaded.status_code >= 400:
                raise GumroadError(f"PUT S3 parte {part.get('part_number')} -> HTTP {uploaded.status_code}")
            headers = getattr(uploaded, "headers", {}) or {}
            etag = headers.get("ETag") or headers.get("etag")
            if not etag:
                raise GumroadError("S3 no devolvió ETag; subida incompleta")
            parts.append({"part_number": part["part_number"], "etag": etag.strip('"')})
        # Rails solo agrupa bien `parts[][...]` si los pares van intercalados.
        pairs = [("upload_id", presign["upload_id"]), ("key", presign["key"])]
        for part in parts:
            pairs.append(("parts[][part_number]", str(part["part_number"])))
            pairs.append(("parts[][etag]", part["etag"]))
        completed = self._request("POST", "/files/complete", form_body=urlencode(pairs))
        file_url = completed.get("file_url")
        if not file_url:
            raise GumroadError("files/complete no devolvió file_url")
        return file_url

    # -- imágenes -----------------------------------------------------------
    def direct_upload_image(self, data: bytes, filename: str, content_type: str = "image/jpeg") -> str:
        checksum = base64.b64encode(hashlib.md5(data).digest()).decode()
        body = self._request(
            "POST",
            "/direct_uploads",
            {
                "blob[filename]": filename,
                "blob[byte_size]": str(len(data)),
                "blob[checksum]": checksum,
                "blob[content_type]": content_type,
            },
        )
        upload = body.get("direct_upload") or {}
        signed_id = body.get("signed_id")
        if not signed_id or not upload.get("url"):
            raise GumroadError("direct_uploads no devolvió signed_id/url")
        put = self.session.request(
            "PUT",
            upload["url"],
            data=data,
            headers=upload.get("headers") or {"Content-Type": content_type},
            timeout=self.timeout,
        )
        if put.status_code >= 400:
            raise GumroadError(f"PUT de imagen -> HTTP {put.status_code}")
        return signed_id

    def add_cover(self, product_id: str, signed_blob_id: str) -> Dict[str, Any]:
        return self._request("POST", f"/products/{product_id}/covers", {"signed_blob_id": signed_blob_id})

    def set_thumbnail(self, product_id: str, signed_blob_id: str) -> Dict[str, Any]:
        return self._request("POST", f"/products/{product_id}/thumbnail", {"signed_blob_id": signed_blob_id})

    # -- verificación pública ----------------------------------------------
    def public_snapshot(self, url: str) -> Dict[str, Any]:
        """Abre la URL pública (sin token) y devuelve estado, título y precio literales."""
        try:
            response = self.session.get(url, headers={"User-Agent": USER_AGENT}, timeout=30, allow_redirects=True)
        except Exception as exc:
            return {"ok": False, "url": url, "error": f"{type(exc).__name__}: {exc}"}
        html = response.text or ""
        title = ""
        m_title = re.search(r"<title[^>]*>(.*?)</title>", html, re.S | re.I)
        if m_title:
            title = re.sub(r"\s+", " ", m_title.group(1)).strip()[:200]
        price = ""
        m_price = re.search(r'"(?:price|formatted_price)"\s*:\s*"?(?P<price>[^",}]+)', html)
        if m_price:
            price = m_price.group("price").strip()[:40]
        if not price:
            m_meta = re.search(r'"amount_cents"\s*:\s*(\d+)', html)
            price = f"{m_meta.group(1)} cents" if m_meta else ""
        return {
            "ok": response.status_code == 200,
            "status": response.status_code,
            "final_url": response.url,
            "title": title,
            "price": price,
        }
