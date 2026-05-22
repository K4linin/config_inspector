"""Страница «Настройки» — карточки разделов с иконками из icons/N.svg."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QPushButton, QScrollArea,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QFont, QPixmap, QPainter, QBrush, QPen

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import styles

# Папка с иконками (SVG) рядом с пакетом pages/
_ICONS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons")


# ── Загрузка иконки из SVG или fallback-квадрат ──────────────────────────────

def _load_svg_px(n: int, bg: str, size: int = 32) -> QPixmap:
    """Загружает icons/{n}.svg; при ошибке — рисует закрашенный квадрат."""
    path = os.path.join(_ICONS_DIR, f"{n}.svg")
    if os.path.isfile(path):
        try:
            from PyQt6.QtSvg import QSvgRenderer
            px = QPixmap(size, size)
            px.fill(Qt.GlobalColor.transparent)
            p = QPainter(px)
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            # фоновый скруглённый прямоугольник
            p.setBrush(QBrush(QColor(bg)))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRoundedRect(0, 0, size, size, 5, 5)
            # SVG поверх
            renderer = QSvgRenderer(path)
            renderer.render(p)
            p.end()
            return px
        except Exception:
            pass
    # Fallback: просто цветной квадрат
    px = QPixmap(size, size)
    px.fill(Qt.GlobalColor.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setBrush(QBrush(QColor(bg)))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRoundedRect(0, 0, size, size, 5, 5)
    p.end()
    return px


# ── Section header ─────────────────────────────────────────────────────────────

def _section_header(title: str) -> QHBoxLayout:
    row = QHBoxLayout()
    row.setSpacing(10)

    lbl = QLabel(title)
    lbl.setStyleSheet("font-size:15px; color:#333; font-weight:500;")
    row.addWidget(lbl)

    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setStyleSheet("color:#CCCCCC;")
    row.addWidget(line, 1)
    return row


# ── Settings card ──────────────────────────────────────────────────────────────

class SettingsCard(QFrame):
    """
    icon_n      : номер иконки (1–10), файл icons/{n}.svg
    bg_color    : цвет фона иконки и заголовка
    title       : заголовок карточки
    description : описание
    links       : список (текст, callable|None) — ссылки внизу карточки
    on_click    : callable, вызывается при клике на карточку (None → info)
    """
    def __init__(self, icon_n, bg_color, title, description,
                 links=None, on_click=None, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setStyleSheet(
            "QFrame#card{background:white;border:1px solid #DDDDDD;border-radius:3px;}"
            "QFrame#card:hover{border-color:#BBBBBB;}"
        )
        self.setMinimumHeight(90)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._on_click = on_click
        self._title    = title

        h = QHBoxLayout(self)
        h.setContentsMargins(12, 12, 12, 12)
        h.setSpacing(12)

        # Иконка (SVG или цветной квадрат)
        icon_lbl = QLabel()
        icon_lbl.setPixmap(_load_svg_px(icon_n, bg_color, 32))
        icon_lbl.setFixedSize(34, 34)
        h.addWidget(icon_lbl, 0, Qt.AlignmentFlag.AlignTop)

        # Текст
        v = QVBoxLayout()
        v.setSpacing(3)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"font-size:13px;font-weight:bold;color:{bg_color};")
        v.addWidget(title_lbl)

        desc_lbl = QLabel(description)
        desc_lbl.setStyleSheet(f"font-size:11px;color:{styles.TEXT_SECONDARY};")
        desc_lbl.setWordWrap(True)
        v.addWidget(desc_lbl)

        if links:
            link_row = QHBoxLayout()
            link_row.setSpacing(6)
            for lnk_text, lnk_cb in links:
                lbl2 = QLabel(
                    f'<a href="#" style="color:{styles.ACCENT_BLUE};'
                    f'text-decoration:none;">{lnk_text}</a>'
                )
                lbl2.setOpenExternalLinks(False)
                lbl2.setStyleSheet("font-size:11px;")
                if lnk_cb:
                    lbl2.linkActivated.connect(lambda _=None, cb=lnk_cb: cb())
                link_row.addWidget(lbl2)
            link_row.addStretch()
            v.addLayout(link_row)

        h.addLayout(v, 1)

    def mousePressEvent(self, e):
        if self._on_click:
            self._on_click()
        else:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(
                self, self._title,
                f"Раздел «{self._title}» открыт (демо-режим)."
            )


# ── SettingsPage ───────────────────────────────────────────────────────────────

def _open_schedule(parent):
    from pages.settings_panels import SchedulePanel
    dlg = SchedulePanel(parent)
    dlg.exec()

def _open_scan(parent):
    from pages.settings_panels import ScanDialog
    dlg = ScanDialog(parent)
    dlg.exec()

def _open_map(parent):
    from pages.settings_panels import NetworkMapPanel
    dlg = NetworkMapPanel(parent)
    dlg.exec()

def _open_reports(parent):
    from pages.settings_panels import ReportsPanel
    dlg = ReportsPanel(parent)
    dlg.exec()


class SettingsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background:{styles.MAIN_BG};")

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background:transparent;border:none;")

        content = QWidget()
        content.setStyleSheet(f"background:{styles.MAIN_BG};")
        v = QVBoxLayout(content)
        v.setContentsMargins(20, 20, 20, 20)
        v.setSpacing(16)

        # ── Настройки сервера ──────────────────────────────────────────────
        v.addLayout(_section_header("Настройки сервера"))

        # Карточки: (icon_n, bg_color, title, description, links, on_click)
        # links = list of (text, callable|None)
        server_cards = [
            (1, styles.ACCENT_GREEN, "Обработка событий",
             "Задание триггеров для обработки событий системы и устройств",
             [], None),
            (2, styles.ACCENT_GREEN, "Профили",
             "Управление профилями для гибкой настройки параметров контроля устройств",
             [], None),
            (3, styles.ACCENT_GREEN, "Устройства",
             "Управление отчётами, проверками, контролем устройств и папок",
             [
                 ("Экспорт",      None),
                 ("Импорт",       None),
                 ("Сканирование", lambda: _open_scan(self)),
                 ("Карта",        lambda: _open_map(self)),
             ],
             lambda: _open_scan(self)),
            (4, styles.ACCENT_GREEN, "Отчёты",
             "Настройка использования и контроля целостности отчётов",
             [], lambda: _open_reports(self)),
            (5, styles.ACCENT_GREEN, "Проверки",
             "Управление проверками устройств, настройка правил и исключений",
             [], None),
            (6, styles.ACCENT_GREEN, "Расписания",
             "Настройка расписаний загрузки отчётов и выполнения операций с устройствами",
             [], lambda: _open_schedule(self)),
        ]

        srv_grid = QGridLayout()
        srv_grid.setSpacing(10)
        for i, args in enumerate(server_cards):
            srv_grid.addWidget(SettingsCard(*args), i // 3, i % 3)
        v.addLayout(srv_grid)

        v.addSpacing(8)

        # ── Администрирование ──────────────────────────────────────────────
        v.addLayout(_section_header("Администрирование"))

        admin_cards = [
            (7,  styles.ACCENT_BLUE, "Модули",
             "Подключение, отключение и настройка модулей системы",
             [], None),
            (8,  styles.ACCENT_BLUE, "Пользователи",
             "Управление пользователями системы и их правами",
             [("Настройки", None)], None),
            (9,  styles.ACCENT_BLUE, "База данных",
             "Настройки хранения данных в БД",
             [], None),
            (10, styles.ACCENT_BLUE, "Лицензии",
             "Управление лицензиями системы",
             [], None),
        ]

        adm_grid = QGridLayout()
        adm_grid.setSpacing(10)
        for i, args in enumerate(admin_cards):
            adm_grid.addWidget(SettingsCard(*args), i // 3, i % 3)
        # Заполнитель для пустых ячеек
        filled = len(admin_cards)
        if filled % 3 != 0:
            for j in range(filled % 3, 3):
                adm_grid.addWidget(QWidget(), filled // 3, j)
        v.addLayout(adm_grid)

        v.addStretch()
        scroll.setWidget(content)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)
