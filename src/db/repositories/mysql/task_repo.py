from __future__ import annotations

from typing import Optional

from src.core.entities import Task
from src.db.repositories.base import IRepository
from src.db.repositories.mysql.base_mysql_repo import BaseMySqlRepository


class TaskRepositoryMySql(BaseMySqlRepository, IRepository[Task]):
    def get_by_id(self, entity_id: int) -> Optional[Task]:
        cur = self._execute(
            """
            SELECT id, project_id, employee_id, title, description, created_at, due_date, completed_at, status
            FROM tasks
            WHERE id=%s
            """,
            (entity_id,),
        )
        row = cur.fetchone()
        return None if row is None else Task(**row)

    def list_all(self) -> list[Task]:
        cur = self._execute(
            """
            SELECT id, project_id, employee_id, title, description, created_at, due_date, completed_at, status
            FROM tasks
            ORDER BY due_date ASC, id DESC
            """
        )
        return [Task(**row) for row in cur.fetchall()]

    def list_all_with_names(self) -> list[dict]:
        cur = self._execute(
            """
            SELECT
              t.id,
              p.name AS project_name,
              CONCAT(e.last_name, ' ', e.first_name, IFNULL(CONCAT(' ', e.middle_name), '')) AS employee_name,
              t.title,
              t.due_date,
              t.status
            FROM tasks t
            JOIN projects p ON p.id = t.project_id
            LEFT JOIN employees e ON e.id = t.employee_id
            ORDER BY t.due_date ASC, t.id DESC
            """
        )
        rows = list(cur.fetchall())
        for r in rows:
            if r.get("employee_name") is None:
                r["employee_name"] = "(не назначено)"
        return rows

    def create(self, entity: Task) -> int:
        cur = self._execute(
            """
            INSERT INTO tasks (project_id, employee_id, title, description, due_date, completed_at, status)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                entity.project_id,
                entity.employee_id,
                entity.title,
                entity.description,
                entity.due_date,
                entity.completed_at,
                entity.status,
            ),
        )
        return int(cur.lastrowid)

    def update(self, entity: Task) -> None:
        assert entity.id is not None
        self._execute(
            """
            UPDATE tasks
            SET project_id=%s, employee_id=%s, title=%s, description=%s, due_date=%s, completed_at=%s, status=%s
            WHERE id=%s
            """,
            (
                entity.project_id,
                entity.employee_id,
                entity.title,
                entity.description,
                entity.due_date,
                entity.completed_at,
                entity.status,
                entity.id,
            ),
        )

    def delete(self, entity_id: int) -> None:
        self._execute("DELETE FROM tasks WHERE id=%s", (entity_id,))


