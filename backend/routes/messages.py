"""Formulario de contacto (Nosotros) y bandeja de mensajes del panel."""

from backend.models.message import create_message, get_all_messages
from backend.web.router import Request, ok, router


@router.post("/api/contact", honeypot=True)
def send(req: Request):
    return ok(create_message(req.body, ip_address=req.client_ip), 201)


@router.get("/api/messages", admin=True)
def list_all(req: Request):
    messages = get_all_messages()
    return ok(messages, count=len(messages))
