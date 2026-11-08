"""
Modelo para Categorías de Maniquíes.
"""

from typing import Any, Dict, List, Optional
from backend.database import query_all, query_one


def get_all_categories() -> List[Dict[str, Any]]:
    """Obtiene todas las categorías activas con conteo de productos."""
    sql = """
        SELECT c.*, COUNT(p.id) as product_count
        FROM categories c
        LEFT JOIN products p ON c.id = p.category_id AND p.is_active = TRUE
        WHERE c.is_active = TRUE
        GROUP BY c.id
        ORDER BY c.display_order ASC, c.name ASC
    """
    return query_all(sql)


def get_category_by_id(category_id: int) -> Optional[Dict[str, Any]]:
    """Obtiene una categoría por su ID."""
    sql = "SELECT * FROM categories WHERE id = %s AND is_active = TRUE"
    return query_one(sql, (category_id,))
