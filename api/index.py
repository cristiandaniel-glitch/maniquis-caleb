"""
Adaptador para Vercel: cada petición a /api/... llega aquí y se atiende con
el mismo manejador del servidor normal (backend/web/handler.py).

vercel.json reescribe /api/<ruta> → /api/index?__route=<ruta>; aquí se
reconstruye la ruta original antes de despachar.
"""

import os
import sys
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import backend.routes  # noqa: E402,F401  (registra las rutas)
from backend.web.handler import SecureRequestHandler  # noqa: E402


class handler(SecureRequestHandler):  # Vercel busca una clase llamada "handler"
    def _dispatch(self, method: str) -> None:
        parts = urllib.parse.urlsplit(self.path)
        query = urllib.parse.parse_qsl(parts.query, keep_blank_values=True)
        route = next((value for key, value in query if key == "__route"), None)
        if route is not None:
            rest = [(key, value) for key, value in query if key != "__route"]
            self.path = "/api/" + route.lstrip("/") + ("?" + urllib.parse.urlencode(rest) if rest else "")
        super()._dispatch(method)
