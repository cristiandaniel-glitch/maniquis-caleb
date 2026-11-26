"""Categorías del catálogo."""

from backend.models import category as categories
from backend.web.router import Request, fail, ok, router


@router.get("/api/categories", cache=True)
def list_all(req: Request):
    rows = categories.list_categories()
    return ok(rows, count=len(rows))


@router.get("/api/categories/<int:category_id>")
def detail(req: Request):
    category = categories.get_category(req.params["category_id"])
    return ok(category) if category else fail("Categoría no encontrada.", 404)


@router.post("/api/categories", admin=True, mutates=True, limit="api")
def create(req: Request):
    new_id = categories.create_category(req.body)
    return ok(categories.get_category(new_id), 201, message="Categoría creada correctamente.")
