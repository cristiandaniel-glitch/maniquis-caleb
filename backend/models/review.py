"""Reseñas públicas de clientes."""

from typing import Any, Dict, List

from backend.core.moderation import contains_profanity
from backend.core.validation import ValidationError, clean_text, to_int
from backend.database import execute_insert, execute_mutation, query_all


def list_reviews(limit: int = 500, include_hidden: bool = False) -> List[Dict[str, Any]]:
    where = "" if include_hidden else "WHERE is_visible"
    return query_all(
        f"""SELECT id, name, boutique, city, product_model, rating, comment, is_verified, is_visible, created_at
            FROM reviews {where} ORDER BY id DESC LIMIT %s""",
        (limit,),
    )


def set_review_visible(review_id: int, visible: bool) -> bool:
    return execute_mutation("UPDATE reviews SET is_visible = %s WHERE id = %s", (visible, review_id)) > 0


def create_review(data: Dict[str, Any]) -> Dict[str, Any]:
    raw = {key: str(data.get(key) or "").strip() for key in ("name", "boutique", "city", "product_model", "comment")}
    if len(raw["name"]) < 2:
        raise ValidationError("Por favor ingresa tu nombre completo o de tu empresa.")
    if len(raw["comment"]) < 10:
        raise ValidationError("Tu reseña debe contener al menos 10 caracteres.")
    if any(contains_profanity(text) for text in raw.values()):
        raise ValidationError("Tu reseña tiene palabras no permitidas. Escríbela de nuevo sin groserías ni insultos.")

    review = {
        "name": clean_text(raw["name"], "Nombre", 60),
        "boutique": clean_text(raw["boutique"], "Tienda", 80),
        "city": clean_text(raw["city"] or "Cusco", "Ciudad", 60),
        "product_model": clean_text(raw["product_model"], "Producto", 80),
        "rating": min(max(to_int(data.get("rating", 5), "Calificación"), 1), 5),
        "comment": clean_text(raw["comment"], "Reseña", 1000),
    }
    review["id"] = execute_insert(
        """INSERT INTO reviews (name, boutique, city, product_model, rating, comment, is_verified)
           VALUES (%s, %s, %s, %s, %s, %s, TRUE)""",
        (review["name"], review["boutique"], review["city"], review["product_model"], review["rating"], review["comment"]),
    )
    review["is_verified"] = 1
    return review
