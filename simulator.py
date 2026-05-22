"""Simulation engine — drives DataStore with random realistic device activity.

Usage:
    from data_store import get_store
    from simulator import Simulator
    store = get_store()
    sim   = Simulator(store)
    sim.start(speed=1)   # or 2, 5
    sim.stop()
"""
from __future__ import annotations
import random, datetime
from PyQt6.QtCore import QObject, QTimer


_BASE_MS = 2500   # tick interval at speed 1×

_VIOLATION_REPORTS = [
    'Windows файлы "Controlmy"',
    'Windows файлы "SecurityCF"',
    'Windows файлы "КЦ"',
    'Linux cat /etc/passwd',
    'Linux cat /etc/shadow',
    'Linux cat /etc/group',
    'Linux /sbin/ausearch',
    'Журнал безопасности',
    'Системные переменные',
    'Службы',
    'Корневые сертификаты',
    'Локальные пользователи и группы',
    'Программы и обновления',
]

_EVENT_MSGS = [
    'Загружен отчёт "Windows файлы"',
    'Загружен отчёт "Службы"',
    'Запуск задания "proverka"',
    'Загружен отчёт "Информация о системе"',
    'Загружен отчёт "Драйверы"',
    'Загружен отчёт "Корневые сертификаты"',
    'Загружен отчёт "Локальные пользователи"',
    'Загружен отчёт "Программы и обновления"',
    'Загружен отчёт "Системные переменные"',
    'Загружен отчёт "Автозагрузка"',
]


class Simulator(QObject):
    def __init__(self, store, parent=None):
        super().__init__(parent)
        self._store  = store
        self._timer  = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._speed  = 1
        self._events = 0      # cumulative event counter

    # ── Public API ─────────────────────────────────────────────────────────────

    @property
    def event_count(self) -> int:
        return self._events

    def start(self, speed: int = 1) -> None:
        self._speed = max(1, min(10, speed))
        self._timer.start(max(300, _BASE_MS // self._speed))

    def stop(self) -> None:
        self._timer.stop()

    def set_speed(self, speed: int) -> None:
        self._speed = max(1, min(10, speed))
        if self._timer.isActive():
            self._timer.setInterval(max(300, _BASE_MS // self._speed))

    def is_running(self) -> bool:
        return self._timer.isActive()

    def reset(self) -> None:
        """Stop and reset event counter (store data not reset)."""
        self.stop()
        self._events = 0

    # ── Tick ───────────────────────────────────────────────────────────────────

    def _tick(self) -> None:
        from data_store import DeviceStatus, ViolationRecord
        store  = self._store
        now    = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        device = random.choice(list(store.devices.values()))
        self._events += 1

        action = random.choices(
            ["event",  "violation", "connect", "disconnect",
             "vuln",   "security",  "fix"],
            weights=[35, 12,        20,        8,
                     8,   4,        13],
        )[0]

        if action == "event":
            msg = random.choice(_EVENT_MSGS)
            store.system_events.insert(0, (device.name, now, "Загрузка отчёта", msg))
            store.system_events = store.system_events[:100]
            device.report_count += 1

        elif action == "violation":
            rpt = random.choice(_VIOLATION_REPORTS)
            store.recent_violations.insert(
                0, ViolationRecord(device.name, "Нарушение целостности", now, rpt)
            )
            store.recent_violations = store.recent_violations[:10]
            device.viol_count   += 1
            device.report_count += 1
            if device.status != DeviceStatus.NO_CONNECTION:
                device.status = DeviceStatus.VIOLATION
            store.system_events.insert(
                0, (device.name, now, "Нарушение", f'Нарушение: {rpt}')
            )

        elif action == "connect":
            if device.status == DeviceStatus.NO_CONNECTION:
                device.status = DeviceStatus.OK
                store.system_events.insert(
                    0, (device.name, now, "Соединение", "Устройство подключено")
                )

        elif action == "disconnect":
            if device.status in (DeviceStatus.OK, DeviceStatus.VIOLATION):
                device.status = DeviceStatus.NO_CONNECTION
                store.system_events.insert(
                    0, (device.name, now, "Соединение", "Потеря связи с устройством")
                )

        elif action == "vuln":
            attr = random.choices(
                ["vuln_critical", "vuln_important", "vuln_info"],
                weights=[10, 30, 60],
            )[0]
            setattr(device, attr, getattr(device, attr) + 1)

        elif action == "security":
            added = random.randint(1, 5)
            store.security.total  += added
            store.security.passed += random.randint(0, added)
            store.security.passed  = min(store.security.passed, store.security.total)

        elif action == "fix":
            if device.viol_count > 0:
                device.viol_count -= 1
                if device.viol_count == 0 and device.status == DeviceStatus.VIOLATION:
                    device.status = DeviceStatus.OK
                store.system_events.insert(
                    0, (device.name, now, "Устранение", "Нарушение принято")
                )

        # Push historical snapshot
        store.push_history(
            viol    = store.total_violations,
            ok      = store.status_count(DeviceStatus.OK),
            sec_pct = store.security_percent(),
        )

        store.changed.emit()
