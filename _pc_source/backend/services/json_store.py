"""Persistencia JSON atómica y con lock para los stores del sistema.

Todos los stores escribían con `path.write_text(...)`: una interrupción a mitad
de escritura dejaba el JSON truncado y sin backup. Aquí se centraliza:

- un lock reentrante por archivo (dos requests concurrentes ya no se pisan),
- escritura a temporal + `os.replace` (nunca queda un archivo a medias),
- lectura tolerante que devuelve el error literal en vez de lanzar,
- cuarentena del archivo dañado para poder recuperarlo a mano.
"""

import json
import os
import threading
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

_REGISTRY_LOCK = threading.Lock()
_LOCKS: Dict[str, threading.RLock] = {}


def lock_for(path: Any) -> threading.RLock:
    """Lock reentrante compartido por todos los escritores de ese archivo."""
    key = str(Path(path).resolve())
    with _REGISTRY_LOCK:
        lock = _LOCKS.get(key)
        if lock is None:
            lock = threading.RLock()
            _LOCKS[key] = lock
        return lock


def read_json(path: Any) -> Tuple[Optional[Any], Optional[str]]:
    """Devuelve (datos, error). Archivo ausente => (None, None) sin error."""
    file_path = Path(path)
    if not file_path.exists():
        return None, None
    try:
        return json.loads(file_path.read_text(encoding="utf-8")), None
    except (json.JSONDecodeError, UnicodeDecodeError, OSError) as exc:
        return None, f"{type(exc).__name__}: {exc}"


def write_json_atomic(path: Any, data: Any) -> None:
    """Escribe JSON con lock y reemplazo atómico (tmp + os.replace)."""
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_for(file_path):
        tmp_path = file_path.with_name(f".{file_path.name}.{os.getpid()}.tmp")
        try:
            with open(tmp_path, "w", encoding="utf-8") as handle:
                json.dump(data, handle, indent=2, ensure_ascii=False)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(tmp_path, file_path)
        finally:
            if tmp_path.exists():
                try:
                    tmp_path.unlink()
                except OSError:
                    pass


def quarantine_corrupt(path: Any) -> Optional[str]:
    """Mueve un JSON ilegible a `<nombre>.corrupt-<fecha>.json` y devuelve ruta."""
    file_path = Path(path)
    if not file_path.exists():
        return None
    stamp = time.strftime("%Y%m%d_%H%M%S")
    backup = file_path.with_name(f"{file_path.stem}.corrupt-{stamp}{file_path.suffix}")
    try:
        with lock_for(file_path):
            os.replace(file_path, backup)
        return str(backup)
    except OSError:
        return None


def update_json(path: Any, mutator: Any) -> Tuple[Any, Optional[str]]:
    """Lock + read + mutar + escribir. `mutator` recibe los datos y los devuelve.

    Si el archivo está corrupto devuelve (None, error) sin escribir: cada store
    decide si regenera por defecto o degrada.
    """
    file_path = Path(path)
    with lock_for(file_path):
        data, error = read_json(file_path)
        if error:
            return None, error
        data = mutator(data)
        write_json_atomic(file_path, data)
        return data, None
