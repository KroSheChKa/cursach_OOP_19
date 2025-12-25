from __future__ import annotations

from typing import Any

import mysql.connector

from src.config import MySqlConfig
from src.core.errors import DatabaseError


class DbConnection:
    """
    Обёртка над соединением MySQL.

    Для демонстрации ООП: контекстный менеджер + явное закрытие ресурса.
    """

    def __init__(self, cfg: MySqlConfig):
        self._cfg = cfg
        self._conn: mysql.connector.MySQLConnection | None = None

    def connect(self) -> None:
        if self._conn is not None and self._conn.is_connected():
            return
        try:
            self._conn = mysql.connector.connect(
                host=self._cfg.host,
                port=self._cfg.port,
                user=self._cfg.user,
                password=self._cfg.password,
                database=self._cfg.database,
                autocommit=True,
            )
        except mysql.connector.Error as e:
            raise DatabaseError(f"Ошибка подключения к MySQL: {e}") from e

    def close(self) -> None:
        if self._conn is None:
            return
        try:
            self._conn.close()
        except mysql.connector.Error:
            # Игнорируем ошибки закрытия, это безопасно для UI.
            pass
        finally:
            self._conn = None

    def cursor(self, *, dictionary: bool = True) -> Any:
        self.connect()
        assert self._conn is not None
        return self._conn.cursor(dictionary=dictionary)

    def __enter__(self) -> "DbConnection":
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def __del__(self) -> None:
        # Демонстрация "деструктора": освобождаем ресурс при сборке мусора
        self.close()


