"""Catálogo de productos: rutas públicas y del panel de administración."""

from backend.core.validation import to_bool
from backend.models import product as products
from backend.web.router import Request, fail, ok, router


@router.get("/api/products", cache=True)
def list_public(req: Request):
    """Catálogo público: solo productos activos. Filtros: category_id, q, featured."""
    category = req.query.get("category_id", "")
    rows = products.list_products(
        category_id=int(category) if category.isdigit() else None,
        search=req.query.get("q") or req.query.get("search"),
        featured_only=req.query.get("featured") in ("true", "1"),
    )
    return ok(rows, count=len(rows))


@router.get("/api/products/<int:product_id>")
def detail_by_id(req: Request):
    product = products.get_product(req.params["product_id"], include_inactive=req.is_admin)
    return ok(product) if product else fail("Producto no encontrado.", 404)


@router.get("/api/products/<slug>")
def detail_by_slug(req: Request):
    product = products.get_product(req.params["slug"], include_inactive=req.is_admin)
    return ok(product) if product else fail("Producto no encontrado.", 404)


# ----------------------------------------------------------------- panel admin

@router.get("/api/admin/products", admin=True)
def list_admin(req: Request):
    """Inventario completo (activos e inactivos) para el panel."""
    rows = products.list_products(include_inactive=True)
    return ok(rows, count=len(rows))


@router.post("/api/products", admin=True, mutates=True, limit="api")
def create(req: Request):
    new_id = products.create_product(req.body)
    return ok(products.get_product(new_id, include_inactive=True), 201, message="Producto creado con éxito.")


@router.put("/api/products/<int:product_id>", admin=True, mutates=True)
def update(req: Request):
    product_id = req.params["product_id"]
    if not products.update_product(product_id, req.body):
        return fail("Producto no encontrado para actualizar.", 404)
    return ok(products.get_product(product_id, include_inactive=True), message="Producto actualizado correctamente.")


@router.patch("/api/products/<int:product_id>/active", admin=True, mutates=True)
def set_active(req: Request):
    """Activar o desactivar un producto: {"is_active": true|false}."""
    if "is_active" not in req.body:
        return fail("Indica si el producto debe estar activo (is_active).")
    active = to_bool(req.body["is_active"])
    if not products.set_product_active(req.params["product_id"], active):
        return fail("Producto no encontrado.", 404)
    message = "Producto activado: ya se ve en el catálogo." if active else "Producto desactivado: ya no se ve en el catálogo."
    return ok(products.get_product(req.params["product_id"], include_inactive=True), message=message)


@router.delete("/api/products/<int:product_id>", admin=True, mutates=True)
def remove(req: Request):
    """Compatibilidad: "eliminar" desactiva el producto (no se pierde el historial)."""
    if not products.set_product_active(req.params["product_id"], False):
        return fail("Producto no encontrado.", 404)
    return ok(message="Producto retirado del catálogo.")
