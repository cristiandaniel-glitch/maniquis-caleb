"""
Punto de entrada del backend (se mantiene por compatibilidad: server.py y
`python -m backend.app` siguen funcionando igual).

La lógica está repartida así:
    backend/web/    servidor, manejador HTTP, enrutador, caché y archivos
    backend/routes/  controladores de la API (un archivo por tema)
    backend/models/  consultas a PostgreSQL
    backend/core/    autenticación, validación, rate limit y moderación
"""

from backend.web.server import run_server

__all__ = ["run_server"]

if __name__ == "__main__":
    run_server()
