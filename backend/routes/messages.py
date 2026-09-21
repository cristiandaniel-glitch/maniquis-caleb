"""
Rutas para el formulario de contacto.
"""

from typing import Any, Dict, Optional, Tuple, Union
from backend.models.message import create_message, get_all_messages


def handle_send_message(payload: Dict[str, Any], client_ip: Optional[str] = None) -> Union[Dict[str, Any], Tuple[Dict[str, Any], int]]:
    """Maneja POST /api/contact."""
    try:
        res = create_message(payload, ip_address=client_ip)
        return {"success": True, "data": res}, 201
    except ValueError as ve:
        return {"success": False, "error": str(ve)}, 400
    except Exception:
        return {"success": False, "error": "Error interno al enviar mensaje."}, 500


def handle_get_messages() -> Dict[str, Any]:
    """Maneja GET /api/messages."""
    messages = get_all_messages()
    return {"success": True, "count": len(messages), "data": messages}
