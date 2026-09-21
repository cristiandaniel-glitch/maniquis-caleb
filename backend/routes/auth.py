"""
Controlador de autenticación y gestión de sesiones administrativas.
"""

from typing import Any, Dict, Optional, Tuple, Union
from backend.security import (
    clear_failed_logins,
    create_admin_session,
    is_ip_blocked,
    record_failed_login,
    validate_admin_token,
    verify_password,
)


def handle_admin_login(payload: Dict[str, Any], client_ip: str) -> Union[Dict[str, Any], Tuple[Dict[str, Any], int]]:
    """Maneja el inicio de sesión administrativo con protección anti-fuerza bruta."""
    blocked, wait_seconds = is_ip_blocked(client_ip)
    if blocked:
        return {
            "success": False,
            "error": f"Demasiados intentos fallidos. Su dirección IP ha sido bloqueada temporalmente por seguridad. Intente en {wait_seconds} segundos."
        }, 429

    password = payload.get("password", "")
    if not password:
        return {"success": False, "error": "Debe ingresar la contraseña de administrador."}, 400

    if not verify_password(password):
        record_failed_login(client_ip)
        blocked_now, wait = is_ip_blocked(client_ip)
        if blocked_now:
            return {
                "success": False,
                "error": f"Contraseña incorrecta. Has alcanzado el límite de intentos. Bloqueo temporal por {wait} segundos."
            }, 429
        return {"success": False, "error": "Credenciales inválidas. Acceso denegado."}, 401

    # Login exitoso: limpiar fallos y generar token seguro
    clear_failed_logins(client_ip)
    token = create_admin_session()

    return {
        "success": True,
        "message": "Autenticación exitosa.",
        "data": {
            "token": token,
            "role": "admin",
            "expires_in": 14400 # 4 horas en segundos
        }
    }


def handle_verify_admin_session(token: Optional[str]) -> Union[Dict[str, Any], Tuple[Dict[str, Any], int]]:
    """Verifica si la sesión actual sigue activa y válida."""
    if not validate_admin_token(token):
        return {"success": False, "error": "Sesión inválida o expirada. Por favor inicie sesión."}, 401

    return {"success": True, "message": "Sesión válida.", "authenticated": True}
