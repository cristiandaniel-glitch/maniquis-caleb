#!/usr/bin/env python3
"""
Punto de entrada principal para ejecutar la aplicación Maniquí Studio.
Verifica la inicialización de la base de datos y arranca el servidor HTTP / REST API.
"""

import os
import sys

# Añadir el directorio raíz al path de Python
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from database.init_db import init_database
from backend.app import run_server
from backend.config import DB_PATH

if __name__ == "__main__":
    print("[*] Verificando estado del sistema y base de datos...")
    if not os.path.exists(DB_PATH):
        print("[i] Base de datos no encontrada. Inicializando automáticamente...")
        init_database()
    else:
        print("[✔] Base de datos detectada y lista.")

    run_server()
