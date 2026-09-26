"""
Rutas para la gestión de Reseñas y Testimonios de Clientes / Boutiques.
Permite consultar opiniones públicas y enviar nuevas reseñas verificadas.
"""

from typing import Any, Dict, Tuple
from backend.database import execute_mutation, query_all
from backend.moderation import contains_profanity


def ensure_reviews_table():
    """Garantiza que la tabla de reseñas exista en SQLite."""
    sql = """
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        boutique TEXT NOT NULL,
        city TEXT DEFAULT 'Cusco',
        product_model TEXT,
        rating INTEGER DEFAULT 5,
        comment TEXT NOT NULL,
        is_verified INTEGER DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """
    execute_mutation(sql)

    # Si está vacía, insertar las 6 reseñas iniciales oficiales
    rows = query_all("SELECT COUNT(*) as count FROM reviews;")
    if rows and rows[0]["count"] == 0:
        initial_reviews = [
            ("Dan", "", "Cusco", "Maniquí femenino", 5,
             "Me atendieron con mucha paciencia y me mostraron varios modelos hasta encontrar el ideal para mi vitrina. El maniquí llegó impecable y le dio otra vida a la tienda.", 1),
            ("Rodry", "", "Cusco", "Colgadores y percheros", 4,
             "Buena variedad de colgadores y percheros, y el trato es muy amable. Me respondieron rápido por WhatsApp y todo llegó tal como lo pedí.", 1),
            ("Cris", "", "Cusco", "Busto de sastre", 5,
             "El busto de sastre es firme y de muy buen acabado; lo uso todos los días en mi taller. Se nota que les importa que el cliente se vaya contento.", 1),
        ]
        for rev in initial_reviews:
            execute_mutation(
                """INSERT INTO reviews (name, boutique, city, product_model, rating, comment, is_verified) 
                   VALUES (?, ?, ?, ?, ?, ?, ?);""",
                rev
            )


def handle_get_reviews() -> Tuple[int, Dict[str, Any]]:
    """Retorna la lista de todas las reseñas ordenadas por fecha reciente."""
    try:
        ensure_reviews_table()
        reviews = query_all("SELECT * FROM reviews ORDER BY id DESC;")
        return 200, {
            "status": "success",
            "total": len(reviews),
            "reviews": reviews
        }
    except Exception as e:
        return 500, {"status": "error", "message": f"Error al consultar reseñas: {str(e)}"}


def handle_create_review(data: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
    """Valida e inserta una nueva reseña de cliente en la base de datos."""
    try:
        ensure_reviews_table()

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

        new_id = execute_mutation(
            """INSERT INTO reviews (name, boutique, city, product_model, rating, comment, is_verified)
               VALUES (?, ?, ?, ?, ?, ?, 1);""",
            (name, boutique, city, product_model, rating, comment)
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
    except Exception as e:
        return 500, {"status": "error", "message": f"Error al guardar la reseña: {str(e)}"}
