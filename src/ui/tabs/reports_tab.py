from __future__ import annotations

from PyQt6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.core.errors import AppError
from src.services.client_service import ClientService
from src.services.employee_service import EmployeeService
from src.services.project_service import ProjectService
from src.services.report_service import ReportService
from src.ui.common import export_table_to_pdf, show_error, show_info


class ReportsTab(QWidget):
    def __init__(
        self,
        report_service: ReportService,
        client_service: ClientService,
        project_service: ProjectService,
        employee_service: EmployeeService,
        parent=None,
    ):
        super().__init__(parent)
        self._reports = report_service
        self._clients = client_service
        self._projects = project_service
        self._employees = employee_service

        self.report_type = QComboBox()
        self.report_type.addItem("Проекты выбранного клиента", "projects_by_client")
        self.report_type.addItem("Проекты с просроченными задачами", "overdue_projects")
        self.report_type.addItem("Сотрудники на проекте", "employees_by_project")
        self.report_type.addItem("Загрузка сотрудника", "employee_workload")

        # Parameters widgets
        self.param_stack = QStackedWidget()
        self.client_combo = QComboBox()
        self.project_combo = QComboBox()
        self.employee_combo = QComboBox()

        self.param_stack.addWidget(self._wrap_param("Клиент", self.client_combo))
        self.param_stack.addWidget(self._wrap_param("Проект", self.project_combo))
        self.param_stack.addWidget(self._wrap_param("Сотрудник", self.employee_combo))
        self.param_stack.addWidget(QWidget())  # empty

        self.btn_generate = QPushButton("Сформировать")
        self.btn_refresh = QPushButton("Обновить списки")
        self.btn_export = QPushButton("Выгрузить в PDF")
        self.btn_generate.clicked.connect(self.generate)
        self.btn_refresh.clicked.connect(self.refresh_sources)
        self.btn_export.clicked.connect(self.on_export)
        self.report_type.currentIndexChanged.connect(self._on_report_changed)

        top = QHBoxLayout()
        top.addWidget(QLabel("Отчёт:"))
        top.addWidget(self.report_type, 2)
        top.addWidget(self.param_stack, 2)
        top.addWidget(self.btn_generate)
        top.addWidget(self.btn_refresh)
        top.addWidget(self.btn_export)
        top.addStretch(1)

        self.table = QTableWidget(0, 0)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        layout = QVBoxLayout()
        layout.addLayout(top)
        layout.addWidget(self.table)
        self.setLayout(layout)

        self._on_report_changed()

    def _wrap_param(self, label: str, widget: QWidget) -> QWidget:
        w = QWidget()
        lay = QHBoxLayout()
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(QLabel(label + ":"))
        lay.addWidget(widget, 1)
        w.setLayout(lay)
        return w

    def _on_report_changed(self) -> None:
        key = str(self.report_type.currentData())
        if key == "projects_by_client":
            self.param_stack.setCurrentIndex(0)
        elif key == "employees_by_project":
            self.param_stack.setCurrentIndex(1)
        elif key == "employee_workload":
            self.param_stack.setCurrentIndex(2)
        else:
            self.param_stack.setCurrentIndex(3)

    def refresh_sources(self) -> None:
        try:
            clients = self._clients.list_clients()
            projects = self._projects.list_projects()
            employees = self._employees.list_employees()
        except AppError as e:
            show_error(self, str(e))
            return

        self.client_combo.clear()
        for c in clients:
            self.client_combo.addItem(c.name, c.id)

        self.project_combo.clear()
        for p in projects:
            self.project_combo.addItem(p.name, p.id)

        self.employee_combo.clear()
        for e in employees:
            self.employee_combo.addItem(e.full_name(), e.id)

        show_info(self, "Списки обновлены.", "Отчёты")

    def generate(self) -> None:
        key = str(self.report_type.currentData())

        try:
            if key == "projects_by_client":
                client_id = int(self.client_combo.currentData())
                rows = self._reports.projects_by_client(client_id)
                headers = ["id", "name", "start_date", "end_date", "status"]
            elif key == "overdue_projects":
                rows = self._reports.overdue_projects()
                headers = ["id", "name", "client_name", "first_overdue_due_date", "overdue_tasks"]
            elif key == "employees_by_project":
                project_id = int(self.project_combo.currentData())
                rows = self._reports.employees_by_project(project_id)
                headers = ["employee_id", "employee_name", "position", "role", "since_date"]
            else:
                employee_id = int(self.employee_combo.currentData())
                rows = self._reports.employee_workload(employee_id)
                headers = ["project_id", "project_name", "task_id", "task_title", "due_date", "status"]
        except (TypeError, ValueError):
            show_error(self, "Не выбран параметр отчёта (клиент/проект/сотрудник).")
            return
        except AppError as e:
            show_error(self, str(e))
            return

        self._fill_table(headers, rows)

        if not rows:
            show_info(self, "Нет данных для выбранного отчёта.", "Отчёт")

    def _fill_table(self, headers: list[str], rows: list[dict]) -> None:
        self.table.setRowCount(0)
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)

        for r in rows:
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)
            for col, h in enumerate(headers):
                self.table.setItem(row_idx, col, QTableWidgetItem(str(r.get(h, ""))))

        self.table.resizeColumnsToContents()

    def on_export(self) -> None:
        title = f"Отчёт — {self.report_type.currentText()}"
        export_table_to_pdf(self, self.table, title)


