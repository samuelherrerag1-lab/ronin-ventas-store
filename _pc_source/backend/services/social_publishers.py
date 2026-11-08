"""Base común y fábrica de publicadores sobre la UI web real.

Los publicadores concretos viven en ``social_threads`` y ``social_pinterest``.
Si ningún selector aparece, se lanza ``SocialError`` con la lista probada: el
job falla honestamente en vez de simular una publicación.
"""

import re
import time
from typing import Any, Dict, List, Optional

from backend.services import social_config as cfg
from backend.services import social_dom as dom

CONFIRM_MARKERS = (
    "posted",
    "publicado",
    "your thread",
    "tu hilo",
    "view post",
    "ver publicación",
    "your pin",
    "ver pin",
    "view pin",
)


class BasePublisher:
    platform = ""
    url_re = re.compile(r"$^")

    def __init__(self, page: Any, job_id: str) -> None:
        self.page = page
        self.job_id = job_id
        self.captured: List[str] = []
        hook = getattr(page, "on", None)
        if callable(hook):
            try:
                hook("response", self._on_response)
            except Exception:
                pass

    def _on_response(self, response: Any) -> None:
        try:
            url = str(response.url)
        except Exception:
            return
        match = self.url_re.search(url)
        if match:
            found = match.group(0)
            absolute = found if found.startswith("http") else "https://" + found
            if absolute not in self.captured:
                self.captured.append(absolute)

    def _first_url(self, anchors: List[str]) -> Optional[str]:
        if self.captured:
            return self.captured[0]
        locator = dom.find_any(self.page, anchors)
        if locator is None:
            return None
        try:
            href = locator.get_attribute("href") or ""
        except Exception:
            return None
        if not href or ("/post/" not in href and "/pin/" not in href):
            return None
        if href.startswith("http"):
            return href
        return f"https://www.{'threads.net' if self.platform == 'threads' else 'pinterest.com'}{href}"

    def _body_text(self) -> str:
        locator = dom.locator_first(self.page, "body")
        if locator is None:
            return ""
        try:
            return (locator.inner_text(timeout=3000) or "").lower()
        except Exception:
            return ""

    def _wait_confirmation(self, timeout_s: float = 45.0) -> Optional[str]:
        deadline = time.time() + timeout_s
        while time.time() < deadline:
            if self.captured:
                return "respuesta de red con URL del post/pin"
            text = self._body_text()
            for marker in CONFIRM_MARKERS:
                if marker in text:
                    return f"texto de confirmación visible: {marker}"
            time.sleep(1.0)
        return None

    def fill(self, piece: Dict[str, Any]) -> Dict[str, Any]:
        raise cfg.SocialError("El publicador no implementa fill()")

    def publish(self) -> Dict[str, Any]:
        raise cfg.SocialError("El publicador no implementa publish()")


def build_publisher(platform: str, page: Any, job_id: str) -> Any:
    if platform == "threads":
        from backend.services.social_threads import ThreadsPublisher

        return ThreadsPublisher(page, job_id)
    if platform == "pinterest":
        from backend.services.social_pinterest import PinterestPublisher

        return PinterestPublisher(page, job_id)
    raise cfg.SocialError(f"Plataforma no soportada: {platform}")
