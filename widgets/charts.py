"""Custom chart widgets drawn with QPainter — no external dependencies."""
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRectF, QPoint
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QBrush


class DonutChart(QWidget):
    """Single-colour ring/donut chart."""

    def __init__(self, value=0, color="#5CB85C", size=100, parent=None):
        super().__init__(parent)
        self._value = max(0, min(100, value))
        self._color = color
        self.setFixedSize(size, size)

    def setValue(self, v: int, color: str | None = None) -> None:
        self._value = max(0, min(100, int(v)))
        if color:
            self._color = color
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        s = min(self.width(), self.height())
        margin = int(s * 0.12)
        rect   = QRectF(margin, margin, s - 2 * margin, s - 2 * margin)
        ring_w = max(8, int(s * 0.14))

        # Background ring
        pen = QPen(QColor("#E0E0E0"))
        pen.setWidth(ring_w)
        pen.setCapStyle(Qt.PenCapStyle.FlatCap)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawArc(rect, 0, 360 * 16)

        # Value arc
        if self._value > 0:
            pen = QPen(QColor(self._color))
            pen.setWidth(ring_w)
            pen.setCapStyle(Qt.PenCapStyle.FlatCap)
            p.setPen(pen)
            p.drawArc(rect, 90 * 16, -int(self._value / 100 * 360 * 16))

        # Centre label
        p.setPen(QPen(QColor("#333333")))
        font = QFont("Segoe UI", max(7, int(s * 0.14)))
        font.setBold(True)
        p.setFont(font)
        p.drawText(rect.toRect(), Qt.AlignmentFlag.AlignCenter, f"{self._value}%")
        p.end()


class MultiDonut(QWidget):
    """Multi-segment ring chart (for device-state card)."""

    def __init__(self, segments=None, size=110, parent=None):
        super().__init__(parent)
        self._segments = segments or []   # [(value, "#RRGGBB"), ...]
        self.setFixedSize(size, size)

    def setSegments(self, segments: list) -> None:
        self._segments = segments
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(Qt.BrushStyle.NoBrush)

        s      = min(self.width(), self.height())
        margin = int(s * 0.12)
        rect   = QRectF(margin, margin, s - 2 * margin, s - 2 * margin)
        ring_w = max(10, int(s * 0.16))

        total = sum(v for v, _ in self._segments) or 1
        start = 90 * 16

        # If no segments, draw solid gray ring
        if not self._segments or total == 0:
            pen = QPen(QColor("#CCCCCC"))
            pen.setWidth(ring_w)
            pen.setCapStyle(Qt.PenCapStyle.FlatCap)
            p.setPen(pen)
            p.drawArc(rect, 0, 360 * 16)
            p.end()
            return

        for value, color in self._segments:
            if value == 0:
                continue
            span = -int(value / total * 360 * 16)
            pen  = QPen(QColor(color))
            pen.setWidth(ring_w)
            pen.setCapStyle(Qt.PenCapStyle.FlatCap)
            p.setPen(pen)
            p.drawArc(rect, start, span)
            start += span
        p.end()


class MiniLineChart(QWidget):
    """Compact line chart for monitoring card."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(130, 85)
        self._violations = [0] * 24 + [0, 0, 0, 1, 0, 3]
        self._accepted   = [0] * 30

    def update_data(self, violations: list[int], accepted: list[int]) -> None:
        self._violations = list(violations)[-30:]
        self._accepted   = list(accepted)[-30:]
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        W, H       = self.width(), self.height()
        mx, mt, mb = 6, 20, 22
        cw, ch     = W - 2 * mx, H - mt - mb

        # Title
        p.setPen(QColor("#999999"))
        p.setFont(QFont("Segoe UI", 8))
        p.drawText(0, 2, W, 16, Qt.AlignmentFlag.AlignCenter, "Статистика за месяц")

        # Chart bg + grid
        p.fillRect(mx, mt, cw, ch, QColor("#FAFAFA"))
        p.setPen(QPen(QColor("#EEEEEE")))
        for i in (1, 2):
            y = mt + ch * i // 3
            p.drawLine(mx, y, mx + cw, y)

        all_vals = self._violations + self._accepted
        mv = max(all_vals) if max(all_vals) > 0 else 1

        self._draw_line(p, self._violations, "#D9534F", mx, mt, cw, ch, mv)
        self._draw_line(p, self._accepted,   "#5CB85C", mx, mt, cw, ch, mv)

        # Legend
        ly = H - mb + 8
        p.setFont(QFont("Segoe UI", 7))
        for i, (color, label) in enumerate([
            ("#D9534F", "Нарушения"),
            ("#5CB85C", "Принято"),
        ]):
            lx = mx + i * (cw // 2)
            p.setPen(QPen(QColor(color), 1.5))
            p.drawLine(lx, ly, lx + 12, ly)
            p.setPen(QColor("#666666"))
            p.drawText(lx + 14, ly - 5, 90, 14,
                       Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                       label)
        p.end()

    def _draw_line(self, p, data, color, x0, y0, w, h, mv):
        n = len(data)
        if n < 2:
            return
        xstep = w / (n - 1)
        pen   = QPen(QColor(color), 1.5)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        p.setPen(pen)
        px, py = None, None
        for i, v in enumerate(data):
            x = int(x0 + i * xstep)
            y = int(y0 + h - (v / mv) * h * 0.88)
            if px is not None:
                p.drawLine(px, py, x, y)
            px, py = x, y


class MiniBarChart(QWidget):
    """Compact bar chart for security-checks card."""

    def __init__(self, color="#5CB85C", parent=None):
        super().__init__(parent)
        self._color = color
        self.setMinimumSize(130, 85)
        self._data = [0] * 30

    def update_data(self, data: list[int], color: str | None = None) -> None:
        self._data  = list(data)[-30:]
        if color:
            self._color = color
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        W, H       = self.width(), self.height()
        mx, mt, mb = 6, 20, 14
        cw, ch     = W - 2 * mx, H - mt - mb

        p.setPen(QColor("#999999"))
        p.setFont(QFont("Segoe UI", 8))
        p.drawText(0, 2, W, 16, Qt.AlignmentFlag.AlignCenter, "Статистика за месяц")

        n  = len(self._data)
        bw = max(1, cw // max(n, 1) - 1)
        mv = max(self._data) or 1

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(QColor(self._color)))
        for i, v in enumerate(self._data):
            bh = int(v / mv * ch * 0.9)
            if bh > 0:
                p.drawRect(mx + i * (cw // n), mt + ch - bh, bw, bh)

        # Legend
        p.setPen(QColor(self._color))
        p.drawRect(mx, H - mb + 4, 10, 4)
        p.setPen(QColor("#666666"))
        p.setFont(QFont("Segoe UI", 7))
        p.drawText(mx + 13, H - mb, 120, 14,
                   Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                   "% защищённости")
        p.end()
