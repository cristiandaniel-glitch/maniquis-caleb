"""
Controladores de la API REST. Importar este paquete registra todas las rutas
en `backend.web.router.router`. Para agregar un tema nuevo: crea su archivo
aquí, decora sus funciones con @router.get/post/... y añádelo a la lista.
"""

from backend.routes import (  # noqa: F401
    auth,
    categories,
    claims,
    health,
    legal,
    messages,
    products,
    reviews,
    stats,
)
