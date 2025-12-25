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
from src.services.client_service import ClientService
from src.services.employee_service import EmployeeService
from src.services.project_service import ProjectService
from src.ui.common import ask_yes_no, export_table_to_pdf, show_error
from src.ui.dialogs.members_dialog import MembersDialog
from src.ui.dialogs.project_dialog import ProjectDialog


class ProjectTab(QWidget):
    def __init__(
        self,
        project_service: ProjectService,
        client_service: ClientService,
        employee_service: EmployeeService,
        parent=None,
    ):
        super().__init__(parent)
        self._projects = project_service
        self._clients = client_service
        self._employees = employee_service
        self._projects_by_id: dict[int, object] = {}

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["id", "Клиент", "Название", "Дата начала", "Дата окончания", "Статус"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self.btn_add = QPushButton("Добавить")
        self.btn_edit = QPushButton("Изменить")
        self.btn_delete = QPushButton("Удалить")
        self.btn_members = QPushButton("Участники проекта")
        self.btn_refresh = QPushButton("Обновить")
        self.btn_export = QPushButton("Выгрузить в PDF")

        self.btn_add.clicked.connect(self.on_add)
        self.btn_edit.clicked.connect(self.on_edit)
        self.btn_delete.clicked.connect(self.on_delete)
        self.btn_members.clicked.connect(self.on_members)
        self.btn_refresh.clicked.connect(self.refresh)
        self.btn_export.clicked.connect(self.on_export)

        buttons = QHBoxLayout()
        buttons.addWidget(self.btn_add)
        buttons.addWidget(self.btn_edit)
        buttons.addWidget(self.btn_delete)
        buttons.addWidget(self.btn_members)
        buttons.addWidget(self.btn_refresh)
        buttons.addWidget(self.btn_export)
        buttons.addStretch(1)

        layout = QVBoxLayout()
        layout.addLayout(buttons)
        layout.addWidget(self.table)
        self.setLayout(layout)

    def refresh(self) -> None:
        try:
            clients = self._clients.list_clients()
            client_name_by_id = {int(c.id): c.name for c in clients if c.id is not None}
            projects = self._projects.list_projects()
        except AppError as e:
            show_error(self, str(e))
            projects = []
            client_name_by_id = {}

        self._projects_by_id = {int(p.id): p for p in projects if p.id is not None}

        self.table.setRowCount(0)
        for p in projects:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(p.id or "")))
            self.table.setItem(row, 1, QTableWidgetItem(client_name_by_id.get(int(p.client_id), str(p.client_id))))
            self.table.setItem(row, 2, QTableWidgetItem(p.name))
            self.table.setItem(row, 3, QTableWidgetItem(str(p.start_date or "")))
            self.table.setItem(row, 4, QTableWidgetItem(str(p.end_date or "")))
            self.table.setItem(row, 5, QTableWidgetItem(p.status))

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
            clients = self._clients.list_clients()
        except AppError as e:
            show_error(self, str(e))
            return
        if not clients:
            QMessageBox.information(self, "Проекты", "Сначала добавьте хотя бы одного клиента.")
            return
        dlg = ProjectDialog(self._projects, clients, None, self)
        if dlg.exec() == dlg.DialogCode.Accepted:
            self.refresh()

    def on_edit(self) -> None:
        pid = self._selected_id()
        if pid is None:
            QMessageBox.information(self, "Изменение", "Выберите проект в таблице.")
            return
        project = self._projects_by_id.get(pid)
        if project is None:
            QMessageBox.information(self, "Изменение", "Не удалось найти выбранный проект.")
            return
        try:
            clients = self._clients.list_clients()
        except AppError as e:
            show_error(self, str(e))
            return
        dlg = ProjectDialog(self._projects, clients, project, self)
        if dlg.exec() == dlg.DialogCode.Accepted:
            self.refresh()

    def on_delete(self) -> None:
        pid = self._selected_id()
        if pid is None:
            QMessageBox.information(self, "Удаление", "Выберите проект в таблице.")
            return
        if not ask_yes_no(self, "Удалить выбранный проект? (задачи/участники будут удалены каскадно)"):
            return
        try:
            self._projects.delete_project(pid)
        except AppError as e:
            show_error(self, str(e))
            return
        self.refresh()

    def on_members(self) -> None:
        pid = self._selected_id()
        if pid is None:
            QMessageBox.information(self, "Участники", "Выберите проект в таблице.")
            return
        try:
            employees = self._employees.list_employees()
        except AppError as e:
            show_error(self, str(e))
            return
        if not employees:
            QMessageBox.information(self, "Участники", "Сначала добавьте хотя бы одного сотрудника.")
            return
        dlg = MembersDialog(self._projects, pid, employees, self)
        dlg.exec()

    def on_export(self) -> None:
        export_table_to_pdf(self, self.table, "Проекты")


