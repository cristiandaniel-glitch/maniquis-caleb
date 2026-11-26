"""
Archivos del frontend (HTML, CSS, JS, imágenes).

Seguridad: solo se entregan archivos que estén DENTRO de la carpeta frontend
y cuya extensión esté en una lista blanca. Así nunca se puede descargar
.env, código Python, la base de datos ni nada fuera de esa carpeta, aunque
la ruta venga codificada (%2e%2e, %5c, etc.).
"""

import gzip
import mimetypes
import os
import threading
import urllib.parse
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from backend.config import STATIC_DIR

mimetypes.add_type("image/webp", ".webp")
mimetypes.add_type("application/manifest+json", ".webmanifest")

STATIC_ROOT = os.path.realpath(STATIC_DIR)

ALLOWED_EXTENSIONS = {
    ".html", ".css", ".js", ".json", ".webmanifest", ".txt", ".xml",
    ".webp", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".avif",
    ".woff", ".woff2", ".mp4", ".webm",
}
LONG_CACHE = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif", ".mp4", ".webm", ".woff", ".woff2", ".svg", ".ico"}
COMPRESSIBLE = ("text/", "application/javascript", "application/json", "image/svg+xml", "application/manifest+json")

# Archivos en memoria, por (ruta, fecha de modificación). Los grandes (videos)
# se leen del disco en cada visita.
CACHE_MAX_FILE = 2 * 1024 * 1024
CACHE_MAX_TOTAL = 64 * 1024 * 1024
_FILES: Dict[str, Tuple[float, bytes]] = {}
_GZIP: Dict[Tuple[str, float], bytes] = {}
_TOTAL = [0]
_LOCK = threading.Lock()

NOT_FOUND_HTML = (
    "<!DOCTYPE html><html lang='es-PE'><head><meta charset='utf-8'>"
    "<meta name='viewport' content='width=device-width,initial-scale=1'>"
    "<title>Página no encontrada | Maniquíes y Exhibidores Caleb</title>"
    "<link rel='stylesheet' href='/css/site.css'></head>"
    "<body style='display:grid;place-items:center;min-height:100vh;text-align:center;padding:24px'>"
    "<main><h1 class='display-l'>Esta página no existe</h1>"
    "<p class='muted' style='margin:12px 0 24px'>Puede que el enlace esté mal escrito o que la página se haya movido.</p>"
    "<a class='btn btn-dark' href='/'>Volver al inicio</a></main></body></html>"
).encode("utf-8")


@dataclass
class StaticFile:
    path: str
    mime: str
    size: int
    mtime: float
    etag: str
    cache_control: str
    compressible: bool


def resolve(raw_path: str) -> Optional[StaticFile]:
    """Convierte la ruta pedida en un archivo seguro del frontend, o None."""
    path = urllib.parse.unquote(raw_path or "/")
    if "\x00" in path or "\\" in path:
        return None
    # Ningún segmento oculto (.git, .env) ni saltos hacia arriba (..)
    if any(part.startswith(".") for part in path.split("/") if part):
        return None
    relative = path.lstrip("/") or "index.html"
    target = os.path.realpath(os.path.join(STATIC_ROOT, relative))
    if os.path.commonpath([STATIC_ROOT, target]) != STATIC_ROOT:
        return None
    # Direcciones sin extensión: /admin → admin.html, /catalogo → catalogo.html
    if not os.path.splitext(target)[1] and os.path.isfile(target + ".html"):
        target += ".html"
    if os.path.isdir(target) and os.path.isfile(os.path.join(target, "index.html")):
        target = os.path.join(target, "index.html")
    ext = os.path.splitext(target)[1].lower()
    if ext not in ALLOWED_EXTENSIONS or not os.path.isfile(target):
        return None
    stat = os.stat(target)
    mime = mimetypes.guess_type(target)[0] or "application/octet-stream"
    if mime.startswith("text/") or mime in ("application/javascript", "application/json"):
        mime += "; charset=utf-8"
    return StaticFile(
        path=target,
        mime=mime,
        size=stat.st_size,
        mtime=stat.st_mtime,
        etag=f'"{int(stat.st_mtime)}-{stat.st_size}"',
        # Imágenes: 1 día y revalidación en segundo plano. HTML/CSS/JS: siempre
        # se revalidan con el ETag (304 si no cambió), así los cambios se ven al instante.
        cache_control="public, max-age=86400, stale-while-revalidate=604800" if ext in LONG_CACHE else "no-cache",
        compressible=mime.startswith(COMPRESSIBLE),
    )


def read(file: StaticFile) -> bytes:
    with _LOCK:
        hit = _FILES.get(file.path)
    if hit and hit[0] == file.mtime:
        return hit[1]
    with open(file.path, "rb") as handle:
        data = handle.read()
    if len(data) <= CACHE_MAX_FILE:
        with _LOCK:
            if _TOTAL[0] + len(data) > CACHE_MAX_TOTAL:
                _FILES.clear()
                _TOTAL[0] = 0
            old = _FILES.get(file.path)
            if old:
                _TOTAL[0] -= len(old[1])
            _FILES[file.path] = (file.mtime, data)
            _TOTAL[0] += len(data)
    return data


def read_gzip(file: StaticFile, raw: bytes) -> bytes:
    key = (file.path, file.mtime)
    with _LOCK:
        hit = _GZIP.get(key)
    if hit is None:
        hit = gzip.compress(raw, compresslevel=6)
        with _LOCK:
            if len(_GZIP) > 200:
                _GZIP.clear()
            _GZIP[key] = hit
    return hit


def read_range(file: StaticFile, header: str) -> Optional[Tuple[int, int, bytes]]:
    """Interpreta 'Range: bytes=inicio-fin'. None si el rango no es válido (→ 416)."""
    spec = header[6:].split(",")[0].strip() if header.startswith("bytes=") else ""
    start_s, sep, end_s = spec.partition("-")
    if not sep or not (start_s.isdigit() or end_s.isdigit()):
        return None
    if start_s.isdigit():
        start = int(start_s)
        end = int(end_s) if end_s.isdigit() else file.size - 1
    else:  # sufijo: últimos N bytes
        start = max(file.size - int(end_s), 0)
        end = file.size - 1
    end = min(end, file.size - 1)
    if start > end or start >= file.size:
        return None
    with open(file.path, "rb") as handle:
        handle.seek(start)
        return start, end, handle.read(end - start + 1)
