"""Suscripción al boletín."""

from backend.models.subscriber import add_subscriber, get_all_subscribers
from backend.web.router import Request, ok, router


@router.post("/api/subscribe", honeypot=True)
def subscribe(req: Request):
    return ok(add_subscriber(str(req.body.get("email") or "")), 201)


@router.get("/api/subscribers", admin=True)
def list_all(req: Request):
    subscribers = get_all_subscribers()
    return ok(subscribers, count=len(subscribers))
