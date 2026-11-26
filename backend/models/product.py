"""Consultas de productos (maniquíes, bustos, colgadores y accesorios)."""

import html
import re
import secrets
from typing import Any, Dict, List, Optional

from backend.core.validation import (
    ValidationError,
    clean_product_image,
    clean_text,
    to_bool,
    to_int,
    to_money,
)
from backend.database import execute_insert, execute_mutation, query_all, query_one

_SELECT = """
    SELECT p.*, c.name AS category_name, c.slug AS category_slug
    FROM products p
    JOIN categories c ON p.category_id = c.id
"""


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")


def list_products(
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    featured_only: bool = False,
    include_inactive: bool = False,
) -> List[Dict[str, Any]]:
    """Catálogo público (solo activos) o inventario completo para el panel."""
    sql = _SELECT + " WHERE TRUE"
    params: List[Any] = []
    if not include_inactive:
        sql += " AND p.is_active = TRUE"
    if category_id:
        sql += " AND p.category_id = %s"
        params.append(category_id)
    if featured_only:
        sql += " AND p.is_featured = TRUE"
    if search:
        pattern = f"%{search.strip()[:80]}%"
        sql += " AND (p.name ILIKE %s OR p.description ILIKE %s OR p.material ILIKE %s OR p.sku ILIKE %s)"
        params.extend([pattern] * 4)
    sql += " ORDER BY p.is_active DESC, p.is_featured DESC, p.created_at DESC"
    return query_all(sql, tuple(params))


def get_product(id_or_slug: Any, include_inactive: bool = False) -> Optional[Dict[str, Any]]:
    column = "p.id" if isinstance(id_or_slug, int) else "p.slug"
    sql = _SELECT + f" WHERE {column} = %s"
    if not include_inactive:
        sql += " AND p.is_active = TRUE"
    return query_one(sql, (id_or_slug,))


def _category_exists(category_id: int) -> bool:
    return query_one("SELECT 1 AS ok FROM categories WHERE id = %s AND is_active = TRUE", (category_id,)) is not None


def _sku_taken(sku: str, exclude_id: Optional[int] = None) -> bool:
    row = query_one("SELECT id FROM products WHERE sku = %s", (sku,))
    return bool(row) and row["id"] != exclude_id


def _clean_fields(data: Dict[str, Any], current: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Valida los campos recibidos. En una edición, lo que no llega se conserva."""
    current = current or {}

    def pick(key: str, default: Any = None) -> Any:
        if key in data:
            return data[key]
        value = current.get(key, default)
        # Lo guardado ya está escapado: se devuelve a texto plano para no escaparlo dos veces.
        return html.unescape(value) if isinstance(value, str) else value

    fields = {
        "name": clean_text(pick("name"), "Nombre", 120, required=True, min_length=2),
        "description": clean_text(pick("description"), "Descripción", 1000, required=True, min_length=5),
        "category_id": to_int(pick("category_id"), "Categoría", minimum=1),
        "material": clean_text(pick("material", "Consultar"), "Material", 80),
        "color": clean_text(pick("color", ""), "Color", 80),
        "dimensions": clean_text(pick("dimensions", ""), "Medidas", 80),
        "price": to_money(pick("price", 0), "Precio"),
        "stock": to_int(pick("stock", 0), "Stock", minimum=0, maximum=1_000_000),
        "image_url": clean_product_image(pick("image_url", "")),
        "is_featured": to_bool(pick("is_featured", False)),
        "is_active": to_bool(pick("is_active", True)),
    }
    if "category_id" in data or not current:
        if not _category_exists(fields["category_id"]):
            raise ValidationError("La categoría elegida no existe.")
    return fields


def create_product(data: Dict[str, Any]) -> int:
    fields = _clean_fields(data)
    sku = clean_text(data.get("sku"), "Código", 40) or f"MNQ-{fields['category_id']}-{secrets.token_hex(4).upper()}"
    if _sku_taken(sku):
        raise ValidationError("Ya existe un producto con ese código.")
    slug = slugify(fields["name"]) or "producto"
    if query_one("SELECT id FROM products WHERE slug = %s", (slug,)):
        slug = f"{slug}-{secrets.token_hex(3)}"
    return execute_insert(
        """INSERT INTO products (category_id, name, slug, sku, description, material, color,
                                 dimensions, price, stock, image_url, is_featured, is_active)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (fields["category_id"], fields["name"], slug, sku, fields["description"], fields["material"],
         fields["color"], fields["dimensions"], fields["price"], fields["stock"], fields["image_url"],
         fields["is_featured"], fields["is_active"]),
    )


def update_product(product_id: int, data: Dict[str, Any]) -> bool:
    current = get_product(product_id, include_inactive=True)
    if not current:
        return False
    fields = _clean_fields(data, current)
    sku = clean_text(data["sku"], "Código", 40) if "sku" in data else current["sku"]
    if sku and sku != current["sku"] and _sku_taken(sku, exclude_id=product_id):
        raise ValidationError("Ya existe un producto con ese código.")
    execute_mutation(
        """UPDATE products SET category_id = %s, name = %s, sku = %s, description = %s,
                  material = %s, color = %s, dimensions = %s, price = %s, stock = %s,
                  image_url = %s, is_featured = %s, is_active = %s, updated_at = now()
           WHERE id = %s""",
        (fields["category_id"], fields["name"], sku, fields["description"], fields["material"],
         fields["color"], fields["dimensions"], fields["price"], fields["stock"], fields["image_url"],
         fields["is_featured"], fields["is_active"], product_id),
    )
    return True


def set_product_active(product_id: int, active: bool) -> bool:
    """Activar / desactivar: el producto se oculta del catálogo sin borrarse."""
    return execute_mutation(
        "UPDATE products SET is_active = %s, updated_at = now() WHERE id = %s", (active, product_id)
    ) > 0
