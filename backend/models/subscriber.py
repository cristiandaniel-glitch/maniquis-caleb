"""
Modelo para Suscripciones al Boletín / Newsletter.
"""

from typing import Any, Dict, List
from backend.database import query_all, query_one
from backend.security import is_valid_email, sanitize_string


def add_subscriber(email: str) -> Dict[str, Any]:
    """Registra un nuevo suscriptor validado en la base de datos."""
    email_clean = sanitize_string(email).lower()
    if not is_valid_email(email_clean):
        raise ValueError("El correo electrónico no es válido.")

    # El índice único sobre lower(email) en PostgreSQL evita carreras entre dos
    # solicitudes simultáneas y mantiene el mensaje funcional del frontend.
    created = query_one(
        """INSERT INTO subscribers (email, status)
           VALUES (%s, 'active')
           ON CONFLICT DO NOTHING
           RETURNING id""",
        (email_clean,),
    )
    if not created:
        return {"email": email_clean, "status": "already_subscribed", "message": "Este correo ya se encuentra suscrito."}

    return {"email": email_clean, "status": "active", "message": "¡Gracias por suscribirte al boletín de Maniquí Studio!"}


def get_all_subscribers() -> List[Dict[str, Any]]:
    """Obtiene la lista de todos los suscriptores."""
    return query_all("SELECT * FROM subscribers ORDER BY created_at DESC")
