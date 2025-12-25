from __future__ import annotations

from typing import Optional

from src.core.entities import Employee
from src.db.repositories.base import IRepository
from src.db.repositories.mysql.base_mysql_repo import BaseMySqlRepository


class EmployeeRepositoryMySql(BaseMySqlRepository, IRepository[Employee]):
    def get_by_id(self, entity_id: int) -> Optional[Employee]:
        cur = self._execute(
            """
            SELECT id, last_name, first_name, middle_name, position, phone, email, is_active
            FROM employees
            WHERE id=%s
            """,
            (entity_id,),
        )
        row = cur.fetchone()
        if row is None:
            return None
        row["is_active"] = bool(row["is_active"])
        return Employee(**row)

    def list_all(self) -> list[Employee]:
        cur = self._execute(
            """
            SELECT id, last_name, first_name, middle_name, position, phone, email, is_active
            FROM employees
            ORDER BY last_name, first_name
            """
        )
        result: list[Employee] = []
        for row in cur.fetchall():
            row["is_active"] = bool(row["is_active"])
            result.append(Employee(**row))
        return result

    def create(self, entity: Employee) -> int:
        cur = self._execute(
            """
            INSERT INTO employees (last_name, first_name, middle_name, position, phone, email, is_active)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                entity.last_name,
                entity.first_name,
                entity.middle_name,
                entity.position,
                entity.phone,
                entity.email,
                1 if entity.is_active else 0,
            ),
        )
        return int(cur.lastrowid)

    def update(self, entity: Employee) -> None:
        assert entity.id is not None
        self._execute(
            """
            UPDATE employees
            SET last_name=%s, first_name=%s, middle_name=%s, position=%s, phone=%s, email=%s, is_active=%s
            WHERE id=%s
            """,
            (
                entity.last_name,
                entity.first_name,
                entity.middle_name,
                entity.position,
                entity.phone,
                entity.email,
                1 if entity.is_active else 0,
                entity.id,
            ),
        )

    def delete(self, entity_id: int) -> None:
        self._execute("DELETE FROM employees WHERE id=%s", (entity_id,))


