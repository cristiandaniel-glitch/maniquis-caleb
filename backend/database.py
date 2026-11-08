"""Acceso seguro a PostgreSQL/Supabase para Maniquí Studio.

El frontend nunca se conecta a Supabase directamente: todas las consultas pasan
por los endpoints REST existentes, donde se conservan autenticación, validación,
rate limiting y sanitización.
"""

import contextlib
import datetime as dt
import ipaddress
import threading
from decimal import Decimal
from typing import Any, Dict, Generator, List, Optional, Sequence

from psycopg import Connection
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from backend.config import (
    DATABASE_POOL_MAX_SIZE,
    DATABASE_POOL_MIN_SIZE,
    DATABASE_POOL_TIMEOUT,
    DATABASE_SSLMODE,
    DATABASE_URL,
)


_pool: Optional[ConnectionPool] = None
_pool_lock = threading.Lock()
_REQUIRED_TABLES = (
    "categories",
    "products",
    "claims_book",
    "contact_messages",
    "subscribers",
    "security_logs",
    "reviews",
    "login_attempts",
)


def _require_database_url() -> str:
    if not DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URL no está configurada. Copia .env.example a .env y agrega "
            "la cadena privada de conexión de Supabase."
        )
    if not DATABASE_URL.startswith(("postgres://", "postgresql://")):
        raise RuntimeError("DATABASE_URL debe usar el esquema postgresql://.")
    return DATABASE_URL


def _get_pool() -> ConnectionPool:
    """Crea el pool de conexiones bajo demanda, seguro para procesos hijos."""
    global _pool
    with _pool_lock:
        if _pool is None:
            min_size = max(0, DATABASE_POOL_MIN_SIZE)
            max_size = max(1, DATABASE_POOL_MAX_SIZE, min_size)
            _pool = ConnectionPool(
                conninfo=_require_database_url(),
                kwargs={
                    "row_factory": dict_row,
                    "connect_timeout": int(DATABASE_POOL_TIMEOUT),
                    "sslmode": DATABASE_SSLMODE,
                },
                min_size=min_size,
                max_size=max_size,
                timeout=DATABASE_POOL_TIMEOUT,
                open=True,
            )
        return _pool


def close_connection_pool() -> None:
    """Cierra el pool antes de bifurcar procesos o al apagar el servidor."""
    global _pool
    with _pool_lock:
        if _pool is not None:
            _pool.close()
            _pool = None


@contextlib.contextmanager
def get_db_connection() -> Generator[Connection[Dict[str, Any]], None, None]:
    """Entrega una conexión transaccional del pool y la devuelve de forma segura."""
    pool = _get_pool()
    with pool.connection(timeout=DATABASE_POOL_TIMEOUT) as conn:
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise


def _json_value(value: Any) -> Any:
    """Convierte tipos PostgreSQL a valores que json.dumps puede enviar al frontend."""
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (dt.datetime, dt.date, dt.time)):
        return value.isoformat()
    if isinstance(value, (ipaddress.IPv4Address, ipaddress.IPv6Address, ipaddress.IPv4Network, ipaddress.IPv6Network)):
        return str(value)
    if isinstance(value, list):
        return [_json_value(item) for item in value]
    if isinstance(value, tuple):
        return [_json_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _json_value(item) for key, item in value.items()}
    return value


def _json_row(row: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if row is None:
        return None
    return {key: _json_value(value) for key, value in row.items()}


def query_all(sql: str, params: Sequence[Any] = ()) -> List[Dict[str, Any]]:
    """Ejecuta un SELECT parametrizado y devuelve diccionarios serializables."""
    with get_db_connection() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [_json_row(row) for row in rows]  # type: ignore[list-item]


def query_one(sql: str, params: Sequence[Any] = ()) -> Optional[Dict[str, Any]]:
    """Ejecuta un SELECT/RETURNING parametrizado y devuelve una fila o None."""
    with get_db_connection() as conn:
        row = conn.execute(sql, params).fetchone()
    return _json_row(row)


def execute_mutation(sql: str, params: Sequence[Any] = ()) -> int:
    """Ejecuta INSERT/UPDATE/DELETE/DDL parametrizado y retorna filas afectadas."""
    with get_db_connection() as conn:
        cursor = conn.execute(sql, params)
        return max(cursor.rowcount, 0)


def execute_insert(sql: str, params: Sequence[Any] = ()) -> int:
    """Inserta una fila y obtiene su ID con RETURNING, sin depender de SQLite."""
    statement = sql.strip().rstrip(";")
    if "returning" not in statement.lower():
        statement = f"{statement} RETURNING id"
    row = query_one(statement, params)
    if not row or row.get("id") is None:
        raise RuntimeError("La inserción no devolvió el identificador esperado.")
    return int(row["id"])


def verify_database_schema() -> None:
    """Falla temprano si DATABASE_URL no llega a Supabase o falta el esquema."""
    missing: List[str] = []
    with get_db_connection() as conn:
        for table in _REQUIRED_TABLES:
            row = conn.execute("SELECT to_regclass(%s) AS table_name", (f"public.{table}",)).fetchone()
            if not row or row["table_name"] is None:
                missing.append(table)
    if missing:
        raise RuntimeError(
            "Faltan tablas de PostgreSQL: " + ", ".join(missing) +
            ". Ejecuta database/schema.postgres.sql en el SQL Editor de Supabase."
        )
