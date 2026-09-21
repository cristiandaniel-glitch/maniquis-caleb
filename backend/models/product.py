"""
Modelo y lógica de negocio para Productos / Maniquíes.
"""

import re
from typing import Any, Dict, List, Optional
from backend.database import execute_mutation, query_all, query_one
from backend.security import sanitize_string


def slugify(text: str) -> str:
    """Genera un slug limpio y amigable para URLs."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")


def get_all_products(
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    featured_only: bool = False,
    is_active: int = 1
) -> List[Dict[str, Any]]:
    """Obtiene el listado de productos con filtros seguros."""
    sql = """
        SELECT p.*, c.name as category_name, c.slug as category_slug
        FROM products p
        JOIN categories c ON p.category_id = c.id
        WHERE p.is_active = ?
    """
    params: List[Any] = [is_active]

    if category_id:
        sql += " AND p.category_id = ?"
        params.append(category_id)

    if featured_only:
        sql += " AND p.is_featured = 1"

    if search:
        search_pattern = f"%{search.strip()}%"
        sql += " AND (p.name LIKE ? OR p.description LIKE ? OR p.material LIKE ? OR p.sku LIKE ?)"
        params.extend([search_pattern, search_pattern, search_pattern, search_pattern])

    sql += " ORDER BY p.is_featured DESC, p.created_at DESC"
    return query_all(sql, tuple(params))


def get_product_by_id(product_id: int) -> Optional[Dict[str, Any]]:
    """Obtiene un producto por su ID."""
    sql = """
        SELECT p.*, c.name as category_name, c.slug as category_slug
        FROM products p
        JOIN categories c ON p.category_id = c.id
        WHERE p.id = ?
    """
    return query_one(sql, (product_id,))


def get_product_by_slug(slug: str) -> Optional[Dict[str, Any]]:
    """Obtiene un producto por su slug."""
    sql = """
        SELECT p.*, c.name as category_name, c.slug as category_slug
        FROM products p
        JOIN categories c ON p.category_id = c.id
        WHERE p.slug = ?
    """
    return query_one(sql, (slug,))


def create_product(data: Dict[str, Any]) -> int:
    """Crea un nuevo producto en la base de datos de manera segura."""
    import secrets
    name = sanitize_string(data.get("name", ""))
    category_id = int(data.get("category_id", 1))
    
    # Generar SKU único si no se proporciona o si ya existe
    provided_sku = data.get("sku")
    if provided_sku:
        sku = sanitize_string(provided_sku)
    else:
        sku = f"MNQ-{category_id}-{secrets.token_hex(4).upper()}"

    description = sanitize_string(data.get("description", ""))
    material = sanitize_string(data.get("material", "Fibra de alta calidad"))
    color = sanitize_string(data.get("color", "Personalizado"))
    dimensions = sanitize_string(data.get("dimensions", "Medidas estándar"))
    price = float(data.get("price", 0.0))
    stock = int(data.get("stock", 1))
    image_url = sanitize_string(data.get("image_url", "/assets/images/mannequin-aura.png"))
    is_featured = 1 if data.get("is_featured") else 0
    slug = slugify(name)

    # Asegurar slug único
    existing = get_product_by_slug(slug)
    if existing:
        slug = f"{slug}-{secrets.token_hex(3)}"

    sql = """
        INSERT INTO products (
            category_id, name, slug, sku, description,
            material, color, dimensions, price, stock,
            image_url, is_featured, is_active
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
    """
    return execute_mutation(sql, (
        category_id, name, slug, sku, description,
        material, color, dimensions, price, stock,
        image_url, is_featured
    ))


def update_product(product_id: int, data: Dict[str, Any]) -> bool:
    """Actualiza un producto existente de forma segura."""
    existing = get_product_by_id(product_id)
    if not existing:
        return False

    name = sanitize_string(data.get("name", existing["name"]))
    category_id = int(data.get("category_id", existing["category_id"]))
    sku = sanitize_string(data.get("sku", existing["sku"]))
    description = sanitize_string(data.get("description", existing["description"]))
    material = sanitize_string(data.get("material", existing["material"]))
    color = sanitize_string(data.get("color", existing["color"]))
    dimensions = sanitize_string(data.get("dimensions", existing["dimensions"]))
    price = float(data.get("price", existing["price"]))
    stock = int(data.get("stock", existing["stock"]))
    image_url = sanitize_string(data.get("image_url", existing["image_url"]))
    is_featured = 1 if data.get("is_featured") is True or data.get("is_featured") == 1 else 0

    sql = """
        UPDATE products SET
            category_id = ?, name = ?, sku = ?, description = ?,
            material = ?, color = ?, dimensions = ?, price = ?,
            stock = ?, image_url = ?, is_featured = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """
    execute_mutation(sql, (
        category_id, name, sku, description,
        material, color, dimensions, price,
        stock, image_url, is_featured, product_id
    ))
    return True


def delete_product(product_id: int) -> bool:
    """Elimina o desactiva lógicamente un producto."""
    sql = "UPDATE products SET is_active = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
    execute_mutation(sql, (product_id,))
    return True
