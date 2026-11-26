"""
Autenticación del panel de administración.

- Contraseña: PBKDF2-HMAC-SHA256 con salt (estándar OWASP). No existe
  contraseña por defecto: sin ADMIN_SALT y ADMIN_PASSWORD_HASH en el .env el
  panel queda cerrado.
- Sesión: token firmado con HMAC-SHA256 que incluye su vencimiento. Ningún
  proceso guarda sesiones en memoria, así cualquier worker puede validarlo.
- Anti fuerza bruta: intentos fallidos en PostgreSQL, compartidos por todos
  los procesos.
"""

import datetime as dt
import hashlib
import hmac
import secrets
import time
from typing import Optional, Tuple

from backend.config import (
    ADMIN_PASSWORD_HASH,
    ADMIN_PBKDF2_ITERATIONS,
    ADMIN_SALT,
    LOGIN_LOCK_SECONDS,
    LOGIN_MAX_ATTEMPTS,
    SESSION_LIFETIME_SECONDS,
    SESSION_SECRET,
)
from backend.database import get_db_connection

# Hash de la contraseña de ejemplo que estuvo publicada en el repositorio.
# Si alguien configura ese valor, el servidor se niega a usarlo.
_LEAKED_HASHES = {"5e6fb4b9cd162d5b3a88c6f1423f984c613161df1a79ba980066284c68f6daae"}

# Se calcula antes de crear los procesos de trabajo, así todos lo comparten.
_SESSION_KEY = (SESSION_SECRET or secrets.token_hex(32)).encode()


def hash_password(password: str, salt: str, iterations: int = ADMIN_PBKDF2_ITERATIONS) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations).hex()


def admin_login_configured() -> bool:
    return bool(ADMIN_SALT and ADMIN_PASSWORD_HASH) and ADMIN_PASSWORD_HASH.lower() not in _LEAKED_HASHES


def verify_password(password: str) -> bool:
    if not admin_login_configured() or not isinstance(password, str) or len(password) > 256:
        return False
    candidate = hash_password(password, ADMIN_SALT)
    return secrets.compare_digest(candidate, ADMIN_PASSWORD_HASH.lower())


def create_admin_session() -> str:
    expires = int(time.time() + SESSION_LIFETIME_SECONDS)
    payload = f"{expires}.{secrets.token_hex(16)}"
    signature = hmac.new(_SESSION_KEY, payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}.{signature}"


def validate_admin_token(header_value: Optional[str]) -> bool:
    """Acepta 'Bearer <token>'. Verifica firma en tiempo constante y vencimiento."""
    if not header_value or not isinstance(header_value, str) or len(header_value) > 300:
        return False
    token = header_value[7:] if header_value.startswith("Bearer ") else header_value
    parts = token.strip().split(".")
    if len(parts) != 3 or not parts[0].isdigit():
        return False
    payload = f"{parts[0]}.{parts[1]}"
    expected = hmac.new(_SESSION_KEY, payload.encode(), hashlib.sha256).hexdigest()
    if not secrets.compare_digest(expected, parts[2]):
        return False
    return time.time() < int(parts[0])


# ------------------------------------------------------------ anti fuerza bruta

def record_failed_login(ip: str) -> None:
    with get_db_connection() as conn:
        conn.execute("INSERT INTO login_attempts (ip_address) VALUES (%s::inet)", (ip,))
        conn.execute("DELETE FROM login_attempts WHERE created_at < now() - INTERVAL '24 hours'")


def is_ip_blocked(ip: str) -> Tuple[bool, int]:
    """(True, segundos_restantes) si la IP superó los intentos permitidos."""
    with get_db_connection() as conn:
        row = conn.execute(
            """SELECT COUNT(*) AS n, MIN(created_at) AS oldest
               FROM login_attempts
               WHERE ip_address = %s::inet
                 AND created_at > now() - (%s * INTERVAL '1 second')""",
            (ip, LOGIN_LOCK_SECONDS),
        ).fetchone()
    if row and row["n"] >= LOGIN_MAX_ATTEMPTS:
        elapsed = (dt.datetime.now(dt.timezone.utc) - row["oldest"]).total_seconds()
        return True, max(int(LOGIN_LOCK_SECONDS - elapsed), 1)
    return False, 0


def clear_failed_logins(ip: str) -> None:
    with get_db_connection() as conn:
        conn.execute("DELETE FROM login_attempts WHERE ip_address = %s::inet", (ip,))
