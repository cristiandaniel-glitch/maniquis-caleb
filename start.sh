#!/usr/bin/env bash
# ==============================================================================
# Script de Inicio Rápido: Maniquí Studio Web
# ==============================================================================

set -e

echo "========================================================"
echo "✨ INICIANDO MANIQUÍ STUDIO & BOUTIQUE"
echo "========================================================"

# Obtener directorio del script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# DATABASE_URL debe estar definida en .env o en las variables del entorno.
# Instalar una sola vez: python3 -m pip install -r requirements.txt
echo "[*] Arrancando servidor HTTP y REST API..."
python3 server.py
