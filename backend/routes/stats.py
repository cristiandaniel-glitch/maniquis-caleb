"""
Rutas para estadísticas y métricas del panel de administración.
"""

from typing import Any, Dict
from backend.database import query_one


def handle_get_stats() -> Dict[str, Any]:
    """Maneja GET /api/stats."""
    p_count = query_one("SELECT COUNT(*) as count FROM products WHERE is_active = TRUE")["count"]
    c_count = query_one("SELECT COUNT(*) as count FROM categories WHERE is_active = TRUE")["count"]
    m_count = query_one("SELECT COUNT(*) as count FROM contact_messages")["count"]
    cl_count = query_one("SELECT COUNT(*) as count FROM claims_book")["count"]
    s_count = query_one("SELECT COUNT(*) as count FROM subscribers WHERE status = 'active'")["count"]
    unread_msg = query_one("SELECT COUNT(*) as count FROM contact_messages WHERE status = 'unread'")["count"]
    pending_claims = query_one("SELECT COUNT(*) as count FROM claims_book WHERE status = 'Pendiente'")["count"]

    return {
        "success": True,
        "data": {
            "products_total": p_count,
            "categories_total": c_count,
            "messages_total": m_count,
            "messages_unread": unread_msg,
            "claims_total": cl_count,
            "claims_pending": pending_claims,
            "subscribers_total": s_count
        }
    }
