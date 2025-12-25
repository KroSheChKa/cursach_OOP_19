from __future__ import annotations

from typing import Optional

from src.core.entities import Project
from src.db.repositories.base import IRepository
from src.db.repositories.mysql.base_mysql_repo import BaseMySqlRepository


class ProjectRepositoryMySql(BaseMySqlRepository, IRepository[Project]):
    def get_by_id(self, entity_id: int) -> Optional[Project]:
        cur = self._execute(
            """
            SELECT id, client_id, name, description, start_date, end_date, status
            FROM projects
            WHERE id=%s
            """,
            (entity_id,),
        )
        row = cur.fetchone()
        return None if row is None else Project(**row)

    def list_all(self) -> list[Project]:
        cur = self._execute(
            """
            SELECT id, client_id, name, description, start_date, end_date, status
            FROM projects
            ORDER BY start_date DESC, id DESC
            """
        )
        return [Project(**row) for row in cur.fetchall()]

    def list_all_with_client_name(self) -> list[dict]:
        cur = self._execute(
            """
            SELECT p.id, p.name, c.name AS client_name, p.start_date, p.end_date, p.status
            FROM projects p
            JOIN clients c ON c.id = p.client_id
            ORDER BY p.start_date DESC, p.id DESC
            """
        )
        return list(cur.fetchall())

    def create(self, entity: Project) -> int:
        cur = self._execute(
            """
            INSERT INTO projects (client_id, name, description, start_date, end_date, status)
            VALUES (%s,%s,%s,%s,%s,%s)
            """,
            (
                entity.client_id,
                entity.name,
                entity.description,
                entity.start_date,
                entity.end_date,
                entity.status,
            ),
        )
        return int(cur.lastrowid)

    def update(self, entity: Project) -> None:
        assert entity.id is not None
        self._execute(
            """
            UPDATE projects
            SET client_id=%s, name=%s, description=%s, start_date=%s, end_date=%s, status=%s
            WHERE id=%s
            """,
            (
                entity.client_id,
                entity.name,
                entity.description,
                entity.start_date,
                entity.end_date,
                entity.status,
                entity.id,
            ),
        )

    def delete(self, entity_id: int) -> None:
        self._execute("DELETE FROM projects WHERE id=%s", (entity_id,))


