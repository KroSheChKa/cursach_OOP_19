from __future__ import annotations

from PyQt6.QtWidgets import (
    QLabel,
    QMainWindow,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
)

from src.app_context import AppContext
from src.core.errors import AppError
from src.ui.common import show_error
from src.ui.tabs.client_tab import ClientTab
from src.ui.tabs.employee_tab import EmployeeTab
from src.ui.tabs.project_tab import ProjectTab
from src.ui.tabs.reports_tab import ReportsTab
from src.ui.tabs.task_tab import TaskTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ПК «Руководитель проектов»")

        self._ctx = AppContext()

        self.btn_connect = QPushButton("Подключиться к MySQL")
        self.status = QLabel("Статус: не подключено")

        self.btn_connect.clicked.connect(self.on_connect)

        top = QHBoxLayout()
        top.addWidget(self.btn_connect)
        top.addWidget(self.status, 1)

        self.tabs = QTabWidget()

        root = QWidget()
        layout = QVBoxLayout()
        layout.addLayout(top)
        layout.addWidget(self.tabs)
        root.setLayout(layout)
        self.setCentralWidget(root)

        # авто‑подключение (если config.ini уже создан)
        self.on_connect(auto=True)

    def on_connect(self, *, auto: bool = False) -> None:
        if self._ctx.clients is not None:
            return
        try:
            self._ctx.connect()
        except AppError as e:
            self.status.setText("Статус: ошибка подключения (см. сообщение)")
            if not auto:
                show_error(self, str(e))
            return

        assert self._ctx.clients is not None
        assert self._ctx.employees is not None
        assert self._ctx.projects is not None
        assert self._ctx.tasks is not None
        assert self._ctx.reports is not None

        self.status.setText("Статус: подключено")
        self.btn_connect.setEnabled(False)

        self._build_tabs()

    def _build_tabs(self) -> None:
        # Tabs
        employee_tab = EmployeeTab(self._ctx.employees, self)
        client_tab = ClientTab(self._ctx.clients, self)
        project_tab = ProjectTab(self._ctx.projects, self._ctx.clients, self._ctx.employees, self)
        task_tab = TaskTab(self._ctx.tasks, self._ctx.projects, self._ctx.employees, self)
        reports_tab = ReportsTab(self._ctx.reports, self._ctx.clients, self._ctx.projects, self._ctx.employees, self)

        self.tabs.addTab(employee_tab, "Сотрудники")
        self.tabs.addTab(client_tab, "Клиенты")
        self.tabs.addTab(project_tab, "Проекты")
        self.tabs.addTab(task_tab, "Задачи")
        self.tabs.addTab(reports_tab, "Отчёты")

        # Initial refresh
        employee_tab.refresh()
        client_tab.refresh()
        project_tab.refresh()
        task_tab.refresh()
        reports_tab.refresh_sources()


