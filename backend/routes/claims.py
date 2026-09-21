"""
Rutas para el Libro de Reclamaciones Virtual.
Cumple estrictamente con la normativa peruana de Indecopi (D.S. N° 011-2011-PCM).
"""

from typing import Any, Dict, Tuple, Union
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
from backend.models.claim import create_claim, get_all_claims, get_claim_by_code


def handle_create_claim(payload: Dict[str, Any]) -> Union[Dict[str, Any], Tuple[Dict[str, Any], int]]:
    """Maneja POST /api/claims."""
    try:
        result = create_claim(payload)
        # Añadir datos de la empresa para la constancia formal
        result["company_info"] = {
            "legal_name": COMPANY_LEGAL_NAME,
            "commercial_name": COMPANY_COMMERCIAL_NAME,
            "tax_id": COMPANY_TAX_ID,
            "dni": COMPANY_DNI,
            "address": COMPANY_ADDRESS,
            "stand": COMPANY_STAND,
            "email": COMPANY_LEGAL_EMAIL,
            "phone_catalog": COMPANY_PHONE_CATALOG,
            "phone_admin": COMPANY_PHONE_ADMIN,
            "legal_response_time": f"Máximo {CLAIM_RESPONSE_DAYS} días hábiles según normativa del Indecopi (Ley N° 29571)."
        }
        return {
            "success": True,
            "data": result
        }, 201
    except ValueError as ve:
        return {"success": False, "error": str(ve)}, 400
    except Exception as e:
        return {"success": False, "error": "No se pudo procesar la hoja de reclamación. Intente nuevamente."}, 500


def handle_get_claim_detail(claim_code: str) -> Union[Dict[str, Any], Tuple[Dict[str, Any], int]]:
    """Maneja GET /api/claims/<code_or_all>."""
    if claim_code == "all":
        claims = get_all_claims()
        return {"success": True, "count": len(claims), "data": claims}

    claim = get_claim_by_code(claim_code)
    if not claim:
        return {"success": False, "error": f"No se encontró ninguna reclamación con el código '{claim_code}'."}, 404

    return {"success": True, "data": claim}
