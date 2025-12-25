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
from src.ui.common import ask_yes_no, export_table_to_pdf, show_error
from src.ui.dialogs.client_dialog import ClientDialog


class ClientTab(QWidget):
    def __init__(self, service: ClientService, parent=None):
        super().__init__(parent)
        self._service = service
        self._clients_by_id: dict[int, object] = {}

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["id", "Название", "Телефон", "Email", "Примечание"])
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
            clients = self._service.list_clients()
        except AppError as e:
            show_error(self, str(e))
            clients = []

        self._clients_by_id = {int(c.id): c for c in clients if c.id is not None}

        self.table.setRowCount(0)
        for c in clients:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(c.id or "")))
            self.table.setItem(row, 1, QTableWidgetItem(c.name))
            self.table.setItem(row, 2, QTableWidgetItem(c.phone or ""))
            self.table.setItem(row, 3, QTableWidgetItem(c.email or ""))
            self.table.setItem(row, 4, QTableWidgetItem((c.note or "")[:80]))

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
        dlg = ClientDialog(self._service, None, self)
        if dlg.exec() == dlg.DialogCode.Accepted:
            self.refresh()

    def on_edit(self) -> None:
        cid = self._selected_id()
        if cid is None:
            QMessageBox.information(self, "Изменение", "Выберите клиента в таблице.")
            return
        client = self._clients_by_id.get(cid)
        if client is None:
            QMessageBox.information(self, "Изменение", "Не удалось найти выбранного клиента.")
            return
        dlg = ClientDialog(self._service, client, self)
        if dlg.exec() == dlg.DialogCode.Accepted:
            self.refresh()

    def on_delete(self) -> None:
        cid = self._selected_id()
        if cid is None:
            QMessageBox.information(self, "Удаление", "Выберите клиента в таблице.")
            return
        if not ask_yes_no(self, "Удалить выбранного клиента? (если есть проекты — удаление будет запрещено БД)"):
            return
        try:
            self._service.delete_client(cid)
        except AppError as e:
            show_error(self, str(e))
            return
        self.refresh()

    def on_export(self) -> None:
        export_table_to_pdf(self, self.table, "Клиенты")


