from __future__ import annotations

from PyQt6.QtWidgets import (
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.core.errors import AppError
from src.services.employee_service import EmployeeService
from src.services.project_service import ProjectService
from src.services.task_service import TaskService
from src.ui.common import ask_yes_no, export_table_to_pdf, show_error
from src.ui.dialogs.task_dialog import TaskDialog


class TaskTab(QWidget):
    def __init__(
        self,
        task_service: TaskService,
        project_service: ProjectService,
        employee_service: EmployeeService,
        parent=None,
    ):
        super().__init__(parent)
        self._tasks = task_service
        self._projects = project_service
        self._employees = employee_service

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["id", "Проект", "Исполнитель", "Задача", "Срок", "Статус"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self.btn_add = QPushButton("Добавить")
        self.btn_edit = QPushButton("Изменить")
        self.btn_delete = QPushButton("Удалить")
        self.btn_refresh = QPushButton("Обновить")
        self.btn_export = QPushButton("Выгрузить в PDF")

        self.btn_add.clicked.connect(self.on_add)
        self.btn_edit.clicked.connect(self.on_edit)
        self.btn_delete.clicked.connect(self.on_delete)
        self.btn_refresh.clicked.connect(self.refresh)
        self.btn_export.clicked.connect(self.on_export)

        buttons = QHBoxLayout()
        buttons.addWidget(self.btn_add)
        buttons.addWidget(self.btn_edit)
        buttons.addWidget(self.btn_delete)
        buttons.addWidget(self.btn_refresh)
        buttons.addWidget(self.btn_export)
        buttons.addStretch(1)

        layout = QVBoxLayout()
        layout.addLayout(buttons)
        layout.addWidget(self.table)
        self.setLayout(layout)

    def refresh(self) -> None:
        try:
            rows = self._tasks.list_tasks_view()
        except AppError as e:
            show_error(self, str(e))
            rows = []

        self.table.setRowCount(0)
        for r in rows:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(r.get("id", ""))))
            self.table.setItem(row, 1, QTableWidgetItem(str(r.get("project_name", ""))))
            self.table.setItem(row, 2, QTableWidgetItem(str(r.get("employee_name", ""))))
            self.table.setItem(row, 3, QTableWidgetItem(str(r.get("title", ""))))
            self.table.setItem(row, 4, QTableWidgetItem(str(r.get("due_date", ""))))
            self.table.setItem(row, 5, QTableWidgetItem(str(r.get("status", ""))))

        self.table.resizeColumnsToContents()

    def _selected_id(self) -> int | None:
        items = self.table.selectedItems()
        if not items:
            return None
        try:
            return int(items[0].text())
        except ValueError:
            return None

    def on_add(self) -> None:
        try:
            projects = self._projects.list_projects()
            employees = self._employees.list_employees()
        except AppError as e:
            show_error(self, str(e))
            return
        if not projects:
            QMessageBox.information(self, "Задачи", "Сначала добавьте хотя бы один проект.")
            return
        dlg = TaskDialog(self._tasks, projects, employees, None, self)
        if dlg.exec() == dlg.DialogCode.Accepted:
            self.refresh()

    def on_edit(self) -> None:
        tid = self._selected_id()
        if tid is None:
            QMessageBox.information(self, "Изменение", "Выберите задачу в таблице.")
            return
        try:
            task = self._tasks.get_task(tid)
            projects = self._projects.list_projects()
            employees = self._employees.list_employees()
        except AppError as e:
            show_error(self, str(e))
            return
        if task is None:
            QMessageBox.information(self, "Изменение", "Не удалось найти выбранную задачу.")
            return
        dlg = TaskDialog(self._tasks, projects, employees, task, self)
        if dlg.exec() == dlg.DialogCode.Accepted:
            self.refresh()

    def on_delete(self) -> None:
        tid = self._selected_id()
        if tid is None:
            QMessageBox.information(self, "Удаление", "Выберите задачу в таблице.")
            return
        if not ask_yes_no(self, "Удалить выбранную задачу?"):
            return
        try:
            self._tasks.delete_task(tid)
        except AppError as e:
            show_error(self, str(e))
            return
        self.refresh()

    def on_export(self) -> None:
        export_table_to_pdf(self, self.table, "Задачи")


