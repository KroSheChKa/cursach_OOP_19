from __future__ import annotations

from datetime import date

from src.core.entities import Project, ProjectMember
from src.core.errors import ValidationError
from src.core.validation import require_non_empty
from src.db.repositories.mysql.project_member_repo import ProjectMemberRepositoryMySql
from src.db.repositories.mysql.project_repo import ProjectRepositoryMySql


class ProjectService:
    PROJECT_STATUSES = ["Planned", "Active", "Completed", "OnHold", "Canceled"]

    def __init__(
        self,
        project_repo: ProjectRepositoryMySql,
        member_repo: ProjectMemberRepositoryMySql,
    ):
        self._projects = project_repo
        self._members = member_repo

    def list_projects(self) -> list[Project]:
        return self._projects.list_all()

    def list_projects_view(self) -> list[dict]:
        return self._projects.list_all_with_client_name()

    def create_project(self, p: Project) -> int:
        p.name = require_non_empty(p.name, "Название проекта")
        if p.client_id <= 0:
            raise ValidationError("Не выбран клиент.")
        if p.start_date is None or not isinstance(p.start_date, date):
            raise ValidationError("Не указана дата начала проекта.")
        if p.status not in self.PROJECT_STATUSES:
            p.status = "Active"
        return self._projects.create(p)

    def update_project(self, p: Project) -> None:
        p.name = require_non_empty(p.name, "Название проекта")
        if p.client_id <= 0:
            raise ValidationError("Не выбран клиент.")
        if p.start_date is None or not isinstance(p.start_date, date):
            raise ValidationError("Не указана дата начала проекта.")
        if p.status not in self.PROJECT_STATUSES:
            p.status = "Active"
        self._projects.update(p)

    def delete_project(self, project_id: int) -> None:
        self._projects.delete(project_id)

    # ---- Members ----
    def list_project_members(self, project_id: int) -> list[dict]:
        return self._members.list_members(project_id)

    def add_project_member(self, project_id: int, employee_id: int, role: str) -> None:
        role = require_non_empty(role, "Роль")
        self._members.add_member(project_id, employee_id, role)

    def remove_project_member(self, project_id: int, employee_id: int) -> None:
        self._members.remove_member(project_id, employee_id)


