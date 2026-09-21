"""
Rutas para la gestión de productos y catálogo.
"""

from typing import Any, Dict, Optional, Tuple, Union
from backend.models.product import (
    create_product,
    delete_product,
    get_all_products,
    get_product_by_id,
    get_product_by_slug,
    update_product,
)


def handle_get_products(query_params: Dict[str, str]) -> Dict[str, Any]:
    """Maneja GET /api/products con filtros de categoría, búsqueda y destacados."""
    category_id_str = query_params.get("category_id")
    category_id = int(category_id_str) if category_id_str and category_id_str.isdigit() else None
    search = query_params.get("q") or query_params.get("search")
    featured_only = query_params.get("featured") in ("true", "1")

    products = get_all_products(category_id=category_id, search=search, featured_only=featured_only)
    return {
        "success": True,
        "count": len(products),
        "data": products
    }


def handle_get_product_detail(product_id_or_slug: str) -> Dict[str, Any]:
    """Maneja GET /api/products/<id_or_slug>."""
    if product_id_or_slug.isdigit():
        product = get_product_by_id(int(product_id_or_slug))
    else:
        product = get_product_by_slug(product_id_or_slug)

    if not product:
        return {"success": False, "error": "Producto no encontrado"}, 404

    return {"success": True, "data": product}


def handle_create_product(payload: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """Maneja POST /api/products."""
    if not payload.get("name") or not payload.get("description"):
        return {"success": False, "error": "El nombre y la descripción son obligatorios."}, 400

    try:
        new_id = create_product(payload)
        product = get_product_by_id(new_id)
        return {
            "success": True,
            "message": "Producto creado con éxito.",
            "data": product
        }, 201
    except Exception as e:
        return {"success": False, "error": f"Error al registrar producto: {str(e)}"}, 400


def handle_update_product(product_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Maneja PUT /api/products/<id>."""
    updated = update_product(product_id, payload)
    if not updated:
        return {"success": False, "error": "Producto no encontrado para actualizar."}, 404

    product = get_product_by_id(product_id)
    return {
        "success": True,
        "message": "Producto actualizado correctamente.",
        "data": product
    }


def handle_delete_product(product_id: int) -> Dict[str, Any]:
    """Maneja DELETE /api/products/<id>."""
    delete_product(product_id)
    return {
        "success": True,
        "message": "Producto eliminado del catálogo."
    }
