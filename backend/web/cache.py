"""
Caché corta (30 s) de las respuestas públicas de la API: productos,
categorías, reseñas y datos legales.

Cualquier cambio (crear, editar, eliminar) toca un archivo "marca de versión"
y todos los procesos descartan su caché al instante.
"""

import gzip
import os
import threading
import time
from typing import Callable, Dict, Optional, Tuple

from backend.config import API_CACHE_TTL, API_CACHE_VERSION_FILE

TTL_SECONDS = API_CACHE_TTL
MAX_ENTRIES = 256

# clave -> (guardado_en, versión, status, json, json_gzip)
Entry = Tuple[float, float, int, bytes, bytes]
_CACHE: Dict[str, Entry] = {}
_LOCK = threading.Lock()


def _data_version() -> float:
    try:
        return os.stat(API_CACHE_VERSION_FILE).st_mtime
    except OSError:
        return 0.0


def bump_data_version() -> None:
    """Marca que los datos cambiaron: invalida la caché en todos los procesos."""
    try:
        with open(API_CACHE_VERSION_FILE, "a"):
            pass
        now = time.time()
        os.utime(API_CACHE_VERSION_FILE, (now, max(now, _data_version() + 0.001)))
    except OSError:
        pass
    with _LOCK:
        _CACHE.clear()


def get_or_build(key: str, build: Callable[[], Tuple[int, bytes]]) -> Tuple[int, bytes, bytes]:
    """Devuelve (status, json, json_gzip) desde la caché o generándolo con `build`."""
    version = _data_version()
    now = time.time()
    with _LOCK:
        hit: Optional[Entry] = _CACHE.get(key)
    if hit and hit[1] == version and now - hit[0] < TTL_SECONDS:
        return hit[2], hit[3], hit[4]
    status, raw = build()
    gz = gzip.compress(raw, compresslevel=6) if len(raw) > 1024 else b""
    if status == 200:
        with _LOCK:
            if len(_CACHE) >= MAX_ENTRIES:
                _CACHE.clear()
            _CACHE[key] = (now, version, status, raw, gz)
    return status, raw, gz
