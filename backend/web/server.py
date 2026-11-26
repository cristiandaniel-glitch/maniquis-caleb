"""
Arranque del servidor web.

En Linux/macOS se crean varios procesos que comparten el mismo puerto (uno
por núcleo, máx. 8): el sistema reparte las visitas entre ellos. En Windows
se usa un solo proceso con muchos hilos.
"""

import os
import signal
import socketserver
import sys
import threading
import time
import http.server

from backend.config import HOST, MAX_THREADS, PORT, STATIC_DIR, WORKERS
from backend.core.auth import admin_login_configured
from backend.database import close_connection_pool, verify_database_schema
from backend.web.handler import SecureRequestHandler

import backend.routes  # noqa: F401  (registra todas las rutas de la API)


class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    """
    Servidor multihilo.
    - request_queue_size: "sala de espera" del sistema operativo para picos de visitas.
    - MAX_THREADS: tope de conexiones atendidas a la vez por proceso; las demás
      esperan en la cola en vez de agotar la memoria.
    """

    daemon_threads = True
    allow_reuse_address = True
    request_queue_size = 1024

    def __init__(self, *args, **kwargs):
        self._slots = threading.BoundedSemaphore(MAX_THREADS)
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
        if isinstance(sys.exc_info()[1], (ConnectionResetError, BrokenPipeError, TimeoutError, OSError)):
            return
        super().handle_error(request, client_address)


def _worker_count() -> int:
    if WORKERS.isdigit() and int(WORKERS) > 0:
        return int(WORKERS)
    return max(1, min(os.cpu_count() or 1, 8))


def _prepare_database() -> None:
    """Falla temprano si no hay conexión o falta el esquema. Cierra el pool antes de fork."""
    verify_database_schema()
    close_connection_pool()


def run_server() -> None:
    _prepare_database()
    httpd = ThreadedHTTPServer((HOST, PORT), SecureRequestHandler)
    workers = _worker_count() if hasattr(os, "fork") else 1

    print("=" * 65)
    print("🚀 SERVIDOR INICIADO: MANIQUÍES Y EXHIBIDORES CALEB")
    print(f"📡 URL Local: http://localhost:{PORT}")
    print(f"⚙️  Procesos: {workers}  ·  hasta {MAX_THREADS} conexiones simultáneas por proceso")
    print(f"📂 Raíz estática: {STATIC_DIR}")
    if admin_login_configured():
        print("🔐 Panel /admin: contraseña configurada")
    else:
        print("⚠️  Panel /admin BLOQUEADO: falta ADMIN_SALT / ADMIN_PASSWORD_HASH en .env")
        print("    Genéralos con: python scripts/generar_clave_admin.py")
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
        # Si un proceso muere por un error inesperado, se reemplaza solo.
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
