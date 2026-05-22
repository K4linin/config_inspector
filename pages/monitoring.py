"""Monitoring dashboard — fully dynamic, reads from DataStore."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QProgressBar, QSizePolicy,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from widgets.charts import DonutChart, MultiDonut, MiniLineChart, MiniBarChart
import styles


# ── Small helpers ─────────────────────────────────────────────────────────────

def _sep():
    f = QFrame()
    f.setFrameShape(QFrame.Shape.HLine)
    f.setStyleSheet("color:#EEEEEE;background:#EEEEEE;max-height:1px;")
    return f


def _section_lbl(text):
    lbl = QLabel(text)
    lbl.setStyleSheet(
        f"font-size:10px;font-weight:bold;color:{styles.TEXT_HEADER};letter-spacing:0.5px;"
    )
    return lbl


def _link_lbl(text, color=None):
    c = color or styles.ACCENT_GREEN
    lbl = QLabel(f'<a href="#" style="color:{c};text-decoration:none;">{text}</a>')
    lbl.setOpenExternalLinks(False)
    return lbl


def _card():
    f = QFrame()
    f.setObjectName("card")
    f.setStyleSheet(
        f"QFrame#card{{background:{styles.CARD_BG};"
        f"border:1px solid {styles.CARD_BORDER};border-radius:2px;}}"
    )
    return f


def _card_header(title, link="подробнее"):
    row = QHBoxLayout()
    row.setContentsMargins(10, 8, 10, 6)
    lbl = QLabel(title)
    lbl.setStyleSheet(
        f"font-size:11px;font-weight:bold;color:{styles.TEXT_HEADER};letter-spacing:0.5px;"
    )
    row.addWidget(lbl)
    row.addStretch()
    row.addWidget(_link_lbl(link))
    return row


def _thin_bar(value=0, maximum=10, color=None):
    bar = QProgressBar()
    bar.setMaximum(max(1, maximum))
    bar.setValue(value)
    bar.setFixedHeight(8)
    bar.setTextVisible(False)
    c = color or styles.ACCENT_BLUE
    bar.setStyleSheet(
        f"QProgressBar{{background:#E4E4E4;border:none;border-radius:4px;}}"
        f"QProgressBar::chunk{{background:{c};border-radius:4px;}}"
    )
    return bar


# ── MonitoringPage ─────────────────────────────────────────────────────────────

class MonitoringPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background:{styles.MAIN_BG};")

        grid = QGridLayout(self)
        grid.setContentsMargins(10, 10, 10, 10)
        grid.setSpacing(10)

        grid.addWidget(self._build_card_control(),  0, 0)
        grid.addWidget(self._build_card_vuln(),     0, 1)
        grid.addWidget(self._build_card_security(), 1, 0)
        grid.addWidget(self._build_card_devices(),  1, 1)

        grid.setRowStretch(0, 1)
        grid.setRowStretch(1, 1)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        # Connect to data store
        from data_store import get_store
        self._store = get_store()
        self._store.changed.connect(self._refresh)
        self._refresh()   # populate with initial values

    # ── Card 1 — КОНТРОЛЬ ИЗМЕНЕНИЙ ──────────────────────────────────────────

    def _build_card_control(self) -> QFrame:
        card = _card()
        vbox = QVBoxLayout(card)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)

        vbox.addLayout(_card_header("КОНТРОЛЬ ИЗМЕНЕНИЙ"))
        vbox.addWidget(_sep())

        body = QHBoxLayout()
        body.setContentsMargins(12, 10, 12, 10)
        body.setSpacing(12)

        self._ctrl_donut = DonutChart(value=0, color=styles.ACCENT_GREEN, size=90)
        body.addWidget(self._ctrl_donut)

        stats = QVBoxLayout()
        stats.setSpacing(2)
        self._ctrl_big = QLabel("0 из 0")
        self._ctrl_big.setStyleSheet("font-size:18px;font-weight:bold;color:#333;")
        stats.addWidget(self._ctrl_big)
        stats.addWidget(QLabel("отчётов с нарушениями"))
        stats.addStretch()
        body.addLayout(stats)
        body.addStretch()

        self._ctrl_chart = MiniLineChart()
        self._ctrl_chart.setMinimumWidth(140)
        body.addWidget(self._ctrl_chart)

        vbox.addLayout(body)
        vbox.addWidget(_sep())

        # Recent violations
        viols_area = QVBoxLayout()
        viols_area.setContentsMargins(12, 6, 12, 8)
        viols_area.setSpacing(4)
        viols_area.addWidget(_section_lbl("ПОСЛЕДНИЕ НАРУШЕНИЯ"))

        # Pre-build 3 rows (some may stay hidden)
        self._ctrl_viol_rows = []
        for _ in range(3):
            row = QHBoxLayout()
            row.setSpacing(6)
            dt_lbl  = QLabel()
            dt_lbl.setStyleSheet(f"color:{styles.TEXT_SECONDARY};font-size:11px;")
            dev_lbl = QLabel()
            dev_lbl.setStyleSheet(f"color:{styles.ACCENT_BLUE};font-size:11px;")
            rpt_lbl = _link_lbl("", styles.ACCENT_BLUE)
            row.addWidget(dt_lbl)
            row.addWidget(dev_lbl)
            row.addStretch()
            row.addWidget(rpt_lbl)

            # Wrap in a container so we can show/hide the row
            container = QWidget()
            container.setLayout(row)
            container.setVisible(False)
            viols_area.addWidget(container)
            self._ctrl_viol_rows.append((container, dt_lbl, dev_lbl, rpt_lbl))

        vbox.addLayout(viols_area)
        vbox.addStretch()
        return card

    # ── Card 2 — УЯЗВИМОСТИ ──────────────────────────────────────────────────

    def _build_card_vuln(self) -> QFrame:
        card = _card()
        vbox = QVBoxLayout(card)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)

        vbox.addLayout(_card_header("УЯЗВИМОСТИ"))
        vbox.addWidget(_sep())

        rows_area = QVBoxLayout()
        rows_area.setContentsMargins(12, 10, 12, 10)
        rows_area.setSpacing(8)

        self._vuln_bars: dict[str, tuple[QProgressBar, QLabel]] = {}

        _VULN_LABELS = [
            ("kritichnyye", "vuln_critical",  "критичные",      styles.ACCENT_RED),
            ("vazhnyye",    "vuln_important", "важные",         styles.ACCENT_ORANGE),
            ("info",        "vuln_info",      "информационные", styles.ACCENT_BLUE),
            ("no_vuln",     None,             "без уязвимостей",styles.ACCENT_GREEN),
        ]

        for key, attr, label_text, color in _VULN_LABELS:
            row = QHBoxLayout()
            row.setSpacing(8)
            lbl = QLabel(label_text)
            lbl.setFixedWidth(130)
            row.addWidget(lbl)
            bar = _thin_bar(0, 1, color)
            row.addWidget(bar)
            num = QLabel("0")
            num.setFixedWidth(24)
            num.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            row.addWidget(num)
            rows_area.addLayout(row)
            self._vuln_bars[key] = (bar, num, attr)

        vbox.addLayout(rows_area)
        vbox.addWidget(_sep())

        bot = QVBoxLayout()
        bot.setContentsMargins(12, 6, 12, 8)
        bot.addWidget(_section_lbl("САМЫЕ УЯЗВИМЫЕ УСТРОЙСТВА"))

        self._vuln_worst_lbl = QLabel()
        self._vuln_worst_lbl.setStyleSheet(
            f"font-size:11px;color:{styles.TEXT_SECONDARY};"
        )
        self._vuln_worst_lbl.setWordWrap(True)
        bot.addWidget(self._vuln_worst_lbl)
        bot.addStretch()
        vbox.addLayout(bot)
        vbox.addStretch()
        return card

    # ── Card 3 — ПРОВЕРКИ БЕЗОПАСНОСТИ ───────────────────────────────────────

    def _build_card_security(self) -> QFrame:
        card = _card()
        vbox = QVBoxLayout(card)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)

        vbox.addLayout(_card_header("ПРОВЕРКИ БЕЗОПАСНОСТИ"))
        vbox.addWidget(_sep())

        body = QHBoxLayout()
        body.setContentsMargins(12, 10, 12, 10)
        body.setSpacing(12)

        self._sec_donut = DonutChart(value=0, color="#AAAAAA", size=90)
        body.addWidget(self._sec_donut)

        stats = QVBoxLayout()
        stats.setSpacing(2)
        self._sec_big = QLabel("0 из 0")
        self._sec_big.setStyleSheet("font-size:18px;font-weight:bold;color:#333;")
        stats.addWidget(self._sec_big)
        stats.addWidget(QLabel("выполнено правил"))
        stats.addStretch()
        body.addLayout(stats)
        body.addStretch()

        self._sec_chart = MiniBarChart(color="#AAAAAA")
        self._sec_chart.setMinimumWidth(140)
        body.addWidget(self._sec_chart)

        vbox.addLayout(body)
        vbox.addWidget(_sep())

        bot = QVBoxLayout()
        bot.setContentsMargins(12, 6, 12, 8)
        bot.addWidget(_section_lbl("САМЫЕ НЕЗАЩИЩЁННЫЕ"))

        self._sec_worst_lbl = QLabel()
        self._sec_worst_lbl.setStyleSheet(
            f"font-size:11px;color:{styles.TEXT_SECONDARY};"
        )
        self._sec_worst_lbl.setWordWrap(True)
        bot.addWidget(self._sec_worst_lbl)
        bot.addStretch()
        vbox.addLayout(bot)
        vbox.addStretch()
        return card

    # ── Card 4 — СОСТОЯНИЕ УСТРОЙСТВ ─────────────────────────────────────────

    def _build_card_devices(self) -> QFrame:
        card = _card()
        vbox = QVBoxLayout(card)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)

        vbox.addLayout(_card_header("СОСТОЯНИЕ УСТРОЙСТВ"))
        vbox.addWidget(_sep())

        body = QHBoxLayout()
        body.setContentsMargins(12, 10, 12, 10)
        body.setSpacing(16)

        self._dev_donut = MultiDonut(size=110)
        body.addWidget(self._dev_donut)

        legend = QVBoxLayout()
        legend.setSpacing(3)
        self._dev_total = QLabel("ВСЕГО УСТРОЙСТВ: 5")
        self._dev_total.setStyleSheet("font-size:10px;font-weight:bold;color:#555;")
        legend.addWidget(self._dev_total)

        _LEGEND = [
            ("no_connection", styles.ACCENT_GRAY,   "НЕТ СВЯЗИ"),
            ("violation",     styles.ACCENT_RED,    "КРИТИЧНО"),
            ("warning",       styles.ACCENT_ORANGE, "ВАЖНО"),
            ("info",          "#5B9BD5",            "ИНФОРМАЦИЯ"),
            ("ok",            styles.ACCENT_GREEN,  "БЕЗ УВЕДОМЛЕНИЙ"),
        ]
        self._dev_legend: dict[str, QLabel] = {}
        for key, color, label in _LEGEND:
            row = QHBoxLayout()
            row.setSpacing(5)
            dot = QLabel("●")
            dot.setStyleSheet(f"color:{color};font-size:10px;")
            row.addWidget(dot)
            cnt = QLabel("0")
            cnt.setStyleSheet("font-size:10px;color:#444;")
            txt = QLabel(label)
            txt.setStyleSheet("font-size:10px;color:#444;")
            row.addWidget(cnt)
            row.addWidget(txt)
            row.addStretch()
            legend.addLayout(row)
            self._dev_legend[key] = cnt

        body.addLayout(legend)
        body.addStretch()
        vbox.addLayout(body)
        vbox.addWidget(_sep())

        dev_area = QVBoxLayout()
        dev_area.setContentsMargins(12, 6, 12, 10)
        dev_area.setSpacing(5)
        dev_area.addWidget(_section_lbl("УСТРОЙСТВА"))

        self._dev_bars: dict[str, tuple[QProgressBar, QLabel]] = {}
        for dtype, color in [("Windows", "#5B9BD5"), ("Linux", styles.ACCENT_GREEN)]:
            row = QHBoxLayout()
            row.setSpacing(8)
            n_lbl = QLabel(f"{dtype} ▪")
            n_lbl.setFixedWidth(70)
            row.addWidget(n_lbl)
            bar = _thin_bar(0, 1, color)
            row.addWidget(bar)
            num = QLabel("0")
            row.addWidget(num)
            dev_area.addLayout(row)
            self._dev_bars[dtype] = (bar, num)

        vbox.addLayout(dev_area)
        vbox.addStretch()
        return card

    # ── Refresh ────────────────────────────────────────────────────────────────

    def _refresh(self) -> None:
        store = self._store
        from data_store import DeviceStatus

        # ── Card 1 ──────────────────────────────────────────────────────────
        pct = store.violation_percent
        clr = styles.ACCENT_GREEN if pct < 30 else (styles.ACCENT_ORANGE if pct < 60 else styles.ACCENT_RED)
        self._ctrl_donut.setValue(pct, clr)
        self._ctrl_big.setText(f"{store.total_violations} из {max(1, store.total_reports)}")
        self._ctrl_chart.update_data(store.viol_history(), store.ok_history())

        recent = store.recent_violations
        for i, (container, dt_lbl, dev_lbl, rpt_lbl) in enumerate(self._ctrl_viol_rows):
            if i < len(recent):
                v = recent[i]
                dt_lbl.setText(v.time)
                dev_lbl.setText(f"▪ {v.device}")
                rpt_lbl.setText(
                    f'<a href="#" style="color:{styles.ACCENT_BLUE};'
                    f'text-decoration:none;">{v.report}</a>'
                )
                container.setVisible(True)
            else:
                container.setVisible(False)

        # ── Card 2 ──────────────────────────────────────────────────────────
        c_count = store.vuln_count("vuln_critical")
        i_count = store.vuln_count("vuln_important")
        f_count = store.vuln_count("vuln_info")
        n_count = store.devices_without_vulns()
        total_d = len(store.devices)
        max_v   = max(1, c_count + i_count + f_count)

        for key, (bar, num, attr) in self._vuln_bars.items():
            if attr is not None:
                val = store.vuln_count(attr)
                bar.setMaximum(max_v)
                bar.setValue(val)
                num.setText(str(val))
            else:
                bar.setMaximum(max(1, total_d))
                bar.setValue(n_count)
                num.setText(str(n_count))

        worst_vuln = store.top_vuln_devices(2)
        if worst_vuln:
            self._vuln_worst_lbl.setText(
                "  ".join(f"{name} ({cnt})" for name, cnt in worst_vuln)
            )
        else:
            self._vuln_worst_lbl.setText("— нет уязвимостей —")

        # ── Card 3 ──────────────────────────────────────────────────────────
        sec_pct = store.security_percent()
        sec_clr = (styles.ACCENT_GREEN if sec_pct >= 70
                   else (styles.ACCENT_ORANGE if sec_pct >= 40 else "#AAAAAA"))
        self._sec_donut.setValue(sec_pct, sec_clr)
        self._sec_big.setText(
            f"{store.security.passed} из {store.security.total}"
        )
        self._sec_chart.update_data(store.sec_history(), sec_clr)

        worst_sec = store.top_insecure_devices(2)
        if worst_sec:
            self._sec_worst_lbl.setText("  ".join(worst_sec))
        else:
            self._sec_worst_lbl.setText("— все устройства защищены —")

        # ── Card 4 ──────────────────────────────────────────────────────────
        n_total = len(store.devices)
        self._dev_total.setText(f"ВСЕГО УСТРОЙСТВ: {n_total}")

        _STATUS_COLORS = {
            "no_connection": styles.ACCENT_GRAY,
            "violation":     styles.ACCENT_RED,
            "warning":       styles.ACCENT_ORANGE,
            "info":          "#5B9BD5",
            "ok":            styles.ACCENT_GREEN,
        }
        segments = []
        for key, color in _STATUS_COLORS.items():
            cnt = store.status_count(DeviceStatus(key))
            self._dev_legend[key].setText(str(cnt))
            if cnt > 0:
                segments.append((cnt, color))

        self._dev_donut.setSegments(segments)

        for dtype, (bar, num) in self._dev_bars.items():
            connected, total = store.platform_counts(dtype)
            bar.setMaximum(max(1, total))
            bar.setValue(connected)
            num.setText(f"{connected}/{total}")
