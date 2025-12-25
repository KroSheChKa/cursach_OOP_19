from __future__ import annotations

if __name__ == "__main__" and __package__ is None:
    # Позволяет запускать файл напрямую: `python src/main.py`
    # (когда рабочая папка = src, пакет `src` иначе не находится).
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import sys

from PyQt6.QtWidgets import QApplication

from src.ui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())


