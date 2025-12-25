from __future__ import annotations

from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QVBoxLayout,
)

from src.core.entities import Client, Project
from src.core.errors import AppError
from src.services.project_service import ProjectService
from src.ui.common import show_error


class ProjectDialog(QDialog):
    def __init__(
        self,
        service: ProjectService,
        clients: list[Client],
        project: Project | None = None,
        parent=None,
    ):
        super().__init__(parent)
        self._service = service
        self._clients = clients
        self._project = project.clone() if project is not None else Project()

        self.setWindowTitle("Карточка проекта")
        self.setModal(True)

        self.client_combo = QComboBox()
        for c in clients:
            self.client_combo.addItem(c.name, c.id)

        self.name = QLineEdit(self._project.name)
        self.description = QTextEdit(self._project.description or "")
        self.description.setMinimumHeight(80)

        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDisplayFormat("yyyy-MM-dd")
        self.start_date.setDate(QDate.currentDate())

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDisplayFormat("yyyy-MM-dd")
        self.end_date.setDate(QDate.currentDate())

        self.has_end_date = QCheckBox("Указать дату окончания")
        self.has_end_date.toggled.connect(self.end_date.setEnabled)

        self.status = QComboBox()
        for s in ProjectService.PROJECT_STATUSES:
            self.status.addItem(s, s)

        # ---- Fill existing ----
        if self._project.client_id:
            idx = self.client_combo.findData(self._project.client_id)
            if idx >= 0:
                self.client_combo.setCurrentIndex(idx)

        if self._project.start_date:
            self.start_date.setDate(QDate(self._project.start_date.year, self._project.start_date.month, self._project.start_date.day))

        if self._project.end_date:
            self.has_end_date.setChecked(True)
            self.end_date.setEnabled(True)
            self.end_date.setDate(QDate(self._project.end_date.year, self._project.end_date.month, self._project.end_date.day))
        else:
            self.has_end_date.setChecked(False)
            self.end_date.setEnabled(False)

        st_idx = self.status.findData(self._project.status)
        if st_idx >= 0:
            self.status.setCurrentIndex(st_idx)

        form = QFormLayout()
        form.addRow("Клиент*", self.client_combo)
        form.addRow("Название*", self.name)
        form.addRow("Описание", self.description)
        form.addRow("Дата начала*", self.start_date)
        form.addRow(self.has_end_date, self.end_date)
        form.addRow("Статус", self.status)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def accept(self) -> None:
        self._project.client_id = int(self.client_combo.currentData())
        self._project.name = self.name.text()
        self._project.description = self.description.toPlainText().strip() or None
        self._project.start_date = self.start_date.date().toPyDate()
        self._project.end_date = self.end_date.date().toPyDate() if self.has_end_date.isChecked() else None
        self._project.status = str(self.status.currentData())

        try:
            if self._project.id is None:
                new_id = self._service.create_project(self._project)
                self._project.id = new_id
            else:
                self._service.update_project(self._project)
        except AppError as e:
            show_error(self, str(e))
            return

        super().accept()


