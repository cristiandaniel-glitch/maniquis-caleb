"""
Rutas para el Libro de Reclamaciones Virtual.
Cumple estrictamente con la normativa peruana de Indecopi (D.S. N° 011-2011-PCM).
"""

from backend.config import (
    CLAIM_RESPONSE_DAYS,
    COMPANY_ADDRESS,
    COMPANY_COMMERCIAL_NAME,
    COMPANY_DNI,
    COMPANY_LEGAL_EMAIL,
    COMPANY_LEGAL_NAME,
    COMPANY_PHONE_ADMIN,
    COMPANY_PHONE_CATALOG,
    COMPANY_STAND,
    COMPANY_TAX_ID,
)
from backend.models.claim import create_claim, get_all_claims, get_claim_by_code, respond_claim
from backend.web.router import Request, fail, ok, router


COMPANY_INFO = {
    "legal_name": COMPANY_LEGAL_NAME,
    "commercial_name": COMPANY_COMMERCIAL_NAME,
    "tax_id": COMPANY_TAX_ID,
    "dni": COMPANY_DNI,
    "address": COMPANY_ADDRESS,
    "stand": COMPANY_STAND,
    "email": COMPANY_LEGAL_EMAIL,
    "phone_catalog": COMPANY_PHONE_CATALOG,
    "phone_admin": COMPANY_PHONE_ADMIN,
    "legal_response_time": f"Máximo {CLAIM_RESPONSE_DAYS} días hábiles según normativa del Indecopi (Ley N° 29571).",
}

# Datos que ve cualquiera que consulte un código (sin datos personales: los
# códigos son correlativos y se pueden adivinar — Ley 29733).
PUBLIC_CLAIM_FIELDS = ("claim_code", "claim_type", "status", "created_at", "response_date")


@router.post("/api/claims", honeypot=True)
def create(req: Request):
    result = create_claim(req.body)
    result["company_info"] = COMPANY_INFO
    return ok(result, 201)


@router.get("/api/claims/all", admin=True)
def list_all(req: Request):
    claims = get_all_claims()
    return ok(claims, count=len(claims))


@router.get("/api/claims/<code>")
def detail(req: Request):
    """Consulta pública del estado. Con sesión de administrador devuelve la hoja completa."""
    claim = get_claim_by_code(req.params["code"])
    if not claim:
        return fail("No se encontró ninguna reclamación con ese código.", 404)
    if not req.is_admin:
        claim = {key: claim.get(key) for key in PUBLIC_CLAIM_FIELDS}
    return ok(claim)


@router.patch("/api/claims/<code>", admin=True)
def respond(req: Request):
    """Panel: {"status": "Atendido", "admin_response": "..."}"""
    claim = respond_claim(req.params["code"], req.body)
    if not claim:
        return fail("No se encontró ninguna reclamación con ese código.", 404)
    return ok(claim, message="Reclamo actualizado.")
