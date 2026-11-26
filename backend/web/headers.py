"""Cabeceras HTTP de seguridad y CORS."""

from typing import Dict, Optional

from backend.config import CORS_ALLOWED_ORIGINS, ENABLE_HSTS

# Google Maps se muestra dentro de un <iframe> (minimapa). Es lo único externo
# que puede incrustarse en el sitio.
_CSP = "; ".join([
    "default-src 'self'",
    "script-src 'self' 'unsafe-inline'",
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
    "font-src 'self' https://fonts.gstatic.com data:",
    "img-src 'self' data: blob: https:",
    "connect-src 'self'",
    "frame-src https://www.google.com https://maps.google.com",
    "object-src 'none'",
    "base-uri 'self'",
    "form-action 'self'",
    "frame-ancestors 'self'",
])


def security_headers() -> Dict[str, str]:
    headers = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "SAMEORIGIN",
        # La cabecera X-XSS-Protection está obsoleta y puede abrir fugas en
        # navegadores antiguos; la recomendación actual es desactivarla.
        "X-XSS-Protection": "0",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Content-Security-Policy": _CSP,
        "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=()",
        "Cross-Origin-Opener-Policy": "same-origin",
    }
    if ENABLE_HSTS:
        headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return headers


def cors_headers(origin: Optional[str]) -> Dict[str, str]:
    """Solo responde CORS a orígenes de la lista blanca (nunca refleja cualquiera)."""
    if not origin or origin not in CORS_ALLOWED_ORIGINS:
        return {}
    return {
        "Access-Control-Allow-Origin": origin,
        "Vary": "Origin",
        "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
        "Access-Control-Max-Age": "86400",
    }
