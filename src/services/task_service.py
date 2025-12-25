from __future__ import annotations

from datetime import date

from src.core.entities import Task
from src.core.errors import ValidationError
from src.core.validation import require_non_empty, validate_completed_at_not_future
from src.db.repositories.mysql.task_repo import TaskRepositoryMySql


class TaskService:
    TASK_STATUSES = ["New", "InProgress", "Done", "Canceled"]

    def __init__(self, repo: TaskRepositoryMySql):
        self._repo = repo

    def get_task(self, task_id: int) -> Task | None:
        return self._repo.get_by_id(task_id)

    def list_tasks_view(self) -> list[dict]:
        return self._repo.list_all_with_names()

    def create_task(self, t: Task) -> int:
        t.title = require_non_empty(t.title, "Название задачи")
        if t.project_id <= 0:
            raise ValidationError("Не выбран проект.")
        if t.due_date is None or not isinstance(t.due_date, date):
            raise ValidationError("Не указан срок (due_date).")
        if t.status not in self.TASK_STATUSES:
            t.status = "New"
        validate_completed_at_not_future(t.completed_at)
        return self._repo.create(t)

    def update_task(self, t: Task) -> None:
        t.title = require_non_empty(t.title, "Название задачи")
        if t.project_id <= 0:
            raise ValidationError("Не выбран проект.")
        if t.due_date is None or not isinstance(t.due_date, date):
            raise ValidationError("Не указан срок (due_date).")
        if t.status not in self.TASK_STATUSES:
            t.status = "New"
        validate_completed_at_not_future(t.completed_at)
        self._repo.update(t)

    def delete_task(self, task_id: int) -> None:
        self._repo.delete(task_id)


