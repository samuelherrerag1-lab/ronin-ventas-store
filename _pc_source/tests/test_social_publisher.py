"""Tests del publicador social real con Playwright mockeado (sin navegador).

Cubren la máquina de estados, la honestidad (login_required, modo seco), la
evidencia, la persistencia de jobs, la cola de auto-respuestas y el scheduler.
"""

import datetime
from contextlib import contextmanager
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import backend.routers.api_social_publish as api_social
import backend.services.publish_scheduler as scheduler
import backend.services.social_config as cfg
import backend.services.social_detect as social_detect
import backend.services.social_jobs as social_jobs
import backend.services.social_pieces as social_pieces
import backend.services.social_publisher as social_publisher
import backend.services.social_replies as social_replies
from tests.social_fakes import FakePage, FakePublisher


@pytest.fixture
def social_paths(tmp_path, monkeypatch):
    social_dir = tmp_path / "publish_jobs"
    evidence = social_dir / "evidence"
    images = social_dir / "images"
    for folder in (social_dir, evidence, images):
        folder.mkdir(parents=True, exist_ok=True)
    paths = {
        "SOCIAL_DIR": social_dir,
        "EVIDENCE_DIR": evidence,
        "REPLY_IMAGES_DIR": images,
        "SESSIONS_PATH": social_dir / "sessions.json",
        "REPLY_QUEUE_PATH": social_dir / "reply_queue.json",
        "SCHEDULE_PATH": social_dir / "schedule.json",
        "PUBLISHED_INDEX_PATH": social_dir / "published_index.json",
    }
    for name, value in paths.items():
        monkeypatch.setattr(cfg, name, value)
    return social_dir


def _logged_in_page() -> FakePage:
    return FakePage(visible={"a[href^='/@']", "div[contenteditable='true']"})


def _session(page):
    @contextmanager
    def factory(platform):
        yield page

    return factory


def _run(piece_ids, dry_run, page, publisher):
    job = social_publisher.create_job("threads", ids=piece_ids, limit=len(piece_ids), dry_run=dry_run)
    return social_publisher.execute_job(
        job["job_id"],
        session_factory=_session(page),
        publisher_factory=lambda platform, page_obj, job_id: publisher,
        sleep_func=lambda seconds: None,
    )


def test_detect_login_requires_observed_signals():
    page = FakePage(url="https://www.threads.net/", visible={"a[href^='/@']"})
    state = social_detect.detect_login(page, "threads")
    assert state["logged_in"] is True and state["signals"]
    login = social_detect.detect_login(FakePage(url="https://www.threads.net/login"), "threads")
    assert login["logged_in"] is False and login["status"] == "login_required"
    unknown = social_detect.detect_login(FakePage(url="https://www.threads.net/"), "threads")
    assert unknown["logged_in"] is False and "sin señales" in unknown["evidence"]


def test_detect_block_captcha():
    assert social_detect.detect_block(FakePage(body="Please confirm you're human: captcha"))["blocked"] is True
    assert social_detect.detect_block(FakePage(body="feed normal"))["blocked"] is False


def test_dry_run_fills_and_never_publishes(social_paths):
    publisher = FakePublisher()
    result = _run(["th_001"], True, _logged_in_page(), publisher)
    piece = result["pieces"][0]
    assert result["status"] == "completed" and result["dry_run"] is True
    assert publisher.fill_calls == 1 and publisher.publish_calls == 0
    assert piece["status"] == "dry_run_ok" and piece["post_url"] is None
    assert result["screenshots"], "el modo seco debe dejar screenshot de evidencia"
    assert social_pieces.published_index() == {}, "un modo seco jamás registra publicación"


def test_job_fails_honestly_without_login(social_paths):
    result = _run(["th_001"], False, FakePage(url="https://www.threads.net/login"), FakePublisher())
    assert result["status"] == "failed"
    assert "login_required" in result["error"]
    assert "POST /api/social/login/threads" in result["error"]
    assert result["pieces"][0]["status"] == "queued"
    assert social_jobs.load_job(result["job_id"])["status"] == "failed"


def test_real_publish_records_url_evidence_and_replies(social_paths):
    result = _run(["th_001"], False, _logged_in_page(), FakePublisher())
    piece = result["pieces"][0]
    assert result["status"] == "completed"
    assert piece["status"] == "published" and piece["post_url"].endswith("ABC123")
    assert piece["self_replies_scheduled"] == 2
    index = social_pieces.published_index()
    assert index["threads"]["th_001"]["post_url"] == piece["post_url"]
    replies = social_replies.list_replies()
    assert len(replies) == 2 and all(entry["post_url"] == piece["post_url"] for entry in replies)


def test_piece_failure_is_literal_and_not_success(social_paths):
    result = _run(["th_001"], True, _logged_in_page(), FakePublisher(fail_fill=True))
    assert result["status"] == "failed"
    assert "selector de editor" in result["pieces"][0]["error"]
    assert result["pieces"][0]["status"] == "failed"


def test_job_persistence_listing_and_evidence(social_paths):
    result = _run(["th_001"], True, _logged_in_page(), FakePublisher())
    stored = social_jobs.load_job(result["job_id"])
    assert stored["platform"] == "threads" and stored["pieces"][0]["id"] == "th_001"
    assert [job["job_id"] for job in social_jobs.list_jobs(limit=5)] == [result["job_id"]]
    assert all((Path(cfg.DATA_DIR) / rel).is_file() for rel in stored["screenshots"])


def test_schedule_validation_and_defaults(social_paths):
    config = scheduler.get_schedule()
    assert config["enabled"] is False and config["dry_run"] is True
    with pytest.raises(cfg.SocialError):
        scheduler.update_schedule({"times_local": ["25:99"]})
    with pytest.raises(cfg.SocialError):
        scheduler.update_schedule({"threads_per_day": 99})


def test_schedule_tick_is_idempotent_per_slot(social_paths, monkeypatch):
    scheduler.update_schedule({"enabled": True, "dry_run": True, "threads_per_day": 2,
                               "pinterest_per_day": 0, "times_local": ["09:00", "18:00"]})
    monkeypatch.setattr(scheduler, "_next_ids", lambda platform, count: ["th_001"] if platform == "threads" else [])
    calls = []

    def runner(platform, ids, limit, dry_run):
        calls.append((platform, tuple(ids), dry_run))
        return {"job_id": f"job_fake_{len(calls)}"}

    now = datetime.datetime(2026, 11, 5, 10, 0)
    first = scheduler.tick(now=now, runner=runner, reply_runner=lambda entry: {})
    second = scheduler.tick(now=now, runner=runner, reply_runner=lambda entry: {})
    assert len(first["jobs"]) == 1 and first["jobs"][0]["platform"] == "threads"
    assert calls == [("threads", ("th_001",), True)]
    assert second["jobs"] == [] and "ya se ejecutó" in second["reason"]


def test_reply_queue_due_attempts_and_success(social_paths):
    entries = social_replies.enqueue_replies(
        "https://www.threads.net/@ron/post/ABC123", ["primera", "segunda"], delay_minutes=[1, 2]
    )
    assert len(entries) == 2
    future = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=5)
    due = social_replies.due_replies(now=future)
    assert len(due) == 2
    social_replies.mark_result(due[0], False, "timeout del editor")
    assert social_replies.list_replies()[0]["attempts"] == 1
    social_replies.mark_result(due[0], True)
    assert social_replies.pending_count() == 1


def test_prepare_pin_image_is_strict_2_3(social_paths, tmp_path):
    image_module = pytest.importorskip("PIL.Image")
    source = tmp_path / "source.png"
    image_module.new("RGB", (640, 640), (12, 12, 12)).save(source)
    output = social_pieces.prepare_pin_image(
        {"id": "pin_x", "image_path": str(source), "aspect_ratio": "2:3"}, "job_test_1"
    )
    assert output and Path(output).is_file()
    with image_module.open(output) as prepared:
        assert prepared.size == (1000, 1500)


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(api_social.router)
    return TestClient(app)


def test_router_session_unmeasured_is_honest(social_paths):
    data = _client().get("/api/social/session/threads").json()
    assert data["measured"] is False
    assert data["state"]["logged_in"] is False and data["state"]["status"] == "unknown"
    assert "Verificar" in data["state"]["evidence"]


def test_router_publish_defaults_to_dry_run(social_paths, monkeypatch):
    monkeypatch.setattr(cfg, "assert_profile_available", lambda: social_paths)
    captured = {}

    def fake_create(platform, ids=None, limit=3, dry_run=True):
        captured.update(platform=platform, ids=ids, limit=limit, dry_run=dry_run)
        return {
            "job_id": "job_fake_router",
            "platform": platform,
            "dry_run": dry_run,
            "status": "queued",
            "pieces": [{"id": "th_001"}],
        }

    monkeypatch.setattr(social_publisher, "create_and_start", fake_create)
    res = _client().post("/api/social/publish", json={"platform": "threads", "ids": ["th_001"]})
    assert res.status_code == 200
    assert captured["dry_run"] is True and captured["limit"] == 3
    assert res.json()["note"].lower().startswith("modo seco")


def test_router_rejects_bad_platform_and_missing_job(social_paths):
    client = _client()
    assert client.post("/api/social/publish", json={"platform": "tiktok"}).status_code == 422
    assert client.get("/api/social/jobs/job_inexistente_123").status_code == 404


def test_router_login_and_lock_conflict(social_paths, monkeypatch):
    monkeypatch.setattr(cfg, "assert_profile_available", lambda: social_paths)
    keeper = api_social.social_login_keeper.login_keeper
    monkeypatch.setattr(
        keeper,
        "start",
        lambda platform: {
            "started": True,
            "running": True,
            "platform": platform,
            "status": "login_window_open",
            "detail": "ventana abierta",
            "login_url": cfg.PLATFORM_LOGIN[platform],
            "profile": str(cfg.profile_dir()),
        },
    )
    res = _client().post("/api/social/login/threads")
    assert res.status_code == 200 and res.json()["started"] is True
    assert "ventana" in res.json()["note"].lower()

    def locked():
        raise cfg.SocialError("perfil en uso por gumroad-publisher")

    monkeypatch.setattr(cfg, "assert_profile_available", locked)
    res_locked = _client().post("/api/social/login/threads")
    assert res_locked.status_code == 409 and "gumroad-publisher" in res_locked.json()["detail"]
