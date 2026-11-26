"""Estado del servicio (para monitoreo del hosting)."""

from backend.web.router import Request, router


@router.get("/api/health")
def health(req: Request):
    return {"status": "healthy", "service": "Maniquíes y Exhibidores Caleb API", "version": "2.0.0"}, 200
