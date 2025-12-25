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
from src.ui.common import ask_yes_no, export_table_to_pdf, show_error
from src.ui.dialogs.employee_dialog import EmployeeDialog


class EmployeeTab(QWidget):
    def __init__(self, service: EmployeeService, parent=None):
        super().__init__(parent)
        self._service = service
        self._employees_by_id: dict[int, object] = {}

        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels(
            ["id", "Фамилия", "Имя", "Отчество", "Должность", "Телефон", "Email", "Активен"]
        )
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
            employees = self._service.list_employees()
        except AppError as e:
            show_error(self, str(e))
            employees = []

        self._employees_by_id = {int(e.id): e for e in employees if e.id is not None}

        self.table.setRowCount(0)
        for e in employees:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(e.id or "")))
            self.table.setItem(row, 1, QTableWidgetItem(e.last_name))
            self.table.setItem(row, 2, QTableWidgetItem(e.first_name))
            self.table.setItem(row, 3, QTableWidgetItem(e.middle_name or ""))
            self.table.setItem(row, 4, QTableWidgetItem(e.position))
            self.table.setItem(row, 5, QTableWidgetItem(e.phone or ""))
            self.table.setItem(row, 6, QTableWidgetItem(e.email or ""))
            self.table.setItem(row, 7, QTableWidgetItem("Да" if e.is_active else "Нет"))

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
        dlg = EmployeeDialog(self._service, None, self)
        if dlg.exec() == dlg.DialogCode.Accepted:
            self.refresh()

    def on_edit(self) -> None:
        emp_id = self._selected_id()
        if emp_id is None:
            QMessageBox.information(self, "Изменение", "Выберите сотрудника в таблице.")
            return
        emp = self._employees_by_id.get(emp_id)
        if emp is None:
            QMessageBox.information(self, "Изменение", "Не удалось найти выбранного сотрудника.")
            return
        dlg = EmployeeDialog(self._service, emp, self)
        if dlg.exec() == dlg.DialogCode.Accepted:
            self.refresh()

    def on_delete(self) -> None:
        emp_id = self._selected_id()
        if emp_id is None:
            QMessageBox.information(self, "Удаление", "Выберите сотрудника в таблице.")
            return
        if not ask_yes_no(self, "Удалить выбранного сотрудника?"):
            return
        try:
            self._service.delete_employee(emp_id)
        except AppError as e:
            show_error(self, str(e))
            return
        self.refresh()

    def on_export(self) -> None:
        export_table_to_pdf(self, self.table, "Сотрудники")


