#!/usr/bin/env python3
"""
Genera las credenciales del panel /admin para pegarlas en el archivo .env.

    python scripts/generar_clave_admin.py

Pide la contraseña sin mostrarla en pantalla y escribe ADMIN_SALT,
ADMIN_PASSWORD_HASH y SESSION_SECRET. La contraseña nunca se guarda.
"""

import getpass
import hashlib
import secrets
import sys

ITERATIONS = 100_000


def main() -> int:
    password = getpass.getpass("Nueva contraseña del panel (mín. 12 caracteres): ")
    if len(password) < 12:
        print("La contraseña es muy corta. Usa al menos 12 caracteres (mejor una frase).")
        return 1
    if password != getpass.getpass("Repite la contraseña: "):
        print("Las contraseñas no coinciden.")
        return 1
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), ITERATIONS).hex()
    print("\nCopia estas líneas en tu .env (y en las variables del hosting):\n")
    print(f"ADMIN_SALT={salt}")
    print(f"ADMIN_PASSWORD_HASH={digest}")
    print(f"SESSION_SECRET={secrets.token_hex(32)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
