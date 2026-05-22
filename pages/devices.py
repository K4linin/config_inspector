"""Страница «Устройства» — дерево + 4 вкладки + правая панель с Настройкой/Уязвимостями."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTreeWidget, QTreeWidgetItem, QTabWidget, QLabel,
    QFrame, QScrollArea, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QHeaderView, QAbstractItemView,
    QButtonGroup, QSizePolicy, QComboBox, QSpinBox,
    QTextEdit, QProgressBar, QCheckBox, QGridLayout,
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QTimer
from PyQt6.QtGui import (
    QColor, QFont, QPixmap, QIcon, QPainter, QPen, QBrush,
    QPolygon,
)
from PyQt6.QtCore import QPoint

import styles

# ══════════════════════════════════════════════════════════════════════════════
#  Модель данных
# ══════════════════════════════════════════════════════════════════════════════

DEVICES = {
    "winpc": {
        "name": "winpc", "type": "Windows", "os": "Windows 10 Pro 21H2",
        "profile": "По умолчанию", "description": "Рабочая станция бухгалтерии",
        "ip": "192.168.15.44", "mac": "A4:B1:C2:D3:E4:F5",
        "group_path": "Корневая группа › windows",
        "status": "violation", "last_seen": "03.01.2026 17:44",
        "last_op": 'Загрузка «Windows файлы «Controlmy»»',
        "violations": [
            {"title": "Нарушение целостности", "severity": "high",
             "time": "14:55 03.01.26", "report": "Windows файлы «SecurityCF»"},
            {"title": "Нарушение целостности", "severity": "high",
             "time": "14:57 03.01.26", "report": "Windows файлы «Controlmy»"},
        ],
        "events": [
            ("03.01.2026 17:44:11", "Запуск",   "Задание «proverka»"),
            ("03.01.2026 17:43:51", "Загрузка", "Отчёт «Windows файлы «Controlmy»»"),
            ("03.01.2026 17:43:51", "Загрузка", "Отчёт «Windows файлы «SecurityCF»»"),
            ("03.01.2026 17:43:29", "Загрузка", "Отчёт «Windows файлы «КЦ»»"),
            ("03.01.2026 17:43:25", "Загрузка", "Отчёт «Устройства»"),
            ("03.01.2026 17:43:11", "Запуск",   "Задание «proverka»"),
        ],
        "reports": [
            ("Текстовый отчёт", "autorun.inf",                  "Архив версий",              "3 мин. назад",     False),
            ("Текстовый отчёт", "hosts",                        "Архив версий",              "3 мин. назад",     False),
            ("Отчёт", "Windows файлы «Controlmy»",              "Нарушение 03.01.26 14:57",  "4 мин. назад",     True),
            ("Отчёт", "Windows файлы «SecurityCF»",             "Нарушение 03.01.26 14:55",  "4 мин. назад",     True),
            ("Отчёт", "Windows файлы «КЦ»",                     "Контроль изменений",        "5 мин. назад",     False),
            ("Отчёт", "Драйверы",                               "Архив версий",              "2 мин. назад",     False),
            ("Отчёт", "Журнал неудачных входов",                "Только последний",          "2 мин. назад",     False),
            ("Отчёт", "Информация о системе",                   "Контроль изменений",        "5 мин. назад",     False),
            ("Отчёт", "Службы",                                 "Архив версий",              "2 мин. назад",     False),
        ],
        "config": {
            "Расписание проверки":     ("combo", ["Каждый час", "Каждые 2 ч.", "Ежедневно"], 0),
            "Уведомлять о нарушениях": ("check", True),
            "Порог критичности":       ("spin",  7, 1, 10),
            "Метод контроля":          ("combo", ["SHA-256", "MD5", "Цифровая подпись"], 0),
            "Авт. принятие изменений": ("check", False),
            "Таймаут соединения (с)":  ("spin",  30, 5, 300),
            "Агент активен":           ("check", True),
            "Порт агента":             ("spin",  4044, 1024, 65535),
        },
        "vulnerabilities": [
            {"name": "CVE-2026-0144",  "severity": "critical", "cvss": 9.3,  "fixed": False,
             "desc": "EternalBlue — удалённое выполнение через SMBv1"},
            {"name": "CVE-2019-0708",  "severity": "critical", "cvss": 9.8,  "fixed": False,
             "desc": "BlueKeep — RDP уязвимость"},
            {"name": "CVE-2021-34527", "severity": "high",     "cvss": 8.8,  "fixed": True,
             "desc": "PrintNightmare — Print Spooler"},
            {"name": "CVE-2020-1472",  "severity": "critical", "cvss": 10.0, "fixed": False,
             "desc": "ZeroLogon — обход Netlogon"},
        ],
        "archive": [
            ("03.01.2026 17:44", "Загрузка отчёта",      "Система",   "Успешно"),
            ("03.01.2026 14:57", "Обнаружено нарушение", "Агент",     "Нарушение"),
            ("03.01.2026 14:55", "Обнаружено нарушение", "Агент",     "Нарушение"),
            ("02.01.2026 08:00", "Плановая проверка",    "Система",   "Успешно"),
        ],
    },
    "192.168.0.4": {
        "name": "192.168.0.4", "type": "Windows", "os": "Windows Server 2016",
        "profile": "По умолчанию", "description": "Файловый сервер",
        "ip": "192.168.0.4", "mac": "B2:C3:D4:E5:F6:A7",
        "group_path": "Корневая группа › windows",
        "status": "ok", "last_seen": "03.01.2026 17:30",
        "last_op": "Плановая проверка",
        "violations": [], "events": [],
        "reports": [
            ("Текстовый отчёт", "autorun.inf", "Архив версий", "1 ч. назад", False),
            ("Текстовый отчёт", "hosts",       "Архив версий", "1 ч. назад", False),
        ],
        "config": {
            "Расписание проверки":     ("combo", ["Каждый час", "Каждые 2 ч.", "Ежедневно"], 2),
            "Уведомлять о нарушениях": ("check", True),
            "Порог критичности":       ("spin",  5, 1, 10),
            "Метод контроля":          ("combo", ["SHA-256", "MD5", "Цифровая подпись"], 0),
            "Авт. принятие изменений": ("check", False),
            "Таймаут соединения (с)":  ("spin",  30, 5, 300),
            "Агент активен":           ("check", True),
            "Порт агента":             ("spin",  4044, 1024, 65535),
        },
        "vulnerabilities": [
            {"name": "CVE-2021-34527", "severity": "high", "cvss": 8.8, "fixed": False,
             "desc": "PrintNightmare — Print Spooler"},
        ],
        "archive": [("03.01.2026 17:30", "Плановая проверка", "Система", "Успешно")],
    },
    "192.168.0.1": {
        "name": "192.168.0.1", "type": "Linux", "os": "Ubuntu 20.04 LTS",
        "profile": "По умолчанию", "description": "Маршрутизатор",
        "ip": "192.168.0.1", "mac": "C3:D4:E5:F6:A7:B8",
        "group_path": "Корневая группа › windows",
        "status": "no_connection", "last_seen": "01.01.2026 12:00",
        "last_op": "Нет подключения",
        "violations": [], "events": [], "reports": [],
        "config": {
            "Расписание проверки":     ("combo", ["Каждый час", "Каждые 2 ч.", "Ежедневно"], 0),
            "Уведомлять о нарушениях": ("check", True),
            "Порог критичности":       ("spin",  5, 1, 10),
            "Метод контроля":          ("combo", ["SHA-256", "MD5", "Цифровая подпись"], 0),
            "Авт. принятие изменений": ("check", False),
            "Таймаут соединения (с)":  ("spin",  30, 5, 300),
            "Агент активен":           ("check", False),
            "Порт агента":             ("spin",  4044, 1024, 65535),
        },
        "vulnerabilities": [],
        "archive": [("01.01.2026 12:00", "Потеря соединения", "Агент", "Ошибка")],
    },
    "DC": {
        "name": "DC", "type": "Windows", "os": "Windows Server 2019",
        "profile": "По умолчанию", "description": "Контроллер домена",
        "ip": "192.168.1.1", "mac": "D4:E5:F6:A7:B8:C9",
        "group_path": "Корневая группа › AD",
        "status": "no_connection", "last_seen": "28.12.2025 18:00",
        "last_op": "Нет подключения",
        "violations": [], "events": [], "reports": [],
        "config": {
            "Расписание проверки":     ("combo", ["Каждый час", "Каждые 2 ч.", "Ежедневно"], 0),
            "Уведомлять о нарушениях": ("check", True),
            "Порог критичности":       ("spin",  8, 1, 10),
            "Метод контроля":          ("combo", ["SHA-256", "MD5", "Цифровая подпись"], 0),
            "Авт. принятие изменений": ("check", False),
            "Таймаут соединения (с)":  ("spin",  60, 5, 300),
            "Агент активен":           ("check", False),
            "Порт агента":             ("spin",  4044, 1024, 65535),
        },
        "vulnerabilities": [
            {"name": "CVE-2020-1472", "severity": "critical", "cvss": 10.0, "fixed": False,
             "desc": "ZeroLogon — обход аутентификации Netlogon"},
        ],
        "archive": [("28.12.2025 18:00", "Потеря соединения", "Агент", "Ошибка")],
    },
    "skdpu": {
        "name": "skdpu", "type": "Linux", "os": "CentOS 7",
        "profile": "По умолчанию", "description": "СКДУ — система контроля",
        "ip": "192.168.1.2", "mac": "E5:F6:A7:B8:C9:D0",
        "group_path": "Корневая группа › net",
        "status": "no_connection", "last_seen": "25.12.2025 10:00",
        "last_op": "Нет подключения",
        "violations": [], "events": [], "reports": [],
        "config": {
            "Расписание проверки":     ("combo", ["Каждый час", "Каждые 2 ч.", "Ежедневно"], 1),
            "Уведомлять о нарушениях": ("check", True),
            "Порог критичности":       ("spin",  5, 1, 10),
            "Метод контроля":          ("combo", ["SHA-256", "MD5", "Цифровая подпись"], 0),
            "Авт. принятие изменений": ("check", False),
            "Таймаут соединения (с)":  ("spin",  30, 5, 300),
            "Агент активен":           ("check", False),
            "Порт агента":             ("spin",  4044, 1024, 65535),
        },
        "vulnerabilities": [],
        "archive": [("25.12.2025 10:00", "Потеря соединения", "Агент", "Ошибка")],
    },
}

_STATUS_RU = {
    "ok":            ("● В норме",       styles.ACCENT_GREEN),
    "violation":     ("● Нарушение",     styles.ACCENT_RED),
    "no_connection": ("● Нет связи",     "#AAAAAA"),
    "warning":       ("● Предупрежд.",   "#F0A500"),
    "critical":      ("● Критическое",   styles.ACCENT_RED),
}

_SEV_RU = {
    "critical": ("Крит.",  styles.ACCENT_RED),
    "high":     ("Высок.", "#E07000"),
    "medium":   ("Средн.", "#F0A500"),
    "low":      ("Низк.",  styles.ACCENT_GREEN),
}

# ══════════════════════════════════════════════════════════════════════════════
#  Иконки (ленивые, QPainter)
# ══════════════════════════════════════════════════════════════════════════════

_IC: dict = {}

def _px_icon(color: str, symbol: str, size: int = 16) -> QIcon:
    px = QPixmap(size, size); px.fill(Qt.GlobalColor.transparent)
    p = QPainter(px); p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setBrush(QBrush(QColor(color))); p.setPen(Qt.PenStyle.NoPen)
    p.drawRoundedRect(1, 1, size-2, size-2, 3, 3)
    p.setPen(QPen(QColor("white"), 1))
    p.setFont(QFont("Segoe UI", max(6, size//2-1), QFont.Weight.Bold))
    p.drawText(px.rect(), Qt.AlignmentFlag.AlignCenter, symbol)
    p.end(); return QIcon(px)

def _ic(key: str) -> QIcon:
    if key not in _IC:
        cfg = {
            "folder":  ("#E8A020", "▤"), "win":     ("#5B9BD5", "W"),
            "win_err": ("#D9534F", "!"), "lnx":     ("#4CAF50", "L"),
            "lnx_err": ("#D9534F", "!"), "report":  ("#888888", "≡"),
        }
        color, sym = cfg.get(key, ("#888", "?"))
        _IC[key] = _px_icon(color, sym)
    return _IC[key]


def _toolbar_icon(kind: str, size: int = 18) -> QIcon:
    """Рисуем иконки тулбара через QPainter."""
    key = f"_tb_{kind}_{size}"
    if key in _IC:
        return _IC[key]
    px = QPixmap(size, size); px.fill(Qt.GlobalColor.transparent)
    p = QPainter(px); p.setRenderHint(QPainter.RenderHint.Antialiasing)
    pen = QPen(QColor("#555555"), 1.5)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen); m = 2; s = size

    if kind == "add_group":
        # Папка + плюс
        p.drawRoundedRect(m, m+3, s-m*2, s-m*2-2, 2, 2)
        p.drawLine(m, m+5, m+5, m+5); p.drawLine(m+5, m+5, m+6, m+3)
        p.drawLine(m+6, m+3, m+10, m+3)
        # плюс
        cx, cy = s-5, m+2
        p.setPen(QPen(QColor("#337AB7"), 1.8))
        p.drawLine(cx-2, cy, cx+2, cy); p.drawLine(cx, cy-2, cx, cy+2)

    elif kind == "add_device":
        # Монитор
        p.drawRoundedRect(m, m+2, s-m*2-2, s-m*2-4, 2, 2)
        cx = (s-m*2-2)//2 + m
        p.drawLine(cx, s-m-4, cx, s-m-2)
        p.drawLine(cx-3, s-m-2, cx+3, s-m-2)
        # плюс
        p.setPen(QPen(QColor("#337AB7"), 1.8))
        p.drawLine(s-5, m+2, s-1, m+2); p.drawLine(s-3, m, s-3, m+4)

    elif kind == "edit":
        # Карандаш
        p.drawLine(m+2, s-m-2, s-m-2, m+2)
        p.drawLine(m, s-m, m+4, s-m-1)
        p.drawLine(m, s-m, m+1, s-m-4)
        pts = [QPoint(s-m-2, m+2), QPoint(s-m+1, m+4), QPoint(s-m-1, m+5)]
        p.drawPolyline(QPolygon(pts))

    elif kind == "delete":
        # Корзина
        p.drawRoundedRect(m+2, m+4, s-m*2-4, s-m-6, 1, 1)
        p.drawLine(m, m+3, s-m, m+3)
        p.drawLine(m+4, m+1, s-m-4, m+1)
        p.drawLine(m+4, m+1, m+4, m+3)
        p.drawLine(s-m-4, m+1, s-m-4, m+3)
        # линии внутри
        for x in [m+5, s//2, s-m-5]:
            p.drawLine(x, m+6, x, s-m-3)

    elif kind == "clone":
        # Два листа
        p.drawRoundedRect(m+3, m, s-m-2, s-m-3, 2, 2)
        p.drawRoundedRect(m, m+3, s-m-3, s-m-2, 2, 2)

    elif kind == "refresh":
        # Стрелка-круг
        from math import cos, sin, pi
        from PyQt6.QtCore import QRectF
        cx, cy, r = s/2, s/2, s/2-m
        p.setPen(QPen(QColor("#555555"), 1.5))
        p.drawArc(int(cx-r), int(cy-r), int(r*2), int(r*2), 30*16, 270*16)
        # стрелка
        ex = int(cx + r * cos(30*pi/180))
        ey = int(cy - r * sin(30*pi/180))
        p.drawLine(ex, ey, ex-4, ey); p.drawLine(ex, ey, ex, ey+4)

    elif kind == "filter":
        # Воронка
        pts = [QPoint(m, m+1), QPoint(s-m, m+1),
               QPoint(s//2+2, s//2), QPoint(s//2+2, s-m-1),
               QPoint(s//2-2, s-m-1), QPoint(s//2-2, s//2),
               QPoint(m, m+1)]
        p.drawPolygon(QPolygon(pts))

    elif kind == "expand":
        p.drawLine(m, s//2-2, s//2, s-m-2)
        p.drawLine(s//2, s-m-2, s-m, s//2-2)

    elif kind == "collapse":
        p.drawLine(m, s//2+2, s//2, m+2)
        p.drawLine(s//2, m+2, s-m, s//2+2)

    p.end()
    _IC[key] = QIcon(px)
    return _IC[key]


def _device_icon(dtype: str, status: str) -> QIcon:
    """Иконка устройства с учётом статуса."""
    is_err = status in ("violation", "no_connection", "critical")
    if dtype == "Linux":
        return _ic("lnx_err" if is_err else "lnx")
    return _ic("win_err" if is_err else "win")


# ══════════════════════════════════════════════════════════════════════════════
#  Сворачиваемая секция
# ══════════════════════════════════════════════════════════════════════════════

class _Collapsible(QWidget):
    def __init__(self, title: str, expanded: bool = False, parent=None):
        super().__init__(parent)
        self.setStyleSheet("QWidget{background:white;}")
        v = QVBoxLayout(self); v.setContentsMargins(0, 0, 0, 0); v.setSpacing(0)

        self._btn = QPushButton()
        self._btn.setFlat(True)
        self._btn.setFixedHeight(28)
        self._btn.setCheckable(True)
        self._btn.setChecked(expanded)
        self._btn.setStyleSheet(
            f"QPushButton{{border:none;border-top:1px solid #EEEEEE;"
            f"background:#F5F5F5;color:{styles.TEXT_HEADER};"
            f"text-align:left;padding:0 10px;font-size:10px;font-weight:bold;"
            f"letter-spacing:0.4px;}}"
            f"QPushButton:hover{{background:#EBF3FF;}}"
            f"QPushButton:checked{{background:#EBF3FF;color:{styles.ACCENT_BLUE};}}"
        )
        self._btn.clicked.connect(self._toggle)
        v.addWidget(self._btn)

        self._body = QWidget()
        self._body.setStyleSheet("background:white;")
        self._body_lay = QVBoxLayout(self._body)
        self._body_lay.setContentsMargins(0, 0, 0, 0)
        self._body_lay.setSpacing(0)
        self._body.setVisible(expanded)
        v.addWidget(self._body)

        self._title = title
        self._update_btn_text()

    def _update_btn_text(self):
        arrow = "▼" if self._btn.isChecked() else "▶"
        self._btn.setText(f"  {arrow}  {self._title.upper()}")

    def _toggle(self):
        self._body.setVisible(self._btn.isChecked())
        self._update_btn_text()

    @property
    def body_layout(self) -> QVBoxLayout:
        return self._body_lay

    def set_expanded(self, v: bool):
        self._btn.setChecked(v)
        self._body.setVisible(v)
        self._update_btn_text()


# ══════════════════════════════════════════════════════════════════════════════
#  Вкладка «Статус»
# ══════════════════════════════════════════════════════════════════════════════

class ViolationItem(QFrame):
    accepted = pyqtSignal()
    def __init__(self, title, time_str, link_text, parent=None):
        super().__init__(parent)
        self.setStyleSheet("QFrame{background:white;border:none;"
                           "border-bottom:1px solid #EEEEEE;}")
        self.setMinimumHeight(68)
        lay = QHBoxLayout(self); lay.setContentsMargins(0, 8, 10, 8)
        bar = QFrame(); bar.setFixedWidth(4)
        bar.setStyleSheet("background:#D9534F;border:none;"); lay.addWidget(bar)
        lay.addSpacing(10)
        vb = QVBoxLayout(); vb.setSpacing(2)
        top = QHBoxLayout()
        tl = QLabel(title); tl.setStyleSheet("font-weight:bold;color:#333;font-size:12px;")
        top.addWidget(tl); top.addStretch()
        ck = QPushButton("✓"); ck.setFixedSize(22, 22)
        ck.setStyleSheet("QPushButton{border:1px solid #CCC;background:white;"
                         "color:#999;font-size:11px;border-radius:2px;}"
                         "QPushButton:hover{background:#EEE;}")
        ck.setToolTip("Принять изменение"); ck.clicked.connect(self.accepted)
        top.addWidget(ck); vb.addLayout(top)
        tl2 = QLabel(time_str); tl2.setStyleSheet(
            f"color:{styles.TEXT_SECONDARY};font-size:10px;"); vb.addWidget(tl2)
        lk = QLabel(f'<a href="#" style="color:{styles.ACCENT_BLUE};'
                    f'text-decoration:none;">{link_text}</a>')
        lk.setStyleSheet("font-size:11px;"); vb.addWidget(lk); lay.addLayout(vb)


class StatusTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent); self._build()

    def _build(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0,0,0,0); root.setSpacing(0)

        left = QWidget(); left.setStyleSheet("background:white;")
        lv = QVBoxLayout(left); lv.setContentsMargins(0,0,0,0); lv.setSpacing(0)

        hdr = QLabel("  УВЕДОМЛЕНИЯ"); hdr.setFixedHeight(28)
        hdr.setStyleSheet(f"font-size:10px;font-weight:bold;color:{styles.TEXT_HEADER};"
                          f"background:#FAFAFA;border-bottom:1px solid #EEEEEE;"
                          f"letter-spacing:0.5px;"); lv.addWidget(hdr)

        self._viols_area = QScrollArea()
        self._viols_area.setWidgetResizable(True)
        self._viols_area.setFrameShape(QFrame.Shape.NoFrame)
        self._viols_area.setStyleSheet("background:white;border:none;")
        self._viols_cont = QWidget(); self._viols_cont.setStyleSheet("background:white;")
        self._viols_lay = QVBoxLayout(self._viols_cont)
        self._viols_lay.setContentsMargins(0,0,0,0)
        self._viols_lay.setSpacing(0); self._viols_lay.addStretch()
        self._viols_area.setWidget(self._viols_cont); lv.addWidget(self._viols_area, 1)

        lo = QFrame(); lo.setFixedHeight(28)
        lo.setStyleSheet(f"background:{styles.MAIN_BG};border-top:1px solid #DDDDDD;")
        lor = QHBoxLayout(lo); lor.setContentsMargins(8,0,8,0)
        lbl = QLabel("Последняя операция:")
        lbl.setStyleSheet(f"color:{styles.TEXT_SECONDARY};font-size:10px;")
        lor.addWidget(lbl)
        self._last_op = QLabel()
        self._last_op.setStyleSheet("color:#444;font-size:10px;")
        lor.addWidget(self._last_op); lor.addStretch(); lv.addWidget(lo)

        bot = QFrame(); bot.setFixedHeight(195)
        bot.setStyleSheet("background:white;border-top:2px solid #E0E0E0;")
        bv = QVBoxLayout(bot); bv.setContentsMargins(0,0,0,0); bv.setSpacing(0)
        tab_row = QHBoxLayout(); tab_row.setContentsMargins(8,4,8,0); tab_row.setSpacing(0)
        _ss = (f"QPushButton{{border:none;border-bottom:2px solid transparent;"
               f"padding:4px 10px;background:transparent;color:{styles.TEXT_SECONDARY};"
               f"font-size:11px;}}"
               f"QPushButton:checked{{color:#333;"
               f"border-bottom:2px solid {styles.ACCENT_BLUE};}}")
        grp = QButtonGroup(bot); grp.setExclusive(True)
        for i, txt in enumerate(["Последние события","Расписания  1","Обработчики  3"]):
            b = QPushButton(txt); b.setCheckable(True); b.setFlat(True)
            b.setStyleSheet(_ss); grp.addButton(b, i); tab_row.addWidget(b)
            if i == 0: b.setChecked(True)
        tab_row.addStretch(); bv.addLayout(tab_row)

        self._events_tbl = _make_table(["Дата/время", "Тип", "Описание"], stretch_col=2)
        bv.addWidget(self._events_tbl, 1); lv.addWidget(bot)
        root.addWidget(left, 1)

    def update_device(self, data: dict):
        self._last_op.setText(data.get("last_op", ""))
        while self._viols_lay.count() > 1:
            it = self._viols_lay.takeAt(0)
            if it.widget(): it.widget().deleteLater()
        for v in data.get("violations", []):
            self._viols_lay.insertWidget(
                self._viols_lay.count()-1,
                ViolationItem(v["title"], v.get("time",""), v.get("report",""))
            )
        evs = data.get("events", [])
        self._events_tbl.setRowCount(len(evs))
        for r, row in enumerate(evs):
            dt, typ, desc = (list(row) + ["",""])[:3]
            for c, val in enumerate([dt, typ, desc]):
                self._events_tbl.setItem(r, c, QTableWidgetItem(str(val)))
            self._events_tbl.setRowHeight(r, 20)


# ══════════════════════════════════════════════════════════════════════════════
#  Вкладка «Отчёты»
# ══════════════════════════════════════════════════════════════════════════════

def _make_table(cols, stretch_col=-1):
    t = QTableWidget(0, len(cols))
    t.setHorizontalHeaderLabels(cols)
    t.verticalHeader().hide(); t.setShowGrid(False)
    t.setAlternatingRowColors(True)
    t.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    t.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    t.setStyleSheet(
        "QTableWidget{border:none;font-size:11px;background:white;}"
        "QTableWidget::item{padding:2px 6px;}"
        f"QTableWidget::item:selected{{background:{styles.TABLE_SELECTED};"
        f"color:{styles.TEXT_PRIMARY};}}"
        "QHeaderView::section{background:#F5F5F5;border:none;"
        "border-bottom:1px solid #DDDDDD;padding:3px 6px;font-size:10px;"
        f"color:{styles.TEXT_HEADER};font-weight:bold;}}")
    for i in range(len(cols)):
        if i == stretch_col:
            t.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
        else:
            t.horizontalHeader().setSectionResizeMode(
                i, QHeaderView.ResizeMode.ResizeToContents)
    return t


class ReportsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._viol_only = False; self._reports = []
        self._build()

    def _build(self):
        v = QVBoxLayout(self); v.setContentsMargins(0,0,0,0); v.setSpacing(0)
        filt = QFrame(); filt.setFixedHeight(36)
        filt.setStyleSheet(f"background:white;border-bottom:1px solid {styles.CARD_BORDER};")
        fr = QHBoxLayout(filt); fr.setContentsMargins(6,4,6,4); fr.setSpacing(4)
        _on = (f"QPushButton{{background:{styles.ACCENT_BLUE};color:white;"
               f"border:none;padding:2px 14px;border-radius:2px;font-size:11px;}}"
               f"QPushButton:!checked{{background:#F0F0F0;color:#555;border:1px solid #CCC;}}")
        _off = (f"QPushButton{{background:#F0F0F0;color:#555;border:1px solid #CCC;"
                f"padding:2px 14px;border-radius:2px;font-size:11px;}}"
                f"QPushButton:checked{{background:{styles.ACCENT_BLUE};color:white;border:none;}}")
        self._all_btn = QPushButton("Все")
        self._all_btn.setCheckable(True); self._all_btn.setChecked(True)
        self._all_btn.setFixedHeight(24); self._all_btn.setStyleSheet(_on)
        self._all_btn.clicked.connect(lambda: self._set_filter(False)); fr.addWidget(self._all_btn)
        self._viol_btn = QPushButton("Только нарушения")
        self._viol_btn.setCheckable(True); self._viol_btn.setFixedHeight(24)
        self._viol_btn.setStyleSheet(_off)
        self._viol_btn.clicked.connect(lambda: self._set_filter(True)); fr.addWidget(self._viol_btn)
        fr.addStretch()
        srch = QLineEdit(); srch.setPlaceholderText("Поиск")
        srch.setFixedSize(150, 24); fr.addWidget(srch); v.addWidget(filt)

        self._tree = QTreeWidget()
        self._tree.setColumnCount(4)
        self._tree.setHeaderLabels(["Отчёт", "Состояние", "Обновлён", ""])
        self._tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for i in (1,2): self._tree.header().setSectionResizeMode(
            i, QHeaderView.ResizeMode.ResizeToContents)
        self._tree.header().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self._tree.header().resizeSection(3, 48)
        self._tree.setAlternatingRowColors(True)
        self._tree.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._tree.setRootIsDecorated(False); self._tree.setIndentation(18)
        self._tree.setStyleSheet(
            "QTreeWidget{border:none;background:white;font-size:11px;}"
            "QTreeWidget::item{height:22px;}"
            "QHeaderView::section{background:#F5F5F5;border:none;"
            "border-bottom:1px solid #DDDDDD;padding:3px 6px;font-size:10px;"
            f"color:{styles.TEXT_HEADER};font-weight:bold;}}")
        v.addWidget(self._tree, 1)

    def _set_filter(self, v):
        self._viol_only = v
        self._all_btn.setChecked(not v); self._viol_btn.setChecked(v); self._populate()

    def update_device(self, data: dict):
        self._reports = data.get("reports", []); self._populate()

    def _populate(self):
        self._tree.clear(); groups = {}; bold = QFont(); bold.setBold(True)
        for group, name, state, date, is_viol in self._reports:
            if self._viol_only and not is_viol: continue
            if group not in groups:
                g = QTreeWidgetItem(self._tree, [f"  {group}", "", "", ""])
                g.setFont(0, bold); g.setForeground(0, QColor("#444"))
                for c in range(4): g.setBackground(c, QColor("#F8F8F8"))
                g.setFlags(g.flags() & ~Qt.ItemFlag.ItemIsSelectable); groups[group] = g
            row = QTreeWidgetItem(groups[group], [f"  {name}", state, date, "⬇ ⚙"])
            row.setIcon(0, _ic("report"))
            if is_viol:
                row.setFont(0, bold); row.setForeground(1, QColor(styles.ACCENT_RED))
            else:
                row.setForeground(1, QColor("#666")); row.setForeground(3, QColor("#BBBBBB"))
        self._tree.expandAll()


# ══════════════════════════════════════════════════════════════════════════════
#  Вкладка «События»
# ══════════════════════════════════════════════════════════════════════════════

class EventsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent); self._build()

    def _build(self):
        v = QVBoxLayout(self); v.setContentsMargins(0,0,0,0); v.setSpacing(0)
        filt = QFrame(); filt.setFixedHeight(36)
        filt.setStyleSheet(f"background:white;border-bottom:1px solid {styles.CARD_BORDER};")
        fr = QHBoxLayout(filt); fr.setContentsMargins(8,4,8,4); fr.setSpacing(6)
        lbl = QLabel("Тип:"); lbl.setStyleSheet(
            f"color:{styles.TEXT_SECONDARY};font-size:11px;"); fr.addWidget(lbl)
        self._type_cb = QComboBox()
        self._type_cb.addItems(["Все типы","Загрузка","Запуск","Нарушение","Соединение","Устранение"])
        self._type_cb.setFixedHeight(24)
        self._type_cb.setStyleSheet(
            "QComboBox{border:1px solid #CCC;padding:1px 6px;background:white;"
            "font-size:11px;border-radius:2px;}"); fr.addWidget(self._type_cb)
        fr.addStretch()
        srch = QLineEdit(); srch.setPlaceholderText("Поиск в событиях")
        srch.setFixedSize(180, 24); fr.addWidget(srch); v.addWidget(filt)
        self._tbl = _make_table(["Дата/время","Тип события","Описание"], stretch_col=2)
        v.addWidget(self._tbl, 1)

    def update_device(self, data: dict):
        evs = data.get("events", [])
        self._tbl.setRowCount(len(evs))
        for r, row in enumerate(evs):
            dt, typ, desc = (list(row) + ["",""])[:3]
            for c, val in enumerate([dt, typ, desc]):
                it = QTableWidgetItem(str(val))
                if str(typ) == "Нарушение": it.setForeground(QColor(styles.ACCENT_RED))
                self._tbl.setItem(r, c, it)
            self._tbl.setRowHeight(r, 20)


# ══════════════════════════════════════════════════════════════════════════════
#  Вкладка «Архив»
# ══════════════════════════════════════════════════════════════════════════════

class ArchiveTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent); self._build()

    def _build(self):
        v = QVBoxLayout(self); v.setContentsMargins(0,0,0,0); v.setSpacing(0)
        filt = QFrame(); filt.setFixedHeight(36)
        filt.setStyleSheet(f"background:white;border-bottom:1px solid {styles.CARD_BORDER};")
        fr = QHBoxLayout(filt); fr.setContentsMargins(8,4,8,4); fr.setSpacing(4)
        for txt in ["Всё время","7 дней","Этот месяц"]:
            b = QPushButton(txt); b.setFixedHeight(24)
            b.setStyleSheet(
                f"QPushButton{{background:#F0F0F0;color:#555;border:1px solid #CCC;"
                f"padding:2px 10px;border-radius:2px;font-size:11px;}}"
                f"QPushButton:hover{{background:{styles.ACCENT_BLUE};color:white;border:none;}}")
            fr.addWidget(b)
        fr.addStretch()
        exp = QPushButton("⬇ Экспорт"); exp.setFixedHeight(24)
        exp.setStyleSheet(
            f"QPushButton{{background:white;color:{styles.ACCENT_BLUE};"
            f"border:1px solid {styles.ACCENT_BLUE};padding:2px 10px;"
            f"border-radius:2px;font-size:11px;}}"
            f"QPushButton:hover{{background:{styles.ACCENT_BLUE};color:white;}}")
        fr.addWidget(exp); v.addWidget(filt)
        self._tbl = _make_table(["Дата/время","Действие","Источник","Результат"], stretch_col=1)
        v.addWidget(self._tbl, 1)

    def update_device(self, data: dict):
        rows = data.get("archive", [])
        self._tbl.setRowCount(len(rows))
        for r, (dt, act, src, res) in enumerate(rows):
            for c, val in enumerate([dt, act, src, res]):
                it = QTableWidgetItem(val)
                if c == 3:
                    it.setForeground(QColor(
                        styles.ACCENT_GREEN if res == "Успешно" else
                        styles.ACCENT_RED   if res == "Ошибка"  else "#E07000"))
                self._tbl.setItem(r, c, it)
            self._tbl.setRowHeight(r, 20)


# ══════════════════════════════════════════════════════════════════════════════
#  Правая панель — карточка + сворачиваемые секции
# ══════════════════════════════════════════════════════════════════════════════

class InfoPanel(QWidget):
    action_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(260)
        self.setStyleSheet(
            f"QWidget{{background:white;border-left:1px solid {styles.CARD_BORDER};}}")

        v = QVBoxLayout(self); v.setContentsMargins(0,0,0,0); v.setSpacing(0)

        # ── Статус-карточка ─────────────────────────────────────────────────
        card = QFrame()
        card.setStyleSheet(
            f"QFrame{{background:white;border-bottom:1px solid {styles.CARD_BORDER};}}")
        cv = QVBoxLayout(card); cv.setContentsMargins(12,10,12,10); cv.setSpacing(3)
        self._name_lbl = QLabel()
        self._name_lbl.setStyleSheet("font-size:13px;font-weight:bold;color:#222;")
        cv.addWidget(self._name_lbl)
        self._ip_lbl = QLabel()
        self._ip_lbl.setStyleSheet(
            f"color:{styles.TEXT_SECONDARY};font-size:10px;font-family:Consolas,monospace;")
        cv.addWidget(self._ip_lbl)
        self._status_lbl = QLabel()
        self._status_lbl.setStyleSheet("font-size:11px;font-weight:bold;")
        cv.addWidget(self._status_lbl)
        self._seen_lbl = QLabel()
        self._seen_lbl.setStyleSheet(f"font-size:10px;color:{styles.TEXT_SECONDARY};")
        cv.addWidget(self._seen_lbl)
        v.addWidget(card)

        # ── Прокручиваемая часть ────────────────────────────────────────────
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background:white;border:none;")
        self._body = QWidget(); self._body.setStyleSheet("background:white;")
        self._blay = QVBoxLayout(self._body)
        self._blay.setContentsMargins(0,0,0,0); self._blay.setSpacing(0)

        # Секция: Действия (всегда открыта)
        self._sec_actions = _Collapsible("Действия", expanded=True)
        self._blay.addWidget(self._sec_actions)

        # Секция: Сведения
        self._sec_info = _Collapsible("Сведения", expanded=True)
        self._blay.addWidget(self._sec_info)

        # Секция: Настройка
        self._sec_config = _Collapsible("Настройка", expanded=False)
        self._config_grid: QGridLayout | None = None
        self._blay.addWidget(self._sec_config)

        # Секция: Уязвимости
        self._sec_vulns = _Collapsible("Уязвимости", expanded=False)
        self._blay.addWidget(self._sec_vulns)

        self._blay.addStretch()
        scroll.setWidget(self._body); v.addWidget(scroll, 1)

    # ── Обновление данных ───────────────────────────────────────────────────

    def update_device(self, data: dict):
        self._name_lbl.setText(data.get("name", ""))
        self._ip_lbl.setText(data.get("ip", ""))
        st_text, st_color = _STATUS_RU.get(data.get("status",""), ("●", "#888"))
        self._status_lbl.setText(st_text)
        self._status_lbl.setStyleSheet(
            f"font-size:11px;font-weight:bold;color:{st_color};")
        self._seen_lbl.setText("Посл. связь: " + data.get("last_seen","—"))

        self._rebuild_actions(data)
        self._rebuild_info(data)
        self._rebuild_config(data)
        self._rebuild_vulns(data)

    def _clear_section(self, sec: _Collapsible):
        lay = sec.body_layout
        while lay.count():
            it = lay.takeAt(0)
            if it.widget(): it.widget().deleteLater()

    def _add_info_row(self, lay: QVBoxLayout, key: str, val: str, val_color="#333"):
        w = QWidget(); w.setStyleSheet("background:white;")
        h = QHBoxLayout(w); h.setContentsMargins(12,2,12,2); h.setSpacing(6)
        kl = QLabel(key + ":"); kl.setFixedWidth(80)
        kl.setStyleSheet(f"color:{styles.TEXT_SECONDARY};font-size:10px;")
        vl = QLabel(val); vl.setStyleSheet(f"color:{val_color};font-size:11px;")
        vl.setWordWrap(True); h.addWidget(kl); h.addWidget(vl, 1)
        lay.addWidget(w)

    # Секция Действия
    def _rebuild_actions(self, data: dict):
        self._clear_section(self._sec_actions)
        lay = self._sec_actions.body_layout
        for sym, txt, color in [
            ("↻", "Загрузить отчёты",     styles.ACCENT_GREEN),
            ("▶", "Проверить соединение",  styles.ACCENT_GREEN),
            ("⚙", "Изменить параметры",    styles.ACCENT_BLUE),
            ("✕", "Удалить устройство",    styles.ACCENT_RED),
        ]:
            b = QPushButton(f"  {sym}  {txt}"); b.setFlat(True)
            b.setFixedHeight(28)
            b.setStyleSheet(
                f"QPushButton{{border:none;background:transparent;color:{color};"
                f"text-align:left;padding:0 12px;font-size:11px;}}"
                f"QPushButton:hover{{background:#F0F7FF;}}")
            b.clicked.connect(lambda _=False, t=txt: self.action_requested.emit(t))
            lay.addWidget(b)

    # Секция Сведения
    def _rebuild_info(self, data: dict):
        self._clear_section(self._sec_info)
        lay = self._sec_info.body_layout
        for k, v in [("ОС", data.get("os","—")), ("Тип", data.get("type","—")),
                     ("Профиль", data.get("profile","—")),
                     ("MAC", data.get("mac","—")),
                     ("Группа", data.get("group_path","—").split(" › ")[-1])]:
            self._add_info_row(lay, k, v)
        viols = data.get("violations", [])
        if viols:
            lay.addWidget(_hsep())
            badge = QLabel(f"  ⚠  Нарушений: {len(viols)}")
            badge.setFixedHeight(24)
            badge.setStyleSheet(
                f"background:#FFF3F3;color:{styles.ACCENT_RED};"
                f"font-size:10px;font-weight:bold;"
                f"border-top:1px solid #FFD0D0;border-bottom:1px solid #FFD0D0;")
            lay.addWidget(badge)

    # Секция Настройка
    def _rebuild_config(self, data: dict):
        self._clear_section(self._sec_config)
        lay = self._sec_config.body_layout
        config = data.get("config", {})
        for name, cfg in config.items():
            row_w = QWidget(); row_w.setStyleSheet("background:white;")
            rh = QHBoxLayout(row_w); rh.setContentsMargins(10,3,10,3); rh.setSpacing(6)
            kl = QLabel(name + ":"); kl.setFixedWidth(140)
            kl.setStyleSheet(f"color:{styles.TEXT_SECONDARY};font-size:10px;")
            rh.addWidget(kl)
            kind = cfg[0]
            if kind == "check":
                w = QCheckBox(); w.setChecked(cfg[1])
                w.setStyleSheet(
                    f"QCheckBox::indicator{{width:13px;height:13px;}}"
                    f"QCheckBox::indicator:checked{{background:{styles.ACCENT_BLUE};"
                    f"border:1px solid {styles.ACCENT_BLUE};border-radius:2px;}}"
                    f"QCheckBox::indicator:unchecked{{background:white;"
                    f"border:1px solid #CCC;border-radius:2px;}}")
            elif kind == "spin":
                w = QSpinBox(); w.setValue(cfg[1]); w.setMinimum(cfg[2]); w.setMaximum(cfg[3])
                w.setFixedWidth(70)
                w.setStyleSheet("QSpinBox{border:1px solid #CCC;padding:1px 4px;"
                                "background:white;font-size:10px;border-radius:2px;}")
            elif kind == "combo":
                w = QComboBox(); w.addItems(cfg[1]); w.setCurrentIndex(cfg[2])
                w.setFixedWidth(110)
                w.setStyleSheet("QComboBox{border:1px solid #CCC;padding:1px 4px;"
                                "background:white;font-size:10px;border-radius:2px;}")
            else:
                w = QLabel(str(cfg[1])); w.setStyleSheet("color:#333;font-size:10px;")
            rh.addWidget(w); rh.addStretch(); lay.addWidget(row_w)

        # Кнопки применить/сбросить
        btn_row = QWidget(); btn_row.setStyleSheet("background:white;")
        bh = QHBoxLayout(btn_row); bh.setContentsMargins(10,6,10,6); bh.setSpacing(6)
        bh.addStretch()
        for txt, primary in [("Сбросить", False), ("Применить", True)]:
            b = QPushButton(txt); b.setFixedHeight(24)
            b.setStyleSheet(
                f"QPushButton{{background:{'#337AB7' if primary else '#F0F0F0'};"
                f"color:{'white' if primary else '#555'};"
                f"border:{'none' if primary else '1px solid #CCC'};"
                f"padding:2px 12px;border-radius:2px;font-size:10px;}}"
                f"QPushButton:hover{{background:{'#2260A0' if primary else '#E0E0E0'};}}")
            bh.addWidget(b)
        lay.addWidget(btn_row)

    # Секция Уязвимости
    def _rebuild_vulns(self, data: dict):
        self._clear_section(self._sec_vulns)
        lay = self._sec_vulns.body_layout
        vulns = data.get("vulnerabilities", [])
        if not vulns:
            lbl = QLabel("  Уязвимостей не обнаружено")
            lbl.setFixedHeight(32)
            lbl.setStyleSheet(f"color:{styles.TEXT_SECONDARY};font-size:11px;"
                              f"background:white;"); lay.addWidget(lbl); return

        for vuln in vulns:
            sev_ru, sev_color = _SEV_RU.get(vuln["severity"], ("?", "#888"))
            f = QFrame(); f.setStyleSheet(
                "QFrame{background:white;border:none;"
                "border-bottom:1px solid #F5F5F5;}")
            fh = QHBoxLayout(f); fh.setContentsMargins(0,5,10,5)
            bar = QFrame(); bar.setFixedWidth(3)
            bar.setStyleSheet(f"background:{sev_color};border:none;")
            fh.addWidget(bar); fh.addSpacing(8)
            col = QVBoxLayout(); col.setSpacing(1)
            top = QHBoxLayout(); top.setSpacing(4)
            nl = QLabel(vuln["name"])
            nl.setStyleSheet("font-weight:bold;font-size:10px;color:#222;")
            top.addWidget(nl)
            bl = QLabel(f" {sev_ru} ")
            bl.setStyleSheet(f"background:{sev_color};color:white;font-size:8px;"
                             f"border-radius:2px;padding:0 3px;font-weight:bold;")
            bl.setFixedHeight(14); top.addWidget(bl)
            if vuln.get("fixed"):
                fl = QLabel(" ✓ ")
                fl.setStyleSheet(f"background:{styles.ACCENT_GREEN};color:white;"
                                 f"font-size:8px;border-radius:2px;")
                fl.setFixedHeight(14); top.addWidget(fl)
            top.addStretch(); col.addLayout(top)
            dl = QLabel(vuln.get("desc","")[:40]+"…" if len(vuln.get("desc",""))>40
                        else vuln.get("desc",""))
            dl.setStyleSheet(f"color:{styles.TEXT_SECONDARY};font-size:10px;")
            dl.setWordWrap(True); col.addWidget(dl)
            fh.addLayout(col); lay.addWidget(f)

        # Кнопка «Проверить»
        btn_row = QWidget(); btn_row.setStyleSheet("background:white;")
        bh = QHBoxLayout(btn_row); bh.setContentsMargins(10,6,10,6)
        b = QPushButton("🔍  Запустить сканирование"); b.setFixedHeight(24)
        b.setStyleSheet(
            f"QPushButton{{background:white;color:{styles.ACCENT_BLUE};"
            f"border:1px solid {styles.ACCENT_BLUE};padding:2px 10px;"
            f"border-radius:2px;font-size:10px;}}"
            f"QPushButton:hover{{background:{styles.ACCENT_BLUE};color:white;}}")
        bh.addWidget(b); bh.addStretch(); lay.addWidget(btn_row)


def _hsep() -> QFrame:
    f = QFrame(); f.setFrameShape(QFrame.Shape.HLine)
    f.setStyleSheet("color:#EEEEEE;background:#EEEEEE;max-height:1px;margin:2px 0;")
    return f


# ══════════════════════════════════════════════════════════════════════════════
#  Диалоги тулбара
# ══════════════════════════════════════════════════════════════════════════════

from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QFormLayout, QMessageBox as _MB


def _dlg_ss() -> str:
    return (f"QDialog{{background:{styles.MAIN_BG};}}"
            f"QLabel{{background:transparent;}}")


def _fld_ss() -> str:
    return ("QLineEdit,QComboBox{border:1px solid #CCC;padding:3px 6px;"
            "background:white;font-size:11px;border-radius:2px;}")


class AddGroupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить группу")
        self.setFixedSize(360, 160)
        self.setStyleSheet(_dlg_ss())
        v = QVBoxLayout(self); v.setContentsMargins(16, 16, 16, 16); v.setSpacing(10)
        form = QFormLayout(); form.setSpacing(8)
        self.name_edit = QLineEdit(); self.name_edit.setStyleSheet(_fld_ss())
        self.name_edit.setPlaceholderText("Например: Серверы")
        self.parent_cb = QComboBox(); self.parent_cb.setStyleSheet(_fld_ss())
        self.parent_cb.addItems(["Корневая группа", "windows", "AD", "net"])
        form.addRow("Название группы:", self.name_edit)
        form.addRow("Родительская группа:", self.parent_cb)
        v.addLayout(form)
        bb = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                              QDialogButtonBox.StandardButton.Cancel)
        bb.accepted.connect(self.accept); bb.rejected.connect(self.reject)
        v.addWidget(bb)
        self.setStyleSheet(_dlg_ss() + _fld_ss())

    def result_data(self):
        return self.name_edit.text().strip(), self.parent_cb.currentText()


class AddDeviceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить устройство")
        self.setFixedSize(440, 320)
        self.setStyleSheet(_dlg_ss())
        v = QVBoxLayout(self); v.setContentsMargins(16, 16, 16, 16); v.setSpacing(10)

        lbl = QLabel("Параметры нового устройства")
        lbl.setStyleSheet("font-size:13px;font-weight:bold;color:#333;")
        v.addWidget(lbl)

        form = QFormLayout(); form.setSpacing(8)
        ss = _fld_ss()
        self.f_name   = QLineEdit(); self.f_name.setStyleSheet(ss)
        self.f_ip     = QLineEdit(); self.f_ip.setStyleSheet(ss)
        self.f_ip.setPlaceholderText("192.168.X.X")
        self.f_os     = QComboBox(); self.f_os.setStyleSheet(ss)
        self.f_os.addItems(["Windows 10 Pro", "Windows 11 Pro", "Windows Server 2022",
                            "Ubuntu 22.04 LTS", "CentOS 7", "Debian 12"])
        self.f_type   = QComboBox(); self.f_type.setStyleSheet(ss)
        self.f_type.addItems(["Windows", "Linux"])
        self.f_group  = QComboBox(); self.f_group.setStyleSheet(ss)
        self.f_group.addItems(["windows", "AD", "net", "Корневая группа"])
        self.f_profile = QComboBox(); self.f_profile.setStyleSheet(ss)
        self.f_profile.addItems(["По умолчанию", "Строгий", "Мягкий"])
        form.addRow("Имя / хост:", self.f_name)
        form.addRow("IP-адрес:",   self.f_ip)
        form.addRow("ОС:",         self.f_os)
        form.addRow("Тип:",        self.f_type)
        form.addRow("Группа:",     self.f_group)
        form.addRow("Профиль:",    self.f_profile)
        v.addLayout(form)

        bb = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                              QDialogButtonBox.StandardButton.Cancel)
        bb.accepted.connect(self._on_ok); bb.rejected.connect(self.reject)
        v.addWidget(bb)
        self._ok = False

    def _on_ok(self):
        if not self.f_name.text().strip():
            _MB.warning(self, "Ошибка", "Введите имя устройства."); return
        if not self.f_ip.text().strip():
            _MB.warning(self, "Ошибка", "Введите IP-адрес."); return
        self._ok = True; self.accept()

    def result_data(self):
        return {
            "name":       self.f_name.text().strip(),
            "ip":         self.f_ip.text().strip(),
            "os":         self.f_os.currentText(),
            "type":       self.f_type.currentText(),
            "group":      self.f_group.currentText(),
            "profile":    self.f_profile.currentText(),
        }


class EditDeviceDialog(QDialog):
    def __init__(self, device_data: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Изменить устройство — {device_data.get('name','')}")
        self.setFixedSize(440, 240)
        self.setStyleSheet(_dlg_ss())
        v = QVBoxLayout(self); v.setContentsMargins(16, 16, 16, 16); v.setSpacing(10)
        form = QFormLayout(); form.setSpacing(8)
        ss = _fld_ss()
        self.f_desc    = QLineEdit(device_data.get("description", ""))
        self.f_desc.setStyleSheet(ss)
        self.f_profile = QComboBox(); self.f_profile.setStyleSheet(ss)
        self.f_profile.addItems(["По умолчанию", "Строгий", "Мягкий"])
        self.f_profile.setCurrentText(device_data.get("profile", "По умолчанию"))
        self.f_ip      = QLineEdit(device_data.get("ip", ""))
        self.f_ip.setStyleSheet(ss)
        form.addRow("Описание:", self.f_desc)
        form.addRow("Профиль:",  self.f_profile)
        form.addRow("IP:",       self.f_ip)
        v.addLayout(form)
        bb = QDialogButtonBox(QDialogButtonBox.StandardButton.Save |
                              QDialogButtonBox.StandardButton.Cancel)
        bb.accepted.connect(self.accept); bb.rejected.connect(self.reject)
        v.addWidget(bb)


class FilterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Фильтр устройств")
        self.setFixedSize(340, 260)
        self.setStyleSheet(_dlg_ss())
        v = QVBoxLayout(self); v.setContentsMargins(16, 16, 16, 16); v.setSpacing(10)
        lbl = QLabel("Показывать устройства:")
        lbl.setStyleSheet("font-size:12px;font-weight:bold;color:#333;")
        v.addWidget(lbl)

        ss_cb = (f"QCheckBox{{font-size:11px;color:{styles.TEXT_HEADER};}}"
                 f"QCheckBox::indicator{{width:13px;height:13px;border:1px solid #CCC;"
                 f"border-radius:2px;background:white;}}"
                 f"QCheckBox::indicator:checked{{background:{styles.ACCENT_BLUE};"
                 f"border-color:{styles.ACCENT_BLUE};}}")
        self.checks = {}
        for key, text in [
            ("ok",            "В норме"),
            ("violation",     "С нарушениями"),
            ("no_connection", "Нет связи"),
            ("warning",       "Предупреждения"),
        ]:
            cb = QCheckBox(text); cb.setChecked(True); cb.setStyleSheet(ss_cb)
            v.addWidget(cb); self.checks[key] = cb

        v.addWidget(QLabel("Тип:"))
        self.type_cb = QComboBox()
        self.type_cb.setStyleSheet(_fld_ss())
        self.type_cb.addItems(["Все типы", "Windows", "Linux"])
        v.addWidget(self.type_cb)
        v.addStretch()

        bb = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                              QDialogButtonBox.StandardButton.Cancel)
        bb.accepted.connect(self.accept); bb.rejected.connect(self.reject)
        v.addWidget(bb)


# ══════════════════════════════════════════════════════════════════════════════
#  Главная страница «Устройства»
# ══════════════════════════════════════════════════════════════════════════════

class DevicesPage(QWidget):
    breadcrumb_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background:{styles.MAIN_BG};")
        self._current = "winpc"
        self._device_items: dict[str, QTreeWidgetItem] = {}

        self._tab_status  = StatusTab()
        self._tab_reports = ReportsTab()
        self._tab_events  = EventsTab()
        self._tab_archive = ArchiveTab()
        self._info_panel  = InfoPanel()

        self._build_ui()
        self._apply_device("winpc")

        # Подключаемся к симулятору
        try:
            from data_store import get_store
            get_store().changed.connect(self._on_store_changed)
        except Exception:
            pass

    # ── Построение UI ────────────────────────────────────────────────────────

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0,0,0,0); root.setSpacing(0)
        root.addWidget(self._build_left())

        sep = QFrame(); sep.setFixedWidth(1)
        sep.setStyleSheet(f"background:{styles.CARD_BORDER};"); root.addWidget(sep)

        self._tabs = QTabWidget()
        self._tabs.setDocumentMode(True)
        self._tabs.setStyleSheet(
            f"QTabWidget::pane{{border:none;background:white;}}"
            f"QTabBar::tab{{background:#F5F5F5;color:{styles.TEXT_SECONDARY};"
            f"padding:6px 16px;border:none;"
            f"border-bottom:2px solid transparent;font-size:11px;}}"
            f"QTabBar::tab:selected{{color:#222;background:white;"
            f"border-bottom:2px solid {styles.ACCENT_BLUE};}}"
            f"QTabBar::tab:hover:!selected{{background:#EBEBEB;}}")
        self._tabs.addTab(self._tab_status,  "Статус")
        self._tabs.addTab(self._tab_reports, "Отчёты")
        self._tabs.addTab(self._tab_events,  "События")
        self._tabs.addTab(self._tab_archive, "Архив")
        root.addWidget(self._tabs, 1)

        sep2 = QFrame(); sep2.setFixedWidth(1)
        sep2.setStyleSheet(f"background:{styles.CARD_BORDER};"); root.addWidget(sep2)
        root.addWidget(self._info_panel)

    def _build_left(self) -> QWidget:
        left = QWidget(); left.setFixedWidth(292)
        left.setStyleSheet("background:white;")
        lv = QVBoxLayout(left); lv.setContentsMargins(0,0,0,0); lv.setSpacing(0)

        # ── Тулбар с иконками ─────────────────────────────────────────────
        toolbar = QFrame(); toolbar.setFixedHeight(36)
        toolbar.setStyleSheet(
            f"background:#F5F5F5;border-bottom:1px solid {styles.CARD_BORDER};")
        tbh = QHBoxLayout(toolbar); tbh.setContentsMargins(6,0,6,0); tbh.setSpacing(2)

        def _tb_btn(kind: str, tip: str) -> QPushButton:
            b = QPushButton(); b.setFixedSize(28, 28); b.setToolTip(tip)
            b.setIcon(_toolbar_icon(kind, 18)); b.setIconSize(QSize(18, 18))
            b.setStyleSheet(
                "QPushButton{border:none;background:transparent;border-radius:3px;}"
                "QPushButton:hover{background:#DDEEFF;}"
                "QPushButton:pressed{background:#C5D9EE;}")
            return b

        # Группа 1: создание
        btn_add_grp = _tb_btn("add_group",  "Добавить группу")
        btn_add_dev = _tb_btn("add_device", "Добавить устройство")
        btn_add_grp.clicked.connect(self._on_add_group)
        btn_add_dev.clicked.connect(self._on_add_device)
        tbh.addWidget(btn_add_grp)
        tbh.addWidget(btn_add_dev)

        # Разделитель
        sep = QFrame(); sep.setFixedSize(1, 20)
        sep.setStyleSheet("background:#CCCCCC;"); tbh.addWidget(sep)
        tbh.addSpacing(2)

        # Группа 2: редактирование
        btn_edit   = _tb_btn("edit",   "Изменить")
        btn_delete = _tb_btn("delete", "Удалить")
        btn_clone  = _tb_btn("clone",  "Копировать")
        btn_edit.clicked.connect(self._on_edit_device)
        btn_delete.clicked.connect(self._on_delete_device)
        btn_clone.clicked.connect(self._on_clone_device)
        tbh.addWidget(btn_edit)
        tbh.addWidget(btn_delete)
        tbh.addWidget(btn_clone)

        # Разделитель
        sep2 = QFrame(); sep2.setFixedSize(1, 20)
        sep2.setStyleSheet("background:#CCCCCC;"); tbh.addWidget(sep2)
        tbh.addSpacing(2)

        # Группа 3: сервис
        btn_refresh = _tb_btn("refresh", "Обновить")
        btn_filter  = _tb_btn("filter",  "Фильтр")
        btn_refresh.clicked.connect(self._on_refresh)
        btn_filter.clicked.connect(self._on_filter_dlg)
        tbh.addWidget(btn_refresh)
        tbh.addWidget(btn_filter)

        tbh.addStretch(); lv.addWidget(toolbar)

        # ── Поиск ─────────────────────────────────────────────────────────
        self._search_edit = QLineEdit()
        self._search_edit.setPlaceholderText("Поиск устройств…")
        self._search_edit.setStyleSheet(
            "QLineEdit{border:none;border-bottom:1px solid #EEEEEE;"
            "padding:4px 8px;background:white;font-size:11px;}")
        self._search_edit.textChanged.connect(self._on_filter)
        lv.addWidget(self._search_edit)

        # ── Дерево ────────────────────────────────────────────────────────
        self._tree = self._build_tree(); lv.addWidget(self._tree, 1)

        # ── Нижние переключатели ──────────────────────────────────────────
        bot = QFrame(); bot.setFixedHeight(34)
        bot.setStyleSheet(f"background:#F5F5F5;border-top:1px solid {styles.CARD_BORDER};")
        bh = QHBoxLayout(bot); bh.setContentsMargins(0,0,0,0); bh.setSpacing(0)
        grp = QButtonGroup(bot); grp.setExclusive(True)
        for i, txt in enumerate(["Группы","Типы","Профили"]):
            b = QPushButton(txt); b.setCheckable(True); b.setFlat(True)
            b.setStyleSheet(
                f"QPushButton{{border:none;border-top:2px solid transparent;"
                f"padding:6px 10px;background:transparent;color:#777;font-size:11px;}}"
                f"QPushButton:checked{{color:#333;background:white;"
                f"border-top:2px solid {styles.ACCENT_BLUE};}}"
                f"QPushButton:hover:!checked{{background:#EBEBEB;}}")
            grp.addButton(b, i); bh.addWidget(b)
            if i == 0: b.setChecked(True)
        bh.addStretch(); lv.addWidget(bot)
        return left

    def _build_tree(self) -> QTreeWidget:
        tree = QTreeWidget()
        tree.setHeaderHidden(True); tree.setRootIsDecorated(True)
        tree.setIndentation(16); tree.setAnimated(True)
        tree.setStyleSheet(
            "QTreeWidget{border:none;outline:none;show-decoration-selected:1;}"
            "QTreeWidget::item{height:22px;padding-left:2px;}"
            f"QTreeWidget::item:selected{{background:{styles.TABLE_SELECTED};"
            f"color:{styles.TEXT_PRIMARY};}}"
            "QTreeWidget::item:hover:!selected{background:#EAF2FF;}")

        def add(parent, label, kind, children=None):
            node = QTreeWidgetItem(parent if parent else tree, [f"  {label}"])
            node.setIcon(0, _ic(kind))
            node.setData(0, Qt.ItemDataRole.UserRole,
                         label if label in DEVICES else None)
            if label in DEVICES:
                self._device_items[label] = node
            if children:
                for args in children: add(node, *args)
            return node

        root_node = add(None, "Корневая группа", "folder")
        add(root_node, "AD",  "folder", [("DC",    "win_err")])
        add(root_node, "net", "folder", [("skdpu", "lnx_err")])
        win = add(root_node, "windows", "folder", [
            ("192.168.0.4", "win"),
            ("winpc",       "win"),
            ("192.168.0.1", "lnx_err"),
        ])
        tree.expandAll()
        for i in range(win.childCount()):
            ch = win.child(i)
            if ch.data(0, Qt.ItemDataRole.UserRole) == "winpc":
                tree.setCurrentItem(ch); break
        tree.currentItemChanged.connect(self._on_tree_select)
        return tree

    # ── Фильтр ───────────────────────────────────────────────────────────────

    def _on_filter(self, text: str):
        q = text.strip().lower()
        def _show(item: QTreeWidgetItem) -> bool:
            match = q in item.text(0).lower()
            child_vis = False
            for i in range(item.childCount()):
                cv = _show(item.child(i)); child_vis = child_vis or cv
            vis = match or child_vis
            item.setHidden(not vis)
            if child_vis: item.setExpanded(True)
            return vis
        root = self._tree.invisibleRootItem()
        for i in range(root.childCount()): _show(root.child(i))

    # ── Выбор устройства ─────────────────────────────────────────────────────

    def _on_tree_select(self, current, previous):
        if not current: return
        key = current.data(0, Qt.ItemDataRole.UserRole)
        if key and key in DEVICES: self._apply_device(key)

    def _apply_device(self, name: str):
        self._current = name
        data = self._build_live_data(name)
        self._tab_status.update_device(data)
        self._tab_reports.update_device(data)
        self._tab_events.update_device(data)
        self._tab_archive.update_device(data)
        self._info_panel.update_device(data)
        grp = data.get("group_path", "")
        self.breadcrumb_changed.emit(f"Устройства  ›  {grp}  ›  {name}")

    # ── Слияние статических данных с live-данными из симулятора ──────────────

    def _build_live_data(self, name: str) -> dict:
        """Берём статику из DEVICES, докладываем live-данные из DataStore."""
        import copy
        data = copy.deepcopy(DEVICES.get(name, {}))

        try:
            from data_store import get_store, DeviceStatus
            store = get_store()
            if name not in store.devices:
                return data

            ds = store.devices[name]

            # Статус из store
            data["status"] = ds.status.value

            # Свежие нарушения из store (только для этого устройства)
            live_viols = [
                {"title": v.title, "severity": "high",
                 "time": v.time, "report": v.report}
                for v in store.recent_violations if v.device == name
            ]
            # Вставляем live-нарушения перед статическими
            data["violations"] = live_viols + [
                v for v in data.get("violations", [])
                if v["report"] not in {lv["report"] for lv in live_viols}
            ]

            # Свежие события из store
            live_events = [
                (e[1], e[2], e[3])
                for e in store.system_events if e[0] == name
            ]
            data["events"] = live_events + data.get("events", [])

            # Последняя операция — из последнего события
            if live_events:
                data["last_op"] = live_events[0][2]

        except Exception:
            pass

        return data

    # ── Обновление по сигналу симулятора ─────────────────────────────────────

    def _on_store_changed(self):
        try:
            from data_store import get_store, DeviceStatus
            store = get_store()

            # Обновляем иконки в дереве
            for dev_name, node in self._device_items.items():
                if dev_name in store.devices:
                    ds = store.devices[dev_name]
                    dtype = DEVICES.get(dev_name, {}).get("type", "Windows")
                    node.setIcon(0, _device_icon(dtype, ds.status.value))
                    # Цвет текста
                    if ds.status == DeviceStatus.VIOLATION:
                        node.setForeground(0, QColor(styles.ACCENT_RED))
                    elif ds.status == DeviceStatus.NO_CONNECTION:
                        node.setForeground(0, QColor("#AAAAAA"))
                    else:
                        node.setForeground(0, QColor(styles.TEXT_PRIMARY))

            # Обновляем текущее устройство
            if self._current in store.devices:
                self._apply_device(self._current)

        except Exception:
            pass

    # ── Обработчики тулбара ───────────────────────────────────────────────────

    def _on_add_group(self):
        dlg = AddGroupDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            name, parent_name = dlg.result_data()
            if not name:
                return
            # Найти родительский узел в дереве
            root = self._tree.invisibleRootItem()
            parent_node = self._find_node_by_label(root, parent_name) or root.child(0)
            node = QTreeWidgetItem(parent_node, [f"  {name}"])
            node.setIcon(0, _ic("folder"))
            node.setData(0, Qt.ItemDataRole.UserRole, None)
            parent_node.setExpanded(True)
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Группа добавлена",
                                    f"Группа «{name}» добавлена в «{parent_name}».")

    def _find_node_by_label(self, parent: QTreeWidgetItem, label: str):
        for i in range(parent.childCount()):
            ch = parent.child(i)
            if ch.text(0).strip() == label:
                return ch
            found = self._find_node_by_label(ch, label)
            if found:
                return found
        return None

    def _on_add_device(self):
        dlg = AddDeviceDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            d = dlg.result_data()
            name = d["name"]
            # Добавляем в DEVICES в памяти
            DEVICES[name] = {
                "name": name, "type": d["type"], "os": d["os"],
                "profile": d["profile"], "description": "",
                "ip": d["ip"], "mac": "—",
                "group_path": f"Корневая группа › {d['group']}",
                "status": "ok", "last_seen": "—", "last_op": "Новое устройство",
                "violations": [], "events": [], "reports": [], "config": {},
                "vulnerabilities": [], "archive": [],
            }
            # Найти группу в дереве и добавить узел
            root = self._tree.invisibleRootItem()
            grp_node = self._find_node_by_label(root, d["group"]) or root.child(0)
            kind = "win" if d["type"] == "Windows" else "lnx"
            node = QTreeWidgetItem(grp_node, [f"  {name}"])
            node.setIcon(0, _ic(kind))
            node.setData(0, Qt.ItemDataRole.UserRole, name)
            self._device_items[name] = node
            grp_node.setExpanded(True)
            self._tree.setCurrentItem(node)

    def _on_edit_device(self):
        if not self._current or self._current not in DEVICES:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Изменить", "Выберите устройство."); return
        dlg = EditDeviceDialog(DEVICES[self._current], self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            DEVICES[self._current]["description"] = dlg.f_desc.text().strip()
            DEVICES[self._current]["profile"]     = dlg.f_profile.currentText()
            DEVICES[self._current]["ip"]          = dlg.f_ip.text().strip()
            self._apply_device(self._current)

    def _on_delete_device(self):
        if not self._current or self._current not in DEVICES:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Удалить", "Выберите устройство."); return
        from PyQt6.QtWidgets import QMessageBox
        ans = QMessageBox.question(
            self, "Удаление",
            f"Удалить устройство «{self._current}» из списка контроля?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if ans == QMessageBox.StandardButton.Yes:
            node = self._device_items.pop(self._current, None)
            if node and node.parent():
                node.parent().removeChild(node)
            DEVICES.pop(self._current, None)
            self._current = next(iter(DEVICES), "")
            if self._current:
                self._apply_device(self._current)

    def _on_clone_device(self):
        if not self._current or self._current not in DEVICES:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Копировать", "Выберите устройство."); return
        import copy, datetime
        src = DEVICES[self._current]
        new_name = f"{self._current}_copy"
        DEVICES[new_name] = copy.deepcopy(src)
        DEVICES[new_name]["name"]    = new_name
        DEVICES[new_name]["status"]  = "ok"
        DEVICES[new_name]["last_op"] = "Копия устройства"
        DEVICES[new_name]["violations"] = []
        DEVICES[new_name]["events"]     = []
        # Добавляем в дерево рядом с оригиналом
        orig_node = self._device_items.get(self._current)
        if orig_node and orig_node.parent():
            parent = orig_node.parent()
            dtype  = src.get("type", "Windows")
            kind   = "win" if dtype == "Windows" else "lnx"
            node   = QTreeWidgetItem(parent, [f"  {new_name}"])
            node.setIcon(0, _ic(kind))
            node.setData(0, Qt.ItemDataRole.UserRole, new_name)
            self._device_items[new_name] = node
            self._tree.setCurrentItem(node)
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Копирование",
                                f"Устройство «{new_name}» создано как копия «{self._current}».")

    def _on_refresh(self):
        """Перестраиваем иконки и обновляем текущее устройство."""
        try:
            from data_store import get_store
            store = get_store()
            for dev_name, node in self._device_items.items():
                if dev_name in store.devices:
                    ds   = store.devices[dev_name]
                    dtype = DEVICES.get(dev_name, {}).get("type", "Windows")
                    node.setIcon(0, _device_icon(dtype, ds.status.value))
        except Exception:
            pass
        if self._current:
            self._apply_device(self._current)

    def _on_filter_dlg(self):
        dlg = FilterDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            allowed = {k for k, cb in dlg.checks.items() if cb.isChecked()}
            type_filter = dlg.type_cb.currentText()
            root = self._tree.invisibleRootItem()

            def _apply(item: QTreeWidgetItem):
                key = item.data(0, Qt.ItemDataRole.UserRole)
                if key and key in DEVICES:
                    dev = DEVICES[key]
                    st_ok   = dev.get("status", "ok") in allowed
                    type_ok = (type_filter == "Все типы" or
                               dev.get("type", "") == type_filter)
                    item.setHidden(not (st_ok and type_ok))
                else:
                    item.setHidden(False)
                for i in range(item.childCount()):
                    _apply(item.child(i))

            for i in range(root.childCount()):
                _apply(root.child(i))
