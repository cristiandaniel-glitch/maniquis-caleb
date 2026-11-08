#!/usr/bin/env python3
"""Migra datos existentes de SQLite a PostgreSQL/Supabase de forma idempotente.

No crea el esquema ni borra datos: ejecuta primero schema.postgres.sql en
Supabase. El comando requiere una ruta explícita al archivo SQLite para evitar
migraciones accidentales.
"""

import argparse
import datetime as dt
import ipaddress
import os
import sqlite3
import sys
from typing import Any, Dict, Iterable, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import psycopg
from psycopg import sql
from psycopg.rows import dict_row

from backend.config import DATABASE_SSLMODE, DATABASE_URL


TABLES: Tuple[Tuple[str, Tuple[str, ...], Tuple[str, ...]], ...] = (
    ("categories", ("id", "name", "slug", "description", "icon", "display_order", "is_active", "created_at", "updated_at"), ("is_active",)),
    ("products", ("id", "category_id", "name", "slug", "sku", "description", "material", "color", "dimensions", "price", "stock", "image_url", "is_featured", "is_active", "created_at", "updated_at"), ("is_featured", "is_active")),
    ("claims_book", ("id", "claim_code", "claim_type", "full_name", "doc_type", "doc_number", "email", "phone", "address", "is_minor", "guardian_name", "contracted_good", "amount_claimed", "good_description", "claim_description", "consumer_request", "status", "admin_response", "response_date", "created_at", "updated_at"), ("is_minor",)),
    ("contact_messages", ("id", "name", "email", "phone", "subject", "message", "status", "ip_address", "created_at"), ()),
    ("subscribers", ("id", "email", "status", "created_at"), ()),
    ("security_logs", ("id", "action", "detail", "ip_address", "user_agent", "created_at"), ()),
    ("reviews", ("id", "name", "boutique", "city", "product_model", "rating", "comment", "is_verified", "created_at"), ("is_verified",)),
)


def _sqlite_table_exists(conn: sqlite3.Connection, table: str) -> bool:
    return conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?", (table,)
    ).fetchone() is not None


def _normalise_ip(value: Any) -> Any:
    if not value:
        return None
    try:
        return str(ipaddress.ip_address(str(value)))
    except ValueError:
        return None


def _normalise_row(row: sqlite3.Row, boolean_columns: Iterable[str]) -> Dict[str, Any]:
    data = dict(row)
    for column in boolean_columns:
        if column in data and data[column] is not None:
            data[column] = bool(data[column])
    for column in ("ip_address",):
        if column in data:
            data[column] = _normalise_ip(data[column])
    if data.get("is_minor") and not str(data.get("guardian_name") or "").strip():
        raise ValueError(
            f"El reclamo {data.get('claim_code', data.get('id'))} marca un menor "
            "sin apoderado; corrige ese dato antes de migrar."
        )
    return data


def _insert_rows(source: sqlite3.Connection, target: psycopg.Connection[Any], table: str, columns: Tuple[str, ...], boolean_columns: Tuple[str, ...]) -> int:
    if not _sqlite_table_exists(source, table):
        return 0

    source_rows = source.execute(
        "SELECT " + ", ".join(columns) + " FROM " + table
    ).fetchall()
    if not source_rows:
        return 0

    statement = sql.SQL(
        "INSERT INTO public.{} ({}) VALUES ({}) ON CONFLICT DO NOTHING"
    ).format(
        sql.Identifier(table),
        sql.SQL(", ").join(sql.Identifier(column) for column in columns),
        sql.SQL(", ").join(sql.Placeholder() for _ in columns),
    )
    with target.cursor() as cursor:
        for row in source_rows:
            data = _normalise_row(row, boolean_columns)
            cursor.execute(statement, tuple(data[column] for column in columns))
    return len(source_rows)


def _migrate_login_attempts(source: sqlite3.Connection, target: psycopg.Connection[Any]) -> int:
    """Convierte el formato SQLite anterior (ip, ts Unix) al formato PostgreSQL."""
    if not _sqlite_table_exists(source, "login_attempts"):
        return 0
    rows = source.execute("SELECT ip, ts FROM login_attempts").fetchall()
    with target.cursor() as cursor:
        for row in rows:
            ip = _normalise_ip(row["ip"])
            if not ip:
                continue
            created_at = dt.datetime.fromtimestamp(float(row["ts"]), tz=dt.timezone.utc)
            cursor.execute(
                """INSERT INTO public.login_attempts (ip_address, created_at)
                   VALUES (%s::inet, %s) ON CONFLICT DO NOTHING""",
                (ip, created_at),
            )
    return len(rows)


def _sync_identities(target: psycopg.Connection[Any]) -> None:
    for table, _columns, _booleans in TABLES:
        target.execute(
            sql.SQL(
                "SELECT setval(pg_get_serial_sequence(%s, 'id'), "
                "COALESCE((SELECT MAX(id) FROM public.{}), 1), "
                "(SELECT COUNT(*) > 0 FROM public.{}))"
            ).format(sql.Identifier(table), sql.Identifier(table)),
            (f"public.{table}",),
        )
    target.execute(
        """SELECT setval(pg_get_serial_sequence('public.login_attempts', 'id'),
               COALESCE((SELECT MAX(id) FROM public.login_attempts), 1),
               (SELECT COUNT(*) > 0 FROM public.login_attempts))"""
    )


def migrate(source_path: str, dry_run: bool = False) -> None:
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL no está configurada en .env.")
    if not os.path.isfile(source_path):
        raise FileNotFoundError(f"No existe la base SQLite indicada: {source_path}")

    source = sqlite3.connect(source_path)
    source.row_factory = sqlite3.Row
    try:
    # Construimos la cadena de conexión limpia asegurando el sslmode
        conn_string = DATABASE_URL
        if "sslmode=" not in conn_string:
            sep = "&" if "?" in conn_string else "?"
            conn_string += f"{sep}sslmode=require"

        with psycopg.connect(
            conn_string, row_factory=dict_row
        ) as target:
            counts = {}
            for table, columns, boolean_columns in TABLES:
                counts[table] = _insert_rows(source, target, table, columns, boolean_columns)
            counts["login_attempts"] = _migrate_login_attempts(source, target)
            if dry_run:
                target.rollback()
                print("Validación completada; --dry-run no escribió datos.")
            else:
                _sync_identities(target)
                target.commit()
                print("Migración completada sin borrar ni sobrescribir datos remotos.")
            for table, count in counts.items():
                print(f"  {table}: {count} filas leídas")
    finally:
        source.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migra SQLite a Supabase/PostgreSQL.")
    parser.add_argument("--source-db", required=True, help="Ruta al archivo .db SQLite de origen.")
    parser.add_argument("--dry-run", action="store_true", help="Valida la migración y revierte la transacción.")
    args = parser.parse_args()
    migrate(args.source_db, dry_run=args.dry_run)
