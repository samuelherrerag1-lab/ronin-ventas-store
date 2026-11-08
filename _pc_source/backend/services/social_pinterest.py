"""Publicador real de Pinterest: creador orgánico, imagen 2:3, título SEO, link y tablero."""

import re
import time
from typing import Any, Dict, List, Optional

from backend.services import social_config as cfg
from backend.services import social_dom as dom
from backend.services import social_pieces
from backend.services.social_pinterest_board import select_board
from backend.services.social_publishers import BasePublisher

PINTEREST_BUILDER = "https://www.pinterest.com/pin-creation-tool/"
PINTEREST_TITLE = [
    "input[placeholder*='Explica en qué consiste' i]",
    "input[placeholder*='title' i]",
    "input[placeholder*='título' i]",
    "textarea[placeholder*='título' i]",
    "input[name='title']",
    "textarea[name='title']",
]
PINTEREST_DESC = [
    "div[contenteditable='true'][aria-label*='Describe tu Pin' i]",
    "div[contenteditable='true'][aria-label*='descrip' i]",
    "textarea[placeholder*='descrip' i]",
    "[data-test-id='pin-builder-description']",
]
PINTEREST_LINK = [
    "input[type='url']",
    "input[placeholder*='enlace' i]",
    "input[placeholder*='link' i]",
    "input[name='link']",
]
PINTEREST_PUBLISH = [
    "button:has-text('Publicar')",
    "div[role='button']:has-text('Publicar')",
    "button:has-text('Publish')",
]
PINTEREST_PIN_URL_ANCHORS = ["a[href*='/pin/']"]
PINTEREST_URL_RE = r"pinterest\.[a-z.]+/pin/\d+"


class PinterestPublisher(BasePublisher):
    platform = "pinterest"
    url_re = re.compile(PINTEREST_URL_RE)

    def _dismiss_onboarding(self) -> None:
        """El creador muestra un tutorial de 4 pasos la primera vez."""
        for _ in range(6):
            dismissed = False
            for name in ("Siguiente", "Entendido", "Got it", "Next"):
                try:
                    button = self.page.get_by_role("button", name=name).first
                    if button.count() > 0 and button.is_visible(timeout=0):
                        dom.safe_click(button, timeout_ms=5000)
                        time.sleep(1.2)
                        dismissed = True
                        break
                except Exception:
                    continue
            if not dismissed:
                return

    def _wait_file_input(self, timeout_s: float = 30.0) -> Any:
        deadline = time.time() + timeout_s
        while time.time() < deadline:
            file_input = dom.attach_file_input(self.page)
            if file_input is not None:
                return file_input
            time.sleep(1.0)
        return None

    def fill(self, piece: Dict[str, Any]) -> Dict[str, Any]:
        prepared = social_pieces.prepare_pin_image(piece, self.job_id)
        if prepared is None:
            raise cfg.SocialError(
                "Pinterest exige una imagen y la pieza no tiene una imagen real en disco "
                f"(item={piece.get('id')}). No se publica un pin vacío."
            )
        self.page.goto(
            PINTEREST_BUILDER, wait_until="domcontentloaded", timeout=cfg.goto_timeout_ms()
        )
        time.sleep(6.0)
        self._dismiss_onboarding()
        file_input = self._wait_file_input(30.0)
        if file_input is None:
            raise cfg.SocialError(
                "No apareció el input de archivo del creador de pines de Pinterest."
            )
        file_input.set_input_files(prepared)
        time.sleep(5.0)

        title_field = dom.find_visible(self.page, PINTEREST_TITLE, timeout_ms=45000)
        if title_field is None:
            raise cfg.SocialError(
                dom.describe("No apareció el campo de título del pin", PINTEREST_TITLE)
            )
        dom.safe_fill(title_field, piece["title"])

        notes: List[str] = []
        desc_field = dom.find_visible(self.page, PINTEREST_DESC, timeout_ms=8000)
        if desc_field is not None:
            dom.safe_fill(desc_field, piece["description"])
        else:
            notes.append("Campo de descripción no localizado; el pin se publica sin descripción.")

        link = piece.get("target_route") or ""
        if link.startswith("http"):
            link_field = dom.find_visible(self.page, PINTEREST_LINK, timeout_ms=8000)
            if link_field is not None:
                dom.safe_fill(link_field, link)
            else:
                notes.append("Campo de link no localizado; el pin se publica sin link.")
        else:
            notes.append("Sin URL pública para el link del pin.")

        if not select_board(self.page, piece.get("board") or ""):
            notes.append(f"No se pudo seleccionar/crear el tablero '{piece.get('board')}'.")
        self._text = f"{piece.get('title') or ''} {piece.get('description') or ''}".strip()
        return {"filled": True, "image_uploaded": prepared, "notes": notes}


    def _publish_button(self) -> Any:
        try:
            role_button = self.page.get_by_role(
                "button", name=re.compile(r"^(publicar|publish)$", re.I)
            )
            total = role_button.count()
            if total > 0:
                return role_button.nth(total - 1)
        except Exception:
            pass
        return dom.find_visible(self.page, PINTEREST_PUBLISH, timeout_ms=20000)

    def _verified_pin_url(self, text: str) -> Optional[str]:
        candidates: List[str] = list(self.captured)
        if re.search(r"/pin/\d+", self.page.url or ""):
            match = re.search(r"(https?://[^?#]*pinterest\.[a-z.]+/pin/\d+)", self.page.url or "")
            if match:
                candidates.insert(0, match.group(1))
        anchor = dom.find_any(self.page, PINTEREST_PIN_URL_ANCHORS)
        if anchor is not None:
            try:
                href = anchor.get_attribute("href") or ""
            except Exception:
                href = ""
            if href:
                candidates.append(href if href.startswith("http") else "https://www.pinterest.com" + href)
        snippet = " ".join((text or "").split()).lower()[:60]
        checked = set()
        for url in candidates:
            clean = re.sub(r"/(media|sent)$", "/", url)
            if clean in checked or not re.search(r"/pin/\d+", clean):
                continue
            checked.add(clean)
            if not snippet:
                return clean
            try:
                self.page.goto(clean, wait_until="domcontentloaded", timeout=cfg.goto_timeout_ms())
                time.sleep(2.5)
                if snippet in " ".join(self._body_text().split()):
                    return clean
            except Exception:
                continue
        return None

    def publish(self) -> Dict[str, Any]:
        button = self._publish_button()
        if button is None:
            raise cfg.SocialError(
                dom.describe("No apareció el botón de publicar pin", PINTEREST_PUBLISH)
            )
        dom.safe_click(button)
        confirmation = self._wait_confirmation(60.0)
        pin_url = self._verified_pin_url(getattr(self, "_text", ""))
        if pin_url is None and confirmation is None:
            raise cfg.SocialError(
                "Se pulsó Publicar en Pinterest pero no hubo confirmación medible (ni URL "
                "verificada del pin ni texto de éxito). No se declara publicado."
            )
        return {"post_url": pin_url, "confirmation": confirmation, "clicked_publish": True}
