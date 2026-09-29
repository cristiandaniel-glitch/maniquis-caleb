"""
Módulo de Seguridad Integral Avanzado para Maniquí Studio.
Incluye:
- Hashing criptográfico seguro con PBKDF2 + SHA-256 y Salt (estándar OWASP)
- Generación y validación de tokens de sesión administrativa seguros (secrets)
- Protección anti-fuerza bruta (bloqueo tras intentos fallidos)
- Sanitización estricta contra XSS y validación de inyecciones
- Cabeceras HTTP de seguridad (CSP, HSTS, X-Frame-Options, etc.)
- Rate Limiter por ventana deslizante
- Filtro de extensiones y archivos sensibles prohibidos
"""

import hashlib
import hmac
import html
import os
import re
import secrets
import threading
import time
from typing import Any, Dict, List, Optional, Set, Tuple

# Extensiones y patrones de archivos prohibidos en el servidor estático
FORBIDDEN_EXTENSIONS: Set[str] = {
    ".db", ".sqlite", ".sqlite3", ".env", ".sql", ".py", ".pyc",
    ".sh", ".bash", ".log", ".git", ".gitignore", ".yml", ".yaml", ".ini", ".conf"
}

# Secreto para firmar las sesiones de administrador. Se genera al arrancar,
# antes de crear los procesos de trabajo, así todos lo comparten. Si se define
# SESSION_SECRET en el entorno, las sesiones sobreviven a los reinicios.
SESSION_SECRET = (os.environ.get("SESSION_SECRET") or secrets.token_hex(32)).encode()

# Rate limiter por ventana fija: { ip: [inicio_ventana, conteo] }. Es por
# proceso (aproximado con varios procesos) y se limpia solo para no crecer.
_RATE_LIMIT_STORAGE: Dict[Tuple[str, str], List[float]] = {}
_RATE_LOCK = threading.Lock()
_RATE_LAST_PRUNE = [0.0]

# Duración del token de sesión (4 horas)
TOKEN_LIFETIME_SECONDS = 4 * 60 * 60

# Configuración por defecto de credenciales admin (se puede sobreescribir con variable de entorno)
# Contraseña por defecto para desarrollo: "AdminManiqui2026!"
DEFAULT_ADMIN_SALT = os.environ.get("ADMIN_SALT", "9f8a3c2b1e7d4a6f")
DEFAULT_ADMIN_HASH = os.environ.get(
    "ADMIN_PASSWORD_HASH",
    # Hash PBKDF2 de "AdminManiqui2026!" con salt "9f8a3c2b1e7d4a6f"
    "5e6fb4b9cd162d5b3a88c6f1423f984c613161df1a79ba980066284c68f6daae"
)


def hash_password(password: str, salt: str = DEFAULT_ADMIN_SALT) -> str:
    """Genera un hash PBKDF2-HMAC-SHA256 con 100,000 iteraciones."""
    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000
    )
    return key.hex()


def verify_password(password: str) -> bool:
    """Verifica si la contraseña ingresada coincide con el hash del administrador."""
    candidate_hash = hash_password(password, DEFAULT_ADMIN_SALT)
    # Comparación en tiempo constante para evitar ataques de temporización (timing attacks)
    return secrets.compare_digest(candidate_hash, DEFAULT_ADMIN_HASH)


def create_admin_session() -> str:
    """
    Genera un token de sesión firmado (HMAC-SHA256) con su fecha de expiración.
    No se guarda en memoria: cualquier proceso del servidor puede validarlo.
    """
    expires = int(time.time() + TOKEN_LIFETIME_SECONDS)
    payload = f"{expires}.{secrets.token_hex(16)}"
    signature = hmac.new(SESSION_SECRET, payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}.{signature}"


def validate_admin_token(token: Optional[str]) -> bool:
    """Verifica la firma del token y que no haya expirado."""
    if not token or not isinstance(token, str):
        return False
    token_clean = token.replace("Bearer ", "").strip()
    parts = token_clean.split(".")
    if len(parts) != 3 or not parts[0].isdigit():
        return False
    payload = f"{parts[0]}.{parts[1]}"
    expected = hmac.new(SESSION_SECRET, payload.encode(), hashlib.sha256).hexdigest()
    if not secrets.compare_digest(expected, parts[2]):
        return False
    return time.time() < int(parts[0])


# --- Anti fuerza bruta: intentos fallidos guardados en SQLite, compartidos por
# todos los procesos (así el bloqueo es igual de estricto con varios workers) ---

def _login_db():
    from backend.database import get_db_connection  # import tardío: evita ciclos
    return get_db_connection()


def ensure_login_attempts_table() -> None:
    with _login_db() as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS login_attempts (ip TEXT NOT NULL, ts REAL NOT NULL)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_login_attempts_ip ON login_attempts (ip, ts)")


def record_failed_login(ip: str) -> None:
    """Registra un intento fallido de inicio de sesión."""
    with _login_db() as conn:
        conn.execute("INSERT INTO login_attempts (ip, ts) VALUES (?, ?)", (ip, time.time()))
        conn.execute("DELETE FROM login_attempts WHERE ts < ?", (time.time() - 86400,))


def is_ip_blocked(ip: str, max_attempts: int = 5, lock_seconds: int = 600) -> Tuple[bool, int]:
    """
    Verifica si una IP está bloqueada por exceso de intentos fallidos.
    Retorna (True, segundos_restantes) o (False, 0).
    """
    now = time.time()
    with _login_db() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS n, MIN(ts) AS oldest FROM login_attempts WHERE ip = ? AND ts > ?",
            (ip, now - lock_seconds),
        ).fetchone()
    if row and row["n"] >= max_attempts:
        remaining = int(lock_seconds - (now - row["oldest"]))
        return True, max(remaining, 1)
    return False, 0


def clear_failed_logins(ip: str) -> None:
    """Limpia los intentos fallidos tras un login exitoso."""
    with _login_db() as conn:
        conn.execute("DELETE FROM login_attempts WHERE ip = ?", (ip,))


def get_security_headers() -> Dict[str, str]:
    """Retorna el conjunto de cabeceras HTTP de seguridad."""
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "SAMEORIGIN",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Content-Security-Policy": (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com data:; "
            "img-src 'self' data: https: blob:; "
            "connect-src 'self';"
        ),
        "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
        # Cache-Control no va aquí: cada respuesta define el suyo (los estáticos
        # se cachean; la API decide según la ruta). Duplicarlo anulaba la caché.
    }


def is_forbidden_path(path: str) -> bool:
    """Verifica si una ruta intenta acceder a archivos sensibles o del sistema."""
    lower_path = path.lower().strip()

    # Prevenir Path Traversal
    if ".." in lower_path or "/." in lower_path or lower_path.startswith("."):
        return True

    # Verificar extensiones prohibidas
    for ext in FORBIDDEN_EXTENSIONS:
        if lower_path.endswith(ext) or f"{ext}?" in lower_path:
            return True

    # Verificar carpetas restringidas
    restricted_dirs = ["database", "backend", ".git", ".venv", "venv", "__pycache__"]
    for rdir in restricted_dirs:
        if lower_path.startswith(f"/{rdir}") or f"/{rdir}/" in lower_path:
            return True

    return False


def sanitize_string(val: Any) -> str:
    """Limpia y escapa caracteres peligrosos para mitigar XSS."""
    if val is None:
        return ""
    if not isinstance(val, str):
        val = str(val)
    # Limitar longitud a 10,000 caracteres para evitar desbordamientos
    val = val[:10000]
    return html.escape(val.strip(), quote=True)


def is_valid_email(email: str) -> bool:
    """Valida formato de correo."""
    if not email or len(email) > 254:
        return False
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email.strip()))


def is_valid_phone(phone: str) -> bool:
    """Valida teléfono."""
    if not phone:
        return True
    pattern = r"^[+0-9\s\-()]{6,20}$"
    return bool(re.match(pattern, phone.strip()))


def is_valid_doc_number(doc_number: str) -> bool:
    """Valida número de documento."""
    if not doc_number:
        return False
    pattern = r"^[a-zA-Z0-9\-]{5,20}$"
    return bool(re.match(pattern, doc_number.strip()))


def check_rate_limit(ip_address: str, max_requests: int = 300, window_seconds: int = 60, bucket: str = "api") -> bool:
    """
    Limita la tasa de peticiones por IP con una ventana fija (O(1) por petición).
    `bucket` separa contadores (p. ej. lecturas de la API y envío de formularios).
    """
    if ip_address in ("127.0.0.1", "::1", "localhost"):
        return True
    now = time.time()
    key = (bucket, ip_address)
    with _RATE_LOCK:
        # Limpieza periódica: quitar IPs inactivas para que la memoria no crezca
        if now - _RATE_LAST_PRUNE[0] > window_seconds:
            for k in [k for k, v in _RATE_LIMIT_STORAGE.items() if now - v[0] >= window_seconds]:
                del _RATE_LIMIT_STORAGE[k]
            _RATE_LAST_PRUNE[0] = now
        entry = _RATE_LIMIT_STORAGE.get(key)
        if entry is None or now - entry[0] >= window_seconds:
            _RATE_LIMIT_STORAGE[key] = [now, 1]
            return True
        entry[1] += 1
        return entry[1] <= max_requests
