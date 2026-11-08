"""Selección o creación del tablero de Pinterest sobre la UI real.

El selector está deshabilitado hasta que la imagen termina de subir; se espera a
que se habilite. Si el tablero no existe se crea con el diálogo real de Pinterest
y se verifica que el botón del tablero muestre el nombre elegido.
"""

import time
from typing import Any

from backend.services import social_dom as dom

BOARD_SELECTORS = [
    "[data-test-id='board-dropdown-select-button']",
    "div[role='button']:has-text('Selecciona un tablero')",
    "[data-test-id='board-selector']",
    "div[role='combobox']",
]


def _wait_enabled(page: Any, timeout_s: float = 30.0) -> Any:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        candidate = dom.find_visible(page, BOARD_SELECTORS, timeout_ms=1000)
        if candidate is not None:
            try:
                if (candidate.get_attribute("aria-disabled") or "").lower() != "true":
                    return candidate
            except Exception:
                pass
        time.sleep(1.0)
    return None


def select_board(page: Any, board: str) -> bool:
    safe_board = (board or "").replace("'", "").replace('"', "").strip()
    if not safe_board:
        return False
    selector = _wait_enabled(page)
    if selector is None:
        return False
    try:
        dom.safe_click(selector)
        time.sleep(1.5)
    except Exception:
        return False

    options = [
        f"div[role='option']:has-text('{safe_board}')",
        f"[data-test-id='board-row']:has-text('{safe_board}')",
        f"div[role='button']:has-text('{safe_board}')",
        f"div[role='menuitem']:has-text('{safe_board}')",
    ]
    option = dom.find_visible(page, options, timeout_ms=4000)
    if option is not None:
        dom.safe_click(option)
        time.sleep(1.0)
        return True

    create = dom.find_visible(
        page,
        [
            "div[role='button']:has-text('Crear tablero')",
            "button:has-text('Crear tablero')",
            "div[role='button']:has-text('Create board')",
        ],
        timeout_ms=5000,
    )
    if create is None:
        return False
    dom.safe_click(create)
    time.sleep(2.0)
    name_input = dom.find_visible(
        page,
        [
            "input[placeholder*='Lugares para ir' i]",
            "div[role='dialog'] input[type='text']",
            "input[name='boardName']",
        ],
        timeout_ms=8000,
    )
    if name_input is None:
        return False
    dom.safe_fill(name_input, safe_board)
    time.sleep(1.0)
    confirm = dom.find_visible(
        page,
        [
            "[data-test-id='board-form-submit-button']",
            "div[role='dialog'] button:has-text('Crear')",
            "button:has-text('Crear')",
        ],
        timeout_ms=8000,
    )
    if confirm is None:
        return False
    dom.safe_click(confirm)
    time.sleep(2.5)
    verified = dom.find_visible(page, BOARD_SELECTORS, timeout_ms=5000)
    if verified is None:
        return False
    try:
        return safe_board.lower() in (verified.inner_text(timeout=2000) or "").lower()
    except Exception:
        return False
