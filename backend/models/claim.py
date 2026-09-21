"""
Modelo para el Libro de Reclamaciones Virtual.
Cumple con la normativa legal de protección al consumidor y comercio electrónico.
"""

import datetime
from typing import Any, Dict, List, Optional
from backend.database import execute_mutation, query_all, query_one
from backend.security import (
    is_valid_doc_number,
    is_valid_email,
    is_valid_phone,
    sanitize_string,
)


def generate_claim_code(claim_type: str) -> str:
    """Genera un código único secuencial para la Hoja de Reclamación."""
    year = datetime.datetime.now().year
    prefix = "REC" if claim_type == "Reclamo" else "QUE"
    
    # Obtener el último número del año
    sql = "SELECT COUNT(*) as total FROM claims_book WHERE claim_code LIKE ?"
    res = query_one(sql, (f"{prefix}-{year}-%",))
    count = (res["total"] if res else 0) + 1
    return f"{prefix}-{year}-{count:04d}"


def create_claim(data: Dict[str, Any]) -> Dict[str, Any]:
    """Valida y crea una nueva entrada en el Libro de Reclamaciones Virtual."""
    claim_type = data.get("claim_type", "Reclamo")
    if claim_type not in ("Reclamo", "Queja"):
        raise ValueError("El tipo de reclamación debe ser 'Reclamo' o 'Queja'.")

    full_name = sanitize_string(data.get("full_name", ""))
    doc_type = sanitize_string(data.get("doc_type", "DNI"))
    doc_number = sanitize_string(data.get("doc_number", ""))
    email = sanitize_string(data.get("email", ""))
    phone = sanitize_string(data.get("phone", ""))
    address = sanitize_string(data.get("address", ""))
    is_minor = 1 if data.get("is_minor") else 0
    guardian_name = sanitize_string(data.get("guardian_name", ""))

    contracted_good = data.get("contracted_good", "Producto")
    if contracted_good not in ("Producto", "Servicio"):
        raise ValueError("El bien contratado debe ser 'Producto' o 'Servicio'.")

    amount_claimed = float(data.get("amount_claimed", 0.0) or 0.0)
    good_description = sanitize_string(data.get("good_description", ""))
    claim_description = sanitize_string(data.get("claim_description", ""))
    consumer_request = sanitize_string(data.get("consumer_request", ""))

    # Validaciones legales mínimas
    if not full_name or len(full_name) < 3:
        raise ValueError("Debe ingresar su nombre completo.")
    if not doc_number or not is_valid_doc_number(doc_number):
        raise ValueError("Debe ingresar un número de documento válido.")
    if not email or not is_valid_email(email):
        raise ValueError("Debe ingresar un correo electrónico válido.")
    if not is_valid_phone(phone):
        raise ValueError("El número telefónico no tiene un formato válido.")
    if not good_description or len(good_description) < 5:
        raise ValueError("Debe detallar el bien o servicio contratado.")
    if not claim_description or len(claim_description) < 10:
        raise ValueError("Debe detallar los motivos de su queja o reclamo.")
    if not consumer_request or len(consumer_request) < 5:
        raise ValueError("Debe especificar su pedido o solución esperada.")

    claim_code = generate_claim_code(claim_type)

    sql = """
        INSERT INTO claims_book (
            claim_code, claim_type, full_name, doc_type, doc_number,
            email, phone, address, is_minor, guardian_name,
            contracted_good, amount_claimed, good_description,
            claim_description, consumer_request, status
        ) VALUES (
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?,
            ?, ?, 'Pendiente'
        )
    """
    execute_mutation(sql, (
        claim_code, claim_type, full_name, doc_type, doc_number,
        email, phone, address, is_minor, guardian_name,
        contracted_good, amount_claimed, good_description,
        claim_description, consumer_request
    ))

    return {
        "claim_code": claim_code,
        "claim_type": claim_type,
        "full_name": full_name,
        "created_at": datetime.datetime.now().isoformat(),
        "status": "Pendiente",
        "message": f"Su {claim_type.lower()} ha sido registrado formalmente bajo el código {claim_code}."
    }


def get_claim_by_code(claim_code: str) -> Optional[Dict[str, Any]]:
    """Obtiene una hoja de reclamación por su código único de seguimiento."""
    sql = "SELECT * FROM claims_book WHERE claim_code = ?"
    return query_one(sql, (claim_code.strip(),))


def get_all_claims(limit: int = 50) -> List[Dict[str, Any]]:
    """Obtiene el listado de reclamaciones para gestión administrativa."""
    sql = "SELECT * FROM claims_book ORDER BY created_at DESC LIMIT ?"
    return query_all(sql, (limit,))
