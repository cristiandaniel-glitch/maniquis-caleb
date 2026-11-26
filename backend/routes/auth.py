"""Ingreso al panel de administración."""

from backend.core import auth
from backend.web.router import Request, fail, ok, router


@router.post("/api/admin/login", limit="login")
def login(req: Request):
    if not auth.admin_login_configured():
        return fail("El panel aún no tiene contraseña configurada en el servidor.", 503)

    blocked, wait = auth.is_ip_blocked(req.client_ip)
    if blocked:
        return fail(f"Demasiados intentos fallidos. Por seguridad, intente de nuevo en {wait} segundos.", 429)

    password = req.body.get("password")
    if not isinstance(password, str) or not password:
        return fail("Debe ingresar la contraseña de administrador.")

    if not auth.verify_password(password):
        auth.record_failed_login(req.client_ip)
        blocked, wait = auth.is_ip_blocked(req.client_ip)
        if blocked:
            return fail(f"Contraseña incorrecta. Alcanzaste el límite de intentos: espera {wait} segundos.", 429)
        return fail("Credenciales inválidas. Acceso denegado.", 401)

    auth.clear_failed_logins(req.client_ip)
    return ok({"token": auth.create_admin_session(), "role": "admin", "expires_in": 14400},
              message="Autenticación exitosa.")


@router.get("/api/admin/verify")
def verify(req: Request):
    if not req.is_admin:
        return fail("Sesión inválida o expirada. Por favor inicie sesión.", 401)
    return ok(message="Sesión válida.", authenticated=True)
