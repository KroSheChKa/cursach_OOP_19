from __future__ import annotations

from src.db.repositories.mysql.report_repo import ReportRepositoryMySql


class ReportService:
    def __init__(self, repo: ReportRepositoryMySql):
        self._repo = repo

    def projects_by_client(self, client_id: int) -> list[dict]:
        return self._repo.projects_by_client(client_id)

    def overdue_projects(self) -> list[dict]:
        return self._repo.overdue_projects()

    def employees_by_project(self, project_id: int) -> list[dict]:
        return self._repo.employees_by_project(project_id)

    def employee_workload(self, employee_id: int) -> list[dict]:
        return self._repo.employee_workload(employee_id)


