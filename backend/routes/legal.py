"""
Rutas para información legal, términos y condiciones y política de privacidad.
Adaptado a la legislación peruana (Indecopi, Ley 29733, SUNAT).
"""

from typing import Any, Dict
from backend.config import (
    CLAIM_RESPONSE_DAYS,
    COMPANY_ACTIVITY,
    COMPANY_ADDRESS,
    COMPANY_COMMERCIAL_NAME,
    COMPANY_DNI,
    COMPANY_EMAIL,
    COMPANY_HOURS_SATURDAYS,
    COMPANY_HOURS_SUNDAYS,
    COMPANY_HOURS_WEEKDAYS,
    COMPANY_LEGAL_EMAIL,
    COMPANY_LEGAL_NAME,
    COMPANY_PHONE_ADMIN,
    COMPANY_PHONE_CATALOG,
    COMPANY_REGIMEN,
    COMPANY_STAND,
    COMPANY_TAX_ID,
    CURRENCY,
    CURRENCY_SYMBOL,
    TAX_DISCLAIMER,
    WARRANTY_MONTHS,
)


def handle_get_legal_info() -> Dict[str, Any]:
    """Maneja GET /api/legal."""
    return {
        "success": True,
        "data": {
            "company": {
                "legal_name": COMPANY_LEGAL_NAME,
                "commercial_name": COMPANY_COMMERCIAL_NAME,
                "tax_id": COMPANY_TAX_ID,
                "dni": COMPANY_DNI,
                "regimen": COMPANY_REGIMEN,
                "activity": COMPANY_ACTIVITY,
                "address": COMPANY_ADDRESS,
                "stand": COMPANY_STAND,
                "phone_catalog": COMPANY_PHONE_CATALOG,
                "phone_admin": COMPANY_PHONE_ADMIN,
                "email_contact": COMPANY_EMAIL,
                "email_legal": COMPANY_LEGAL_EMAIL,
                "hours_weekdays": COMPANY_HOURS_WEEKDAYS,
                "hours_saturdays": COMPANY_HOURS_SATURDAYS,
                "hours_sundays": COMPANY_HOURS_SUNDAYS,
                "claim_response_days": CLAIM_RESPONSE_DAYS,
                "warranty_months": WARRANTY_MONTHS,
                "currency": CURRENCY,
                "currency_symbol": CURRENCY_SYMBOL,
                "tax_disclaimer": TAX_DISCLAIMER
            },
            "legal_policies": {
                "claims_legislation": f"Conforme al Código de Protección y Defensa del Consumidor (Ley N° 29571) y D.S. N° 011-2011-PCM, las reclamaciones serán atendidas en un plazo máximo de {CLAIM_RESPONSE_DAYS} días hábiles.",
                "privacy_legislation": "En cumplimiento de la Ley N° 29733 (Ley de Protección de Datos Personales de Perú) y su Reglamento D.S. 003-2013-JUS, sus datos personales son tratados con estricta confidencialidad para fines de atención comercial y gestión de pedidos.",
                "arco_rights": f"Puede ejercer sus derechos de Acceso, Rectificación, Cancelación y Oposición (ARCO) dirigiendo una solicitud formal a {COMPANY_LEGAL_EMAIL}."
            }
        }
    }
