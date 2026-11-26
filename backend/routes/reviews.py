"""Reseñas y testimonios de clientes (formato de respuesta que espera resenas.html)."""

from backend.core.validation import to_bool
from backend.models.review import create_review, list_reviews, set_review_visible
from backend.web.router import Request, fail, ok, router


@router.get("/api/reviews", cache=True)
def list_all(req: Request):
    reviews = list_reviews()
    return {"success": True, "status": "success", "total": len(reviews), "reviews": reviews}, 200


@router.post("/api/reviews", honeypot=True, mutates=True)
def create(req: Request):
    review = create_review(req.body)
    return {
        "success": True,
        "status": "success",
        "message": "¡Gracias! Tu reseña ha sido publicada con éxito.",
        "review": review,
    }, 201


@router.get("/api/admin/reviews", admin=True)
def list_admin(req: Request):
    reviews = list_reviews(include_hidden=True)
    return ok(reviews, count=len(reviews))


@router.patch("/api/reviews/<int:review_id>/visible", admin=True, mutates=True)
def set_visible(req: Request):
    """Panel: ocultar una reseña falsa u ofensiva (o volver a mostrarla)."""
    visible = to_bool(req.body.get("is_visible", True))
    if not set_review_visible(req.params["review_id"], visible):
        return fail("Reseña no encontrada.", 404)
    return ok(message="Reseña visible en la página." if visible else "Reseña oculta: ya no se muestra en la página.")
