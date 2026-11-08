"""Dobles de Playwright para tests del publicador social (sin navegador real).

Un ``FakePage`` imita solo lo que el publicador usa de verdad: url, locators,
screenshot y listener de respuestas. Así la máquina de estados, la honestidad y
la persistencia se prueban sin abrir Chrome.
"""

from pathlib import Path


class FakeLocator:
    def __init__(self, visible: bool, text: str = "", attrs: dict = None) -> None:
        self._visible = visible
        self._text = text
        self._attrs = attrs or {}
        self.clicks = 0
        self.filled = None
        self.files = None

    @property
    def first(self):
        return self

    def count(self) -> int:
        return 1 if self._visible else 0

    def is_visible(self, timeout: int = 0) -> bool:
        return self._visible

    def get_attribute(self, name: str):
        return self._attrs.get(name)

    def inner_text(self, timeout: int = 0) -> str:
        return self._text

    def click(self, timeout: int = 0, force: bool = False) -> None:
        self.clicks += 1

    def fill(self, text: str, timeout: int = 0) -> None:
        self.filled = text

    def type(self, text: str, delay: int = 0) -> None:
        self.filled = text

    def press(self, key: str) -> None:
        pass

    def set_input_files(self, path: str) -> None:
        self.files = path


class FakePage:
    def __init__(self, url: str = "https://www.threads.net/", visible=None, body: str = "") -> None:
        self.url = url
        self._visible = set(visible or [])
        self._body = body
        self.shots = []
        self.responses = []

    def locator(self, selector: str) -> FakeLocator:
        visible = selector in self._visible
        return FakeLocator(visible, text=self._body if selector == "body" else "")

    def goto(self, url: str, **kwargs) -> None:
        self.url = url

    def screenshot(self, path: str = "", full_page: bool = False, **kwargs) -> None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"\x89PNG\r\n\x1a\nfake")
        self.shots.append(str(target))

    def on(self, event: str, handler) -> None:
        self.responses.append((event, handler))


class FakePublisher:
    def __init__(self, result=None, fail_fill: bool = False) -> None:
        self.fill_calls = 0
        self.publish_calls = 0
        self.fail_fill = fail_fill
        self.result = result or {"post_url": "https://www.threads.net/@ron/post/ABC123", "confirmation": "ok"}

    def fill(self, piece):
        self.fill_calls += 1
        if self.fail_fill:
            from backend.services import social_config as cfg

            raise cfg.SocialError("selector de editor no encontrado en la prueba")
        return {"filled": True}

    def publish(self):
        self.publish_calls += 1
        return dict(self.result)
