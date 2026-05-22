from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QToolButton, QButtonGroup,
    QStackedWidget, QSizeGrip, QFrame,
)
from PyQt6.QtCore import Qt, QPoint, QSize, QRect
from PyQt6.QtGui import (
    QPainter, QColor, QFont, QPen, QPixmap, QIcon, QBrush, QPalette,
)

import styles


# ── Icon helpers ──────────────────────────────────────────────────────────────

def _logo_icon(cell=7):
    """4-colour grid logo (EFROS style)."""
    size = cell * 2 + 3
    px = QPixmap(size, size)
    px.fill(Qt.GlobalColor.transparent)
    p = QPainter(px)
    colors = ["#337AB7", "#5CB85C", "#D9534F", "#F0AD4E"]
    for idx, c in enumerate(colors):
        row, col = divmod(idx, 2)
        p.fillRect(col * (cell + 1), row * (cell + 1), cell, cell, QColor(c))
    p.end()
    return px


def _nav_icon(kind: str, size=26) -> QIcon:
    """Draw simple line-art icon for sidebar nav."""
    px = QPixmap(size, size)
    px.fill(Qt.GlobalColor.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    pen = QPen(QColor("white"), 1.8)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)

    m = 3
    if kind == "monitor":
        # Screen rectangle
        p.drawRoundedRect(m, m, size - 2 * m, size - m - 8, 2, 2)
        # Stand
        cx = size // 2
        p.drawLine(cx, size - 8, cx, size - 4)
        p.drawLine(cx - 5, size - 4, cx + 5, size - 4)
    elif kind == "server":
        rh = (size - 2 * m) // 3 - 1
        for i in range(3):
            p.drawRoundedRect(m, m + i * (rh + 2), size - 2 * m, rh, 2, 2)
    elif kind == "alert":
        pts = [QPoint(size // 2, m + 1), QPoint(size - m, size - m - 1), QPoint(m, size - m - 1)]
        from PyQt6.QtGui import QPolygon
        p.drawPolygon(QPolygon(pts))
        cx = size // 2
        p.drawLine(cx, size // 2 - 1, cx, size - 10)
        p.setBrush(QBrush(QColor("white")))
        p.drawEllipse(QPoint(cx, size - 7), 1, 1)
    elif kind == "gear":
        from math import cos, sin, pi
        cx, cy, r_out, r_in = size / 2, size / 2, size / 2 - m, size / 2 - m - 4
        teeth = 8
        from PyQt6.QtGui import QPolygonF
        from PyQt6.QtCore import QPointF
        pts = []
        for i in range(teeth * 2):
            angle = pi / teeth * i - pi / 2
            r = r_out if i % 2 == 0 else r_in
            pts.append(QPointF(cx + r * cos(angle), cy + r * sin(angle)))
        p.drawPolygon(QPolygonF(pts))
        p.setBrush(QBrush(QColor(styles.SIDEBAR_BG)))
        p.setPen(QPen(QColor("white"), 1.5))
        p.drawEllipse(QPoint(size // 2, size // 2), int(r_in - 3), int(r_in - 3))
    elif kind == "eft":
        # Прицел / crosshair — символ EFT
        cx, cy = size // 2, size // 2
        ro = size // 2 - m
        ri = ro - 4
        # Внешнее кольцо
        p.drawEllipse(cx - ro, cy - ro, ro * 2, ro * 2)
        # Внутреннее кольцо
        p.drawEllipse(cx - ri + 2, cy - ri + 2, (ri - 2) * 2, (ri - 2) * 2)
        # Крест — горизонталь и вертикаль с зазором в центре
        gap = 3
        p.drawLine(m, cy, cx - gap, cy)
        p.drawLine(cx + gap, cy, size - m, cy)
        p.drawLine(cx, m, cx, cy - gap)
        p.drawLine(cx, cy + gap, cx, size - m)
    p.end()
    return QIcon(px)


def _user_icon(size=26) -> QPixmap:
    px = QPixmap(size, size)
    px.fill(Qt.GlobalColor.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setBrush(QBrush(QColor("#5A7A9A")))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(0, 0, size, size)
    p.setBrush(QBrush(QColor("white")))
    hw = size // 4
    p.drawEllipse(size // 2 - hw, size // 4 - 1, hw * 2, hw * 2)
    p.drawEllipse(size // 2 - hw - 2, size // 2 + 2, (hw + 2) * 2, (hw + 3) * 2)
    p.end()
    return px


# ── Title bar ─────────────────────────────────────────────────────────────────

class TitleBar(QWidget):
    def __init__(self, main_win, parent=None):
        super().__init__(parent)
        self._win = main_win
        self._drag_pos = None
        self.setFixedHeight(40)

        # Force solid background — reliable across Windows themes / dark-mode
        self.setAutoFillBackground(True)
        pal = self.palette()
        pal.setColor(QPalette.ColorRole.Window, QColor(styles.TITLE_BAR_BG))
        self.setPalette(pal)
        # Also set via stylesheet for child-widget inheritance
        self.setObjectName("titleBarWidget")
        self.setStyleSheet(
            f"QWidget#titleBarWidget {{ background:{styles.TITLE_BAR_BG}; }}"
        )
        self._build()

    def _build(self):
        h = QHBoxLayout(self)
        h.setContentsMargins(8, 0, 0, 0)
        h.setSpacing(0)

        # Logo
        logo_lbl = QLabel()
        logo_lbl.setPixmap(_logo_icon(6))
        h.addWidget(logo_lbl)
        h.addSpacing(8)

        # App title
        title = QLabel("Config Inspector 3.1.9")
        title.setStyleSheet("color:white; font-size:13px; font-weight:500;")
        h.addWidget(title)
        h.addSpacing(14)

        # Back / Forward
        for symbol, tip in [("←", "Назад"), ("→", "Вперёд")]:
            btn = QPushButton(symbol)
            btn.setObjectName("titleBtn")
            btn.setFixedSize(28, 40)
            btn.setToolTip(tip)
            btn.setStyleSheet(
                "QPushButton{background:transparent;border:none;color:white;font-size:15px;}"
                "QPushButton:hover{background:rgba(255,255,255,30);}"
            )
            h.addWidget(btn)
        h.addSpacing(8)

        # Breadcrumb
        self.breadcrumb = QLabel("Мониторинг")
        self.breadcrumb.setStyleSheet("color:rgba(255,255,255,200);font-size:12px;")
        h.addWidget(self.breadcrumb)
        h.addStretch()

        # User
        user_px = _user_icon(24)
        usr_lbl = QLabel()
        usr_lbl.setPixmap(user_px)
        h.addWidget(usr_lbl)
        h.addSpacing(5)

        usr_name = QLabel("root")
        usr_name.setStyleSheet("color:white; margin-right:8px;")
        h.addWidget(usr_name)

        menu_btn = QPushButton("≡")
        menu_btn.setFixedSize(40, 40)
        menu_btn.setStyleSheet(
            "QPushButton{background:transparent;border:none;color:white;font-size:18px;}"
            "QPushButton:hover{background:rgba(255,255,255,30);}"
        )
        h.addWidget(menu_btn)

        # Window controls
        for sym, obj, tip in [("─", "titleBtn", "Свернуть"),
                               ("□", "titleBtn", "Развернуть"),
                               ("✕", "closeBtn", "Закрыть")]:
            btn = QPushButton(sym)
            btn.setObjectName(obj)
            btn.setFixedSize(45, 40)
            btn.setToolTip(tip)
            btn.setStyleSheet(
                f"QPushButton{{background:transparent;border:none;color:white;font-size:{'11' if sym != '✕' else '12'}px;}}"
                f"QPushButton:hover{{background:{'#C42B1C' if sym == '✕' else 'rgba(255,255,255,40)'};}}"
            )
            if sym == "─":
                btn.clicked.connect(self._win.showMinimized)
            elif sym == "□":
                btn.clicked.connect(self._toggle_max)
            else:
                btn.clicked.connect(self._win.close)
            h.addWidget(btn)

    def _toggle_max(self):
        if self._win.isMaximized():
            self._win.showNormal()
        else:
            self._win.showMaximized()

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = e.globalPosition().toPoint() - self._win.pos()

    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.MouseButton.LeftButton and self._drag_pos:
            self._win.move(e.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, e):
        self._drag_pos = None

    def mouseDoubleClickEvent(self, e):
        self._toggle_max()


# ── Main window ───────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):

    _NAV = [
        ("Мониторинг", "monitor"),
        ("Устройства",  "server"),
        ("События",     "alert"),
        ("Настройки",   "gear"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window
        )
        self.resize(1400, 900)
        self.setMinimumSize(1100, 680)

        central = QWidget()
        central.setAutoFillBackground(True)
        pal = central.palette()
        pal.setColor(QPalette.ColorRole.Window, QColor(styles.SIDEBAR_BG))
        central.setPalette(pal)
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Title bar ──────────────────────────────────────────────────
        self._title_bar = TitleBar(self)
        root.addWidget(self._title_bar)

        # ── Body: sidebar + stack ──────────────────────────────────────
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        root.addLayout(body, 1)

        # Sidebar
        self._sidebar = self._make_sidebar()
        body.addWidget(self._sidebar)

        # Thin separator
        sep = QFrame()
        sep.setFixedWidth(1)
        sep.setStyleSheet("background:#1A3347;")
        body.addWidget(sep)

        # Page stack
        self._stack = QStackedWidget()
        self._stack.setStyleSheet(f"background:{styles.MAIN_BG};")
        body.addWidget(self._stack, 1)

        # Simulation bar (always visible at bottom)
        self._simulator = None
        self._sim_bar = self._build_sim_bar()
        root.addWidget(self._sim_bar)

        # Resize grip
        grip = QSizeGrip(self)
        grip.setFixedSize(16, 16)
        grip.move(self.width() - 16, self.height() - 16)

    # ── Simulation bar ─────────────────────────────────────────────────────────

    def _build_sim_bar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(32)
        bar.setStyleSheet(
            "QWidget{background:#1E3347;}"
            "QLabel{color:rgba(255,255,255,180);font-size:11px;}"
            "QPushButton{background:rgba(255,255,255,15);"
            "border:1px solid rgba(255,255,255,40);"
            "color:white;font-size:11px;padding:2px 10px;"
            "border-radius:2px;min-height:0;}"
            "QPushButton:hover{background:rgba(255,255,255,30);}"
            "QPushButton:checked{background:#2A7A2A;border-color:#3A9A3A;}"
        )
        h = QHBoxLayout(bar)
        h.setContentsMargins(12, 0, 12, 0)
        h.setSpacing(8)

        # Status dot
        self._sim_dot = QLabel("●")
        self._sim_dot.setStyleSheet("color:#555555;font-size:14px;")
        h.addWidget(self._sim_dot)

        # Toggle start/stop
        self._sim_toggle = QPushButton("▶  Симуляция")
        self._sim_toggle.setCheckable(True)
        self._sim_toggle.setFixedWidth(120)
        self._sim_toggle.clicked.connect(self._on_sim_toggle)
        h.addWidget(self._sim_toggle)

        h.addWidget(QLabel("  Скорость:"))

        # Speed buttons
        self._speed_btns: dict[int, QPushButton] = {}
        for speed in (1, 2, 5):
            b = QPushButton(f"{speed}×")
            b.setCheckable(True)
            b.setFixedWidth(34)
            b.clicked.connect(lambda checked, s=speed: self._on_speed(s))
            h.addWidget(b)
            self._speed_btns[speed] = b
        self._speed_btns[1].setChecked(True)

        h.addSpacing(20)
        self._sim_event_lbl = QLabel("Событий: 0")
        h.addWidget(self._sim_event_lbl)

        h.addStretch()
        hint = QLabel("⚡ Нажмите ▶ Симуляция чтобы запустить эмуляцию работы устройств")
        hint.setStyleSheet("color:rgba(255,255,255,80);font-style:italic;font-size:10px;")
        h.addWidget(hint)

        return bar

    def set_simulator(self, sim) -> None:
        self._simulator = sim
        try:
            from data_store import get_store
            get_store().changed.connect(self._update_sim_counter)
        except Exception:
            pass

    def _on_sim_toggle(self, checked: bool) -> None:
        if self._simulator is None:
            return
        if checked:
            speed = next((s for s, b in self._speed_btns.items() if b.isChecked()), 1)
            self._simulator.start(speed)
            self._sim_dot.setStyleSheet("color:#4CAF50;font-size:14px;")
            self._sim_toggle.setText("■  Остановить")
        else:
            self._simulator.stop()
            self._sim_dot.setStyleSheet("color:#555555;font-size:14px;")
            self._sim_toggle.setText("▶  Симуляция")

    def _on_speed(self, speed: int) -> None:
        for s, b in self._speed_btns.items():
            b.setChecked(s == speed)
        if self._simulator and self._simulator.is_running():
            self._simulator.set_speed(speed)

    def _update_sim_counter(self) -> None:
        if self._simulator:
            self._sim_event_lbl.setText(f"Событий: {self._simulator.event_count}")

    # ── Sidebar ────────────────────────────────────────────────────────────

    def _make_sidebar(self):
        sidebar = QWidget()
        sidebar.setFixedWidth(95)
        sidebar.setStyleSheet(f"background:{styles.SIDEBAR_BG};")

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._nav_group = QButtonGroup(self)
        self._nav_group.setExclusive(True)
        self._nav_btns = []

        for idx, (label, kind) in enumerate(self._NAV):
            btn = QToolButton()
            btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            btn.setIcon(_nav_icon(kind, 26))
            btn.setIconSize(QSize(26, 26))
            btn.setText(label)
            btn.setCheckable(True)
            btn.setFixedSize(95, 78)
            btn.setStyleSheet(
                f"""
                QToolButton {{
                    border: none;
                    background: transparent;
                    color: rgba(255,255,255,190);
                    font-size: 10px;
                    padding-top: 6px;
                    padding-bottom: 4px;
                }}
                QToolButton:hover {{
                    background: {styles.SIDEBAR_HOVER};
                    color: white;
                }}
                QToolButton:checked {{
                    background: {styles.SIDEBAR_ACTIVE};
                    color: white;
                }}
                """
            )
            self._nav_group.addButton(btn, idx)
            layout.addWidget(btn)
            self._nav_btns.append(btn)

        layout.addStretch()

        self._nav_group.idClicked.connect(self.navigate)
        self._nav_btns[0].setChecked(True)
        return sidebar

    # ── Public API ─────────────────────────────────────────────────────────

    def add_page(self, widget):
        self._stack.addWidget(widget)

    def navigate(self, index: int):
        self._stack.setCurrentIndex(index)
        if 0 <= index < len(self._NAV):
            self._title_bar.breadcrumb.setText(self._NAV[index][0])
        if 0 <= index < len(self._nav_btns):
            self._nav_btns[index].setChecked(True)

    def set_breadcrumb(self, text: str):
        self._title_bar.breadcrumb.setText(text)
