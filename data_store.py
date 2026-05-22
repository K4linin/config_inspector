"""Central mutable data model.
All pages that want live updates read from get_store() and connect to changed.
Must be imported AFTER QApplication is created (call get_store() lazily).
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from PyQt6.QtCore import QObject, pyqtSignal


class DeviceStatus(str, Enum):
    OK            = "ok"
    VIOLATION     = "violation"
    NO_CONNECTION = "no_connection"
    WARNING       = "warning"
    CRITICAL      = "critical"
    INFO          = "info"


@dataclass
class DeviceState:
    name:           str
    dtype:          str            # "Windows" | "Linux"
    status:         DeviceStatus = DeviceStatus.NO_CONNECTION
    viol_count:     int = 0
    report_count:   int = 0
    vuln_critical:  int = 0
    vuln_important: int = 0
    vuln_info:      int = 0


@dataclass
class SecurityState:
    total:  int = 0
    passed: int = 0


@dataclass
class ViolationRecord:
    device: str
    title:  str
    time:   str
    report: str


class DataStore(QObject):
    """Observable store — emit ``changed`` after every mutation."""
    changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.devices: dict[str, DeviceState] = {
            "winpc":       DeviceState("winpc",       "Windows", DeviceStatus.VIOLATION,     2, 16),
            "192.168.0.4": DeviceState("192.168.0.4", "Windows", DeviceStatus.OK,            0,  2),
            "192.168.0.1": DeviceState("192.168.0.1", "Linux",   DeviceStatus.NO_CONNECTION, 0,  0),
            "DC":          DeviceState("DC",          "Windows", DeviceStatus.NO_CONNECTION, 0,  0),
            "skdpu":       DeviceState("skdpu",       "Linux",   DeviceStatus.NO_CONNECTION, 0,  0),
        }

        self.recent_violations: list[ViolationRecord] = [
            ViolationRecord("winpc", "Нарушение целостности",
                            "03.07.2017 14:55", 'Windows файлы "SecurityCF"'),
            ViolationRecord("winpc", "Нарушение целостности",
                            "03.07.2017 14:57", 'Windows файлы "Controlmy"'),
        ]
        self.security = SecurityState()
        self.system_events: list[tuple] = []  # (device, time, type, msg)

        # 30-point historical data for line/bar charts
        self._viol_history: list[int] = [0] * 26 + [1, 0, 2, 1]
        self._ok_history:   list[int] = [2] * 26 + [1, 2, 1, 2]
        self._sec_history:  list[int] = [0] * 30

    # ── Computed properties ────────────────────────────────────────────────────

    @property
    def total_reports(self) -> int:
        return sum(d.report_count for d in self.devices.values())

    @property
    def total_violations(self) -> int:
        return sum(d.viol_count for d in self.devices.values())

    @property
    def violation_percent(self) -> int:
        t = self.total_reports
        if t == 0:
            return 0
        return min(100, int(self.total_violations / t * 100))

    def vuln_count(self, attr: str) -> int:
        """attr: 'vuln_critical' | 'vuln_important' | 'vuln_info'"""
        return sum(getattr(d, attr, 0) for d in self.devices.values())

    def devices_without_vulns(self) -> int:
        return sum(
            1 for d in self.devices.values()
            if d.vuln_critical == 0 and d.vuln_important == 0 and d.vuln_info == 0
        )

    def status_count(self, status: DeviceStatus) -> int:
        return sum(1 for d in self.devices.values() if d.status == status)

    def platform_counts(self, dtype: str) -> tuple[int, int]:
        """Return (connected, total) for the given OS type."""
        devs = [d for d in self.devices.values() if d.dtype == dtype]
        connected = sum(1 for d in devs if d.status != DeviceStatus.NO_CONNECTION)
        return connected, len(devs)

    def top_vuln_devices(self, n: int = 2) -> list[tuple[str, int]]:
        """Return [(name, total_vulns)] sorted descending, top-n."""
        scored = []
        for d in self.devices.values():
            total = d.vuln_critical + d.vuln_important + d.vuln_info
            if total > 0:
                scored.append((d.name, total))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:n]

    def top_insecure_devices(self, n: int = 2) -> list[str]:
        """Devices with most violations (lowest security) for display."""
        scored = [(d.name, d.viol_count) for d in self.devices.values() if d.viol_count > 0]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [name for name, _ in scored[:n]]

    def security_percent(self) -> int:
        if self.security.total == 0:
            return 0
        return min(100, int(self.security.passed / self.security.total * 100))

    # ── History ───────────────────────────────────────────────────────────────

    def push_history(self, viol: int, ok: int, sec_pct: int) -> None:
        self._viol_history.pop(0); self._viol_history.append(viol)
        self._ok_history.pop(0);   self._ok_history.append(ok)
        self._sec_history.pop(0);  self._sec_history.append(sec_pct)

    def viol_history(self) -> list[int]:
        return list(self._viol_history)

    def ok_history(self) -> list[int]:
        return list(self._ok_history)

    def sec_history(self) -> list[int]:
        return list(self._sec_history)


# ── Module-level singleton ────────────────────────────────────────────────────

_store: DataStore | None = None


def get_store() -> DataStore:
    """Lazily create and return the shared DataStore."""
    global _store
    if _store is None:
        _store = DataStore()
    return _store
