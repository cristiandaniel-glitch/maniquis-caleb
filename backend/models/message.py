"""
Modelo para Mensajes del Formulario de Contacto.
"""

from typing import Any, Dict, List, Optional
from backend.database import execute_insert, query_all
from backend.core.validation import ValidationError, is_valid_email, is_valid_phone, sanitize_string


def create_message(data: Dict[str, Any], ip_address: Optional[str] = None) -> Dict[str, Any]:
    """Crea un mensaje de contacto validado."""
    name = sanitize_string(data.get("name", ""), 120)
    email = sanitize_string(data.get("email", ""), 254)
    phone = sanitize_string(data.get("phone", ""), 20)
    subject = sanitize_string(data.get("subject") or "Consulta General", 150)
    message = sanitize_string(data.get("message", ""), 3000)

    if not name or len(name) < 2:
        raise ValidationError("Por favor ingrese su nombre.")
    if not email or not is_valid_email(email):
        raise ValidationError("Por favor ingrese un correo electrónico válido.")
    if not is_valid_phone(phone):
        raise ValidationError("El formato de teléfono no es válido.")
    if not message or len(message) < 5:
        raise ValidationError("El mensaje debe contener al menos 5 caracteres.")

    sql = """
        INSERT INTO contact_messages (name, email, phone, subject, message, status, ip_address)
        VALUES (%s, %s, %s, %s, %s, 'unread', %s::inet)
    """
    msg_id = execute_insert(sql, (name, email, phone, subject, message, ip_address or "127.0.0.1"))
    return {
        "id": msg_id,
        "name": name,
        "email": email,
        "subject": subject,
        "message": "Mensaje recibido correctamente. Nos pondremos en contacto a la brevedad."
    }


def get_all_messages(limit: int = 1000) -> List[Dict[str, Any]]:
    """Obtiene los mensajes de contacto ordenados por fecha."""
    sql = "SELECT * FROM contact_messages ORDER BY created_at DESC LIMIT %s"
    return query_all(sql, (limit,))
