"""
Modelo para el Libro de Reclamaciones Virtual.
Cumple con la normativa legal de protección al consumidor y comercio electrónico.
"""

import datetime
from typing import Any, Dict, List, Optional
from backend.database import get_db_connection, query_all, query_one
from backend.core.validation import (
    ValidationError,
    is_valid_doc_number,
    is_valid_email,
    is_valid_phone,
    sanitize_string,
    to_bool,
    to_money,
)

DOC_TYPES = ("DNI", "CE", "Pasaporte", "RUC")


def create_claim(data: Dict[str, Any]) -> Dict[str, Any]:
    """Valida y crea una nueva entrada en el Libro de Reclamaciones Virtual."""
    claim_type = data.get("claim_type", "Reclamo")
    if claim_type not in ("Reclamo", "Queja"):
        raise ValidationError("El tipo de reclamación debe ser 'Reclamo' o 'Queja'.")

    full_name = sanitize_string(data.get("full_name", ""), 120)
    doc_type = str(data.get("doc_type") or "DNI").strip()
    if doc_type not in DOC_TYPES:
        raise ValidationError("Tipo de documento no válido.")
    doc_number = sanitize_string(data.get("doc_number", ""), 20)
    email = sanitize_string(data.get("email", ""), 254)
    phone = sanitize_string(data.get("phone", ""), 20)
    address = sanitize_string(data.get("address", ""), 250)
    is_minor = to_bool(data.get("is_minor", False))
    guardian_name = sanitize_string(data.get("guardian_name", ""), 120)

    contracted_good = data.get("contracted_good", "Producto")
    if contracted_good not in ("Producto", "Servicio"):
        raise ValidationError("El bien contratado debe ser 'Producto' o 'Servicio'.")

    amount_claimed = to_money(data.get("amount_claimed") or 0, "Monto reclamado")
    good_description = sanitize_string(data.get("good_description", ""), 1000)
    claim_description = sanitize_string(data.get("claim_description", ""), 3000)
    consumer_request = sanitize_string(data.get("consumer_request", ""), 2000)

    # Validaciones legales mínimas
    if not full_name or len(full_name) < 3:
        raise ValidationError("Debe ingresar su nombre completo.")
    if not doc_number or not is_valid_doc_number(doc_number):
        raise ValidationError("Debe ingresar un número de documento válido.")
    if not email or not is_valid_email(email):
        raise ValidationError("Debe ingresar un correo electrónico válido.")
    if not is_valid_phone(phone):
        raise ValidationError("El número telefónico no tiene un formato válido.")
    if is_minor and len(guardian_name) < 3:
        raise ValidationError("Debe ingresar el nombre del padre, madre o apoderado del menor de edad.")
    if not good_description or len(good_description) < 5:
        raise ValidationError("Debe detallar el bien o servicio contratado.")
    if not claim_description or len(claim_description) < 10:
        raise ValidationError("Debe detallar los motivos de su queja o reclamo.")
    if not consumer_request or len(consumer_request) < 5:
        raise ValidationError("Debe especificar su pedido o solución esperada.")

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
    return query_one("SELECT * FROM claims_book WHERE claim_code = %s", (claim_code.strip()[:30],))


def get_all_claims(limit: int = 1000) -> List[Dict[str, Any]]:
    """Obtiene el listado de reclamaciones para gestión administrativa."""
    sql = "SELECT * FROM claims_book ORDER BY created_at DESC LIMIT %s"
    return query_all(sql, (limit,))


CLAIM_STATUSES = ("Pendiente", "En Proceso", "Atendido", "Cerrado")


def respond_claim(claim_code: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """El proveedor cambia el estado y/o registra su respuesta al consumidor."""
    claim = get_claim_by_code(claim_code)
    if not claim:
        return None
    status = str(data.get("status") or claim["status"]).strip()
    if status not in CLAIM_STATUSES:
        raise ValidationError("Estado no válido.")
    response = data.get("admin_response")
    if response is not None:
        response = sanitize_string(response, 3000) or None
        if response and len(response) < 10:
            raise ValidationError("La respuesta debe tener al menos 10 caracteres.")
    else:
        response = claim.get("admin_response")
    if status in ("Atendido", "Cerrado") and not response:
        raise ValidationError("Para marcarlo como atendido escribe la respuesta que se dio al consumidor.")
    query_one(
        """UPDATE claims_book
           SET status = %s,
               admin_response = %s,
               response_date = CASE WHEN %s::text IS NOT NULL AND admin_response IS DISTINCT FROM %s::text
                                    THEN now() ELSE response_date END
           WHERE id = %s RETURNING id""",
        (status, response, response, response, claim["id"]),
    )
    return get_claim_by_code(claim_code)
