"""Fakes HTTP compartidos por los tests de Gumroad (cero red real).

Cualquier URL no registrada levanta `AssertionError`: si el código intenta salir
a internet durante `pytest`, el test falla de inmediato.
"""

import json
import re

SLUG = "maquina-silenciosa-pdf"
SHORT_URL = f"https://samuel.gumroad.com/l/{SLUG}"


class FakeResponse:
    def __init__(self, status_code=200, payload=None, text="", headers=None, url=""):
        self.status_code = status_code
        self._payload = payload
        self.text = text or json.dumps(payload or {})
        self.headers = headers or {}
        self.url = url

    def json(self):
        if self._payload is None:
            raise ValueError("sin JSON")
        return self._payload


class FakeSession:
    def __init__(self):
        self.calls = []
        self.routes = []

    def add(self, method, pattern, response):
        self.routes.append((method, re.compile(pattern), response))
        return self

    def _dispatch(self, method, url, data=None, headers=None):
        self.calls.append({"method": method, "url": url, "data": data, "headers": dict(headers or {})})
        for expected_method, pattern, response in self.routes:
            if expected_method == method and pattern.search(url):
                return response(data or {}, self) if callable(response) else response
        raise AssertionError(f"Llamada de red inesperada en test: {method} {url}")

    def request(self, method, url, data=None, headers=None, timeout=None):
        return self._dispatch(method, url, data, headers)

    def get(self, url, headers=None, timeout=None, allow_redirects=True):
        return self._dispatch("GET", url, None, headers)


def make_product(**overrides):
    product = {
        "id": "P-E01",
        "name": "La Máquina Silenciosa de Archivos PDF",
        "custom_permalink": SLUG,
        "short_url": SHORT_URL,
        "price": 1900,
        "published": False,
        "files": [{"id": "f1", "name": "e01.html", "size": 100}],
        "covers": [],
    }
    product.update(overrides)
    return product


def build_session():
    session = FakeSession()
    session.add("GET", r"/v2/user", FakeResponse(200, {"success": True, "user": {"email": "example@example.invalid", "user_id": "u1"}}))
    session.add("GET", r"/v2/products$", FakeResponse(200, {"success": True, "products": []}))
    session.add("GET", r"/v2/products/P-E01$", FakeResponse(200, {"success": True, "product": make_product(files=[{"id": "f1"}], covers=[{"id": "c1"}])}))
    session.add("POST", r"/v2/files/presign$", FakeResponse(200, {
        "success": True, "upload_id": "up1", "key": "attachments/u/1/original/e01.html",
        "file_url": "https://s3.example/e01.html",
        "parts": [{"part_number": 1, "presigned_url": "https://s3.example/part1"}]}))
    session.add("PUT", r"https://s3\.example/part1", FakeResponse(200, headers={"ETag": '"abc123"'}))
    session.add("POST", r"/v2/files/complete$", FakeResponse(200, {"success": True, "file_url": "https://s3.example/e01.html"}))
    session.add("POST", r"/v2/products$", FakeResponse(200, {"success": True, "product": make_product()}))
    session.add("POST", r"/v2/direct_uploads$", FakeResponse(200, {
        "signed_id": "signed-1", "direct_upload": {"url": "https://storage.example/img1",
                                                   "headers": {"Content-Type": "image/jpeg"}}}))
    session.add("PUT", r"https://storage\.example/img1", FakeResponse(200))
    session.add("POST", r"/v2/products/P-E01/covers$", FakeResponse(200, {"success": True, "covers": [{"id": "c1"}]}))
    session.add("PUT", r"/v2/products/P-E01/enable$", FakeResponse(200, {"success": True, "product": make_product(published=True)}))
    session.add("GET", r"samuel\.gumroad\.com/l/", FakeResponse(
        200, text='<html><title>La Máquina Silenciosa</title>"formatted_price": "$19"</html>'))
    return session
