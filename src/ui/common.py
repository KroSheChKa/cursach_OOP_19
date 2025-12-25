from __future__ import annotations

from datetime import datetime
from pathlib import Path
import html

from PyQt6.QtCore import QMarginsF
from PyQt6.QtGui import QPageLayout, QPageSize, QTextDocument
from PyQt6.QtPrintSupport import QPrinter
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QWidget


def show_error(parent: QWidget | None, message: str, title: str = "Ошибка") -> None:
    QMessageBox.critical(parent, title, message)


def show_info(parent: QWidget | None, message: str, title: str = "Сообщение") -> None:
    QMessageBox.information(parent, title, message)


def ask_yes_no(parent: QWidget | None, message: str, title: str = "Подтверждение") -> bool:
    res = QMessageBox.question(
        parent,
        title,
        message,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No,
    )
    return res == QMessageBox.StandardButton.Yes


def export_table_to_pdf(parent: QWidget | None, table, title: str = "Экспорт") -> None:
    """
    Экспорт содержимого QTableWidget в PDF через встроенный принтер Qt.
    Работает с любыми таблицами на вкладках, чтобы не дублировать логику.
    """
    if table.rowCount() == 0 or table.columnCount() == 0:
        QMessageBox.information(parent, "Экспорт", "Нет данных для выгрузки.")
        return

    # Путь по умолчанию: домашняя папка, имя с датой/временем
    safe_name = title.replace(" ", "_")
    suggested = Path.home() / f"{safe_name}_{datetime.now():%Y-%m-%d_%H-%M}.pdf"

    path, _ = QFileDialog.getSaveFileName(
        parent,
        "Сохранить в PDF",
        str(suggested),
        "PDF файлы (*.pdf)",
    )
    if not path:
        return

    try:
        headers = [
            (table.horizontalHeaderItem(i).text() if table.horizontalHeaderItem(i) else f"col_{i+1}")
            for i in range(table.columnCount())
        ]
        rows: list[list[str]] = []
        for r in range(table.rowCount()):
            row_data: list[str] = []
            for c in range(table.columnCount()):
                item = table.item(r, c)
                row_data.append(html.escape(item.text()) if item else "")
            rows.append(row_data)

        html_rows = "".join(
            f"<tr>{''.join(f'<td>{cell}</td>' for cell in row)}</tr>" for row in rows
        )
        html_headers = "".join(f"<th>{html.escape(h)}</th>" for h in headers)

        doc = QTextDocument()
        doc.setHtml(
            f"""
            <html>
                <head>
                    <meta charset="utf-8" />
                    <style>
                        body {{ font-family: Arial, sans-serif; font-size: 10pt; }}
                        h2 {{ margin-bottom: 12px; }}
                        table {{ border-collapse: collapse; width: 100%; }}
                        th, td {{ border: 1px solid #444; padding: 4px 6px; text-align: left; }}
                        th {{ background: #f0f0f0; }}
                    </style>
                </head>
                <body>
                    <h2>{html.escape(title)}</h2>
                    <table>
                        <thead><tr>{html_headers}</tr></thead>
                        <tbody>{html_rows}</tbody>
                    </table>
                </body>
            </html>
            """
        )

        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(path)
        printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
        printer.setPageMargins(QMarginsF(10, 10, 10, 10), QPageLayout.Unit.Millimeter)
        printer.setPageOrientation(QPageLayout.Orientation.Portrait)

        doc.print(printer)
        QMessageBox.information(parent, "Экспорт", f"PDF сохранён:\n{path}")
    except Exception as exc:  # noqa: BLE001
        show_error(parent, f"Не удалось создать PDF: {exc}")


