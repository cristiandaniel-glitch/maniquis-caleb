"""Formulario de contacto (Nosotros) y bandeja de mensajes del panel."""

from backend.models.message import create_message, get_all_messages, set_message_status
from backend.web.router import Request, fail, ok, router


@router.post("/api/contact", honeypot=True)
def send(req: Request):
    return ok(create_message(req.body, ip_address=req.client_ip), 201)


@router.get("/api/messages", admin=True)
def list_all(req: Request):
    messages = get_all_messages()
    return ok(messages, count=len(messages))


@router.patch("/api/messages/<int:message_id>", admin=True)
def update_status(req: Request):
    """Panel: {"status": "read" | "unread" | "archived"}"""
    if not set_message_status(req.params["message_id"], str(req.body.get("status") or "")):
        return fail("Mensaje no encontrado.", 404)
    return ok(message="Mensaje actualizado.")
