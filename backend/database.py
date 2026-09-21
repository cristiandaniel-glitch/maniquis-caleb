"""
Gestor de Base de Datos SQLite seguro para Maniquí Studio.
Todas las consultas se ejecutan con parámetros enlazados (evitando inyecciones SQL)
y retornan diccionarios limpios.
"""

import contextlib
import sqlite3
from typing import Any, Dict, Generator, List, Optional, Tuple

from backend.config import DB_PATH


def dict_factory(cursor: sqlite3.Cursor, row: Tuple[Any, ...]) -> Dict[str, Any]:
    """Convierte cada fila de SQLite en un diccionario con los nombres de las columnas."""
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}


@contextlib.contextmanager
def get_db_connection() -> Generator[sqlite3.Connection, None, None]:
    """Generador de conexión de alto rendimiento con manejo automático de commits, rollbacks y cierre."""
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    conn.row_factory = dict_factory
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute("PRAGMA busy_timeout = 5000;")
    conn.execute("PRAGMA cache_size = -64000;")  # 64MB de caché en memoria RAM
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def query_all(sql: str, params: Tuple[Any, ...] = ()) -> List[Dict[str, Any]]:
    """Ejecuta una consulta SELECT parametrizada y retorna todas las filas como lista de diccionarios."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        return cursor.fetchall()


def query_one(sql: str, params: Tuple[Any, ...] = ()) -> Optional[Dict[str, Any]]:
    """Ejecuta una consulta SELECT parametrizada y retorna una sola fila o None."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        return cursor.fetchone()


def execute_mutation(sql: str, params: Tuple[Any, ...] = ()) -> int:
    """
    Ejecuta una sentencia INSERT/UPDATE/DELETE parametrizada.
    Retorna el ID del último registro insertado (lastrowid) o el número de filas afectadas.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        return cursor.lastrowid or cursor.rowcount
