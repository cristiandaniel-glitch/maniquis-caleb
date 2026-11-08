"""
Modelo para el Libro de Reclamaciones Virtual.
Cumple con la normativa legal de protección al consumidor y comercio electrónico.
"""

import datetime
from typing import Any, Dict, List, Optional
from backend.database import get_db_connection, query_all, query_one
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
    
    # Siguiente al número más alto del año (no se repite aunque se borre alguno)
    sql = "SELECT MAX(CAST(substr(claim_code, 10) AS INTEGER)) AS last FROM claims_book WHERE claim_code LIKE %s"
    res = query_one(sql, (f"{prefix}-{year}-%",))
    last = (res["last"] if res and res["last"] is not None else 0)
    return f"{prefix}-{year}-{last + 1:04d}"


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
    is_minor = bool(data.get("is_minor"))
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
    if is_minor and len(guardian_name) < 3:
        raise ValueError("Debe ingresar el nombre del padre, madre o apoderado del menor de edad.")
    if not good_description or len(good_description) < 5:
        raise ValueError("Debe detallar el bien o servicio contratado.")
    if not claim_description or len(claim_description) < 10:
        raise ValueError("Debe detallar los motivos de su queja o reclamo.")
    if not consumer_request or len(consumer_request) < 5:
        raise ValueError("Debe especificar su pedido o solución esperada.")

    sql = """
        INSERT INTO claims_book (
            claim_code, claim_type, full_name, doc_type, doc_number,
            email, phone, address, is_minor, guardian_name,
            contracted_good, amount_claimed, good_description,
            claim_description, consumer_request, status
        ) VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s,
            %s, %s, 'Pendiente'
        )
    """
    year = datetime.datetime.now().year
    prefix = "REC" if claim_type == "Reclamo" else "QUE"

    # Serializa solo la generación del código para el tipo y año respectivos.
    # Evita duplicados con varios procesos/backend workers sin relajar UNIQUE.
    with get_db_connection() as conn:
        conn.execute(
            "SELECT pg_advisory_xact_lock(hashtext(%s))",
            (f"claim-code:{prefix}:{year}",),
        )
        row = conn.execute(
            """SELECT MAX(CAST(substr(claim_code, 10) AS INTEGER)) AS last
               FROM claims_book WHERE claim_code LIKE %s""",
            (f"{prefix}-{year}-%",),
        ).fetchone()
        last = row["last"] if row and row["last"] is not None else 0
        claim_code = f"{prefix}-{year}-{int(last) + 1:04d}"
        conn.execute(sql, (
            claim_code, claim_type, full_name, doc_type, doc_number,
            email, phone, address, bool(is_minor), guardian_name or None,
            contracted_good, amount_claimed, good_description,
            claim_description, consumer_request,
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
    sql = "SELECT * FROM claims_book WHERE claim_code = %s"
    return query_one(sql, (claim_code.strip(),))


def get_all_claims(limit: int = 1000) -> List[Dict[str, Any]]:
    """Obtiene el listado de reclamaciones para gestión administrativa."""
    sql = "SELECT * FROM claims_book ORDER BY created_at DESC LIMIT %s"
    return query_all(sql, (limit,))
