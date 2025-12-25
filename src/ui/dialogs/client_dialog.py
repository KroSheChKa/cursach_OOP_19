from __future__ import annotations

from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QVBoxLayout,
)

from src.core.entities import Client
from src.core.errors import AppError
from src.services.client_service import ClientService
from src.ui.common import show_error


class ClientDialog(QDialog):
    def __init__(self, service: ClientService, client: Client | None = None, parent=None):
        super().__init__(parent)
        self._service = service
        self._client = client.clone() if client is not None else Client()

        self.setWindowTitle("Карточка клиента")
        self.setModal(True)

        self.name = QLineEdit(self._client.name)
        self.phone = QLineEdit(self._client.phone or "")
        self.email = QLineEdit(self._client.email or "")
        self.note = QTextEdit(self._client.note or "")
        self.note.setMinimumHeight(80)

        form = QFormLayout()
        form.addRow("Название*", self.name)
        form.addRow("Телефон", self.phone)
        form.addRow("Email", self.email)
        form.addRow("Примечание", self.note)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def accept(self) -> None:
        self._client.name = self.name.text()
        self._client.phone = self.phone.text().strip() or None
        self._client.email = self.email.text().strip() or None
        self._client.note = self.note.toPlainText().strip() or None

        try:
            if self._client.id is None:
                new_id = self._service.create_client(self._client)
                self._client.id = new_id
            else:
                self._service.update_client(self._client)
        except AppError as e:
            show_error(self, str(e))
            return

        super().accept()


