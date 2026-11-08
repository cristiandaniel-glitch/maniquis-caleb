#!/usr/bin/env python3
"""Valida el esquema PostgreSQL/Supabase configurado para la aplicación.

El antiguo inicializador SQLite fue retirado para impedir que un integrante
arranque accidentalmente una base local distinta a la del equipo. El esquema se
aplica como migración versionada desde ``schema.postgres.sql`` en Supabase.
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.database import close_connection_pool, verify_database_schema


def init_database(force_reset: bool = False) -> None:
    """Mantiene compatibilidad con scripts previos, sin crear ni borrar datos."""
    if force_reset:
        raise RuntimeError(
            "--reset ya no está disponible: la base compartida no se borra desde "
            "este proyecto. Use una migración revisada en Supabase."
        )
    try:
        verify_database_schema()
        print("[✓] PostgreSQL/Supabase conectado y esquema validado.")
    finally:
        close_connection_pool()


if __name__ == "__main__":
    init_database(force_reset="--reset" in sys.argv)
