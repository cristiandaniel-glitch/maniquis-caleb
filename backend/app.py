"""
Servidor HTTP y Enrutador REST API para Maniquí Studio.
Implementación segura, rápida y modular basada en la biblioteca estándar de Python.
Incluye autenticación administrativa, protección contra ataques y filtros de archivos sensibles.
"""

import http.server
import json
import mimetypes
import os
import socketserver
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
    get_security_headers,
    is_forbidden_path,
    validate_admin_token,
)


class SecureRequestHandler(http.server.BaseHTTPRequestHandler):
    """Manejador HTTP con soporte para CORS, cabeceras de seguridad y API REST."""

    protocol_version = "HTTP/1.1"

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

    def send_json_response(self, data: Any, status_code: int = 200) -> None:
        """Envía una respuesta JSON formateada de forma segura."""
        response_bytes = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_bytes)))
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

    def do_GET(self) -> None:
        """Maneja peticiones GET tanto de la API como de archivos estáticos."""
        client_ip = self.client_address[0]
        if not check_rate_limit(client_ip, max_requests=RATE_LIMIT_PER_MINUTE):
            self.send_json_response({"success": False, "error": "Límite de peticiones excedido (Rate Limit). Espere un momento."}, 429)
            return

        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/")
        if not path:
            path = "/"
        query_params = dict(urllib.parse.parse_qsl(parsed.query))

        # --- Rutas Públicas de la API REST ---
        if path == "/api/health":
            self.send_json_response({"status": "healthy", "service": "Maniquí Studio API", "version": "1.0.0"})
            return

        if path == "/api/products":
            res = handle_get_products(query_params)
            self.send_json_response(res)
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
            res = handle_get_categories()
            self.send_json_response(res)
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
            res = handle_get_legal_info()
            self.send_json_response(res)
            return

        # Consultar estado de una reclamación específica (público)
        if path.startswith("/api/claims/") and not path.endswith("/all"):
            claim_code = path[len("/api/claims/"):]
            res = handle_get_claim_detail(claim_code)
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
            code, res = handle_get_reviews()
            self.send_json_response(res, code)
            return

        # Servir archivo estático seguro
        self.serve_static_file(parsed.path)

    def do_POST(self) -> None:
        """Maneja peticiones POST."""
        client_ip = self.client_address[0]
        if not check_rate_limit(client_ip, max_requests=RATE_LIMIT_PER_MINUTE):
            self.send_json_response({"success": False, "error": "Demasiadas peticiones."}, 429)
            return

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
            if ext.lower() in [".jpg", ".jpeg", ".png", ".webp", ".gif", ".mp4", ".woff", ".woff2", ".svg"]:
                cache_control = "public, max-age=31536000, immutable"
            elif ext.lower() in [".css", ".js"]:
                cache_control = "public, max-age=86400, stale-while-revalidate=604800"
            else:
                cache_control = "no-cache, must-revalidate"

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
                with open(target_path, "rb") as f:
                    content = f.read()

                self.send_response(200)
                self.send_header("Content-Type", mime_type)
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
    """Servidor HTTP multihilo para atender peticiones concurrentes."""
    daemon_threads = True
    allow_reuse_address = True


def run_server() -> None:
    """Inicia el servidor web."""
    server_address = (HOST, PORT)
    httpd = ThreadedHTTPServer(server_address, SecureRequestHandler)
    print("=" * 65)
    print(f"🚀 SERVIDOR INICIADO: MANIQUÍ STUDIO")
    print(f"📡 URL Local: http://localhost:{PORT}")
    print(f"🛡️  Seguridad: Autenticación PBKDF2, Tokens y Bloqueo Anti-Ataques ACTIVOS")
    print(f"⚖️  Libro de Reclamaciones: /api/claims y formulario integrado")
    print(f"📂 Raíz estática: {STATIC_DIR}")
    print("=" * 65)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Deteniendo servidor de forma segura...")
        httpd.shutdown()
        httpd.server_close()
        print("[✔] Servidor detenido.")


if __name__ == "__main__":
    run_server()
