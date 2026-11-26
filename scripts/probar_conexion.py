#!/usr/bin/env python3
"""
Prueba la conexión a la base de datos del archivo .env.

    python scripts/probar_conexion.py

Supabase usa servidores "pooler" con nombres como
aws-0-sa-east-1.pooler.supabase.com o aws-1-sa-east-1.pooler.supabase.com,
y depende del proyecto cuál corresponde. Si el del .env no funciona, el
script prueba las otras variantes y, si encuentra la buena, corrige el .env.
"""

import os
import re
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")

try:
    import psycopg
    from dotenv import dotenv_values
except ImportError:
    print("Primero instala las dependencias: pip install -r requirements.txt")
    sys.exit(1)


def try_url(url: str, sslmode: str) -> str:
    try:
        with psycopg.connect(url, sslmode=sslmode, connect_timeout=8, prepare_threshold=None) as conn:
            conn.execute("SELECT 1")
        return ""
    except Exception as error:  # noqa: BLE001 - solo se muestra el tipo de error
        return str(error).strip().splitlines()[0][:120]


def main() -> int:
    if not os.path.exists(ENV_PATH):
        print("No existe el archivo .env en la carpeta del proyecto.")
        return 1
    env = dotenv_values(ENV_PATH)
    url = (env.get("DATABASE_URL") or "").strip()
    sslmode = (env.get("DATABASE_SSLMODE") or "require").strip()
    if not url:
        print("El .env no tiene DATABASE_URL.")
        return 1

    host = re.search(r"@([^:/]+)", url)
    print(f"Probando {host.group(1) if host else 'la base'} ...")
    error = try_url(url, sslmode)
    if not error:
        print("✅ Conexión correcta. Ya puedes iniciar: python3 server.py")
        return 0
    print(f"   No conectó: {error}")

    match = re.search(r"aws-(\d+)-([a-z0-9-]+)\.pooler\.supabase\.com", url)
    if not match:
        print("❌ Revisa DATABASE_URL en Supabase → Connect.")
        return 1
    for n in ("0", "1", "2"):
        if n == match.group(1):
            continue
        candidate = url.replace(match.group(0), f"aws-{n}-{match.group(2)}.pooler.supabase.com")
        print(f"Probando aws-{n}-{match.group(2)} ...")
        if not try_url(candidate, sslmode):
            with open(ENV_PATH, encoding="utf-8") as handle:
                text = handle.read()
            with open(ENV_PATH, "w", encoding="utf-8") as handle:
                handle.write(text.replace(url, candidate))
            print(f"✅ Conectó con aws-{n}. Corregí tu .env.")
            print("   Usa este mismo valor de DATABASE_URL en Vercel.")
            return 0
    print("❌ Ninguna variante conectó. Copia la cadena exacta de Supabase → Connect → Transaction pooler.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
