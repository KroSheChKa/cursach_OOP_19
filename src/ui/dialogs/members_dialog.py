from __future__ import annotations

from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from src.core.entities import Employee
from src.core.errors import AppError
from src.services.project_service import ProjectService
from src.ui.common import ask_yes_no, show_error


class MembersDialog(QDialog):
    def __init__(
        self,
        project_service: ProjectService,
        project_id: int,
        employees: list[Employee],
        parent=None,
    ):
        super().__init__(parent)
        self._service = project_service
        self._project_id = project_id
        self._employees = employees

        self.setWindowTitle("Участники проекта")
        self.setModal(True)

        self.employee_combo = QComboBox()
        for e in employees:
            self.employee_combo.addItem(e.full_name(), e.id)

        self.role = QLineEdit("Member")
        self.btn_add = QPushButton("Добавить")
        self.btn_remove = QPushButton("Удалить выбранного")

        self.btn_add.clicked.connect(self._on_add)
        self.btn_remove.clicked.connect(self._on_remove)

        top = QFormLayout()
        top.addRow("Сотрудник", self.employee_combo)
        top.addRow("Роль", self.role)

        actions = QHBoxLayout()
        actions.addWidget(self.btn_add)
        actions.addWidget(self.btn_remove)
        actions.addStretch(1)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["employee_id", "ФИО", "Должность", "Роль"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.accept)

        layout = QVBoxLayout()
        layout.addLayout(top)
        layout.addLayout(actions)
        layout.addWidget(QLabel("Текущие участники:"))
        layout.addWidget(self.table)
        layout.addWidget(buttons)
        self.setLayout(layout)

        self.refresh()

    def refresh(self) -> None:
        try:
            rows = self._service.list_project_members(self._project_id)
        except AppError as e:
            show_error(self, str(e))
            rows = []

        self.table.setRowCount(0)
        for r in rows:
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)
            emp_id = r["employee_id"]
            fio = " ".join(x for x in [r["last_name"], r["first_name"], r.get("middle_name")] if x)
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(emp_id)))
            self.table.setItem(row_idx, 1, QTableWidgetItem(fio))
            self.table.setItem(row_idx, 2, QTableWidgetItem(str(r.get("position") or "")))
            self.table.setItem(row_idx, 3, QTableWidgetItem(str(r.get("role") or "")))

        self.table.resizeColumnsToContents()

    def _selected_employee_id(self) -> int | None:
        items = self.table.selectedItems()
        if not items:
            return None
        # first column is employee_id
        try:
            return int(items[0].text())
        except ValueError:
            return None

    def _on_add(self) -> None:
        employee_id = int(self.employee_combo.currentData())
        role = self.role.text()
        try:
            self._service.add_project_member(self._project_id, employee_id, role)
        except AppError as e:
            show_error(self, str(e))
            return
        self.refresh()

    def _on_remove(self) -> None:
        employee_id = self._selected_employee_id()
        if employee_id is None:
            QMessageBox.information(self, "Удаление", "Выберите строку участника для удаления.")
            return
        if not ask_yes_no(self, "Удалить выбранного участника из проекта?"):
            return
        try:
            self._service.remove_project_member(self._project_id, employee_id)
        except AppError as e:
            show_error(self, str(e))
            return
        self.refresh()


