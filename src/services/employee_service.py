from __future__ import annotations

from src.core.entities import Employee
from src.core.validation import require_non_empty, validate_email_optional, validate_employee_fio
from src.db.repositories.mysql.employee_repo import EmployeeRepositoryMySql


class EmployeeService:
    def __init__(self, repo: EmployeeRepositoryMySql):
        self._repo = repo

    def list_employees(self) -> list[Employee]:
        return self._repo.list_all()

    def create_employee(self, e: Employee) -> int:
        e.position = require_non_empty(e.position, "Должность")
        e.last_name, e.first_name, e.middle_name = validate_employee_fio(
            e.last_name, e.first_name, e.middle_name
        )
        validate_email_optional(e.email)
        return self._repo.create(e)

    def update_employee(self, e: Employee) -> None:
        e.position = require_non_empty(e.position, "Должность")
        e.last_name, e.first_name, e.middle_name = validate_employee_fio(
            e.last_name, e.first_name, e.middle_name
        )
        validate_email_optional(e.email)
        self._repo.update(e)

    def delete_employee(self, employee_id: int) -> None:
        self._repo.delete(employee_id)


