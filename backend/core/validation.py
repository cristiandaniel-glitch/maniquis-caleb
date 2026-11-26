"""
Validación y limpieza de datos que llegan del navegador.

Regla del proyecto: el servidor nunca confía en lo que envía el frontend.
Cada campo se convierte al tipo esperado y, si no se puede, se responde 400
con un mensaje claro (nunca un error 500 ni un detalle interno).
"""

import html
import re
from typing import Any, Optional


class ValidationError(ValueError):
    """Dato inválido enviado por el cliente. Su mensaje se muestra al usuario."""


def sanitize_string(val: Any, max_length: int = 10_000) -> str:
    """Recorta y escapa caracteres HTML para que un texto nunca se ejecute como código."""
    if val is None:
        return ""
    if not isinstance(val, str):
        val = str(val)
    return html.escape(val.strip()[:max_length], quote=True)


def clean_text(val: Any, field: str, max_length: int, required: bool = False, min_length: int = 0) -> str:
    """Texto escapado con límites de longitud medidos sobre lo que escribió el usuario."""
    raw = "" if val is None else str(val).strip()
    if required and not raw:
        raise ValidationError(f"El campo «{field}» es obligatorio.")
    if raw and len(raw) < min_length:
        raise ValidationError(f"El campo «{field}» es demasiado corto.")
    if len(raw) > max_length:
        raise ValidationError(f"El campo «{field}» no puede superar {max_length} caracteres.")
    return sanitize_string(raw, max_length)


def to_int(val: Any, field: str, minimum: Optional[int] = None, maximum: Optional[int] = None) -> int:
    if isinstance(val, bool):
        raise ValidationError(f"«{field}» debe ser un número entero.")
    try:
        number = int(str(val).strip())
    except (TypeError, ValueError):
        raise ValidationError(f"«{field}» debe ser un número entero.") from None
    if minimum is not None and number < minimum:
        raise ValidationError(f"«{field}» no puede ser menor que {minimum}.")
    if maximum is not None and number > maximum:
        raise ValidationError(f"«{field}» no puede ser mayor que {maximum}.")
    return number


def to_money(val: Any, field: str, maximum: float = 10_000_000) -> float:
    if isinstance(val, bool):
        raise ValidationError(f"«{field}» debe ser un monto.")
    try:
        number = round(float(str(val).strip() or 0), 2)
    except (TypeError, ValueError):
        raise ValidationError(f"«{field}» debe ser un monto válido.") from None
    if number != number or number < 0 or number > maximum:  # NaN, negativos o absurdos
        raise ValidationError(f"«{field}» debe estar entre 0 y {maximum:,.0f}.")
    return number


def to_bool(val: Any) -> bool:
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        return val != 0
    return str(val).strip().lower() in ("true", "1", "on", "yes", "si", "sí")


# Fotos de productos: solo archivos del propio sitio dentro de /assets/productos/.
_PRODUCT_IMAGE = re.compile(r"^/assets/productos/[A-Za-z0-9_\-]+\.(?:webp|png|jpe?g)$")
DEFAULT_PRODUCT_IMAGE = "/assets/productos/maniqui-femenino-abstracto-blanco.webp"


def clean_product_image(val: Any) -> str:
    raw = str(val or "").strip()
    if not raw:
        return DEFAULT_PRODUCT_IMAGE
    if not _PRODUCT_IMAGE.match(raw):
        raise ValidationError("La foto debe estar en /assets/productos/ y terminar en .webp, .png o .jpg.")
    return raw


def is_valid_email(email: str) -> bool:
    if not email or len(email) > 254:
        return False
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email.strip()))


def is_valid_phone(phone: str) -> bool:
    if not phone:
        return True
    return bool(re.match(r"^[+0-9\s\-()]{6,20}$", phone.strip()))


def is_valid_doc_number(doc_number: str) -> bool:
    if not doc_number:
        return False
    return bool(re.match(r"^[a-zA-Z0-9\-]{5,20}$", doc_number.strip()))
