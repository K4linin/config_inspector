import sys
import os

# Ensure local packages are importable regardless of CWD
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from styles import get_app_stylesheet


def main():
    # High-DPI support
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("Config Inspector")
    app.setOrganizationName("Efros")
    app.setStyleSheet(get_app_stylesheet())

    # Импортируем ПОСЛЕ создания QApplication — некоторые модули
    # создают QPixmap на уровне модуля, что требует QGuiApplication.
    from login_window import LoginWindow
    from app_window import MainWindow
    from pages.monitoring import MonitoringPage
    from pages.devices import DevicesPage
    from pages.events import EventsPage
    from pages.settings import SettingsPage
    from data_store import get_store
    from simulator import Simulator

    # ── Shared data store (created once here, pages call get_store() lazily) ──
    store = get_store()

    # ── Simulator ─────────────────────────────────────────────────────────────
    sim = Simulator(store)

    # ── Main window (hidden until login) ──────────────────────────────────────
    win = MainWindow()
    win.add_page(MonitoringPage())  # 0 — Мониторинг
    win.add_page(DevicesPage())     # 1 — Устройства
    win.add_page(EventsPage())      # 2 — События
    win.add_page(SettingsPage())    # 3 — Настройки

    # Wire simulator to the window's simulation bar
    win.set_simulator(sim)

    # ── Login window ──────────────────────────────────────────────────────────
    login = LoginWindow()

    # Wire DevicesPage breadcrumb → MainWindow title bar
    devices_page = win._stack.widget(1)
    if hasattr(devices_page, "breadcrumb_changed"):
        devices_page.breadcrumb_changed.connect(win.set_breadcrumb)

    def on_logged_in():
        login.hide()
        win.navigate(0)
        win.show()
        win.activateWindow()

    login.login_successful.connect(on_logged_in)
    login.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
