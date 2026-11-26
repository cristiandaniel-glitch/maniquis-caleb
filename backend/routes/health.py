"""Estado del servicio (para monitoreo del hosting)."""

from backend.database import database_ok
from backend.web.router import Request, router


@router.get("/api/health")
def health(req: Request):
    db = database_ok()
    return {
        "status": "healthy" if db else "degraded",
        "database": "ok" if db else "sin conexión",
        "service": "Maniquíes y Exhibidores Caleb API",
        "version": "2.1.0",
    }, (200 if db else 503)
