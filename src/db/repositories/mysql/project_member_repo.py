from __future__ import annotations

from src.db.repositories.mysql.base_mysql_repo import BaseMySqlRepository


class ProjectMemberRepositoryMySql(BaseMySqlRepository):
    def list_members(self, project_id: int) -> list[dict]:
        cur = self._execute(
            """
            SELECT
              pm.project_id,
              pm.employee_id,
              pm.role,
              pm.since_date,
              e.last_name,
              e.first_name,
              e.middle_name,
              e.position
            FROM project_members pm
            JOIN employees e ON e.id = pm.employee_id
            WHERE pm.project_id=%s
            ORDER BY e.last_name, e.first_name
            """,
            (project_id,),
        )
        return list(cur.fetchall())

    def add_member(self, project_id: int, employee_id: int, role: str) -> None:
        self._execute(
            """
            INSERT INTO project_members (project_id, employee_id, role, since_date)
            VALUES (%s,%s,%s, CURRENT_DATE)
            """,
            (project_id, employee_id, role),
        )

    def remove_member(self, project_id: int, employee_id: int) -> None:
        self._execute(
            "DELETE FROM project_members WHERE project_id=%s AND employee_id=%s",
            (project_id, employee_id),
        )


