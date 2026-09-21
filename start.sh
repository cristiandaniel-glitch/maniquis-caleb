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

# 1. Verificar existencia de base de datos
if [ ! -f "database/maniqui.db" ]; then
    echo "[*] Base de datos no encontrada. Inicializando..."
    python3 database/init_db.py
fi

# 2. Iniciar servidor principal
echo "[*] Arrancando servidor HTTP y REST API..."
python3 server.py
