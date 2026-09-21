"""
Rutas para la suscripción al boletín / newsletter.
"""

from typing import Any, Dict, Tuple, Union
from backend.models.subscriber import add_subscriber, get_all_subscribers


def handle_subscribe(payload: Dict[str, Any]) -> Union[Dict[str, Any], Tuple[Dict[str, Any], int]]:
    """Maneja POST /api/subscribe."""
    email = payload.get("email", "")
    try:
        res = add_subscriber(email)
        return {"success": True, "data": res}, 201
    except ValueError as ve:
        return {"success": False, "error": str(ve)}, 400
    except Exception:
        return {"success": False, "error": "Error interno al suscribir correo."}, 500


def handle_get_subscribers() -> Dict[str, Any]:
    """Maneja GET /api/subscribers."""
    subs = get_all_subscribers()
    return {"success": True, "count": len(subs), "data": subs}
