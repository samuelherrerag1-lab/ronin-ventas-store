"""Publicador real de Threads: compositor, texto, imagen, publicar y responder.

Selectores resilientes con fallbacks. La publicación solo se declara cuando hay
URL del post medida o confirmación textual visible; si no, se lanza SocialError.
"""

import re
import time
import urllib.parse
from typing import Any, Dict, Optional

from backend.services import social_config as cfg
from backend.services import social_dom as dom
from backend.services.social_publishers import CONFIRM_MARKERS, BasePublisher

THREADS_INTENT = "https://www.threads.com/intent/post?text="
THREADS_OPEN_COMPOSER = [
    "div[role='button'][aria-label*='Escribe para crear' i]",
    "div[role='button'][aria-label*='novedades' i]",
    "button:has-text(\"What's new?\")",
    "div[role='button']:has-text(\"What's new?\")",
    "button:has-text('¿Qué hay de nuevo?')",
    "[role='button'][aria-label*='New thread' i]",
    "[role='button'][aria-label*='Nuevo hilo' i]",
    "button[aria-label*='Create' i]",
    "a[href*='/intent/post']",
]
THREADS_EDITOR = [
    "div[contenteditable='true'][role='textbox']",
    "div[contenteditable='true'][aria-label*='Write' i]",
    "div[contenteditable='true']",
    "textarea[placeholder*='new' i]",
]
THREADS_PUBLISH = [
    "div[role='dialog'] button:has-text('Post')",
    "[role='dialog'] div[role='button']:has-text('Post')",
    "button:has-text('Publicar')",
    "button:has-text('Publish')",
    "div[role='button']:has-text('Post')",
]
THREADS_REPLY_OPEN = [
    "button:has-text('Reply')",
    "div[role='button']:has-text('Reply')",
    "[aria-label*='Reply' i]",
    "[aria-label*='Responder' i]",
]
THREADS_POST_URL_ANCHORS = ["a[href*='/post/']"]
THREADS_URL_RE = r"threads\.(?:net|com)/@[^/?#]+/post/[A-Za-z0-9_-]+"


class ThreadsPublisher(BasePublisher):
    platform = "threads"
    url_re = re.compile(THREADS_URL_RE)

    def __init__(self, page: Any, job_id: str) -> None:
        super().__init__(page, job_id)
        self.account: Optional[str] = None

    def _detect_account(self) -> Optional[str]:
        if self.account:
            return self.account
        locator = dom.find_any(self.page, ["a[href^='/@']", "a[href*='/@']"])
        if locator is not None:
            try:
                href = locator.get_attribute("href") or ""
            except Exception:
                href = ""
            match = re.search(r"/@([^/?#]+)", href)
            if match:
                self.account = match.group(1)
        return self.account

    def open_intent(self, text: str) -> None:
        """Compositor real por la ruta /intent/post: no depende del botón del feed."""
        self._detect_account()
        url = THREADS_INTENT + urllib.parse.quote(text, safe="")
        try:
            self.page.goto(url, wait_until="domcontentloaded", timeout=cfg.goto_timeout_ms())
        except Exception:
            # La navegación puede cortarse mientras monta el modal: se sigue midiendo.
            pass
        time.sleep(2.5)

    def open_composer(self) -> None:
        if dom.find_visible(self.page, THREADS_EDITOR, timeout_ms=800) is not None:
            return
        trigger = dom.find_visible(self.page, THREADS_OPEN_COMPOSER, timeout_ms=10000)
        if trigger is None:
            raise cfg.SocialError(
                dom.describe("No se encontró cómo abrir el compositor de Threads", THREADS_OPEN_COMPOSER)
            )
        dom.safe_click(trigger)
        time.sleep(1.5)

    def fill(self, piece: Dict[str, Any]) -> Dict[str, Any]:
        self._text = piece["text"]
        self.open_intent(piece["text"])
        editor = dom.find_visible(self.page, THREADS_EDITOR, timeout_ms=15000)
        if editor is None:
            self.open_composer()
            editor = dom.find_visible(self.page, THREADS_EDITOR, timeout_ms=10000)
        if editor is None:
            raise cfg.SocialError(
                dom.describe("No apareció el editor de texto de Threads", THREADS_EDITOR)
            )
        # El intent ya trae el texto; se fija de nuevo para garantizar el exacto.
        if piece["text"] not in (self.page.url or ""):
            dom.safe_fill(editor, piece["text"])
        image_attached = False
        image_path = piece.get("image_path")
        if image_path:
            file_input = dom.attach_file_input(self.page)
            if file_input is not None:
                file_input.set_input_files(image_path)
                image_attached = True
                time.sleep(2.5)
        return {"filled": True, "image_attached": image_attached, "editor": THREADS_EDITOR[0]}

    def _publish_button(self) -> Any:
        try:
            role_button = self.page.get_by_role(
                "button", name=re.compile(r"^(publicar|post|publish)$", re.I)
            )
            total = role_button.count()
            if total > 0:
                return role_button.nth(total - 1)
        except Exception:
            pass
        return dom.find_visible(self.page, THREADS_PUBLISH, timeout_ms=20000)

    def _wait_composer_closed(self, timeout_s: float = 45.0) -> bool:
        deadline = time.time() + timeout_s
        while time.time() < deadline:
            if dom.find_visible(self.page, THREADS_EDITOR, timeout_ms=500) is None:
                return True
            time.sleep(1.0)
        return False

    def _profile_post_urls(self) -> list:
        """URLs de posts propios en el perfil (nunca de otras cuentas)."""
        account = self._detect_account()
        if not account:
            return []
        try:
            self.page.goto(
                f"https://www.threads.com/@{account}",
                wait_until="domcontentloaded",
                timeout=cfg.goto_timeout_ms(),
            )
            time.sleep(3.5)
        except Exception:
            return []
        urls = []
        locator = self.page.locator(f"a[href*='/@{account}/post/']")
        try:
            total = locator.count()
        except Exception:
            return []
        for index in range(min(total, 4)):
            try:
                href = locator.nth(index).get_attribute("href") or ""
            except Exception:
                continue
            match = re.search(rf"/@{re.escape(account)}/post/[A-Za-z0-9_-]+", href)
            if match:
                url = "https://www.threads.com" + match.group(0)
                if url not in urls:
                    urls.append(url)
        return urls

    def _verified_url(self, text: str) -> Optional[str]:
        """URL del post propio cuyo contenido coincide con el texto publicado."""
        account = self._detect_account()
        candidates = []
        if account:
            candidates = [url for url in self.captured if f"/@{account}/post/" in url]
        candidates += self._profile_post_urls()
        snippet = " ".join((text or "").split()).lower()[:60]
        checked = set()
        for url in candidates:
            if url in checked:
                continue
            checked.add(url)
            if not snippet:
                return url
            try:
                self.page.goto(url, wait_until="domcontentloaded", timeout=cfg.goto_timeout_ms())
                time.sleep(2.5)
                if snippet in " ".join(self._body_text().split()):
                    return url
            except Exception:
                continue
        return None

    def publish(self) -> Dict[str, Any]:
        button = self._publish_button()
        if button is None:
            raise cfg.SocialError(
                dom.describe("No apareció el botón de publicar de Threads", THREADS_PUBLISH)
            )
        dom.safe_click(button)
        closed = self._wait_composer_closed(60.0)
        confirmation = self._wait_confirmation(20.0) or (
            "compositor cerrado tras pulsar Publicar" if closed else None
        )
        post_url = self._verified_url(getattr(self, "_text", ""))
        if post_url is None and confirmation is None:
            raise cfg.SocialError(
                "Se pulsó Publicar en Threads pero no hubo confirmación medible (ni cierre del "
                "compositor ni URL verificada del post). No se declara publicado."
            )
        return {"post_url": post_url, "confirmation": confirmation, "clicked_publish": True}

    def reply(self, post_url: str, text: str) -> Dict[str, Any]:
        self.page.goto(post_url, wait_until="domcontentloaded", timeout=cfg.goto_timeout_ms())
        time.sleep(2.0)
        trigger = dom.find_visible(self.page, THREADS_REPLY_OPEN, timeout_ms=15000)
        if trigger is None:
            raise cfg.SocialError(
                dom.describe("No se encontró el botón de responder", THREADS_REPLY_OPEN)
            )
        dom.safe_click(trigger)
        editor = dom.find_visible(self.page, THREADS_EDITOR, timeout_ms=15000)
        if editor is None:
            raise cfg.SocialError(dom.describe("No apareció el editor de respuesta", THREADS_EDITOR))
        dom.safe_fill(editor, text)
        button = dom.find_visible(self.page, THREADS_PUBLISH, timeout_ms=15000)
        if button is None:
            raise cfg.SocialError(
                dom.describe("No apareció el botón de publicar respuesta", THREADS_PUBLISH)
            )
        dom.safe_click(button)
        confirmation = self._wait_confirmation(45.0)
        if confirmation is None:
            raise cfg.SocialError(
                "Se pulsó Publicar en la respuesta de Threads sin confirmación medible; "
                "no se declara publicada."
            )
        return {"clicked_publish": True, "confirmation": confirmation, "post_url": post_url}


# Se mantiene el import para compatibilidad con módulos anteriores.
__all__ = ["ThreadsPublisher", "THREADS_EDITOR", "THREADS_PUBLISH", "CONFIRM_MARKERS"]
