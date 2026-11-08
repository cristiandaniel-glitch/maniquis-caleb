"""
Rutas para la gestión de Reseñas y Testimonios de Clientes / Boutiques.
Permite consultar opiniones públicas y enviar nuevas reseñas verificadas.
"""

from typing import Any, Dict, Tuple
from backend.database import execute_insert, query_all
from backend.moderation import contains_profanity


def handle_get_reviews() -> Tuple[int, Dict[str, Any]]:
    """Retorna la lista de todas las reseñas ordenadas por fecha reciente."""
    try:
        reviews = query_all("SELECT * FROM reviews ORDER BY id DESC;")
        return 200, {
            "status": "success",
            "total": len(reviews),
            "reviews": reviews
        }
    except Exception:
        return 500, {"status": "error", "message": "No se pudieron consultar las reseñas. Intente nuevamente."}


def handle_create_review(data: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
    """Valida e inserta una nueva reseña de cliente en la base de datos."""
    try:
        name = str(data.get("name", "")).strip()
        boutique = str(data.get("boutique", "")).strip()  # opcional
        city = str(data.get("city", "Cusco")).strip() or "Cusco"
        product_model = str(data.get("product_model", "")).strip()
        rating = int(data.get("rating", 5))
        comment = str(data.get("comment", "")).strip()

        if not name or len(name) < 2:
            return 400, {"status": "error", "message": "Por favor ingresa tu nombre completo o de tu empresa."}
        if len(name) > 60 or len(boutique) > 80 or len(city) > 60 or len(product_model) > 80 or len(comment) > 1000:
            return 400, {"status": "error", "message": "Uno de los campos es demasiado largo."}
        if any(contains_profanity(t) for t in (name, boutique, city, product_model, comment)):
            return 400, {"status": "error", "message": "Tu reseña tiene palabras no permitidas. Escríbela de nuevo sin groserías ni insultos."}
        if not comment or len(comment) < 10:
            return 400, {"status": "error", "message": "Tu reseña debe contener al menos 10 caracteres."}
        if rating < 1 or rating > 5:
            rating = 5

        new_id = execute_insert(
            """INSERT INTO reviews (name, boutique, city, product_model, rating, comment, is_verified)
               VALUES (%s, %s, %s, %s, %s, %s, TRUE);""",
            (name, boutique, city, product_model, rating, comment),
        )

        return 201, {
            "status": "success",
            "message": "¡Gracias! Tu reseña ha sido publicada con éxito.",
            "review": {
                "id": new_id,
                "name": name,
                "boutique": boutique,
                "city": city,
                "product_model": product_model,
                "rating": rating,
                "comment": comment,
                "is_verified": 1
            }
        }
    except Exception:
        return 500, {"status": "error", "message": "No se pudo guardar la reseña. Intente nuevamente."}
