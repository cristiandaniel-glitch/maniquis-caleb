"""
Servidor HTTP y Enrutador REST API para Maniquí Studio.
Implementación segura, rápida y modular basada en la biblioteca estándar de Python.
Incluye autenticación administrativa, protección contra ataques y filtros de archivos sensibles.
"""

import gzip
import http.server
import json
import mimetypes
import os
import signal
import socketserver
import sys
import threading
import time
import urllib.parse
from typing import Any, Dict, Optional, Tuple

from backend.config import (
    CORS_ALLOWED_ORIGINS,
    HOST,
    MAX_CONTENT_LENGTH,
    PORT,
    RATE_LIMIT_PER_MINUTE,
    STATIC_DIR,
)
from backend.routes.auth import handle_admin_login, handle_verify_admin_session
from backend.routes.categories import handle_get_categories, handle_get_category_detail
from backend.routes.claims import handle_create_claim, handle_get_claim_detail
from backend.routes.legal import handle_get_legal_info
from backend.routes.messages import handle_get_messages, handle_send_message
from backend.routes.newsletter import handle_get_subscribers, handle_subscribe
from backend.routes.products import (
    handle_create_product,
    handle_delete_product,
    handle_get_product_detail,
    handle_get_products,
    handle_update_product,
)
from backend.routes.reviews import handle_create_review, handle_get_reviews
from backend.routes.stats import handle_get_stats
from backend.security import (
    FORBIDDEN_EXTENSIONS,
    check_rate_limit,
    ensure_login_attempts_table,
    get_security_headers,
    is_forbidden_path,
    validate_admin_token,
)
from backend.config import DB_PATH


mimetypes.add_type("image/webp", ".webp")


# Compresión gzip para texto (HTML, CSS, JS, JSON, SVG). Los estáticos
# comprimidos se guardan en memoria por (ruta, fecha de modificación) para no
# recomprimir en cada visita; las imágenes WebP/JPG ya vienen comprimidas.
COMPRESSIBLE = ("text/", "application/javascript", "application/json", "image/svg+xml")
_GZIP_CACHE: Dict[Tuple[str, float], bytes] = {}
_GZIP_LOCK = threading.Lock()


# Archivos estáticos en memoria: evita leer el disco en cada visita. Se guarda
# por (ruta, fecha de modificación): si el archivo cambia se vuelve a leer.
# Los archivos grandes (videos) se siguen leyendo del disco.
STATIC_CACHE_MAX_FILE = 2 * 1024 * 1024
STATIC_CACHE_MAX_TOTAL = 64 * 1024 * 1024
_STATIC_CACHE: Dict[str, Tuple[float, bytes]] = {}
_STATIC_CACHE_SIZE = [0]


def _read_static(path: str, mtime: float, size: int) -> bytes:
    hit = _STATIC_CACHE.get(path)
    if hit and hit[0] == mtime:
        return hit[1]
    with open(path, "rb") as f:
        data = f.read()
    if size <= STATIC_CACHE_MAX_FILE:
        with _GZIP_LOCK:
            if _STATIC_CACHE_SIZE[0] + size > STATIC_CACHE_MAX_TOTAL:
                _STATIC_CACHE.clear()
                _STATIC_CACHE_SIZE[0] = 0
            old = _STATIC_CACHE.get(path)
            if old:
                _STATIC_CACHE_SIZE[0] -= len(old[1])
            _STATIC_CACHE[path] = (mtime, data)
            _STATIC_CACHE_SIZE[0] += len(data)
    return data


# Respuestas públicas de la API (productos, categorías, reseñas, datos legales)
# guardadas unos segundos. Cualquier cambio (POST/PUT/DELETE) toca el archivo
# "marca de versión" y todos los procesos descartan su caché al instante.
API_CACHE_TTL = 30.0
_API_CACHE: Dict[str, Tuple[float, float, int, bytes, bytes]] = {}
_API_CACHE_LOCK = threading.Lock()
_VERSION_FILE = os.path.join(os.path.dirname(os.path.abspath(DB_PATH)), ".api-cache-version")


def _data_version() -> float:
    try:
        return os.stat(_VERSION_FILE).st_mtime
    except OSError:
        return 0.0


def bump_data_version() -> None:
    """Marca que los datos cambiaron: invalida la caché de la API en todos los procesos."""
    try:
        with open(_VERSION_FILE, "a"):
            pass
        now = time.time()
        os.utime(_VERSION_FILE, (now, max(now, _data_version() + 0.001)))
    except OSError:
        pass
    with _API_CACHE_LOCK:
        _API_CACHE.clear()


def _gzip_static(path: str, mtime: float, raw: bytes) -> bytes:
    key = (path, mtime)
    with _GZIP_LOCK:
        hit = _GZIP_CACHE.get(key)
    if hit is None:
        hit = gzip.compress(raw, compresslevel=6)
        with _GZIP_LOCK:
            if len(_GZIP_CACHE) > 200:
                _GZIP_CACHE.clear()
            _GZIP_CACHE[key] = hit
    return hit


class SecureRequestHandler(http.server.BaseHTTPRequestHandler):
    """Manejador HTTP con soporte para CORS, cabeceras de seguridad y API REST."""

    protocol_version = "HTTP/1.1"
    # Conexiones lentas o abandonadas se cierran a los 10 s (evita que ocupen hilos)
    timeout = 10

    def send_security_headers(self) -> None:
        """Aplica todas las cabeceras HTTP de seguridad."""
        headers = get_security_headers()
        for key, value in headers.items():
            self.send_header(key, value)

    def send_cors_headers(self) -> None:
        """Aplica las cabeceras CORS."""
        origin = self.headers.get("Origin", "*")
        if "*" in CORS_ALLOWED_ORIGINS or origin in CORS_ALLOWED_ORIGINS:
            self.send_header("Access-Control-Allow-Origin", origin)
        else:
            self.send_header("Access-Control-Allow-Origin", CORS_ALLOWED_ORIGINS[0])

        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS, HEAD")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With")
        self.send_header("Access-Control-Max-Age", "86400")

    # Datos públicos que cambian poco: el navegador puede reutilizarlos 60 s,
    # lo que evita repetir la misma consulta en cada página.
    PUBLIC_CACHEABLE = ("/api/products", "/api/categories", "/api/reviews", "/api/legal")

    def accepts_gzip(self) -> bool:
        return "gzip" in (self.headers.get("Accept-Encoding") or "")

    def send_json_response(self, data: Any, status_code: int = 200, _cached: Optional[Tuple[bytes, bytes]] = None) -> None:
        """Envía una respuesta JSON formateada de forma segura."""
        path = urllib.parse.urlparse(self.path).path.rstrip("/")
        if _cached is not None:
            raw, gz = _cached
        else:
            raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
            gz = b""
        if self.command == "GET" and status_code == 200 and path in self.PUBLIC_CACHEABLE:
            cache_control = "public, max-age=60, stale-while-revalidate=300"
        else:
            cache_control = "no-store"
        use_gzip = len(raw) > 1024 and self.accepts_gzip()
        if use_gzip:
            response_bytes = gz or gzip.compress(raw, compresslevel=6)
        else:
            response_bytes = raw
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        if use_gzip:
            self.send_header("Content-Encoding", "gzip")
        self.send_header("Vary", "Accept-Encoding")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.send_header("Cache-Control", cache_control)
        self.send_cors_headers()
        self.send_security_headers()
        self.end_headers()
        self.wfile.write(response_bytes)

    def parse_body_json(self) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Lee y decodifica el cuerpo de la petición como JSON con límite de tamaño."""
        content_length_str = self.headers.get("Content-Length")
        if not content_length_str:
            return None, "Cuerpo de solicitud vacío"

        try:
            length = int(content_length_str)
            if length > MAX_CONTENT_LENGTH:
                return None, "El tamaño del contenido excede el límite permitido."
            raw_body = self.rfile.read(length)
            data = json.loads(raw_body.decode("utf-8"))
            return data, None
        except ValueError:
            return None, "Formato JSON inválido"
        except Exception as e:
            return None, f"Error al procesar los datos: {str(e)}"

    def get_auth_token(self) -> Optional[str]:
        """Extrae el token de autorización de la cabecera Authorization."""
        return self.headers.get("Authorization")

    def is_authenticated_admin(self) -> bool:
        """Verifica si la petición actual cuenta con un token de administrador válido."""
        token = self.get_auth_token()
        return validate_admin_token(token)

    def do_OPTIONS(self) -> None:
        """Maneja peticiones preflight CORS."""
        self.send_response(204)
        self.send_cors_headers()
        self.send_security_headers()
        self.end_headers()

    def do_HEAD(self) -> None:
        """Maneja peticiones HEAD respondiendo con las cabeceras correspondientes."""
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/")
        if not path:
            path = "/"

        if is_forbidden_path(path):
            self.send_response(403)
            self.send_security_headers()
            self.end_headers()
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_cors_headers()
        self.send_security_headers()
        self.end_headers()

    def send_cached_api(self, key: str, producer) -> None:
        """Responde una ruta pública de la API desde la caché (o la genera y guarda)."""
        version = _data_version()
        now = time.time()
        with _API_CACHE_LOCK:
            hit = _API_CACHE.get(key)
        if hit and hit[1] == version and now - hit[0] < API_CACHE_TTL:
            self.send_json_response(None, hit[2], _cached=(hit[3], hit[4]))
            return
        data, code = producer()
        raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
        gz = gzip.compress(raw, compresslevel=6) if len(raw) > 1024 else b""
        if code == 200:
            with _API_CACHE_LOCK:
                if len(_API_CACHE) > 256:
                    _API_CACHE.clear()
                _API_CACHE[key] = (now, version, code, raw, gz)
        self.send_json_response(None, code, _cached=(raw, gz))

    def do_GET(self) -> None:
        """Maneja peticiones GET tanto de la API como de archivos estáticos."""
        client_ip = self.client_address[0]
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/")
        if not path:
            path = "/"
        query_params = dict(urllib.parse.parse_qsl(parsed.query))

        # Páginas, imágenes, CSS y JS se sirven sin límite por IP: son baratos
        # (vienen de memoria) y muchos clientes pueden compartir una IP pública
        # (redes móviles, galerías con Wi-Fi). El límite se aplica a la API.
        if not path.startswith("/api/"):
            self.serve_static_file(parsed.path)
            return
        if not check_rate_limit(client_ip, max_requests=RATE_LIMIT_PER_MINUTE, bucket="api"):
            self.send_json_response({"success": False, "error": "Límite de peticiones excedido (Rate Limit). Espere un momento."}, 429)
            return

        # --- Rutas Públicas de la API REST ---
        if path == "/api/health":
            self.send_json_response({"status": "healthy", "service": "Maniquí Studio API", "version": "1.0.0"})
            return

        if path == "/api/products":
            self.send_cached_api("products?" + parsed.query, lambda: (handle_get_products(query_params), 200))
            return

        if path.startswith("/api/products/"):
            param = path[len("/api/products/"):]
            res = handle_get_product_detail(param)
            if isinstance(res, tuple):
                self.send_json_response(res[0], res[1])
            else:
                self.send_json_response(res)
            return

        if path == "/api/categories":
            self.send_cached_api("categories", lambda: (handle_get_categories(), 200))
            return

        if path.startswith("/api/categories/"):
            cat_id_str = path[len("/api/categories/"):]
            if cat_id_str.isdigit():
                res = handle_get_category_detail(int(cat_id_str))
                if isinstance(res, tuple):
                    self.send_json_response(res[0], res[1])
                else:
                    self.send_json_response(res)
                return

        if path == "/api/legal":
            self.send_cached_api("legal", lambda: (handle_get_legal_info(), 200))
            return

        # Consultar estado de una reclamación específica (público)
        if path.startswith("/api/claims/") and not path.endswith("/all"):
            claim_code = path[len("/api/claims/"):]
            res = handle_get_claim_detail(claim_code, is_admin=self.is_authenticated_admin())
            if isinstance(res, tuple):
                self.send_json_response(res[0], res[1])
            else:
                self.send_json_response(res)
            return

        # --- Rutas Administrativas Protegidas (Requieren Token) ---
        if path == "/api/admin/verify":
            res = handle_verify_admin_session(self.get_auth_token())
            if isinstance(res, tuple):
                self.send_json_response(res[0], res[1])
            else:
                self.send_json_response(res)
            return

        if path == "/api/claims/all":
            if not self.is_authenticated_admin():
                self.send_json_response({"success": False, "error": "Acceso no autorizado. Inicie sesión como administrador."}, 401)
                return
            res = handle_get_claim_detail("all")
            if isinstance(res, tuple):
                self.send_json_response(res[0], res[1])
            else:
                self.send_json_response(res)
            return

        if path == "/api/messages":
            if not self.is_authenticated_admin():
                self.send_json_response({"success": False, "error": "Acceso no autorizado. Inicie sesión como administrador."}, 401)
                return
            res = handle_get_messages()
            self.send_json_response(res)
            return

        if path == "/api/subscribers":
            if not self.is_authenticated_admin():
                self.send_json_response({"success": False, "error": "Acceso no autorizado. Inicie sesión como administrador."}, 401)
                return
            res = handle_get_subscribers()
            self.send_json_response(res)
            return

        if path == "/api/stats":
            if not self.is_authenticated_admin():
                self.send_json_response({"success": False, "error": "Acceso no autorizado. Inicie sesión como administrador."}, 401)
                return
            res = handle_get_stats()
            self.send_json_response(res)
            return

        if path == "/api/reviews":
            self.send_cached_api("reviews", lambda: tuple(reversed(handle_get_reviews())))
            return

        self.send_json_response({"success": False, "error": "Ruta no encontrada"}, 404)

    def do_POST(self) -> None:
        """Maneja peticiones POST."""
        client_ip = self.client_address[0]
        # Formularios (reseñas, reclamos, contacto, login): 30 por minuto por IP
        if not check_rate_limit(client_ip, max_requests=30, bucket="post"):
            self.send_json_response({"success": False, "error": "Demasiadas peticiones. Espere un minuto e intente de nuevo."}, 429)
            return
        try:
            self._do_post(client_ip)
        finally:
            if urllib.parse.urlparse(self.path).path.rstrip("/") in ("/api/reviews", "/api/products"):
                bump_data_version()

    def _do_post(self, client_ip: str) -> None:

        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/")

        body_data, err = self.parse_body_json()
        if err:
            self.send_json_response({"success": False, "error": err}, 400)
            return

        # Login Administrativo
        if path == "/api/admin/login":
            res = handle_admin_login(body_data, client_ip)
            if isinstance(res, tuple):
                self.send_json_response(res[0], res[1])
            else:
                self.send_json_response(res)
            return

        # Reclamaciones (Público con trampa Honeypot anti-spam)
        if path == "/api/claims":
            # Trampa Honeypot para bots
            if body_data.get("website_url") or body_data.get("bot_check"):
                self.send_json_response({"success": True, "message": "Procesado correctamente."})
                return
            res = handle_create_claim(body_data)
            if isinstance(res, tuple):
                self.send_json_response(res[0], res[1])
            else:
                self.send_json_response(res)
            return

        # Contacto (Público con trampa Honeypot)
        if path == "/api/contact":
            if body_data.get("website_url") or body_data.get("bot_check"):
                self.send_json_response({"success": True, "message": "Mensaje enviado."})
                return
            res = handle_send_message(body_data, client_ip=client_ip)
            if isinstance(res, tuple):
                self.send_json_response(res[0], res[1])
            else:
                self.send_json_response(res)
            return

        # Newsletter (Público)
        if path == "/api/subscribe":
            res = handle_subscribe(body_data)
            if isinstance(res, tuple):
                self.send_json_response(res[0], res[1])
            else:
                self.send_json_response(res)
            return

        # Reseñas de Clientes (Público con trampa Honeypot)
        if path == "/api/reviews":
            if body_data.get("website_url") or body_data.get("bot_check"):
                self.send_json_response({"status": "success", "message": "Reseña registrada."})
                return
            code, res = handle_create_review(body_data)
            self.send_json_response(res, code)
            return

        # Crear Producto (Ruta Protegida Admin)
        if path == "/api/products":
            if not self.is_authenticated_admin():
                self.send_json_response({"success": False, "error": "Acceso denegado. Se requiere autenticación de administrador para crear productos."}, 401)
                return
            res = handle_create_product(body_data)
            if isinstance(res, tuple):
                self.send_json_response(res[0], res[1])
            else:
                self.send_json_response(res)
            return

        self.send_json_response({"success": False, "error": "Ruta no encontrada"}, 404)

    def do_PUT(self) -> None:
        """Maneja peticiones PUT protegidas."""
        try:
            self._do_put()
        finally:
            bump_data_version()

    def _do_put(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path.startswith("/api/products/"):
            if not self.is_authenticated_admin():
                self.send_json_response({"success": False, "error": "Acceso denegado. Se requiere autenticación de administrador."}, 401)
                return

            prod_id_str = path[len("/api/products/"):]
            if prod_id_str.isdigit():
                body_data, err = self.parse_body_json()
                if err:
                    self.send_json_response({"success": False, "error": err}, 400)
                    return
                res = handle_update_product(int(prod_id_str), body_data)
                if isinstance(res, tuple):
                    self.send_json_response(res[0], res[1])
                else:
                    self.send_json_response(res)
                return

        self.send_json_response({"success": False, "error": "Ruta no encontrada"}, 404)

    def do_DELETE(self) -> None:
        """Maneja peticiones DELETE protegidas."""
        try:
            self._do_delete()
        finally:
            bump_data_version()

    def _do_delete(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path.startswith("/api/products/"):
            if not self.is_authenticated_admin():
                self.send_json_response({"success": False, "error": "Acceso denegado. Se requiere autenticación de administrador."}, 401)
                return

            prod_id_str = path[len("/api/products/"):]
            if prod_id_str.isdigit():
                res = handle_delete_product(int(prod_id_str))
                self.send_json_response(res)
                return

        self.send_json_response({"success": False, "error": "Ruta no encontrada"}, 404)

    def serve_static_file(self, raw_path: str) -> None:
        """Sirve archivos estáticos desde la carpeta frontend bloqueando archivos sensibles."""
        if is_forbidden_path(raw_path):
            self.send_response(403)
            self.send_security_headers()
            self.end_headers()
            self.wfile.write(b"403 Acceso Denegado (Archivo Protegido)")
            return

        clean_path = raw_path.lstrip("/")
        if not clean_path or clean_path == "/":
            clean_path = "index.html"

        # Prevenir Path Traversal
        target_path = os.path.abspath(os.path.join(STATIC_DIR, clean_path))
        if not target_path.startswith(os.path.abspath(STATIC_DIR)):
            self.send_response(403)
            self.send_security_headers()
            self.end_headers()
            self.wfile.write(b"403 Acceso Denegado")
            return

        if not os.path.exists(target_path) or os.path.isdir(target_path):
            fallback = os.path.join(STATIC_DIR, "index.html")
            if os.path.exists(fallback):
                target_path = fallback
            else:
                self.send_response(404)
                self.send_security_headers()
                self.end_headers()
                self.wfile.write(b"404 No Encontrado")
                return

        # Doble verificación contra extensiones no autorizadas
        _, ext = os.path.splitext(target_path)
        if ext.lower() in FORBIDDEN_EXTENSIONS:
            self.send_response(403)
            self.send_security_headers()
            self.end_headers()
            self.wfile.write(b"403 Archivo no accesible")
            return

        mime_type, _ = mimetypes.guess_type(target_path)
        if not mime_type:
            mime_type = "application/octet-stream"

        try:
            stat_info = os.stat(target_path)
            file_size = stat_info.st_size
            etag = f'"{int(stat_info.st_mtime)}-{file_size}"'

            # Validación condicional 304 Not Modified
            if_none_match = self.headers.get("If-None-Match")
            if if_none_match and if_none_match.strip() == etag:
                self.send_response(304)
                self.send_header("ETag", etag)
                self.send_cors_headers()
                self.send_security_headers()
                self.end_headers()
                return

            # Política de Caché Inteligente de Alto Rendimiento
            # Imágenes y videos: se reutilizan un día y luego se revalidan en segundo
            # plano. CSS, JS y HTML: siempre se revalidan con el ETag (responde 304
            # sin reenviar el archivo si no cambió), así los cambios se ven al instante.
            if ext.lower() in [".jpg", ".jpeg", ".png", ".webp", ".gif", ".mp4", ".woff", ".woff2", ".svg"]:
                cache_control = "public, max-age=86400, stale-while-revalidate=604800"
            else:
                cache_control = "no-cache"

            range_header = self.headers.get("Range")

            if range_header and range_header.startswith("bytes="):
                range_spec = range_header[6:]
                parts = range_spec.split("-")
                start = int(parts[0]) if parts[0] else 0
                end = int(parts[1]) if len(parts) > 1 and parts[1] else file_size - 1
                if start >= file_size or end >= file_size or start > end:
                    self.send_response(416)
                    self.send_header("Content-Range", f"bytes */{file_size}")
                    self.end_headers()
                    return

                length = end - start + 1
                with open(target_path, "rb") as f:
                    f.seek(start)
                    chunk = f.read(length)

                self.send_response(206)
                self.send_header("Content-Type", mime_type)
                self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
                self.send_header("Content-Length", str(length))
                self.send_header("Accept-Ranges", "bytes")
                self.send_header("ETag", etag)
                self.send_header("Cache-Control", cache_control)
                self.send_cors_headers()
                self.send_security_headers()
                self.end_headers()
                self.wfile.write(chunk)
            else:
                content = _read_static(target_path, stat_info.st_mtime, file_size)

                use_gzip = mime_type.startswith(COMPRESSIBLE) and len(content) > 1024 and self.accepts_gzip()
                if use_gzip:
                    content = _gzip_static(target_path, stat_info.st_mtime, content)

                self.send_response(200)
                self.send_header("Content-Type", mime_type)
                if use_gzip:
                    self.send_header("Content-Encoding", "gzip")
                self.send_header("Vary", "Accept-Encoding")
                self.send_header("Content-Length", str(len(content)))
                self.send_header("Accept-Ranges", "bytes")
                self.send_header("ETag", etag)
                self.send_header("Cache-Control", cache_control)
                self.send_cors_headers()
                self.send_security_headers()
                self.end_headers()
                self.wfile.write(content)
        except (ConnectionResetError, BrokenPipeError):
            pass
        except Exception as e:
            try:
                self.send_response(500)
                self.send_security_headers()
                self.end_headers()
                self.wfile.write(f"Error al leer archivo: {str(e)}".encode("utf-8"))
            except Exception:
                pass

    def log_message(self, format: str, *args: Any) -> None:
        """Personaliza el formato de logs en consola."""
        print(f"[{self.log_date_time_string()}] {self.address_string()} -> {format % args}")


class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    """
    Servidor HTTP multihilo para atender peticiones concurrentes.

    - request_queue_size: "sala de espera" del sistema operativo. Con el valor
      por defecto (5) las visitas simultáneas eran rechazadas y el navegador
      reintentaba tras 1 s, 3 s...
    - MAX_THREADS: tope de conexiones atendidas a la vez por proceso; las
      demás esperan en la cola en vez de agotar la memoria.
    """
    daemon_threads = True
    allow_reuse_address = True
    request_queue_size = 1024
    MAX_THREADS = int(os.environ.get("MAX_THREADS", 256))

    def __init__(self, *args, **kwargs):
        self._slots = threading.BoundedSemaphore(self.MAX_THREADS)
        super().__init__(*args, **kwargs)

    def process_request(self, request, client_address):
        self._slots.acquire()
        try:
            super().process_request(request, client_address)
        except Exception:
            self._slots.release()
            raise

    def process_request_thread(self, request, client_address):
        try:
            super().process_request_thread(request, client_address)
        finally:
            self._slots.release()

    def handle_error(self, request, client_address):
        # Clientes que cortan la conexión a mitad (muy común en celulares) no
        # son errores del servidor: no llenar la consola con trazas.
        exc = sys.exc_info()[1]
        if isinstance(exc, (ConnectionResetError, BrokenPipeError, TimeoutError, OSError)):
            return
        super().handle_error(request, client_address)


def _worker_count() -> int:
    """Procesos de trabajo: uno por núcleo (máx. 8). WORKERS=1 para un solo proceso."""
    env = os.environ.get("WORKERS")
    if env and env.isdigit() and int(env) > 0:
        return int(env)
    return max(1, min(os.cpu_count() or 1, 8))


def _prepare_database() -> None:
    """Tareas de base de datos que antes se repetían en cada visita."""
    from backend.routes.reviews import ensure_reviews_table
    try:
        ensure_reviews_table()
        ensure_login_attempts_table()
    except Exception as e:  # la web sigue funcionando aunque falle
        print(f"[!] Aviso al preparar la base de datos: {e}")


def run_server() -> None:
    """
    Inicia el servidor web.

    En Linux/macOS se crean varios procesos que comparten el mismo puerto
    (uno por núcleo): el sistema reparte las visitas entre ellos, así el sitio
    aprovecha todo el procesador. En Windows se usa un solo proceso.
    """
    _prepare_database()
    server_address = (HOST, PORT)
    httpd = ThreadedHTTPServer(server_address, SecureRequestHandler)
    workers = _worker_count() if hasattr(os, "fork") else 1

    print("=" * 65)
    print(f"🚀 SERVIDOR INICIADO: MANIQUÍ STUDIO")
    print(f"📡 URL Local: http://localhost:{PORT}")
    print(f"⚙️  Procesos: {workers}  ·  hasta {ThreadedHTTPServer.MAX_THREADS} conexiones simultáneas por proceso")
    print(f"🛡️  Seguridad: Autenticación PBKDF2, Tokens y Bloqueo Anti-Ataques ACTIVOS")
    print(f"⚖️  Libro de Reclamaciones: /api/claims y formulario integrado")
    print(f"📂 Raíz estática: {STATIC_DIR}")
    print("=" * 65)

    if workers == 1:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[*] Deteniendo servidor de forma segura...")
        finally:
            httpd.server_close()
            print("[✔] Servidor detenido.")
        return

    children = []

    def spawn() -> int:
        pid = os.fork()
        if pid == 0:  # proceso hijo: atiende visitas hasta que lo detengan
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            signal.signal(signal.SIGTERM, lambda *_: os._exit(0))
            try:
                httpd.serve_forever()
            finally:
                os._exit(0)
        return pid

    for _ in range(workers):
        children.append(spawn())

    stopping = [False]

    def stop(*_):
        stopping[0] = True

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    try:
        # Si un proceso muere por un error inesperado, se reemplaza solo
        while not stopping[0]:
            try:
                pid, _status = os.waitpid(-1, os.WNOHANG)
            except ChildProcessError:
                pid = 0
            if pid and pid in children and not stopping[0]:
                children.remove(pid)
                children.append(spawn())
                print(f"[!] Un proceso del servidor se reinició automáticamente (pid {pid}).")
            time.sleep(0.5)
    finally:
        print("\n[*] Deteniendo servidor de forma segura...")
        for pid in children:
            try:
                os.kill(pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
        for pid in children:
            try:
                os.waitpid(pid, 0)
            except ChildProcessError:
                pass
        httpd.server_close()
        print("[✔] Servidor detenido.")


if __name__ == "__main__":
    run_server()
