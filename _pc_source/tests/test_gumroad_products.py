"""Tests del cliente HTTP de la API v2 de Gumroad. Cero llamadas reales.

Verifica el contrato (Bearer + /user, errores 401, presign->PUT->complete con
ETag, direct_uploads con checksum, covers) y que cualquier URL no registrada en
el mock haga fallar el test en vez de salir a la red.
"""

import base64
import hashlib
from urllib.parse import parse_qsl

import pytest

from backend.services import gumroad_catalog as cat
from backend.services.gumroad_products import GumroadClient, GumroadError
from tests.gumroad_fakes import SLUG, FakeResponse, FakeSession, build_session


def test_get_user_sends_bearer_and_parses_user():
    session = build_session()
    user = GumroadClient("tok_test", session=session).get_user()
    assert user["email"] == "example@example.invalid"
    assert session.calls[0]["headers"]["Authorization"] == "Bearer tok_test"


def test_http_error_raises_gumroad_error():
    session = FakeSession().add("GET", r"/v2/user", FakeResponse(401, {"success": False, "message": "bad token"}))
    with pytest.raises(GumroadError) as exc:
        GumroadClient("tok", session=session).get_user()
    assert exc.value.status == 401
    assert "401" in str(exc.value)


def test_upload_file_presign_put_complete():
    session = build_session()
    path = cat.deliverable_path("E01", SLUG)
    file_url = GumroadClient("tok", session=session).upload_file(path)
    assert file_url == "https://s3.example/e01.html"
    assert [call["method"] for call in session.calls] == ["POST", "PUT", "POST"]
    pairs = parse_qsl(session.calls[-1]["data"])
    assert ("upload_id", "up1") in pairs
    assert ("parts[][part_number]", "1") in pairs
    assert ("parts[][etag]", "abc123") in pairs
    assert pairs.index(("parts[][part_number]", "1")) < pairs.index(("parts[][etag]", "abc123"))
    assert len(session.calls[1]["data"]) == path.stat().st_size


def test_direct_upload_image_checksum_and_signed_id():
    session = build_session()
    signed = GumroadClient("tok", session=session).direct_upload_image(b"fakejpeg", "E01_cover.jpg")
    assert signed == "signed-1"
    body = session.calls[0]["data"]
    assert body["blob[checksum]"] == base64.b64encode(hashlib.md5(b"fakejpeg").digest()).decode()
    assert body["blob[content_type]"] == "image/jpeg"
    assert session.calls[1]["method"] == "PUT"


def test_public_snapshot_reads_title_and_price():
    session = build_session()
    snapshot = GumroadClient("tok", session=session).public_snapshot("https://samuel.gumroad.com/l/maquina-silenciosa-pdf")
    assert snapshot["ok"] is True and snapshot["status"] == 200
    assert "Máquina Silenciosa" in snapshot["title"]
    assert snapshot["price"] == "$19"
