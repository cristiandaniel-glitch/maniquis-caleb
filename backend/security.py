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
import html
import os
import re
import secrets
import time
from typing import Any, Dict, List, Optional, Set, Tuple

# Extensiones y patrones de archivos prohibidos en el servidor estático
FORBIDDEN_EXTENSIONS: Set[str] = {
    ".db", ".sqlite", ".sqlite3", ".env", ".sql", ".py", ".pyc",
    ".sh", ".bash", ".log", ".git", ".gitignore", ".yml", ".yaml", ".ini", ".conf"
}

# Almacén en memoria de tokens de sesión: { token: { "created_at": float, "expires_at": float } }
_ACTIVE_ADMIN_TOKENS: Dict[str, Dict[str, float]] = {}

# Almacén de intentos de login fallidos: { ip: [timestamp1, timestamp2, ...] }
_FAILED_LOGIN_ATTEMPTS: Dict[str, List[float]] = {}

# Almacén de Rate Limiter: { ip: [timestamp1, timestamp2, ...] }
_RATE_LIMIT_STORAGE: Dict[str, List[float]] = {}

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
    """Genera un token criptográfico seguro de 64 caracteres para el administrador."""
    token = secrets.token_hex(32)
    now = time.time()
    _ACTIVE_ADMIN_TOKENS[token] = {
        "created_at": now,
        "expires_at": now + TOKEN_LIFETIME_SECONDS
    }
    return token


def validate_admin_token(token: Optional[str]) -> bool:
    """Verifica si un token de sesión es válido y no ha expirado."""
    if not token or not isinstance(token, str):
        return False

    token_clean = token.replace("Bearer ", "").strip()
    if token_clean not in _ACTIVE_ADMIN_TOKENS:
        return False

    session = _ACTIVE_ADMIN_TOKENS[token_clean]
    if time.time() > session["expires_at"]:
        del _ACTIVE_ADMIN_TOKENS[token_clean]
        return False

    return True


def record_failed_login(ip: str) -> None:
    """Registra un intento fallido de inicio de sesión."""
    now = time.time()
    if ip not in _FAILED_LOGIN_ATTEMPTS:
        _FAILED_LOGIN_ATTEMPTS[ip] = []
    _FAILED_LOGIN_ATTEMPTS[ip].append(now)


def is_ip_blocked(ip: str, max_attempts: int = 5, lock_seconds: int = 600) -> Tuple[bool, int]:
    """
    Verifica si una IP está bloqueada por exceso de intentos fallidos.
    Retorna (True, segundos_restantes) o (False, 0).
    """
    now = time.time()
    if ip not in _FAILED_LOGIN_ATTEMPTS:
        return False, 0

    # Filtrar intentos en los últimos lock_seconds
    valid_attempts = [t for t in _FAILED_LOGIN_ATTEMPTS[ip] if now - t < lock_seconds]
    _FAILED_LOGIN_ATTEMPTS[ip] = valid_attempts

    if len(valid_attempts) >= max_attempts:
        oldest = valid_attempts[0]
        remaining = int(lock_seconds - (now - oldest))
        return True, max(remaining, 1)

    return False, 0


def clear_failed_logins(ip: str) -> None:
    """Limpia los intentos fallidos tras un login exitoso."""
    if ip in _FAILED_LOGIN_ATTEMPTS:
        del _FAILED_LOGIN_ATTEMPTS[ip]


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
        "Cache-Control": "no-cache, no-store, must-revalidate"
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


def check_rate_limit(ip_address: str, max_requests: int = 300, window_seconds: int = 60) -> bool:
    """Limita la tasa de peticiones por IP."""
    if ip_address in ("127.0.0.1", "::1", "localhost"):
        return True
    now = time.time()
    if ip_address not in _RATE_LIMIT_STORAGE:
        _RATE_LIMIT_STORAGE[ip_address] = [now]
        return True

    timestamps = [t for t in _RATE_LIMIT_STORAGE[ip_address] if now - t < window_seconds]
    timestamps.append(now)
    _RATE_LIMIT_STORAGE[ip_address] = timestamps

    return len(timestamps) <= max_requests
