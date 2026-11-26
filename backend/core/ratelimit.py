"""
Límite de peticiones por IP con ventana fija (O(1) por petición).

Es por proceso: con varios workers el límite real es aproximado, suficiente
para frenar bots y abusos. El login además tiene su propio bloqueo en la base
de datos (backend/core/auth.py).
"""

import threading
import time
from typing import Dict, List, Tuple

_STORAGE: Dict[Tuple[str, str], List[float]] = {}
_LOCK = threading.Lock()
_LAST_PRUNE = [0.0]


def check_rate_limit(ip_address: str, max_requests: int, window_seconds: int = 60, bucket: str = "api") -> bool:
    """True si la IP aún puede hacer peticiones en este `bucket` (api, form, login...)."""
    now = time.time()
    key = (bucket, ip_address)
    with _LOCK:
        if now - _LAST_PRUNE[0] > window_seconds:
            for k in [k for k, v in _STORAGE.items() if now - v[0] >= window_seconds]:
                del _STORAGE[k]
            _LAST_PRUNE[0] = now
        entry = _STORAGE.get(key)
        if entry is None or now - entry[0] >= window_seconds:
            _STORAGE[key] = [now, 1]
            return True
        entry[1] += 1
        return entry[1] <= max_requests
