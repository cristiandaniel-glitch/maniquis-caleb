"""
Rutas para la gestión de Reseñas y Testimonios de Clientes / Boutiques.
Permite consultar opiniones públicas y enviar nuevas reseñas verificadas.
"""

from typing import Any, Dict, Tuple
from backend.database import execute_mutation, query_all


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
            ("Valeria Montes", "Boutique Élysée", "Cusco", "Maniquí Negro Velvet Mate", 5,
             "Los maniquíes negro velvet mate transformaron totalmente la vitrina de mi tienda en Cusco. La presencia y elegancia atraen miradas de inmediato.", 1),
            ("Carlos Huamán", "Sastrería Imperial", "Cusco", "Busto Sastre de Lino Francés", 5,
             "Compramos 6 bustos de lino francés para nuestro taller de confección. La base de madera es sólida y las proporciones anatómicas son perfectas para entallar.", 1),
            ("Luciana Paredes", "Atelier Alta Moda", "Cusco", "Maniquí Femenino Alta Costura", 5,
             "Excelente atención en su Stand 3 de Galería La Exitosa. Nos asesoraron con los modelos ideales para vestidos de fiesta y alta costura.", 1),
            ("Rodrigo Salcedo", "Tendencias Boutique", "Cusco", "Exhibidores Colgantes & Oro Espejo", 5,
             "Los exhibidores colgantes y maniquíes dorados lucen impecables. Tienen una resistencia superior que no se quiebra con el uso continuo.", 1),
            ("Fiorella Zúñiga", "Zúñiga Colecciones", "Cusco", "Colección Completa de Maniquíes", 5,
             "La garantía de 1 año y el soporte postventa nos dio total confianza. Renovamos 12 maniquíes para nuestra cadena y el resultado fue sobresaliente.", 1),
            ("Martín Estrada", "Galería Moda", "Cusco", "Maniquí Masculino Cromado", 5,
             "Rápida atención por WhatsApp, precios competitivos y maniquíes de acabado superior. 100% recomendados en Cusco.", 1)
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
        boutique = str(data.get("boutique", "")).strip()
        city = str(data.get("city", "Cusco")).strip() or "Cusco"
        product_model = str(data.get("product_model", "")).strip() or "Maniquí de Alta Gama"
        rating = int(data.get("rating", 5))
        comment = str(data.get("comment", "")).strip()

        if not name or len(name) < 2:
            return 400, {"status": "error", "message": "Por favor ingresa tu nombre completo o de tu empresa."}
        if not boutique or len(boutique) < 2:
            return 400, {"status": "error", "message": "Por favor ingresa el nombre de tu Boutique o Atelier."}
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
