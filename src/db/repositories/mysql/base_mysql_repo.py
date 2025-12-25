from __future__ import annotations

from typing import Any

import mysql.connector

from src.core.errors import DatabaseError
from src.db.connection import DbConnection


class BaseMySqlRepository:
    def __init__(self, db: DbConnection):
        self._db = db

    def _execute(self, query: str, params: tuple[Any, ...] = ()) -> Any:
        try:
            cur = self._db.cursor(dictionary=True)
            cur.execute(query, params)
            return cur
        except mysql.connector.Error as e:
            raise DatabaseError(f"Ошибка запроса к БД: {e}") from e


