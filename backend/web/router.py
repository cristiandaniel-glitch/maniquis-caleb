"""
Enrutador declarativo de la API.

Cada controlador se registra con un decorador que dice, en una sola línea,
qué método y ruta atiende y qué protecciones necesita:

    @router.get("/api/products", cache=True)
    def list_products(req): ...

    @router.put("/api/products/<int:product_id>", admin=True, mutates=True)
    def update_product(req): ...

Todos los controladores reciben un `Request` y devuelven `(datos, código_http)`.
"""

import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

Response = Tuple[Dict[str, Any], int]
Handler = Callable[["Request"], Response]

_CONVERTERS = {
    "int": (r"[0-9]{1,12}", int),
    "str": (r"[A-Za-z0-9_\-]{1,120}", str),
}


@dataclass
class Request:
    method: str
    path: str
    client_ip: str
    query: Dict[str, str] = field(default_factory=dict)
    params: Dict[str, Any] = field(default_factory=dict)
    body: Dict[str, Any] = field(default_factory=dict)
    is_admin: bool = False
    headers: Any = None


@dataclass
class Route:
    method: str
    pattern: str
    handler: Handler
    regex: "re.Pattern[str]"
    casts: Dict[str, Callable[[str], Any]]
    admin: bool = False       # exige token de administrador
    cache: bool = False       # respuesta pública que se puede guardar unos segundos
    mutates: bool = False     # al terminar, invalida la caché pública
    limit: str = "api"        # grupo de rate limit: api | form | login
    honeypot: bool = False    # formularios públicos con trampa para bots


def _compile(pattern: str) -> Tuple["re.Pattern[str]", Dict[str, Callable[[str], Any]]]:
    casts: Dict[str, Callable[[str], Any]] = {}

    def repl(match: "re.Match[str]") -> str:
        kind, name = match.group(1) or "str", match.group(2)
        regex, cast = _CONVERTERS[kind]
        casts[name] = cast
        return f"(?P<{name}>{regex})"

    body = re.sub(r"<(?:(\w+):)?(\w+)>", repl, pattern)
    return re.compile(f"^{body}$"), casts


class Router:
    def __init__(self) -> None:
        self.routes: List[Route] = []

    def add(self, method: str, pattern: str, **options: Any) -> Callable[[Handler], Handler]:
        def decorator(func: Handler) -> Handler:
            regex, casts = _compile(pattern)
            self.routes.append(Route(method, pattern, func, regex, casts, **options))
            return func
        return decorator

    def get(self, pattern: str, **options: Any):
        return self.add("GET", pattern, **options)

    def post(self, pattern: str, **options: Any):
        options.setdefault("limit", "form")
        return self.add("POST", pattern, **options)

    def put(self, pattern: str, **options: Any):
        return self.add("PUT", pattern, **options)

    def patch(self, pattern: str, **options: Any):
        return self.add("PATCH", pattern, **options)

    def delete(self, pattern: str, **options: Any):
        return self.add("DELETE", pattern, **options)

    def match(self, method: str, path: str) -> Tuple[Optional[Route], Dict[str, Any], List[str]]:
        """Devuelve (ruta, parámetros, métodos_permitidos_para_esa_ruta)."""
        allowed: List[str] = []
        for route in self.routes:
            found = route.regex.match(path)
            if not found:
                continue
            if route.method == method:
                params = {k: route.casts[k](v) for k, v in found.groupdict().items()}
                return route, params, []
            allowed.append(route.method)
        return None, {}, allowed


router = Router()


def ok(data: Any = None, status: int = 200, **extra: Any) -> Response:
    body: Dict[str, Any] = {"success": True}
    if data is not None:
        body["data"] = data
    body.update(extra)
    return body, status


def fail(message: str, status: int = 400) -> Response:
    return {"success": False, "error": message}, status
