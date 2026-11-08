"""
Configuración centralizada del sistema Novedades Caleb / Maniquíes Caleb.
Datos oficiales conforme al Registro Único de Contribuyentes (SUNAT - Perú).
"""

import os

from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# En producción las variables deben configurarse en el proveedor. Este archivo
# permite que cada integrante use su propio .env local, que está excluido de Git.
load_dotenv(os.path.join(BASE_DIR, ".env"))

# Servidor
PORT = int(os.environ.get("PORT", 8000))
HOST = os.environ.get("HOST", "0.0.0.0")
DEBUG = os.environ.get("DEBUG", "False").lower() in ("true", "1", "yes")

# Base de datos PostgreSQL / Supabase. La validación se hace al iniciar el
# servidor, para que no se arranque accidentalmente contra una base local.
DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
# Tolera el error común de pegar la asignación completa dentro del valor, por
# ejemplo DATABASE_URL=DATABASE_URL=postgresql://...; el prefijo se elimina en
# memoria y nunca se registra ni se muestra la credencial.
if DATABASE_URL.startswith("DATABASE_URL="):
    DATABASE_URL = DATABASE_URL[len("DATABASE_URL="):].strip()
DATABASE_SSLMODE = os.environ.get("DATABASE_SSLMODE", "require").strip()
DATABASE_POOL_MIN_SIZE = int(os.environ.get("DATABASE_POOL_MIN_SIZE", "1"))
DATABASE_POOL_MAX_SIZE = int(os.environ.get("DATABASE_POOL_MAX_SIZE", "5"))
DATABASE_POOL_TIMEOUT = float(os.environ.get("DATABASE_POOL_TIMEOUT", "10"))

# Marca local para invalidar la caché de respuestas públicas de cada proceso.
# No contiene datos ni credenciales de la base de datos.
API_CACHE_VERSION_FILE = os.environ.get(
    "API_CACHE_VERSION_FILE", os.path.join(BASE_DIR, "database", ".api-cache-version")
)

# Directorio de Frontend y estáticos
STATIC_DIR = os.environ.get("STATIC_DIR", os.path.join(BASE_DIR, "frontend"))

# Seguridad
CORS_ALLOWED_ORIGINS = os.environ.get("CORS_ALLOWED_ORIGINS", "*").split(",")
MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", 10 * 1024 * 1024)) # 10 MB
RATE_LIMIT_PER_MINUTE = int(os.environ.get("RATE_LIMIT_PER_MINUTE", 300))

# ==============================================================================
# DATOS LEGALES Y COMERCIALES OFICIALES (SUNAT - PERÚ)
# ==============================================================================
COMPANY_LEGAL_NAME = "ROMERO ENRIQUEZ PATRICK JUNIOR"
COMPANY_COMMERCIAL_NAME = "NOVEDADES CALEB - Maniquíes & Exhibidores"
COMPANY_TAX_ID = "RUC: 10727851971"
COMPANY_DNI = "DNI: 72785197"
COMPANY_REGIMEN = "Nuevo RUS (Régimen Único Simplificado)"
COMPANY_ACTIVITY = "Actividad Económica: Venta y distribución de maniquíes, bustos y colgantes de fierro, plástico y madera"

# Ubicación física del establecimiento
COMPANY_ADDRESS = "Calle 119 Tomás Tuyro Túpac (4to Paradero de San Sebastián, al frente de Tottus), Galería Comercial La Exitosa, Stand N° 3, San Sebastián, Cusco - Perú"
COMPANY_STAND = "Stand N° 3 - Galería La Exitosa (4to Paradero San Sebastián, Frente a Tottus)"

# Canales de comunicación
COMPANY_PHONE_CATALOG = "+51 916 126 747" # Pedidos y Catálogo
COMPANY_PHONE_ADMIN = "+51 924 044 084"   # Administración y Gerencia
COMPANY_EMAIL = "maniquicaleb.pe@gmail.com"
COMPANY_LEGAL_EMAIL = "legal.exhicaleb.pe@gmail.com"

# Horarios de Atención
COMPANY_HOURS_WEEKDAYS = "Lunes a Viernes: 8:00 AM - 6:00 PM (Almuerzo: 1:00 PM - 3:00 PM)"
COMPANY_HOURS_SATURDAYS = "Sábados: 8:00 AM - 12:00 PM"
COMPANY_HOURS_SUNDAYS = "Domingos: Cerrado"

# Moneda y Facturación
CURRENCY = "PEN"
CURRENCY_SYMBOL = "S/"
TAX_DISCLAIMER = "Precios en Soles peruanos (S/). Contribuyente sujeto al Nuevo Régimen Único Simplificado (Nuevo RUS) - Emisión de Boleta de Venta y Guía de Remisión."

# Libro de Reclamaciones (Normativa Indecopi - D.S. N° 011-2011-PCM)
CLAIM_RESPONSE_DAYS = 15 # Días hábiles máximos conforme al Código de Protección al Consumidor
WARRANTY_MONTHS = 12    # 1 año de garantía comercial en estructuras
