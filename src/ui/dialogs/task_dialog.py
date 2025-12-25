from __future__ import annotations

from datetime import datetime

from PyQt6.QtCore import QDate, QDateTime
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDateTimeEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QVBoxLayout,
)

from src.core.entities import Employee, Project, Task
from src.core.errors import AppError
from src.services.task_service import TaskService
from src.ui.common import show_error


class TaskDialog(QDialog):
    def __init__(
        self,
        service: TaskService,
        projects: list[Project],
        employees: list[Employee],
        task: Task | None = None,
        parent=None,
    ):
        super().__init__(parent)
        self._service = service
        self._projects = projects
        self._employees = employees
        self._task = task.clone() if task is not None else Task()

        self.setWindowTitle("Карточка задачи")
        self.setModal(True)

        self.project_combo = QComboBox()
        for p in projects:
            self.project_combo.addItem(p.name, p.id)

        self.employee_combo = QComboBox()
        self.employee_combo.addItem("(не назначено)", None)
        for e in employees:
            self.employee_combo.addItem(e.full_name(), e.id)

        self.title = QLineEdit(self._task.title)
        self.description = QTextEdit(self._task.description or "")
        self.description.setMinimumHeight(80)

        self.due_date = QDateEdit()
        self.due_date.setCalendarPopup(True)
        self.due_date.setDisplayFormat("yyyy-MM-dd")
        self.due_date.setDate(QDate.currentDate())

        self.status = QComboBox()
        for s in TaskService.TASK_STATUSES:
            self.status.addItem(s, s)

        self.has_completed_at = QCheckBox("Указать дату завершения")
        self.completed_at = QDateTimeEdit()
        self.completed_at.setCalendarPopup(True)
        self.completed_at.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.completed_at.setDateTime(QDateTime.currentDateTime())
        self.has_completed_at.toggled.connect(self.completed_at.setEnabled)

        # ---- Fill existing ----
        if self._task.project_id:
            idx = self.project_combo.findData(self._task.project_id)
            if idx >= 0:
                self.project_combo.setCurrentIndex(idx)

        if self._task.employee_id is not None:
            idx = self.employee_combo.findData(self._task.employee_id)
            if idx >= 0:
                self.employee_combo.setCurrentIndex(idx)

        if self._task.due_date:
            self.due_date.setDate(QDate(self._task.due_date.year, self._task.due_date.month, self._task.due_date.day))

        st_idx = self.status.findData(self._task.status)
        if st_idx >= 0:
            self.status.setCurrentIndex(st_idx)

        if self._task.completed_at:
            self.has_completed_at.setChecked(True)
            self.completed_at.setEnabled(True)
            self.completed_at.setDateTime(QDateTime.fromPyDateTime(self._task.completed_at))
        else:
            self.has_completed_at.setChecked(False)
            self.completed_at.setEnabled(False)

        form = QFormLayout()
        form.addRow("Проект*", self.project_combo)
        form.addRow("Исполнитель", self.employee_combo)
        form.addRow("Название*", self.title)
        form.addRow("Описание", self.description)
        form.addRow("Срок (due_date)*", self.due_date)
        form.addRow("Статус", self.status)
        form.addRow(self.has_completed_at, self.completed_at)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def accept(self) -> None:
        self._task.project_id = int(self.project_combo.currentData())
        self._task.employee_id = self.employee_combo.currentData()
        self._task.title = self.title.text()
        self._task.description = self.description.toPlainText().strip() or None
        self._task.due_date = self.due_date.date().toPyDate()
        self._task.status = str(self.status.currentData())

        if self.has_completed_at.isChecked():
            dt = self.completed_at.dateTime().toPyDateTime()
            self._task.completed_at = dt if isinstance(dt, datetime) else None
        else:
            self._task.completed_at = None

        try:
            if self._task.id is None:
                new_id = self._service.create_task(self._task)
                self._task.id = new_id
            else:
                self._service.update_task(self._task)
        except AppError as e:
            show_error(self, str(e))
            return

        super().accept()


