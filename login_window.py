from PyQt6.QtWidgets import (
    QDialog, QHBoxLayout, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QCheckBox,
    QFrame, QWidget, QMessageBox,
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QRect
from PyQt6.QtGui import (
    QPainter, QColor, QPolygon, QFont, QPen, QBrush, QPixmap, QIcon,
)


def _make_logo_icon(size=18):
    px = QPixmap(size, size)
    px.fill(Qt.GlobalColor.transparent)
    p = QPainter(px)
    h = size // 2
    colors = ["#337AB7", "#5CB85C", "#D9534F", "#F0AD4E"]
    positions = [(0, 0), (h, 0), (0, h), (h, h)]
    for (x, y), c in zip(positions, colors):
        p.fillRect(x, y, h - 1, h - 1, QColor(c))
    p.end()
    return QIcon(px)


class _Branding(QWidget):
    """Right panel with decorative background + product name."""

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 0, 40, 0)
        layout.addStretch(2)

        # EFROS logo row
        logo_row = QHBoxLayout()
        logo_lbl = QLabel()
        logo_lbl.setPixmap(_make_logo_icon(20).pixmap(20, 20))
        efros_lbl = QLabel("EFROS")
        efros_lbl.setStyleSheet(
            "font-size:13px; font-weight:bold; color:#555; margin-left:6px;"
        )
        logo_row.addWidget(logo_lbl)
        logo_row.addWidget(efros_lbl)
        logo_row.addStretch()
        layout.addLayout(logo_row)
        layout.addSpacing(8)

        ci_lbl = QLabel("Config Inspector")
        ci_lbl.setStyleSheet(
            "font-size:36px; color:#2D6099; font-family:'Segoe UI'; font-weight:300;"
        )
        layout.addWidget(ci_lbl)

        prem_lbl = QLabel("Premium")
        prem_lbl.setStyleSheet(
            "font-size:22px; color:#6699BB; font-style:italic; margin-top:-6px;"
        )
        layout.addWidget(prem_lbl)

        layout.addStretch(3)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        W, H = self.width(), self.height()

        p.fillRect(self.rect(), QColor("#E8E8E8"))

        shapes = [
            ([(55, 0), (340, 0), (300, H), (15, H)], "#DCDCDC"),
            ([(220, 0), (W + 40, 0), (W + 40, H), (180, H)], "#D2D2D2"),
            ([(W - 140, 0), (W + 40, 0), (W + 40, 180), (W - 180, 0)], "#C8C8C8"),
        ]
        p.setPen(Qt.PenStyle.NoPen)
        for pts, color in shapes:
            poly = QPolygon([QPoint(x, y) for x, y in pts])
            p.setBrush(QBrush(QColor(color)))
            p.drawPolygon(poly)
        p.end()


class LoginWindow(QDialog):
    login_successful = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog
        )
        self.setFixedSize(920, 500)
        self._drag_pos = None
        self._build_ui()

    # ── UI ────────────────────────────────────────────────────────────────

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ─ Left form panel ─────────────────────────────────────────────
        left = QWidget()
        left.setFixedWidth(365)
        left.setStyleSheet("background:#E8E8E8;")

        form = QVBoxLayout(left)
        form.setContentsMargins(50, 90, 40, 50)
        form.setSpacing(6)

        # Subtitle
        sub = QLabel("Network Configuration Change & Compliance Management System")
        sub.setStyleSheet("color:#666; font-size:10px;")
        sub.setWordWrap(True)
        form.addWidget(sub)
        form.addSpacing(30)

        # Server
        srv_row = QHBoxLayout()
        srv_row.addWidget(QLabel("Сервер"))
        self.server_cb = QComboBox()
        self.server_cb.addItem("localhost")
        self.server_cb.setFixedWidth(190)
        srv_row.addWidget(self.server_cb)
        srv_row.addStretch()
        form.addLayout(srv_row)

        port_lbl = QLabel(
            '<a href="#" style="color:#337AB7;text-decoration:none;">порт подключения</a>'
        )
        port_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        port_lbl.setContentsMargins(0, 0, 4, 6)
        form.addWidget(port_lbl)

        self.curr_user_cb = QCheckBox("Вход под текущим пользователем")
        form.addWidget(self.curr_user_cb)
        form.addSpacing(8)

        # Login
        lg_row = QHBoxLayout()
        lbl = QLabel("Логин")
        lbl.setFixedWidth(65)
        self.login_edit = QLineEdit("root")
        self.login_edit.setFixedWidth(190)
        lg_row.addWidget(lbl)
        lg_row.addWidget(self.login_edit)
        lg_row.addStretch()
        form.addLayout(lg_row)
        form.addSpacing(4)

        # Password
        pw_row = QHBoxLayout()
        lbl2 = QLabel("Пароль")
        lbl2.setFixedWidth(65)
        self.pass_edit = QLineEdit()
        self.pass_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_edit.setPlaceholderText("RU")
        self.pass_edit.setFixedWidth(190)
        pw_row.addWidget(lbl2)
        pw_row.addWidget(self.pass_edit)
        pw_row.addStretch()
        form.addLayout(pw_row)
        form.addSpacing(22)

        # Connect button
        self.connect_btn = QPushButton("Подключиться")
        self.connect_btn.setObjectName("primaryBtn")
        self.connect_btn.setFixedSize(160, 36)
        self.connect_btn.clicked.connect(self._on_connect)
        btn_row = QHBoxLayout()
        btn_row.addWidget(self.connect_btn)
        btn_row.addStretch()
        form.addLayout(btn_row)
        form.addStretch()

        root.addWidget(left)

        # Divider
        div = QFrame()
        div.setFixedWidth(1)
        div.setStyleSheet("background:#BBBBBB;")
        root.addWidget(div)

        # ─ Right branding ───────────────────────────────────────────────
        root.addWidget(_Branding(), 1)

        # Help label (absolute)
        help_lbl = QLabel("? Справка", self)
        help_lbl.setStyleSheet("color:#888; font-size:10px;")
        help_lbl.move(self.width() - 70, self.height() - 22)

    # ── Slots ─────────────────────────────────────────────────────────────

    def _on_connect(self):
        if not self.login_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите логин")
            return
        self.login_successful.emit()

    # ── Drag ──────────────────────────────────────────────────────────────

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = e.globalPosition().toPoint() - self.pos()

    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.MouseButton.LeftButton and self._drag_pos:
            self.move(e.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, e):
        self._drag_pos = None

    def keyPressEvent(self, e):
        if e.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self._on_connect()
