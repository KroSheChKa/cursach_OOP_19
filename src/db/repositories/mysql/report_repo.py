from __future__ import annotations

from src.db.repositories.mysql.base_mysql_repo import BaseMySqlRepository


class ReportRepositoryMySql(BaseMySqlRepository):
    def projects_by_client(self, client_id: int) -> list[dict]:
        cur = self._execute(
            """
            SELECT p.id, p.name, p.start_date, p.end_date, p.status
            FROM projects p
            WHERE p.client_id=%s
            ORDER BY p.start_date DESC, p.id DESC
            """,
            (client_id,),
        )
        return list(cur.fetchall())

    def overdue_projects(self) -> list[dict]:
        cur = self._execute(
            """
            SELECT
              p.id,
              p.name,
              c.name AS client_name,
              MIN(t.due_date) AS first_overdue_due_date,
              COUNT(*) AS overdue_tasks
            FROM projects p
            JOIN clients c ON c.id = p.client_id
            JOIN tasks t ON t.project_id = p.id
            WHERE t.due_date < CURRENT_DATE
              AND t.status NOT IN ('Done','Canceled')
            GROUP BY p.id, p.name, c.name
            ORDER BY first_overdue_due_date ASC, overdue_tasks DESC
            """
        )
        return list(cur.fetchall())

    def employees_by_project(self, project_id: int) -> list[dict]:
        cur = self._execute(
            """
            SELECT
              e.id AS employee_id,
              CONCAT(e.last_name, ' ', e.first_name, IFNULL(CONCAT(' ', e.middle_name), '')) AS employee_name,
              e.position,
              pm.role,
              pm.since_date
            FROM project_members pm
            JOIN employees e ON e.id = pm.employee_id
            WHERE pm.project_id=%s
            ORDER BY e.last_name, e.first_name
            """,
            (project_id,),
        )
        return list(cur.fetchall())

    def employee_workload(self, employee_id: int) -> list[dict]:
        cur = self._execute(
            """
            SELECT
              p.id AS project_id,
              p.name AS project_name,
              t.id AS task_id,
              t.title AS task_title,
              t.due_date,
              t.status
            FROM tasks t
            JOIN projects p ON p.id = t.project_id
            WHERE t.employee_id=%s
              AND t.status IN ('New','InProgress')
            ORDER BY t.due_date ASC, t.id DESC
            """,
            (employee_id,),
        )
        return list(cur.fetchall())


