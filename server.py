#!/usr/bin/env python3
"""Punto de entrada de Maniquí Studio con PostgreSQL/Supabase."""

import os
import sys

# Añadir el directorio raíz al path de Python
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.app import run_server

if __name__ == "__main__":
    print("[*] Verificando conexión y esquema de PostgreSQL/Supabase...")
    run_server()
