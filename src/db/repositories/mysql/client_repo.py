from __future__ import annotations

from typing import Optional

from src.core.entities import Client
from src.db.repositories.base import IRepository
from src.db.repositories.mysql.base_mysql_repo import BaseMySqlRepository


class ClientRepositoryMySql(BaseMySqlRepository, IRepository[Client]):
    def get_by_id(self, entity_id: int) -> Optional[Client]:
        cur = self._execute("SELECT id, name, phone, email, note FROM clients WHERE id=%s", (entity_id,))
        row = cur.fetchone()
        return None if row is None else Client(**row)

    def list_all(self) -> list[Client]:
        cur = self._execute("SELECT id, name, phone, email, note FROM clients ORDER BY name")
        return [Client(**row) for row in cur.fetchall()]

    def create(self, entity: Client) -> int:
        cur = self._execute(
            "INSERT INTO clients (name, phone, email, note) VALUES (%s,%s,%s,%s)",
            (entity.name, entity.phone, entity.email, entity.note),
        )
        return int(cur.lastrowid)

    def update(self, entity: Client) -> None:
        assert entity.id is not None
        self._execute(
            "UPDATE clients SET name=%s, phone=%s, email=%s, note=%s WHERE id=%s",
            (entity.name, entity.phone, entity.email, entity.note, entity.id),
        )

    def delete(self, entity_id: int) -> None:
        self._execute("DELETE FROM clients WHERE id=%s", (entity_id,))


