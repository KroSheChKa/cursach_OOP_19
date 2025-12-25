from __future__ import annotations

from src.config import ConfigError, load_mysql_config
from src.core.errors import DatabaseError
from src.db.connection import DbConnection
from src.db.repositories.mysql.client_repo import ClientRepositoryMySql
from src.db.repositories.mysql.employee_repo import EmployeeRepositoryMySql
from src.db.repositories.mysql.project_member_repo import ProjectMemberRepositoryMySql
from src.db.repositories.mysql.project_repo import ProjectRepositoryMySql
from src.db.repositories.mysql.report_repo import ReportRepositoryMySql
from src.db.repositories.mysql.task_repo import TaskRepositoryMySql
from src.services.client_service import ClientService
from src.services.employee_service import EmployeeService
from src.services.project_service import ProjectService
from src.services.report_service import ReportService
from src.services.task_service import TaskService


class AppContext:
    """
    Контейнер зависимостей (DI) для приложения.

    Демонстрирует динамическое создание объектов (репозиториев/сервисов) по конфигурации.
    """

    def __init__(self) -> None:
        self.db: DbConnection | None = None

        self.clients: ClientService | None = None
        self.employees: EmployeeService | None = None
        self.projects: ProjectService | None = None
        self.tasks: TaskService | None = None
        self.reports: ReportService | None = None

    def connect(self) -> None:
        try:
            cfg = load_mysql_config("config.ini")
        except ConfigError as e:
            raise DatabaseError(str(e)) from e

        self.db = DbConnection(cfg)
        self.db.connect()

        # repositories
        client_repo = ClientRepositoryMySql(self.db)
        employee_repo = EmployeeRepositoryMySql(self.db)
        project_repo = ProjectRepositoryMySql(self.db)
        member_repo = ProjectMemberRepositoryMySql(self.db)
        task_repo = TaskRepositoryMySql(self.db)
        report_repo = ReportRepositoryMySql(self.db)

        # services
        self.clients = ClientService(client_repo)
        self.employees = EmployeeService(employee_repo)
        self.projects = ProjectService(project_repo, member_repo)
        self.tasks = TaskService(task_repo)
        self.reports = ReportService(report_repo)

    def close(self) -> None:
        if self.db is not None:
            self.db.close()


