"""
Rutas para la gestión de categorías.
"""

from typing import Any, Dict
from backend.models.category import get_all_categories, get_category_by_id


def handle_get_categories() -> Dict[str, Any]:
    """Maneja GET /api/categories."""
    categories = get_all_categories()
    return {
        "success": True,
        "count": len(categories),
        "data": categories
    }


def handle_get_category_detail(category_id: int) -> Dict[str, Any]:
    """Maneja GET /api/categories/<id>."""
    category = get_category_by_id(category_id)
    if not category:
        return {"success": False, "error": "Categoría no encontrada"}, 404
    return {"success": True, "data": category}
