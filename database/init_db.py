#!/usr/bin/env python3
"""
Script de inicialización de la base de datos SQLite para Maniquí Studio.
Crea las tablas según schema.sql e inserta los datos iniciales de seed.sql.
"""

import os
import sqlite3
import sys

# Rutas base
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "maniqui.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "database", "schema.sql")
SEED_PATH = os.path.join(BASE_DIR, "database", "seed.sql")


def init_database(force_reset: bool = False) -> None:
    """Inicializa la base de datos aplicando schema y seed."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    if force_reset and os.path.exists(DB_PATH):
        print(f"[*] Eliminando base de datos anterior: {DB_PATH}")
        os.remove(DB_PATH)

    print(f"[*] Conectando a base de datos en: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 1. Habilitar claves foráneas
        cursor.execute("PRAGMA foreign_keys = ON;")

        # 2. Ejecutar esquema
        print("[*] Aplicando esquema de tablas...")
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            schema_sql = f.read()
        cursor.executescript(schema_sql)

        # 3. Insertar datos iniciales si no existen
        cursor.execute("SELECT COUNT(*) FROM products;")
        count = cursor.fetchone()[0]
        if count == 0:
            print("[*] Poblando datos iniciales (Seed Data)...")
            with open(SEED_PATH, "r", encoding="utf-8") as f:
                seed_sql = f.read()
            cursor.executescript(seed_sql)
            print("[+] Datos iniciales cargados correctamente.")
        else:
            print(f"[i] La base de datos ya contiene {count} productos. Saltando seed.")

        conn.commit()
        print("[✔] Base de datos inicializada con éxito y lista para producción.")
    except Exception as e:
        conn.rollback()
        print(f"[!] Error al inicializar la base de datos: {e}", file=sys.stderr)
        raise e
    finally:
        conn.close()


if __name__ == "__main__":
    reset = "--reset" in sys.argv
    init_database(force_reset=reset)
