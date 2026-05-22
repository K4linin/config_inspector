from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QFrame,
    QPushButton, QCheckBox, QScrollArea,
    QCalendarWidget, QHeaderView, QAbstractItemView,
    QComboBox, QLineEdit, QSizePolicy,
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import styles


EVENTS_DATA = [
    ("192.168.0.1", "03.01.2026 0:49:22", "Загрузка отчёта",             'Ошибка загрузки отчёта "Linux \'uname -i\'"'),
    ("192.168.0.1", "03.01.2026 0:49:22", "Запуск действий по триггеру", 'Запуск по триггеру "Ошибки при работе с устройством"'),
    ("192.168.0.1", "03.01.2026 0:48:52", "Загрузка отчёта",             'Ошибка загрузки отчёта "Linux \'uname -sr\'"'),
    ("192.168.0.1", "03.01.2026 0:48:52", "Запуск действий по триггеру", 'Запуск по триггеру "Ошибки при работе с устройством"'),
    ("192.168.0.1", "03.01.2026 0:48:22", "Загрузка отчёта",             'Ошибка загрузки отчёта "Linux /sbin/ausearch"'),
    ("192.168.0.1", "03.01.2026 0:48:22", "Запуск действий по триггеру", 'Запуск по триггеру "Ошибки при работе с устройством"'),
    ("Сервер",      "03.01.2026 0:48:06", "Аудит",                       "Добавление профиля \"Windows\", пользователь 'root'"),
    ("192.168.0.1", "03.01.2026 0:47:52", "Загрузка отчёта",             'Ошибка загрузки отчёта "Linux cat /etc/shadow"'),
    ("192.168.0.1", "03.01.2026 0:47:52", "Запуск действий по триггеру", 'Запуск по триггеру "Ошибки при работе с устройством"'),
    ("192.168.0.1", "03.01.2026 0:47:21", "Загрузка отчёта",             'Ошибка загрузки отчёта "Linux cat /etc/passwd"'),
    ("192.168.0.1", "03.01.2026 0:47:21", "Запуск действий по триггеру", 'Запуск по триггеру "Ошибки при работе с устройством"'),
    ("192.168.0.1", "03.01.2026 0:46:55", "Загрузка отчёта",             'Ошибка загрузки отчёта "Linux cat /etc/group"'),
]

_ALL_DEVICES = sorted({r[0] for r in EVENTS_DATA})
_ALL_TYPES   = sorted({r[2] for r in EVENTS_DATA})


class EventsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background:{styles.MAIN_BG};")

        self._active_rows = list(range(len(EVENTS_DATA)))
        self._live_mode   = False

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_main(), 1)
        root.addWidget(self._build_filter())

        self._refresh_table()
        self._on_selection()

    # ── Main content ──────────────────────────────────────────────────────────

    def _build_main(self):
        main_w = QWidget()
        main_w.setStyleSheet("background:white;")
        mv = QVBoxLayout(main_w)
        mv.setContentsMargins(0, 0, 0, 0)
        mv.setSpacing(0)

        # Drag-to-group hint bar
        hint = QLabel("Drag a column header here to group by that column")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint.setFixedHeight(28)
        hint.setStyleSheet(
            "background:#F8F8F8;border-bottom:1px solid #E5E5E5;"
            "color:#AAAAAA;font-style:italic;font-size:11px;"
        )
        mv.addWidget(hint)

        # Events table
        self._table = QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(["Устройство", "Время", "Тип", "Сообщение"])
        hdr = self._table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self._table.verticalHeader().hide()
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setShowGrid(True)
        self._table.setWordWrap(False)
        self._table.itemSelectionChanged.connect(self._on_selection)
        mv.addWidget(self._table, 1)

        # Details panel
        self._detail_frame = QFrame()
        self._detail_frame.setFixedHeight(130)
        self._detail_frame.setStyleSheet(
            f"background:white;border-top:2px solid {styles.CARD_BORDER};"
        )
        dv = QVBoxLayout(self._detail_frame)
        dv.setContentsMargins(10, 6, 10, 6)
        dv.setSpacing(4)

        self._detail_title = QLabel("<b>Дополнительно:</b>")
        dv.addWidget(self._detail_title)

        self._detail_msg = QLabel()
        self._detail_msg.setStyleSheet(f"color:{styles.TEXT_SECONDARY};font-size:11px;")
        self._detail_msg.setWordWrap(True)
        dv.addWidget(self._detail_msg)

        self._detail_tbl = QTableWidget(2, 2)
        self._detail_tbl.setHorizontalHeaderLabels(["Название", "Значение"])
        self._detail_tbl.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self._detail_tbl.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self._detail_tbl.verticalHeader().hide()
        self._detail_tbl.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._detail_tbl.setFixedHeight(62)
        for r, (n, v) in enumerate([("Тип события", ""), ("Результат", "")]):
            self._detail_tbl.setItem(r, 0, QTableWidgetItem(n))
            self._detail_tbl.setItem(r, 1, QTableWidgetItem(v))
            self._detail_tbl.setRowHeight(r, 20)
        dv.addWidget(self._detail_tbl)

        mv.addWidget(self._detail_frame)
        return main_w

    # ── Filter panel ──────────────────────────────────────────────────────────

    def _build_filter(self):
        # Outer container — используем objectName чтобы стиль НЕ протекал в дочерние виджеты
        outer = QWidget()
        outer.setObjectName("filterOuter")
        outer.setFixedWidth(268)
        outer.setStyleSheet(
            f"QWidget#filterOuter{{"
            f"background:#F8F8F8;"
            f"border-left:1px solid {styles.CARD_BORDER};"
            f"}}"
        )
        outer_v = QVBoxLayout(outer)
        outer_v.setContentsMargins(0, 0, 0, 0)
        outer_v.setSpacing(0)

        # Top action buttons (always visible, outside scroll)
        top = QWidget()
        top.setObjectName("filterTop")
        top.setStyleSheet("QWidget#filterTop{background:#F8F8F8;border:none;}")
        tv = QVBoxLayout(top)
        tv.setContentsMargins(8, 8, 8, 4)
        tv.setSpacing(4)

        refresh_btn = QPushButton("Обновить")
        refresh_btn.clicked.connect(self._load_live_events)
        tv.addWidget(refresh_btn)

        reset_btn = QPushButton("Сбросить фильтр")
        reset_btn.clicked.connect(self._reset_filter)
        tv.addWidget(reset_btn)

        tv.addWidget(self._hsep())

        outer_v.addWidget(top)

        # Scrollable filter body
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea{background:#F8F8F8;border:none;}")

        body = QWidget()
        body.setObjectName("filterBody")
        body.setStyleSheet("QWidget#filterBody{background:#F8F8F8;border:none;}")
        fv = QVBoxLayout(body)
        fv.setContentsMargins(8, 4, 8, 8)
        fv.setSpacing(6)

        # Section header
        hdr = QLabel("Фильтр*")
        hdr.setStyleSheet("font-weight:bold;font-size:12px;color:#333;")
        fv.addWidget(hdr)

        # Time filter
        self._time_cb = QCheckBox("По Времени")
        self._time_cb.setChecked(True)
        fv.addWidget(self._time_cb)

        for lbl_txt, default in [("с", "01.01.2026"), ("по", "03.01.2026")]:
            row = QHBoxLayout()
            lbl_w = QLabel(lbl_txt)
            lbl_w.setStyleSheet(f"color:{styles.TEXT_SECONDARY};font-size:11px;"
                                f"background:transparent;")
            lbl_w.setFixedWidth(18)
            row.addWidget(lbl_w)
            le = QLineEdit(default)
            le.setFixedHeight(24)
            le.setStyleSheet(
                "QLineEdit{border:1px solid #CCCCCC;border-radius:2px;"
                "padding:1px 6px;background:white;font-size:11px;}"
                "QLineEdit:focus{border-color:#4A90D9;}"
            )
            row.addWidget(le, 1)
            fv.addLayout(row)

        # Calendar
        cal = QCalendarWidget()
        cal.setSelectedDate(QDate(2026, 1, 3))
        cal.setMaximumHeight(195)
        cal.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        cal.setStyleSheet(
            "QCalendarWidget{font-size:10px;background:white;}"
            "QCalendarWidget QToolButton{font-size:10px;color:#333;background:transparent;"
            "border:none;padding:2px;}"
            "QCalendarWidget QMenu{font-size:10px;}"
            "QCalendarWidget QAbstractItemView{"
            "font-size:10px;selection-background-color:#D6E4F7;"
            "selection-color:#333;}"
        )
        fv.addWidget(cal)

        fv.addWidget(self._hsep())

        # ── Device filter ────────────────────────────────────────────────
        dev_hdr = QHBoxLayout()
        dev_lbl = QLabel("По устройствам")
        dev_lbl.setStyleSheet("font-weight:bold;font-size:11px;color:#444;")
        dev_hdr.addWidget(dev_lbl)
        clr_btn = QPushButton("Clear")
        clr_btn.setFixedHeight(20)
        clr_btn.setFixedWidth(46)
        clr_btn.setStyleSheet(
            "QPushButton{font-size:10px;padding:1px 4px;"
            f"border:1px solid {styles.INPUT_BORDER};"
            "background:#FFF;border-radius:2px;color:#555;}"
            "QPushButton:hover{background:#EEE;}"
        )
        clr_btn.clicked.connect(self._clear_device_filter)
        dev_hdr.addWidget(clr_btn)
        fv.addLayout(dev_hdr)

        # QCheckBox per device (instead of QListWidget)
        self._dev_checks: dict[str, QCheckBox] = {}
        dev_box = QFrame()
        dev_box.setStyleSheet(
            f"QFrame{{background:white;border:1px solid {styles.INPUT_BORDER};"
            "border-radius:2px;padding:2px;}}"
        )
        dev_bv = QVBoxLayout(dev_box)
        dev_bv.setContentsMargins(6, 4, 6, 4)
        dev_bv.setSpacing(2)
        for dev in _ALL_DEVICES:
            cb = QCheckBox(dev)
            cb.setStyleSheet("QCheckBox{font-size:11px;color:#333;background:transparent;}")
            dev_bv.addWidget(cb)
            self._dev_checks[dev] = cb
        fv.addWidget(dev_box)

        # ── Type filter ──────────────────────────────────────────────────
        type_lbl = QLabel("По типу")
        type_lbl.setStyleSheet("font-weight:bold;font-size:11px;color:#444;margin-top:4px;")
        fv.addWidget(type_lbl)

        self._type_checks: dict[str, QCheckBox] = {}
        type_box = QFrame()
        type_box.setStyleSheet(
            f"QFrame{{background:white;border:1px solid {styles.INPUT_BORDER};"
            "border-radius:2px;padding:2px;}}"
        )
        type_bv = QVBoxLayout(type_box)
        type_bv.setContentsMargins(6, 4, 6, 4)
        type_bv.setSpacing(2)
        for t in _ALL_TYPES:
            cb = QCheckBox(t)
            cb.setStyleSheet("QCheckBox{font-size:11px;color:#333;background:transparent;}")
            type_bv.addWidget(cb)
            self._type_checks[t] = cb
        fv.addWidget(type_box)

        fv.addStretch()

        scroll.setWidget(body)
        outer_v.addWidget(scroll, 1)

        # Bottom apply/cancel buttons (always visible, outside scroll)
        bot = QWidget()
        bot.setObjectName("filterBot")
        bot.setStyleSheet("QWidget#filterBot{background:#F8F8F8;border:none;}")
        bv = QVBoxLayout(bot)
        bv.setContentsMargins(8, 4, 8, 8)
        bv.setSpacing(4)

        bv.addWidget(self._hsep())

        apply_btn = QPushButton("Применить")
        apply_btn.setObjectName("primaryBtn")
        apply_btn.setStyleSheet(
            f"QPushButton{{background:{styles.BTN_PRIMARY_BG};color:white;"
            "border:none;padding:6px;border-radius:2px;font-size:12px;}}"
            "QPushButton:hover{background:#245080;}"
        )
        apply_btn.clicked.connect(self._apply_filter)
        bv.addWidget(apply_btn)

        cancel_btn = QPushButton("Отменить")
        cancel_btn.clicked.connect(self._reset_filter)
        bv.addWidget(cancel_btn)

        outer_v.addWidget(bot)
        return outer

    # ── Filter logic ──────────────────────────────────────────────────────────

    def _checked_devs(self) -> list[str]:
        return [d for d, cb in self._dev_checks.items() if cb.isChecked()]

    def _checked_types(self) -> list[str]:
        return [t for t, cb in self._type_checks.items() if cb.isChecked()]

    def _apply_filter(self) -> None:
        dev_filter  = self._checked_devs()
        type_filter = self._checked_types()
        data        = self._current_data()

        self._active_rows = []
        for idx, (dev, dt, typ, msg) in enumerate(data):
            if dev_filter  and dev not in dev_filter:
                continue
            if type_filter and typ not in type_filter:
                continue
            self._active_rows.append(idx)

        self._refresh_table()

    def _reset_filter(self) -> None:
        self._live_mode = False
        for cb in self._dev_checks.values():
            cb.setChecked(False)
        for cb in self._type_checks.values():
            cb.setChecked(False)
        self._active_rows = list(range(len(EVENTS_DATA)))
        self._refresh_table()

    def _clear_device_filter(self) -> None:
        for cb in self._dev_checks.values():
            cb.setChecked(False)

    def _load_live_events(self) -> None:
        try:
            from data_store import get_store
            live = get_store().system_events
        except Exception:
            live = []

        if live:
            self._merged_data = list(live) + list(EVENTS_DATA)
            self._live_mode   = True
        else:
            self._merged_data = list(EVENTS_DATA)
            self._live_mode   = False

        self._active_rows = list(range(len(self._merged_data)))
        self._refresh_table()

    def _current_data(self) -> list:
        if self._live_mode and hasattr(self, "_merged_data"):
            return self._merged_data
        return EVENTS_DATA

    # ── Table refresh ─────────────────────────────────────────────────────────

    def _refresh_table(self) -> None:
        self._table.setRowCount(0)
        data = self._current_data()
        for row_idx, data_idx in enumerate(self._active_rows):
            if data_idx >= len(data):
                continue
            dev, dt, typ, msg = data[data_idx]
            self._table.insertRow(row_idx)
            for c, val in enumerate([dev, dt, typ, msg]):
                item = QTableWidgetItem(val)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self._table.setItem(row_idx, c, item)
            self._table.setRowHeight(row_idx, 22)

        if self._table.rowCount() > 0:
            self._table.selectRow(0)

    # ── Details ───────────────────────────────────────────────────────────────

    def _on_selection(self) -> None:
        rows = self._table.selectionModel().selectedRows()
        if not rows:
            self._detail_msg.setText("")
            return
        table_row = rows[0].row()
        if table_row >= len(self._active_rows):
            return
        data_idx = self._active_rows[table_row]
        data     = self._current_data()
        if data_idx >= len(data):
            return
        dev, dt, typ, msg = data[data_idx]
        self._detail_msg.setText(
            f'{msg}. <a href="#" style="color:{styles.ACCENT_BLUE};'
            'text-decoration:none;">Подробнее</a>'
        )
        self._detail_tbl.setItem(0, 1, QTableWidgetItem(typ))
        result = "Ошибка" if "Ошибка" in msg else "Успех"
        self._detail_tbl.setItem(1, 1, QTableWidgetItem(result))

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _hsep() -> QFrame:
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color:#DDDDDD;background:#DDDDDD;max-height:1px;")
        return sep
