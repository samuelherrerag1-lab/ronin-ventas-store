"""Tests del motor de alta en Gumroad: idempotencia, cupo, publicación y catálogo.

Todo con HTTP mockeado (cero red). Cubre los invariantes de honestidad: nunca
crear sin entregable, no publicar sin archivo, no persistir borradores como
checkout y detenerse en cuanto Gumroad agota el cupo diario.
"""

import pytest

from backend.models.catalog_models import ProductSKU
from backend.services import gumroad_catalog as cat
from backend.services.gumroad_catalog_sync import GumroadSync
from backend.services.gumroad_media import cover_to_jpeg_bytes
from backend.services.gumroad_products import GumroadClient
from tests.gumroad_fakes import SHORT_URL, SLUG, FakeResponse, FakeSession, build_session


@pytest.fixture()
def e01():
    return next(sku for sku in cat.load_catalog() if sku["sku_id"] == "E01")


@pytest.fixture()
def isolated_state(monkeypatch):
    monkeypatch.setattr(cat, "save_state", lambda state: None)
    return {"account": {}, "products": {}}


@pytest.fixture()
def engine(isolated_state, e01):
    session = build_session()
    client = GumroadClient("tok_test", session=session)
    return GumroadSync(client, state=isolated_state, catalog=[e01], delay=0,
                       image_converter=lambda path: b"fakejpeg")


def _sku(sku_id="E01"):
    return next(s for s in cat.load_catalog() if s["sku_id"] == sku_id)


def test_create_draft_with_file_and_cover(engine, e01):
    entry = engine.ensure_draft(e01)
    assert entry["status"] == "draft_ready"
    assert entry["file_attached"] is True
    assert entry["cover_attached"] is True
    assert entry["published"] is False
    assert entry["gumroad_url"] == SHORT_URL
    assert any(call["path"] == "/products" and call["status"] == 200 for call in engine.client.calls)


def test_create_payload_uses_draft_file_price_and_slug(engine, e01):
    engine.ensure_draft(e01)
    posts = [c for c in engine.client.session.calls if c["method"] == "POST" and c["url"].endswith("/v2/products")]
    assert len(posts) == 1
    data = posts[0]["data"]
    assert data["draft"] == "true" and data["published"] == "false"
    assert data["custom_permalink"] == SLUG
    assert data["price"] == str(cat.price_cents(e01["price_usd"]))
    assert data["files[][url]"] == "https://s3.example/e01.html"
    assert isinstance(data["tags[]"], list)


def test_second_run_is_idempotent(engine):
    first = engine.run(["E01"])
    second = engine.run(["E01"])
    assert first["created"] == ["E01"]
    assert second["existing"] == ["E01"]
    calls = engine.client.session.calls
    assert len([c for c in calls if c["method"] == "POST" and c["url"].endswith("/v2/products")]) == 1
    assert len([c for c in calls if c["url"].endswith("/v2/files/presign")]) == 1
    assert len([c for c in calls if c["url"].endswith("/covers")]) == 1


def test_missing_deliverable_never_creates_product(engine):
    ghost = {"sku_id": "E01", "slug": "slug-que-no-existe", "title": "X", "subtitle": "Y",
             "format": "ebook_blueprint", "niche": "dinero_digital_faceless", "price_usd": 19.0,
             "price_cop": 0, "bridge_route": "/x", "hook_angle": "h", "deliverable_spec": "d"}
    entry = engine.ensure_draft(ghost)
    assert entry["status"] == "missing_file"
    assert not [c for c in engine.client.session.calls if c["method"] == "POST" and c["url"].endswith("/v2/products")]


def test_daily_quota_stops_run_without_uploading_the_rest(monkeypatch):
    session = FakeSession()
    session.add("GET", r"/v2/products$", FakeResponse(200, {"success": True, "products": []}))
    session.add("POST", r"/v2/files/presign$", FakeResponse(200, {
        "success": True, "upload_id": "up1", "key": "attachments/u/1/original/e01.html",
        "file_url": "https://s3.example/e01.html",
        "parts": [{"part_number": 1, "presigned_url": "https://s3.example/part1"}]}))
    session.add("PUT", r"https://s3\.example/part1", FakeResponse(200, headers={"ETag": '"abc123"'}))
    session.add("POST", r"/v2/files/complete$", FakeResponse(200, {"success": True, "file_url": "https://s3.example/e01.html"}))
    session.add("POST", r"/v2/products$",
                FakeResponse(200, {"success": False, "message": "Sorry, you can only create 10 products per day."}))
    monkeypatch.setattr(cat, "save_state", lambda state: None)
    engine = GumroadSync(GumroadClient("tok", session=session), state={"account": {}, "products": {}},
                         catalog=[_sku("E01"), _sku("E02")], delay=0, image_converter=lambda path: b"fakejpeg")
    results = engine.run(["E01", "E02"])
    assert results["blocked_quota"] == ["E01", "E02"]
    assert results["created"] == [] and results["failed"] == []
    assert len([c for c in session.calls if c["url"].endswith("/v2/files/presign")]) == 1


def test_publish_requires_attached_file(engine):
    engine.state["products"]["E01"] = {"product_id": "P-E01", "file_attached": False, "gumroad_url": SHORT_URL}
    entry = engine.publish("E01")
    assert entry.get("published") is not True
    assert not [c for c in engine.client.session.calls if c["url"].endswith("/enable")]


def test_publish_enables_with_file(engine):
    engine.state["products"]["E01"] = {"product_id": "P-E01", "file_attached": True, "gumroad_url": SHORT_URL}
    entry = engine.publish("E01")
    assert entry["published"] is True and entry["status"] == "published"
    assert [c for c in engine.client.session.calls if c["url"].endswith("/enable")]


def _catalog_model():
    return [ProductSKU(sku_id="E01", slug=SLUG, title="T", subtitle="S", format="ebook_blueprint",
                       niche="dinero_digital_faceless", price_usd=19.0, price_cop=79800,
                       bridge_route="/blueprint/x", hook_angle="h", deliverable_spec="d")]


def test_apply_urls_to_catalog_via_atomic_update(monkeypatch):
    catalog = _catalog_model()
    monkeypatch.setattr(cat, "atomic_update_catalog", lambda mutator: mutator(catalog))
    state = {"products": {"E01": {"gumroad_url": SHORT_URL, "published": True}}}
    assert cat.apply_urls_to_catalog(state) == {"applied": 1, "skipped_drafts": 0, "published": 1}
    assert catalog[0].gumroad_url == SHORT_URL and catalog[0].status == "published"


def test_apply_urls_skips_unpublished_drafts_by_default(monkeypatch):
    catalog = _catalog_model()
    monkeypatch.setattr(cat, "atomic_update_catalog", lambda mutator: mutator(catalog))
    state = {"products": {"E01": {"gumroad_url": SHORT_URL, "published": False}}}
    assert cat.apply_urls_to_catalog(state) == {"applied": 0, "skipped_drafts": 1, "published": 0}
    assert catalog[0].gumroad_url == "" and catalog[0].status != "published"


def test_description_is_honest(e01):
    text = cat.build_description(e01).lower()
    assert "no garantiza ingresos" in text
    assert "descarga inmediata" in text
    assert "garantizado" not in text


def test_cover_to_jpeg_converts_webp(tmp_path):
    from PIL import Image

    source = tmp_path / "cover.webp"
    Image.new("RGB", (584, 800), (224, 122, 95)).save(source, format="WEBP")
    data = cover_to_jpeg_bytes(source)
    assert data[:2] == b"\xff\xd8"
    assert len(data) > 1000
