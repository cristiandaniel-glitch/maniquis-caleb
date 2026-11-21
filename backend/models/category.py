"""
Modelo para Categorías de Maniquíes.
"""

from typing import Any, Dict, List, Optional
from backend.database import execute_insert, query_all, query_one
from backend.models.product import slugify
from backend.security import sanitize_string


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


def create_category(data: Dict[str, Any]) -> int:
    """Crea una categoría activa con un slug único."""
    raw_name = str(data.get("name") or "").strip()
    name = sanitize_string(raw_name)
    if not name:
        raise ValueError("Escribe el nombre de la categoría.")
    if len(raw_name) > 80:
        raise ValueError("El nombre de la categoría no puede superar 80 caracteres.")

    duplicate = query_one(
        "SELECT id FROM categories WHERE LOWER(name) IN (LOWER(%s), LOWER(%s)) LIMIT 1",
        (name, raw_name),
    )
    if duplicate:
        raise ValueError("Ya existe una categoría con ese nombre.")

    base_slug = slugify(raw_name) or "categoria"
    slug = base_slug
    suffix = 2
    while query_one("SELECT id FROM categories WHERE slug = %s LIMIT 1", (slug,)):
        slug = f"{base_slug}-{suffix}"
        suffix += 1

    raw_description = str(data.get("description") or "").strip()
    if len(raw_description) > 300:
        raise ValueError("La descripción no puede superar 300 caracteres.")
    description = sanitize_string(raw_description) or None
    order_row = query_one("SELECT COALESCE(MAX(display_order), 0) + 1 AS next_order FROM categories")
    display_order = int(order_row["next_order"] if order_row else 1)

    sql = """
        INSERT INTO categories (name, slug, description, icon, display_order, is_active)
        VALUES (%s, %s, %s, 'tag', %s, TRUE)
    """
    return execute_insert(sql, (name, slug, description, display_order))
