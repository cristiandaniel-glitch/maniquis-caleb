"""Consultas de categorías del catálogo."""

from typing import Any, Dict, List, Optional

from backend.core.validation import ValidationError, clean_text
from backend.database import execute_insert, query_all, query_one
from backend.models.product import slugify


def list_categories() -> List[Dict[str, Any]]:
    """Categorías activas con la cantidad de productos activos de cada una."""
    return query_all(
        """SELECT c.*, COUNT(p.id) AS product_count
           FROM categories c
           LEFT JOIN products p ON c.id = p.category_id AND p.is_active = TRUE
           WHERE c.is_active = TRUE
           GROUP BY c.id
           ORDER BY c.display_order ASC, c.name ASC"""
    )


def get_category(category_id: int) -> Optional[Dict[str, Any]]:
    return query_one("SELECT * FROM categories WHERE id = %s AND is_active = TRUE", (category_id,))


def create_category(data: Dict[str, Any]) -> int:
    raw_name = str(data.get("name") or "").strip()
    name = clean_text(raw_name, "Nombre de la categoría", 80, required=True, min_length=2)
    description = clean_text(data.get("description"), "Descripción", 300) or None

    if query_one("SELECT id FROM categories WHERE LOWER(name) IN (LOWER(%s), LOWER(%s)) LIMIT 1", (name, raw_name)):
        raise ValidationError("Ya existe una categoría con ese nombre.")

    base_slug = slugify(raw_name) or "categoria"
    slug, suffix = base_slug, 2
    while query_one("SELECT id FROM categories WHERE slug = %s LIMIT 1", (slug,)):
        slug, suffix = f"{base_slug}-{suffix}", suffix + 1

    order_row = query_one("SELECT COALESCE(MAX(display_order), 0) + 1 AS next_order FROM categories")
    return execute_insert(
        """INSERT INTO categories (name, slug, description, icon, display_order, is_active)
           VALUES (%s, %s, %s, 'tag', %s, TRUE)""",
        (name, slug, description, int(order_row["next_order"] if order_row else 1)),
    )
