from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QVBoxLayout,
)

from src.core.entities import Employee
from src.core.errors import AppError
from src.services.employee_service import EmployeeService
from src.ui.common import show_error


class EmployeeDialog(QDialog):
    def __init__(self, service: EmployeeService, employee: Employee | None = None, parent=None):
        super().__init__(parent)
        self._service = service
        self._employee = employee.clone() if employee is not None else Employee()

        self.setWindowTitle("Карточка сотрудника")
        self.setModal(True)

        self.last_name = QLineEdit(self._employee.last_name)
        self.first_name = QLineEdit(self._employee.first_name)
        self.middle_name = QLineEdit(self._employee.middle_name or "")
        self.position = QLineEdit(self._employee.position)
        self.phone = QLineEdit(self._employee.phone or "")
        self.email = QLineEdit(self._employee.email or "")
        self.is_active = QCheckBox("Активен")
        self.is_active.setChecked(bool(self._employee.is_active))

        form = QFormLayout()
        form.addRow("Фамилия*", self.last_name)
        form.addRow("Имя*", self.first_name)
        form.addRow("Отчество", self.middle_name)
        form.addRow("Должность*", self.position)
        form.addRow("Телефон", self.phone)
        form.addRow("Email", self.email)
        form.addRow("", self.is_active)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def accept(self) -> None:
        self._employee.last_name = self.last_name.text()
        self._employee.first_name = self.first_name.text()
        self._employee.middle_name = self.middle_name.text().strip() or None
        self._employee.position = self.position.text()
        self._employee.phone = self.phone.text().strip() or None
        self._employee.email = self.email.text().strip() or None
        self._employee.is_active = bool(self.is_active.checkState() == Qt.CheckState.Checked)

        try:
            if self._employee.id is None:
                new_id = self._service.create_employee(self._employee)
                self._employee.id = new_id
            else:
                self._service.update_employee(self._employee)
        except AppError as e:
            show_error(self, str(e))
            return

        super().accept()


