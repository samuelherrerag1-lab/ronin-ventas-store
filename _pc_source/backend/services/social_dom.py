"""Helpers de DOM tolerantes a fallos: localizar, esperar, rellenar y pulsar.

Se usan tanto en los publicadores reales como en la detección de sesión. Todo
error de Playwright se traga para intentar el siguiente selector; el fallo real
se reporta arriba con los selectores probados.
"""

import time
from typing import Any, List, Optional


def page_url(page: Any) -> str:
    try:
        return str(page.url or "")
    except Exception:
        return ""


def locator_first(page: Any, selector: str) -> Any:
    try:
        return page.locator(selector).first
    except Exception:
        return None


def visible(page: Any, selector: str, timeout_ms: int = 0) -> bool:
    locator = locator_first(page, selector)
    if locator is None:
        return False
    try:
        if locator.count() == 0:
            return False
        return bool(locator.is_visible(timeout=timeout_ms))
    except Exception:
        return False


def find_visible(page: Any, selectors: List[str], timeout_ms: int = 8000) -> Any:
    """Espera hasta ``timeout_ms`` al primero de los selectores visibles."""
    deadline = time.time() + max(0.0, timeout_ms / 1000.0)
    while True:
        for selector in selectors:
            locator = locator_first(page, selector)
            if locator is None:
                continue
            try:
                if locator.count() > 0 and locator.is_visible(timeout=0):
                    return locator
            except Exception:
                continue
        if time.time() >= deadline:
            return None
        time.sleep(0.4)


def find_any(page: Any, selectors: List[str]) -> Any:
    """Primer selector con al menos un nodo, visible o no (inputs ocultos)."""
    for selector in selectors:
        locator = locator_first(page, selector)
        if locator is None:
            continue
        try:
            if locator.count() > 0:
                return locator
        except Exception:
            continue
    return None


def safe_click(locator: Any, timeout_ms: int = 15000) -> None:
    try:
        locator.click(timeout=timeout_ms)
    except Exception:
        locator.click(timeout=timeout_ms, force=True)


def safe_fill(locator: Any, text: str, timeout_ms: int = 15000) -> None:
    try:
        locator.fill(text, timeout=timeout_ms)
    except Exception:
        locator.click(timeout=timeout_ms)
        try:
            locator.press("Control+A")
            locator.press("Backspace")
        except Exception:
            pass
        locator.type(text, delay=12)


def attach_file_input(page: Any) -> Optional[Any]:
    """Input de archivo aunque esté oculto (Playwright permite set_input_files)."""
    return find_any(page, ["input[type='file']"])


def describe(missing: str, selectors: List[str]) -> str:
    return f"{missing}. Selectores probados: {', '.join(selectors)}"
