"""Resumen numérico del panel de administración (una sola consulta)."""

from backend.database import query_one
from backend.web.router import Request, ok, router


@router.get("/api/stats", admin=True)
def summary(req: Request):
    row = query_one(
        """SELECT
             (SELECT COUNT(*) FROM products WHERE is_active)                      AS products_total,
             (SELECT COUNT(*) FROM products WHERE NOT is_active)                  AS products_inactive,
             (SELECT COUNT(*) FROM categories WHERE is_active)                    AS categories_total,
             (SELECT COUNT(*) FROM contact_messages)                              AS messages_total,
             (SELECT COUNT(*) FROM contact_messages WHERE status = 'unread')      AS messages_unread,
             (SELECT COUNT(*) FROM claims_book)                                   AS claims_total,
             (SELECT COUNT(*) FROM claims_book WHERE status = 'Pendiente')        AS claims_pending"""
    )
    return ok(row)
