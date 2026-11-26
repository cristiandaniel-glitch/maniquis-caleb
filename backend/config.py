"""
Configuración centralizada de Maniquíes y Exhibidores Caleb.

Todo lo que cambia entre la PC de cada integrante y el servidor de producción
se lee de variables de entorno (archivo .env, que NO se sube a Git).
Los datos comerciales oficiales (SUNAT) están al final.
"""

import os

from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Cada integrante usa su propio .env local, excluido de Git.
load_dotenv(os.path.join(BASE_DIR, ".env"))


def _bool(name: str, default: bool = False) -> bool:
    return os.environ.get(name, str(default)).strip().lower() in ("true", "1", "yes", "si", "sí")


def _list(name: str, default: str = "") -> list:
    return [item.strip() for item in os.environ.get(name, default).split(",") if item.strip()]


# ------------------------------------------------------------------ servidor
PORT = int(os.environ.get("PORT", 8000))
HOST = os.environ.get("HOST", "0.0.0.0")
DEBUG = _bool("DEBUG")
STATIC_DIR = os.environ.get("STATIC_DIR", os.path.join(BASE_DIR, "frontend"))
MAX_THREADS = int(os.environ.get("MAX_THREADS", 256))
# Procesos de trabajo (Linux/macOS). Vacío = uno por núcleo (máx. 8).
WORKERS = os.environ.get("WORKERS", "").strip()

# ------------------------------------------------------------ base de datos
DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
# Tolera el error común de pegar DATABASE_URL=DATABASE_URL=postgresql://...
if DATABASE_URL.startswith("DATABASE_URL="):
    DATABASE_URL = DATABASE_URL[len("DATABASE_URL="):].strip()
DATABASE_SSLMODE = os.environ.get("DATABASE_SSLMODE", "require").strip()
DATABASE_POOL_MIN_SIZE = int(os.environ.get("DATABASE_POOL_MIN_SIZE", "1"))
DATABASE_POOL_MAX_SIZE = int(os.environ.get("DATABASE_POOL_MAX_SIZE", "5"))
DATABASE_POOL_TIMEOUT = float(os.environ.get("DATABASE_POOL_TIMEOUT", "10"))

# Marca local para invalidar la caché de respuestas públicas en todos los procesos.
API_CACHE_VERSION_FILE = os.environ.get(
    "API_CACHE_VERSION_FILE", os.path.join(BASE_DIR, "database", ".api-cache-version")
)

# ---------------------------------------------------------------- seguridad
# Orígenes de otros dominios que pueden llamar a la API. Vacío = solo el mismo
# dominio (lo normal: el frontend lo sirve este mismo backend).
CORS_ALLOWED_ORIGINS = _list("CORS_ALLOWED_ORIGINS")
# Tamaño máximo del cuerpo JSON de una petición (la API solo recibe formularios).
MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", 1024 * 1024))  # 1 MB
RATE_LIMIT_PER_MINUTE = int(os.environ.get("RATE_LIMIT_PER_MINUTE", 300))
FORM_RATE_LIMIT_PER_MINUTE = int(os.environ.get("FORM_RATE_LIMIT_PER_MINUTE", 30))

# Si el sitio está detrás de un proxy (Nginx, Render, Railway, Cloudflare...),
# todas las visitas llegan con la IP del proxy. Con TRUST_PROXY=true se usa la
# IP real del cliente que el proxy agrega en X-Forwarded-For. NO activarlo si
# el servidor está expuesto directamente: cualquiera podría falsificar su IP.
TRUST_PROXY = _bool("TRUST_PROXY")
# Activar solo cuando el sitio ya funciona con HTTPS (dominio con candado).
ENABLE_HSTS = _bool("ENABLE_HSTS")

# Credenciales del panel. Se generan con: python scripts/generar_clave_admin.py
# Sin ellas el panel queda bloqueado (no existe contraseña por defecto).
ADMIN_SALT = os.environ.get("ADMIN_SALT", "").strip()
ADMIN_PASSWORD_HASH = os.environ.get("ADMIN_PASSWORD_HASH", "").strip()
ADMIN_PBKDF2_ITERATIONS = int(os.environ.get("ADMIN_PBKDF2_ITERATIONS", 100_000))
# Firma de las sesiones. Si falta, se genera una al arrancar (las sesiones se
# pierden al reiniciar el servidor, pero sigue siendo seguro).
SESSION_SECRET = os.environ.get("SESSION_SECRET", "").strip()
SESSION_LIFETIME_SECONDS = 4 * 60 * 60  # 4 horas
LOGIN_MAX_ATTEMPTS = 5
LOGIN_LOCK_SECONDS = 600

# ==============================================================================
# DATOS LEGALES Y COMERCIALES OFICIALES (SUNAT - PERÚ)
# ==============================================================================
COMPANY_LEGAL_NAME = "ROMERO ENRIQUEZ PATRICK JUNIOR"
COMPANY_COMMERCIAL_NAME = "Maniquíes y Exhibidores Caleb"
COMPANY_TAX_ID = "RUC: 10727851971"
COMPANY_DNI = "DNI: 72785197"
COMPANY_REGIMEN = "Nuevo RUS (Régimen Único Simplificado)"
COMPANY_ACTIVITY = "Actividad Económica: Venta y distribución de maniquíes, bustos y colgantes de fierro, plástico y madera"

# Ubicación física del establecimiento
COMPANY_ADDRESS = "Calle 119 Tomás Tuyro Túpac (4to Paradero de San Sebastián, al frente de Tottus), Galería Comercial La Exitosa, Stand N° 3, San Sebastián, Cusco - Perú"
COMPANY_STAND = "Stand N° 3 - Galería La Exitosa (4to Paradero San Sebastián, Frente a Tottus)"
# Coordenadas del stand (13°31'51.0"S 71°55'57.6"W), usadas por el minimapa.
COMPANY_LAT = -13.530833
COMPANY_LNG = -71.932660

# Canales de comunicación
COMPANY_PHONE_CATALOG = "+51 916 126 747"  # Pedidos y Catálogo
COMPANY_PHONE_ADMIN = "+51 924 044 084"    # Administración y Gerencia
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
CLAIM_RESPONSE_DAYS = 15  # Días hábiles máximos conforme al Código de Protección al Consumidor
WARRANTY_MONTHS = 12      # 1 año de garantía comercial en estructuras
