"""
Rutas para la gestión de categorías.
"""

from typing import Any, Dict, Tuple
from backend.models.category import create_category, get_all_categories, get_category_by_id


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


def handle_create_category(payload: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """Maneja POST /api/categories para el panel de administración."""
    try:
        category_id = create_category(payload)
        category = get_category_by_id(category_id)
        return {
            "success": True,
            "message": "Categoría creada correctamente.",
            "data": category,
        }, 201
    except ValueError as error:
        return {"success": False, "error": str(error)}, 400
    except Exception:
        return {
            "success": False,
            "error": "No se pudo crear la categoría. Verifica el nombre e inténtalo de nuevo.",
        }, 400
