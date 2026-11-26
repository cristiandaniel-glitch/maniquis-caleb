"""Reseñas y testimonios de clientes (formato de respuesta que espera resenas.html)."""

from backend.models.review import create_review, list_reviews
from backend.web.router import Request, router


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
