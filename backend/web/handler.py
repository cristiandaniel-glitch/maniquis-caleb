"""
Manejador HTTP: recibe cada petición, aplica las protecciones comunes y la
entrega al controlador correspondiente (API) o al servidor de archivos.

Orden de una petición a la API:
  1. ruta y método válidos (404 / 405)
  2. rate limit por IP según el grupo de la ruta (429)
  3. token de administrador si la ruta lo exige (401)
  4. cuerpo JSON validado: tipo, tamaño y que sea un objeto (400 / 413 / 415)
  5. controlador → (datos, código). Errores de validación → 400; cualquier
     otro error → 500 genérico (el detalle solo va al log del servidor)
"""

import gzip
import http.server
import ipaddress
import json
import traceback
import urllib.parse
from typing import Any, Dict, Optional, Tuple

from backend.config import (
    FORM_RATE_LIMIT_PER_MINUTE,
    MAX_CONTENT_LENGTH,
    RATE_LIMIT_PER_MINUTE,
    TRUST_PROXY,
)
from backend.core.auth import validate_admin_token
from backend.core.ratelimit import check_rate_limit
from backend.core.validation import ValidationError
from backend.web import cache, static
from backend.web.headers import cors_headers, security_headers
from backend.web.router import Request, Route, router

# Peticiones por minuto y por IP de cada grupo de rutas.
RATE_LIMITS = {
    "api": RATE_LIMIT_PER_MINUTE,
    "form": FORM_RATE_LIMIT_PER_MINUTE,
    "login": 10,
}
PUBLIC_CACHE_CONTROL = "public, max-age=60, stale-while-revalidate=300"


class BadRequest(Exception):
    def __init__(self, message: str, status: int = 400) -> None:
        super().__init__(message)
        self.status = status


class SecureRequestHandler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    # Conexiones lentas o abandonadas se cierran a los 10 s (no ocupan hilos).
    timeout = 10
    # No revelar versión de Python ni del servidor.
    server_version = "Caleb"

    def version_string(self) -> str:
        return self.server_version

    # ------------------------------------------------------------ utilidades
    @property
    def client_ip(self) -> str:
        if TRUST_PROXY:
            forwarded = self.headers.get("X-Forwarded-For", "")
            # La última IP la agrega nuestro propio proxy: es la única confiable.
            candidate = forwarded.split(",")[-1].strip()
            try:
                return str(ipaddress.ip_address(candidate))
            except ValueError:
                pass
        return self.client_address[0]

    def _send(self, status: int, body: bytes, content_type: str, extra: Optional[Dict[str, str]] = None,
              head_only: bool = False) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        for key, value in {**security_headers(), **cors_headers(self.headers.get("Origin")), **(extra or {})}.items():
            self.send_header(key, value)
        self.end_headers()
        if not head_only and self.command != "HEAD":
            self.wfile.write(body)

    def send_json(self, data: Any, status: int = 200, cache_control: str = "no-store",
                  _raw: Optional[Tuple[bytes, bytes]] = None) -> None:
        raw, gz = _raw if _raw else (json.dumps(data, ensure_ascii=False).encode("utf-8"), b"")
        extra = {"Cache-Control": cache_control, "Vary": "Accept-Encoding"}
        if len(raw) > 1024 and "gzip" in (self.headers.get("Accept-Encoding") or ""):
            raw = gz or gzip.compress(raw, compresslevel=6)
            extra["Content-Encoding"] = "gzip"
        self._send(status, raw, "application/json; charset=utf-8", extra)

    def read_json_body(self) -> Dict[str, Any]:
        if self.headers.get("Transfer-Encoding"):
            raise BadRequest("Envío fragmentado no permitido.", 411)
        length_header = self.headers.get("Content-Length", "0").strip()
        if not length_header.isdigit():
            raise BadRequest("Cabecera Content-Length inválida.")
        length = int(length_header)
        if length > MAX_CONTENT_LENGTH:
            raise BadRequest("El tamaño del contenido excede el límite permitido.", 413)
        if length == 0:
            return {}
        content_type = (self.headers.get("Content-Type") or "").split(";")[0].strip().lower()
        if content_type != "application/json":
            raise BadRequest("El contenido debe enviarse como JSON.", 415)
        raw = self.rfile.read(length)
        try:
            data = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, ValueError):
            raise BadRequest("Formato JSON inválido.") from None
        if not isinstance(data, dict):
            raise BadRequest("Se esperaba un objeto JSON.")
        return data

    # ------------------------------------------------------------ métodos HTTP
    def do_GET(self) -> None:
        self._dispatch("GET")

    def do_HEAD(self) -> None:
        self._dispatch("GET")

    def do_POST(self) -> None:
        self._dispatch("POST")

    def do_PUT(self) -> None:
        self._dispatch("PUT")

    def do_PATCH(self) -> None:
        self._dispatch("PATCH")

    def do_DELETE(self) -> None:
        self._dispatch("DELETE")

    def do_OPTIONS(self) -> None:
        self._send(204, b"", "text/plain", {"Allow": "GET, HEAD, POST, PUT, PATCH, DELETE, OPTIONS"})

    # ------------------------------------------------------------ despacho
    def _dispatch(self, method: str) -> None:
        parsed = urllib.parse.urlsplit(self.path)
        path = parsed.path.rstrip("/") or "/"
        try:
            if path == "/api" or path.startswith("/api/"):
                self._handle_api(method, path, parsed.query)
            elif method == "GET":
                self._serve_static(parsed.path)
            else:
                self.send_json({"success": False, "error": "Método no permitido."}, 405)
        except (ConnectionResetError, BrokenPipeError, TimeoutError):
            pass

    def _handle_api(self, method: str, path: str, query_string: str) -> None:
        route, params, allowed = router.match(method, path)
        if route is None:
            if allowed:
                self.send_json({"success": False, "error": "Método no permitido."}, 405)
            else:
                self.send_json({"success": False, "error": "Ruta no encontrada."}, 404)
            return

        ip = self.client_ip
        if not check_rate_limit(ip, RATE_LIMITS.get(route.limit, RATE_LIMIT_PER_MINUTE), bucket=route.limit):
            self.send_json({"success": False, "error": "Demasiadas peticiones. Espere un minuto e intente de nuevo."}, 429)
            return

        is_admin = validate_admin_token(self.headers.get("Authorization"))
        if route.admin and not is_admin:
            self.send_json({"success": False, "error": "Acceso no autorizado. Inicie sesión como administrador."}, 401)
            return

        try:
            body = self.read_json_body() if method in ("POST", "PUT", "PATCH") else {}
        except BadRequest as error:
            self.close_connection = True
            self.send_json({"success": False, "error": str(error)}, error.status)
            return

        if route.honeypot and (body.get("website_url") or body.get("bot_check")):
            # Bot atrapado: se le responde "éxito" sin guardar nada.
            self.send_json({"success": True, "status": "success", "message": "Recibido."}, 201)
            return

        query = dict(urllib.parse.parse_qsl(query_string, max_num_fields=20))
        req = Request(method=method, path=path, client_ip=ip, query=query, params=params,
                      body=body, is_admin=is_admin, headers=self.headers)

        if route.cache and method == "GET":
            key = path + "?" + urllib.parse.urlencode(sorted(query.items()))
            status, raw, gz = cache.get_or_build(key, lambda: self._run_raw(route, req))
            control = PUBLIC_CACHE_CONTROL if status == 200 else "no-store"
            self.send_json(None, status, control, _raw=(raw, gz))
            return

        data, status = self._run(route, req)
        if route.mutates and status < 400:
            cache.bump_data_version()
        self.send_json(data, status)

    def _run(self, route: Route, req: Request) -> Tuple[Dict[str, Any], int]:
        try:
            return route.handler(req)
        except ValidationError as error:
            return {"success": False, "error": str(error)}, 400
        except Exception:
            traceback.print_exc()
            return {"success": False, "error": "Ocurrió un error interno. Intente nuevamente."}, 500

    def _run_raw(self, route: Route, req: Request) -> Tuple[int, bytes]:
        data, status = self._run(route, req)
        return status, json.dumps(data, ensure_ascii=False).encode("utf-8")

    # ------------------------------------------------------------ archivos
    def _serve_static(self, raw_path: str) -> None:
        file = static.resolve(raw_path)
        if file is None:
            self._send(404, static.NOT_FOUND_HTML, "text/html; charset=utf-8", {"Cache-Control": "no-store"})
            return

        base = {"ETag": file.etag, "Cache-Control": file.cache_control, "Accept-Ranges": "bytes", "Vary": "Accept-Encoding"}
        if (self.headers.get("If-None-Match") or "").strip() == file.etag:
            self._send(304, b"", file.mime, base, head_only=True)
            return

        range_header = self.headers.get("Range")
        if range_header:
            part = static.read_range(file, range_header)
            if part is None:
                self._send(416, b"", "text/plain", {"Content-Range": f"bytes */{file.size}"})
                return
            start, end, chunk = part
            self._send(206, chunk, file.mime, {**base, "Content-Range": f"bytes {start}-{end}/{file.size}"})
            return

        content = static.read(file)
        if file.compressible and len(content) > 1024 and "gzip" in (self.headers.get("Accept-Encoding") or ""):
            content = static.read_gzip(file, content)
            base["Content-Encoding"] = "gzip"
        self._send(200, content, file.mime, base)

    def log_message(self, format: str, *args: Any) -> None:
        print(f"[{self.log_date_time_string()}] {self.client_ip} -> {format % args}")
