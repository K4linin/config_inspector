"""Диалоговые панели для страницы Настройки."""
import sys, os, random
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QPushButton, QTableWidget, QTableWidgetItem,
    QLineEdit, QComboBox, QHeaderView, QAbstractItemView,
    QDialogButtonBox, QProgressBar, QCheckBox, QSpinBox,
    QScrollArea, QSizePolicy, QMessageBox, QTabWidget,
    QTimeEdit, QDateEdit,
)
from PyQt6.QtCore import Qt, QSize, QTimer, QTime, QDate, QPoint, QRect
from PyQt6.QtGui import (
    QColor, QFont, QPainter, QPen, QBrush, QPixmap,
)

import styles

# ══════════════════════════════════════════════════════════════════════════════
#  Утилиты
# ══════════════════════════════════════════════════════════════════════════════

def _dlg_style() -> str:
    return (f"QDialog{{background:{styles.MAIN_BG};}}"
            f"QLabel{{background:transparent;}}"
            f"QFrame{{background:transparent;}}")

def _section_lbl(text: str) -> QLabel:
    l = QLabel(text)
    l.setStyleSheet(f"font-size:12px;font-weight:bold;color:#333;"
                    f"padding-bottom:4px;border-bottom:1px solid #DDDDDD;")
    return l

def _primary_btn(text: str) -> QPushButton:
    b = QPushButton(text)
    b.setFixedHeight(28)
    b.setStyleSheet(
        f"QPushButton{{background:{styles.ACCENT_BLUE};color:white;border:none;"
        f"padding:2px 16px;border-radius:2px;font-size:11px;}}"
        f"QPushButton:hover{{background:#2260A0;}}"
    )
    return b

def _sec_btn(text: str) -> QPushButton:
    b = QPushButton(text)
    b.setFixedHeight(28)
    b.setStyleSheet(
        "QPushButton{background:white;color:#555;border:1px solid #CCC;"
        "padding:2px 14px;border-radius:2px;font-size:11px;}"
        "QPushButton:hover{background:#EBEBEB;}"
    )
    return b

def _make_tbl(cols: list, stretch: int = -1) -> QTableWidget:
    t = QTableWidget(0, len(cols))
    t.setHorizontalHeaderLabels(cols)
    t.verticalHeader().hide(); t.setShowGrid(False)
    t.setAlternatingRowColors(True)
    t.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    t.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    t.setStyleSheet(
        "QTableWidget{border:1px solid #DDDDDD;font-size:11px;background:white;}"
        "QTableWidget::item{padding:3px 6px;}"
        f"QTableWidget::item:selected{{background:{styles.TABLE_SELECTED};"
        f"color:{styles.TEXT_PRIMARY};}}"
        "QHeaderView::section{background:#F5F5F5;border:none;"
        "border-bottom:1px solid #DDDDDD;padding:4px 6px;font-size:10px;"
        f"color:{styles.TEXT_HEADER};font-weight:bold;}}")
    for i in range(len(cols)):
        m = QHeaderView.ResizeMode.Stretch if i == stretch else QHeaderView.ResizeMode.ResizeToContents
        t.horizontalHeader().setSectionResizeMode(i, m)
    return t


# ══════════════════════════════════════════════════════════════════════════════
#  Расписание загрузки отчётов и выполнения операций
# ══════════════════════════════════════════════════════════════════════════════

_SCHED_DATA = [
    ("proverka",         "winpc",       "Загрузка отчёта",  "Каждый час",     "03.01.2026 17:44", "Активно"),
    ("security_check",   "192.168.0.4", "Проверка",         "Ежедневно 08:00","03.01.2026 08:00", "Активно"),
    ("full_scan",        "winpc",       "Полное сканирование","Еженедельно Пн","30.12.2025 08:00", "Активно"),
    ("backup_report",    "DC",          "Резервная копия",  "Ежедневно 23:00","—",                "Ожидание"),
    ("audit_log",        "Сервер",      "Аудит",            "Каждые 30 мин",  "03.01.2026 17:30", "Активно"),
    ("integrity_check",  "skdpu",       "Контроль целостности","Ежедневно 06:00","—",             "Остановлено"),
]


class SchedulePanel(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Расписание загрузки отчётов и выполнения операций")
        self.setMinimumSize(860, 580)
        self.setStyleSheet(_dlg_style())
        self._build()

    def _build(self):
        v = QVBoxLayout(self); v.setContentsMargins(16, 16, 16, 16); v.setSpacing(10)

        v.addWidget(_section_lbl("Расписание загрузки отчётов и выполнения операций"))

        # Панель инструментов
        tb = QHBoxLayout(); tb.setSpacing(6)
        self._add_btn   = _primary_btn("＋  Добавить")
        self._edit_btn  = _sec_btn("✎  Изменить")
        self._del_btn   = _sec_btn("✕  Удалить")
        self._run_btn   = _sec_btn("▶  Выполнить сейчас")
        for b in (self._add_btn, self._edit_btn, self._del_btn, self._run_btn):
            tb.addWidget(b)
        tb.addStretch()

        self._status_lbl = QLabel()
        self._status_lbl.setStyleSheet(
            f"color:{styles.ACCENT_GREEN};font-size:11px;")
        tb.addWidget(self._status_lbl)
        v.addLayout(tb)

        # Таблица расписаний
        self._tbl = _make_tbl(
            ["Название задания", "Устройство", "Тип операции",
             "Расписание", "Последнее выполнение", "Статус"], stretch=0)
        self._tbl.setMinimumHeight(280)

        for row_data in _SCHED_DATA:
            r = self._tbl.rowCount(); self._tbl.insertRow(r)
            for c, val in enumerate(row_data):
                it = QTableWidgetItem(val)
                if c == 5:
                    color = (styles.ACCENT_GREEN  if val == "Активно"    else
                             "#F0A500"             if val == "Ожидание"   else
                             styles.ACCENT_RED)
                    it.setForeground(QColor(color))
                self._tbl.setItem(r, c, it)
            self._tbl.setRowHeight(r, 22)
        v.addWidget(self._tbl)

        # Раздел настройки нового задания
        v.addSpacing(4)
        v.addWidget(_section_lbl("Параметры задания"))

        grid = QGridLayout(); grid.setSpacing(8)
        lbl_ss = f"color:{styles.TEXT_HEADER};font-size:11px;"
        fld_ss = ("QLineEdit,QComboBox,QTimeEdit,QDateEdit{border:1px solid #CCC;"
                  "padding:3px 6px;background:white;font-size:11px;border-radius:2px;}")

        fields = [
            ("Название:",      QLineEdit),
            ("Устройство:",    QComboBox),
            ("Тип операции:",  QComboBox),
            ("Расписание:",    QComboBox),
        ]
        self._flds = {}
        for i, (name, Cls) in enumerate(fields):
            lbl = QLabel(name); lbl.setStyleSheet(lbl_ss)
            w = Cls(); w.setStyleSheet(fld_ss); w.setFixedHeight(26)
            if isinstance(w, QComboBox):
                if "Устройство" in name:
                    w.addItems(["winpc", "192.168.0.4", "192.168.0.1", "DC", "skdpu", "Сервер"])
                elif "Тип" in name:
                    w.addItems(["Загрузка отчёта", "Проверка", "Полное сканирование",
                                "Резервная копия", "Аудит", "Контроль целостности"])
                elif "Расписание" in name:
                    w.addItems(["Каждые 15 мин", "Каждые 30 мин", "Каждый час",
                                "Каждые 2 ч.", "Ежедневно 08:00", "Ежедневно 23:00",
                                "Еженедельно Пн", "Еженедельно Пт"])
            row, col = divmod(i, 2)
            grid.addWidget(lbl, row, col*2)
            grid.addWidget(w,   row, col*2+1)
            self._flds[name] = w
        grid.setColumnStretch(1, 1); grid.setColumnStretch(3, 1)
        v.addLayout(grid)

        # Кнопки
        brow = QHBoxLayout(); brow.addStretch()
        save = _primary_btn("Сохранить задание")
        save.clicked.connect(self._on_save)
        brow.addWidget(save); brow.addWidget(_sec_btn("Закрыть"))
        v.addLayout(brow)

        # Подключаем кнопки тулбара
        self._add_btn.clicked.connect(self._on_add)
        self._edit_btn.clicked.connect(self._on_edit)
        self._del_btn.clicked.connect(self._on_delete)
        self._run_btn.clicked.connect(self._on_run)

    def _on_save(self):
        name = self._flds.get("Название:")
        if isinstance(name, QLineEdit) and name.text().strip():
            r = self._tbl.rowCount(); self._tbl.insertRow(r)
            device = self._flds["Устройство:"].currentText()
            op     = self._flds["Тип операции:"].currentText()
            sched  = self._flds["Расписание:"].currentText()
            for c, val in enumerate([name.text(), device, op, sched, "—", "Ожидание"]):
                self._tbl.setItem(r, c, QTableWidgetItem(val))
            self._tbl.setRowHeight(r, 22)
            name.clear()
            self._status_lbl.setText("✓ Задание добавлено")
            QTimer.singleShot(3000, lambda: self._status_lbl.setText(""))

    def _on_add(self):
        if isinstance(self._flds.get("Название:"), QLineEdit):
            self._flds["Название:"].setFocus()

    def _on_edit(self):
        r = self._tbl.currentRow()
        if r < 0:
            QMessageBox.information(self, "Изменение", "Выберите задание в таблице."); return
        name = self._tbl.item(r, 0).text() if self._tbl.item(r, 0) else ""
        QMessageBox.information(self, "Изменение", f"Редактирование задания «{name}» (демо).")

    def _on_delete(self):
        r = self._tbl.currentRow()
        if r < 0:
            QMessageBox.information(self, "Удаление", "Выберите задание."); return
        name = self._tbl.item(r, 0).text() if self._tbl.item(r, 0) else ""
        if QMessageBox.question(self, "Удаление", f"Удалить задание «{name}»?",
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                                ) == QMessageBox.StandardButton.Yes:
            self._tbl.removeRow(r)

    def _on_run(self):
        r = self._tbl.currentRow()
        if r < 0:
            QMessageBox.information(self, "Выполнение", "Выберите задание."); return
        name = self._tbl.item(r, 0).text() if self._tbl.item(r, 0) else ""
        self._status_lbl.setText(f"▶ Выполняется: {name}…")
        QTimer.singleShot(2500, lambda: self._status_lbl.setText(f"✓ {name} выполнено"))


# ══════════════════════════════════════════════════════════════════════════════
#  Сканирование сети
# ══════════════════════════════════════════════════════════════════════════════

class ScanDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Сканирование сети")
        self.setMinimumSize(680, 500)
        self.setStyleSheet(_dlg_style())
        self._scan_results = []
        self._build()

    def _build(self):
        v = QVBoxLayout(self); v.setContentsMargins(16, 16, 16, 16); v.setSpacing(10)
        v.addWidget(_section_lbl("Сканирование сети — обнаружение устройств"))

        # Настройки сканирования
        cfg = QFrame(); cfg.setStyleSheet(
            "QFrame{background:white;border:1px solid #DDDDDD;border-radius:3px;padding:4px;}")
        cv = QGridLayout(cfg); cv.setContentsMargins(12,10,12,10); cv.setSpacing(8)
        fld_ss = ("QLineEdit,QComboBox{border:1px solid #CCC;padding:3px 6px;"
                  "background:white;font-size:11px;border-radius:2px;}")
        lbl_ss = f"color:{styles.TEXT_HEADER};font-size:11px;"

        cv.addWidget(QLabel("Диапазон IP:"), 0, 0)
        self._ip_from = QLineEdit("192.168.0.1"); self._ip_from.setStyleSheet(fld_ss)
        self._ip_from.setFixedWidth(140)
        cv.addWidget(self._ip_from, 0, 1)
        cv.addWidget(QLabel("—"), 0, 2)
        self._ip_to = QLineEdit("192.168.1.254"); self._ip_to.setStyleSheet(fld_ss)
        self._ip_to.setFixedWidth(140)
        cv.addWidget(self._ip_to, 0, 3)

        cv.addWidget(QLabel("Подсеть:"), 1, 0)
        self._subnet = QLineEdit("255.255.255.0"); self._subnet.setStyleSheet(fld_ss)
        self._subnet.setFixedWidth(140)
        cv.addWidget(self._subnet, 1, 1)

        cv.addWidget(QLabel("Протокол:"), 1, 2)
        self._proto = QComboBox(); self._proto.addItems(["ICMP (Ping)", "ARP", "TCP SYN", "SNMP"])
        self._proto.setStyleSheet(fld_ss); self._proto.setFixedWidth(140)
        cv.addWidget(self._proto, 1, 3)

        lbl_t = QLabel("Таймаут (мс):"); lbl_t.setStyleSheet(lbl_ss)
        cv.addWidget(lbl_t, 2, 0)
        self._timeout = QSpinBox(); self._timeout.setRange(100, 5000); self._timeout.setValue(500)
        self._timeout.setStyleSheet(fld_ss); self._timeout.setFixedWidth(80)
        cv.addWidget(self._timeout, 2, 1)

        cv.addWidget(QLabel("Потоков:"), 2, 2)
        self._threads = QSpinBox(); self._threads.setRange(1, 64); self._threads.setValue(16)
        self._threads.setStyleSheet(fld_ss); self._threads.setFixedWidth(80)
        cv.addWidget(self._threads, 2, 3)

        v.addWidget(cfg)

        # Прогресс
        self._progress = QProgressBar()
        self._progress.setRange(0, 100); self._progress.setValue(0)
        self._progress.setFixedHeight(16)
        self._progress.setStyleSheet(
            f"QProgressBar{{border:1px solid #CCC;border-radius:2px;background:white;text-align:center;"
            f"font-size:10px;color:#555;}}"
            f"QProgressBar::chunk{{background:{styles.ACCENT_BLUE};border-radius:2px;}}")
        self._progress.setVisible(False)
        v.addWidget(self._progress)

        # Кнопки управления
        br = QHBoxLayout(); br.setSpacing(6)
        self._scan_btn = _primary_btn("🔍  Начать сканирование")
        self._scan_btn.clicked.connect(self._start_scan)
        self._stop_btn = _sec_btn("■  Стоп")
        self._stop_btn.setEnabled(False)
        self._stop_btn.clicked.connect(self._stop_scan)
        self._add_selected = _sec_btn("＋  Добавить выбранные")
        self._add_selected.clicked.connect(self._add_devices)
        self._status_scan = QLabel()
        self._status_scan.setStyleSheet(f"color:{styles.ACCENT_GREEN};font-size:11px;")
        for w in (self._scan_btn, self._stop_btn, self._add_selected): br.addWidget(w)
        br.addStretch(); br.addWidget(self._status_scan)
        v.addLayout(br)

        # Результаты
        lbl_r = QLabel("Обнаруженные устройства:"); lbl_r.setStyleSheet(
            f"font-size:11px;font-weight:bold;color:#333;")
        v.addWidget(lbl_r)

        self._res_tbl = _make_tbl(
            ["IP-адрес", "Имя хоста", "ОС", "MAC-адрес", "Статус", "Время отклика"], stretch=1)
        v.addWidget(self._res_tbl, 1)

        # Таймер симуляции сканирования
        self._sim_timer = QTimer(); self._sim_timer.timeout.connect(self._sim_step)
        self._sim_step_n = 0

    def _start_scan(self):
        self._res_tbl.setRowCount(0)
        self._progress.setValue(0); self._progress.setVisible(True)
        self._scan_btn.setEnabled(False); self._stop_btn.setEnabled(True)
        self._status_scan.setText("Сканирование…")
        self._sim_step_n = 0
        self._sim_timer.start(200)

    def _stop_scan(self):
        self._sim_timer.stop()
        self._scan_btn.setEnabled(True); self._stop_btn.setEnabled(False)
        self._status_scan.setText("Остановлено")

    _SIM_DEVICES = [
        ("192.168.0.1",  "router.local",    "Linux / OpenWRT",         "C3:D4:E5:F6:A7:B8", "Доступен",    "2 мс"),
        ("192.168.0.4",  "fileserver.local","Windows Server 2016",     "B2:C3:D4:E5:F6:A7", "Доступен",    "1 мс"),
        ("192.168.0.15", "winpc.local",     "Windows 10 Pro",          "A4:B1:C2:D3:E4:F5", "Доступен",    "3 мс"),
        ("192.168.1.1",  "DC.local",        "Windows Server 2019",     "D4:E5:F6:A7:B8:C9", "Нет ответа",  "—"),
        ("192.168.1.2",  "skdpu.local",     "CentOS 7",                "E5:F6:A7:B8:C9:D0", "Нет ответа",  "—"),
        ("192.168.0.100","unknown-100",     "Неизвестно",              "F1:A2:B3:C4:D5:E6", "Доступен",    "8 мс"),
    ]

    def _sim_step(self):
        total = len(self._SIM_DEVICES)
        self._sim_step_n += 1
        pct = min(100, int(self._sim_step_n / total * 100))
        self._progress.setValue(pct)

        idx = self._sim_step_n - 1
        if idx < total:
            dev = self._SIM_DEVICES[idx]
            r = self._res_tbl.rowCount(); self._res_tbl.insertRow(r)
            for c, val in enumerate(dev):
                it = QTableWidgetItem(val)
                if c == 4:
                    it.setForeground(QColor(styles.ACCENT_GREEN if val == "Доступен"
                                           else styles.ACCENT_RED))
                self._res_tbl.setItem(r, c, it)
            self._res_tbl.setRowHeight(r, 22)

        if self._sim_step_n >= total:
            self._sim_timer.stop()
            self._scan_btn.setEnabled(True); self._stop_btn.setEnabled(False)
            self._progress.setValue(100)
            self._status_scan.setText(f"✓ Найдено устройств: {total}")

    def _add_devices(self):
        rows = {i.row() for i in self._res_tbl.selectedItems()}
        if not rows:
            QMessageBox.information(self, "Добавление", "Выберите устройства в таблице."); return
        n = len(rows)
        QMessageBox.information(self, "Добавление",
                                f"Добавлено {n} устройств в список контроля (демо).")


# ══════════════════════════════════════════════════════════════════════════════
#  Интерактивная карта сети
# ══════════════════════════════════════════════════════════════════════════════

_MAP_NODES = {
    "Сервер":       (320, 60,  "ok",            "Windows Server"),
    "winpc":        (120, 200, "violation",      "Windows 10"),
    "192.168.0.4":  (320, 200, "ok",             "Win Server 2016"),
    "192.168.0.1":  (520, 200, "no_connection",  "Ubuntu 20.04"),
    "DC":           (200, 330, "no_connection",  "Win Server 2019"),
    "skdpu":        (450, 330, "no_connection",  "CentOS 7"),
}
_MAP_EDGES = [
    ("Сервер", "winpc"), ("Сервер", "192.168.0.4"),
    ("Сервер", "192.168.0.1"), ("Сервер", "DC"), ("Сервер", "skdpu"),
    ("192.168.0.4", "DC"),
]
_STATUS_COLORS = {
    "ok":            "#4CAF50",
    "violation":     "#D9534F",
    "no_connection": "#AAAAAA",
}

class _MapCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(640, 400)
        self.setStyleSheet("background:white;")
        self._selected = None
        self._hovered  = None
        self.setMouseTracking(True)

    def _node_rect(self, name: str) -> QRect:
        x, y = _MAP_NODES[name][:2]
        return QRect(x - 46, y - 20, 92, 40)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Фон сетки
        p.setPen(QPen(QColor("#F0F0F0"), 1))
        for i in range(0, self.width(), 30):
            p.drawLine(i, 0, i, self.height())
        for i in range(0, self.height(), 30):
            p.drawLine(0, i, self.width(), i)

        # Рёбра
        for a, b in _MAP_EDGES:
            xa, ya = _MAP_NODES[a][:2]
            xb, yb = _MAP_NODES[b][:2]
            st_a = _MAP_NODES[a][2]; st_b = _MAP_NODES[b][2]
            line_color = ("#AAAAAA" if "no_connection" in (st_a, st_b)
                          else styles.ACCENT_BLUE)
            style = Qt.PenStyle.DotLine if "no_connection" in (st_a, st_b) else Qt.PenStyle.SolidLine
            p.setPen(QPen(QColor(line_color), 2, style))
            p.drawLine(xa, ya, xb, yb)

        # Узлы
        bold = QFont("Segoe UI", 9, QFont.Weight.Bold)
        small = QFont("Segoe UI", 8)
        for name, (x, y, status, os_name) in _MAP_NODES.items():
            color = _STATUS_COLORS.get(status, "#888")
            rect = self._node_rect(name)
            is_sel = name == self._selected
            is_hov = name == self._hovered

            # Тень
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(QColor(0, 0, 0, 30)))
            p.drawRoundedRect(rect.adjusted(3, 3, 3, 3), 6, 6)

            # Тело
            bg = QColor(color)
            if is_sel:
                bg = bg.lighter(115)
                p.setPen(QPen(QColor(color).darker(130), 2))
            elif is_hov:
                p.setPen(QPen(QColor(color), 2))
            else:
                p.setPen(QPen(QColor(color).darker(110), 1))
            p.setBrush(QBrush(bg))
            p.drawRoundedRect(rect, 6, 6)

            # Имя
            p.setPen(QPen(QColor("white")))
            p.setFont(bold)
            p.drawText(rect.adjusted(0, -4, 0, -4), Qt.AlignmentFlag.AlignCenter, name)

            # ОС
            p.setFont(small)
            p.setPen(QPen(QColor("white").darker(110) if status == "ok" else QColor("white")))
            p.drawText(rect.adjusted(0, 8, 0, 8), Qt.AlignmentFlag.AlignCenter, os_name)

            # Статус-точка
            dot_color = "#FFFFFF"
            p.setBrush(QBrush(QColor(dot_color))); p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(rect.right() - 10, rect.top() + 4, 8, 8)
            inner = (styles.ACCENT_GREEN if status == "ok"
                     else styles.ACCENT_RED if status == "violation" else "#AAAAAA")
            p.setBrush(QBrush(QColor(inner)))
            p.drawEllipse(rect.right() - 8, rect.top() + 6, 5, 5)

        p.end()

    def mouseMoveEvent(self, e):
        pos = e.position().toPoint()
        hit = None
        for name in _MAP_NODES:
            if self._node_rect(name).contains(pos):
                hit = name; break
        if hit != self._hovered:
            self._hovered = hit
            self.setCursor(Qt.CursorShape.PointingHandCursor if hit
                           else Qt.CursorShape.ArrowCursor)
            self.update()

    def mousePressEvent(self, e):
        pos = e.position().toPoint()
        for name in _MAP_NODES:
            if self._node_rect(name).contains(pos):
                self._selected = name
                self.update()
                return
        self._selected = None; self.update()


class NetworkMapPanel(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Карта сети")
        self.setMinimumSize(720, 560)
        self.setStyleSheet(_dlg_style())
        self._build()

    def _build(self):
        v = QVBoxLayout(self); v.setContentsMargins(16, 16, 16, 16); v.setSpacing(10)
        v.addWidget(_section_lbl("Интерактивная карта сети"))

        # Легенда
        leg = QHBoxLayout(); leg.setSpacing(16)
        for color, txt in [("#4CAF50", "В норме"), ("#D9534F", "Нарушение"), ("#AAAAAA", "Нет связи")]:
            dot = QLabel("●"); dot.setStyleSheet(f"color:{color};font-size:14px;")
            lbl = QLabel(txt); lbl.setStyleSheet(f"font-size:11px;color:{styles.TEXT_SECONDARY};")
            leg.addWidget(dot); leg.addWidget(lbl)
        leg.addStretch()

        # Кнопки
        ref = _sec_btn("↻  Обновить")
        ref.clicked.connect(self._refresh)
        exp = _sec_btn("⬇  Экспорт PNG")
        leg.addWidget(ref); leg.addWidget(exp)
        v.addLayout(leg)

        # Холст
        self._canvas = _MapCanvas()
        v.addWidget(self._canvas, 1)

        # Инфо-панель
        self._info = QLabel("Кликните на устройство для просмотра информации")
        self._info.setFixedHeight(26)
        self._info.setStyleSheet(
            f"background:#F5F5F5;border:1px solid #DDDDDD;border-radius:2px;"
            f"padding:0 10px;color:{styles.TEXT_SECONDARY};font-size:11px;")
        v.addWidget(self._info)

        # Обновляем инфо при выборе узла
        timer = QTimer(self); timer.timeout.connect(self._update_info); timer.start(200)

    def _update_info(self):
        sel = self._canvas._selected
        if sel and sel in _MAP_NODES:
            x, y, status, os_name = _MAP_NODES[sel]
            st_text = {"ok":"В норме","violation":"Нарушение","no_connection":"Нет связи"}.get(status,status)
            self._info.setText(f"  {sel}  —  {os_name}  —  Статус: {st_text}")
        else:
            self._info.setText("  Кликните на устройство для просмотра информации")

    def _refresh(self):
        self._canvas._selected = None; self._canvas.update()


# ══════════════════════════════════════════════════════════════════════════════
#  Создание отчёта для контроля целостности файлов
# ══════════════════════════════════════════════════════════════════════════════

_REPORTS_DEMO = [
    ("Windows файлы «Controlmy»",  "winpc",       "SHA-256", "Контроль изменений", "03.01.2026 14:57", "Нарушение"),
    ("Windows файлы «SecurityCF»", "winpc",       "SHA-256", "Контроль изменений", "03.01.2026 14:55", "Нарушение"),
    ("Windows файлы «КЦ»",         "winpc",       "SHA-256", "Архив версий",        "03.01.2026 17:29", "OK"),
    ("hosts",                       "192.168.0.4", "MD5",     "Архив версий",        "03.01.2026 16:00", "OK"),
    ("autorun.inf",                 "192.168.0.4", "MD5",     "Архив версий",        "03.01.2026 16:00", "OK"),
    ("Корневые сертификаты",        "winpc",       "SHA-256", "Архив версий",        "03.01.2026 17:29", "OK"),
]


class ReportsPanel(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Отчёты — контроль целостности файлов")
        self.setMinimumSize(820, 580)
        self.setStyleSheet(_dlg_style())
        self._build()

    def _build(self):
        v = QVBoxLayout(self); v.setContentsMargins(16, 16, 16, 16); v.setSpacing(10)
        v.addWidget(_section_lbl("Управление отчётами контроля целостности"))

        tabs = QTabWidget()
        tabs.setStyleSheet(
            f"QTabWidget::pane{{border:1px solid #DDDDDD;background:white;}}"
            f"QTabBar::tab{{background:#F5F5F5;color:{styles.TEXT_SECONDARY};"
            f"padding:6px 16px;border:none;border-bottom:2px solid transparent;font-size:11px;}}"
            f"QTabBar::tab:selected{{color:#222;background:white;"
            f"border-bottom:2px solid {styles.ACCENT_BLUE};}}"
        )
        tabs.addTab(self._build_list_tab(),   "Список отчётов")
        tabs.addTab(self._build_create_tab(), "Создать отчёт")
        v.addWidget(tabs, 1)

    def _build_list_tab(self) -> QWidget:
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(8, 8, 8, 8); v.setSpacing(6)

        tb = QHBoxLayout(); tb.setSpacing(6)
        crt = _primary_btn("＋  Создать"); crt.clicked.connect(self._on_create)
        edt = _sec_btn("✎  Изменить")
        dlt = _sec_btn("✕  Удалить"); dlt.clicked.connect(self._on_delete)
        rn  = _sec_btn("▶  Запустить"); rn.clicked.connect(self._on_run)
        for b in (crt, edt, dlt, rn): tb.addWidget(b)
        tb.addStretch()
        self._list_status = QLabel()
        self._list_status.setStyleSheet(f"color:{styles.ACCENT_GREEN};font-size:11px;")
        tb.addWidget(self._list_status)
        v.addLayout(tb)

        self._list_tbl = _make_tbl(
            ["Отчёт", "Устройство", "Алгоритм", "Режим", "Последнее обновление", "Статус"],
            stretch=0)
        for row in _REPORTS_DEMO:
            r = self._list_tbl.rowCount(); self._list_tbl.insertRow(r)
            for c, val in enumerate(row):
                it = QTableWidgetItem(val)
                if c == 5:
                    it.setForeground(QColor(styles.ACCENT_GREEN if val == "OK"
                                           else styles.ACCENT_RED))
                self._list_tbl.setItem(r, c, it)
            self._list_tbl.setRowHeight(r, 22)
        v.addWidget(self._list_tbl, 1)
        return w

    def _build_create_tab(self) -> QWidget:
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(16, 12, 16, 12); v.setSpacing(10)

        fld_ss = ("QLineEdit,QComboBox{border:1px solid #CCC;padding:4px 8px;"
                  "background:white;font-size:11px;border-radius:2px;}")
        lbl_ss = f"color:{styles.TEXT_HEADER};font-size:11px;"
        grid = QGridLayout(); grid.setSpacing(10); grid.setColumnStretch(1, 1)

        fields = [
            ("Название отчёта:",    QLineEdit, None),
            ("Устройство:",         QComboBox, ["winpc","192.168.0.4","192.168.0.1","DC","skdpu"]),
            ("Путь / файл:",        QLineEdit, None),
            ("Алгоритм хэша:",      QComboBox, ["SHA-256","SHA-512","MD5","CRC32"]),
            ("Режим контроля:",     QComboBox, ["Контроль изменений","Архив версий","Только последний"]),
            ("Описание:",           QLineEdit, None),
        ]
        self._create_flds = {}
        for i, (name, Cls, items) in enumerate(fields):
            lbl = QLabel(name); lbl.setStyleSheet(lbl_ss); grid.addWidget(lbl, i, 0)
            w2 = Cls(); w2.setStyleSheet(fld_ss); w2.setFixedHeight(28)
            if isinstance(w2, QComboBox) and items: w2.addItems(items)
            grid.addWidget(w2, i, 1); self._create_flds[name] = w2
        v.addLayout(grid)

        chk_row = QHBoxLayout()
        for txt in ["Включить подкаталоги", "Игнорировать временные файлы",
                    "Уведомлять при нарушении"]:
            cb = QCheckBox(txt); cb.setChecked(True)
            cb.setStyleSheet(
                f"QCheckBox{{font-size:11px;color:{styles.TEXT_HEADER};}}"
                f"QCheckBox::indicator{{width:13px;height:13px;"
                f"border:1px solid #CCC;border-radius:2px;background:white;}}"
                f"QCheckBox::indicator:checked{{background:{styles.ACCENT_BLUE};"
                f"border-color:{styles.ACCENT_BLUE};}}")
            chk_row.addWidget(cb)
        chk_row.addStretch(); v.addLayout(chk_row)

        v.addStretch()
        btn_row = QHBoxLayout(); btn_row.addStretch()
        crt = _primary_btn("Создать отчёт"); crt.clicked.connect(self._save_new)
        btn_row.addWidget(crt); btn_row.addWidget(_sec_btn("Отменить"))
        v.addLayout(btn_row)
        return w

    def _on_create(self):
        QMessageBox.information(self, "Создание", "Перейдите на вкладку «Создать отчёт».")

    def _on_delete(self):
        r = self._list_tbl.currentRow()
        if r < 0: QMessageBox.information(self, "Удаление", "Выберите отчёт."); return
        name = self._list_tbl.item(r, 0).text() if self._list_tbl.item(r, 0) else ""
        if QMessageBox.question(self, "Удаление", f"Удалить отчёт «{name}»?",
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                                ) == QMessageBox.StandardButton.Yes:
            self._list_tbl.removeRow(r)

    def _on_run(self):
        r = self._list_tbl.currentRow()
        if r < 0: QMessageBox.information(self, "Запуск", "Выберите отчёт."); return
        name = self._list_tbl.item(r, 0).text() if self._list_tbl.item(r, 0) else ""
        self._list_status.setText(f"▶ Загрузка: {name}…")
        QTimer.singleShot(2000, lambda: self._list_status.setText(f"✓ Завершено: {name}"))

    def _save_new(self):
        name_w = self._create_flds.get("Название отчёта:")
        name = name_w.text().strip() if isinstance(name_w, QLineEdit) else ""
        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите название отчёта."); return
        dev = self._create_flds["Устройство:"].currentText()
        alg = self._create_flds["Алгоритм хэша:"].currentText()
        mode = self._create_flds["Режим контроля:"].currentText()
        import datetime
        now = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
        r = self._list_tbl.rowCount(); self._list_tbl.insertRow(r)
        for c, val in enumerate([name, dev, alg, mode, now, "OK"]):
            it = QTableWidgetItem(val)
            if c == 5: it.setForeground(QColor(styles.ACCENT_GREEN))
            self._list_tbl.setItem(r, c, it)
        self._list_tbl.setRowHeight(r, 22)
        if isinstance(name_w, QLineEdit): name_w.clear()
        QMessageBox.information(self, "Создано", f"Отчёт «{name}» создан успешно.")
