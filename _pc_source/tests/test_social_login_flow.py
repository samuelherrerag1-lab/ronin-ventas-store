"""Tests del login humano multi-pestaña con Playwright mockeado (sin Chrome)."""

from contextlib import contextmanager

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import backend.routers.api_social_publish as api_social
import backend.services.social_browser as browser
import backend.services.social_config as cfg
import backend.services.social_login_flow as flow_module
from tests.social_fakes import FakePage


@pytest.fixture
def flow_paths(tmp_path, monkeypatch):
    social_dir = tmp_path / "publish_jobs"
    evidence = social_dir / "evidence"
    for folder in (social_dir, evidence):
        folder.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(cfg, "SOCIAL_DIR", social_dir)
    monkeypatch.setattr(cfg, "EVIDENCE_DIR", evidence)
    monkeypatch.setattr(cfg, "SESSIONS_PATH", social_dir / "sessions.json")
    monkeypatch.setattr(cfg, "REPLY_QUEUE_PATH", social_dir / "reply_queue.json")
    monkeypatch.setattr(cfg, "assert_profile_available", lambda: tmp_path)
    monkeypatch.setattr(cfg, "login_poll_s", lambda: 0.01)
    return social_dir


class FakeContext:
    def __init__(self, extra_page):
        self.extra_page = extra_page

    def new_page(self):
        return self.extra_page


def _no_goto(self, url, **kwargs):
    return None


def _mount(monkeypatch, first, second):
    first.goto = _no_goto.__get__(first, FakePage)
    second.goto = _no_goto.__get__(second, FakePage)

    @contextmanager
    def fake_persistent():
        yield FakeContext(second), first

    monkeypatch.setattr(browser, "persistent_context", fake_persistent)


def test_flow_completes_when_both_logins_are_measured(flow_paths, monkeypatch):
    threads = FakePage(url="https://www.threads.net/", visible={"a[href^='/@']", "div[contenteditable='true']"})
    pinterest = FakePage(url="https://www.pinterest.com/", visible={"[data-test-id='header-profile']"})
    _mount(monkeypatch, threads, pinterest)
    flow = flow_module.MultiLoginFlow()
    started = flow.start(["threads", "pinterest"], timeout_s=5)
    assert started["started"] is True and started["running"] is True
    final = flow.wait(max_extra_s=10)
    assert final["status"] == "completed"
    assert set(final["logged"]) == {"threads", "pinterest"} and final["pending"] == []
    sessions = browser.load_sessions()["platforms"]
    assert sessions["threads"]["logged_in"] is True and sessions["threads"]["stale"] is False
    assert sessions["pinterest"]["logged_in"] is True
    assert "URL=" in sessions["threads"]["evidence"]


def test_flow_times_out_honestly_without_login(flow_paths, monkeypatch):
    threads = FakePage(url="https://www.threads.net/login")
    pinterest = FakePage(url="https://www.pinterest.com/login/")
    _mount(monkeypatch, threads, pinterest)
    flow = flow_module.MultiLoginFlow()
    flow.start(["threads", "pinterest"], timeout_s=0.2)
    final = flow.wait(max_extra_s=10)
    assert final["status"] == "timeout"
    assert set(final["pending"]) == {"threads", "pinterest"} and final["logged"] == []
    sessions = browser.load_sessions()["platforms"]
    assert sessions["threads"]["status"] == "login_timeout"
    assert sessions["threads"]["logged_in"] is False


def test_flow_status_file_and_idle_default(flow_paths):
    idle = flow_module.read_flow_status()
    assert idle["running"] is False and idle["status"] == "idle"
    flow = flow_module.MultiLoginFlow()
    flow._set(running=True, status="waiting_for_human", detail="prueba")
    stored = flow_module.read_flow_status()
    assert stored["status"] == "waiting_for_human" and stored["detail"] == "prueba"


def test_router_login_all_starts_single_window(flow_paths, monkeypatch):
    monkeypatch.setattr(cfg, "assert_profile_available", lambda: flow_paths)
    monkeypatch.setattr(
        api_social.social_login_flow.multi_login_flow,
        "start",
        lambda timeout_s=None: {"started": True, "running": True, "status": "waiting_for_human", "platforms": {}, "logged": [], "pending": ["threads", "pinterest"], "detail": "abierta"},
    )
    app = FastAPI()
    app.include_router(api_social.router)
    res = TestClient(app).post("/api/social/login/all", json={"timeout_s": 600})
    assert res.status_code == 200
    assert res.json()["started"] is True and "no cierres" in res.json()["note"].lower()
