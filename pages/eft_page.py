"""EFT Data Inspector — страница, встроенная в Config Inspector."""
import sys
import os
import importlib.util as _ilu

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSplitter, QListWidget, QListWidgetItem,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal

# ── Изоляция модулей EFT ──────────────────────────────────────────────────────
# Config Inspector и EFT Inspector оба имеют styles.py — нужно предотвратить конфликт.
# Загружаем EFT styles под уникальным именем, временно подменяем sys.modules['styles'],
# импортируем компоненты EFT (они привяжутся к EFT-стилям), затем восстанавливаем.

_EFT = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'eft_inspector')
)
if _EFT not in sys.path:
    sys.path.insert(0, _EFT)

# Загружаем EFT styles в изолированный модуль
_es = _ilu.spec_from_file_location('_eft_styles', os.path.join(_EFT, 'styles.py'))
_eft_styles = _ilu.module_from_spec(_es)
sys.modules['_eft_styles'] = _eft_styles
_es.loader.exec_module(_eft_styles)

# Временно регистрируем EFT styles как 'styles', чтобы импортируемые модули
# привязали свой module-level `import styles` к EFT-версии
_saved_styles = sys.modules.get('styles')
sys.modules['styles'] = _eft_styles

# Импортируем EFT-компоненты — теперь каждый из них сохранит ссылку на _eft_styles
from explorer import ExplorerPanel      # noqa: E402
from inspector import InspectorPanel    # noqa: E402
from references import ReferencesPanel  # noqa: E402
import sample_data as _eft_db           # noqa: E402

# Восстанавливаем оригинальный styles Config Inspector
if _saved_styles is not None:
    sys.modules['styles'] = _saved_styles
elif 'styles' in sys.modules and sys.modules['styles'] is _eft_styles:
    del sys.modules['styles']

_S = _eft_styles  # псевдоним для стилей EFT в этом файле


# ── Поисковая строка (переиспользуем логику из eft/app_window, без его импорта) ──

class _SearchBar(QWidget):
    item_chosen = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(44)
        self.setStyleSheet(f"background:{_S.BG_PANEL};")

        h = QHBoxLayout(self)
        h.setContentsMargins(12, 6, 12, 6)
        h.setSpacing(8)

        lbl = QLabel("🔍")
        lbl.setStyleSheet("font-size:14px;background:transparent;")
        h.addWidget(lbl)

        self._edit = QLineEdit()
        self._edit.setPlaceholderText("Поиск по ID, имени или типу…   (Ctrl+F)")
        self._edit.setStyleSheet(
            f"background:{_S.BG_SECONDARY};border:1px solid {_S.BORDER};"
            f"border-radius:3px;padding:4px 8px;color:{_S.TEXT_PRIMARY};font-size:13px;"
        )
        self._edit.textChanged.connect(self._on_change)
        self._edit.returnPressed.connect(self._on_enter)
        h.addWidget(self._edit, 1)

        clr = QPushButton("✕")
        clr.setFixedSize(24, 24)
        clr.setStyleSheet(
            f"QPushButton{{background:transparent;border:none;"
            f"color:{_S.TEXT_DIM};font-size:13px;}}"
            f"QPushButton:hover{{color:{_S.TEXT_PRIMARY};}}"
        )
        clr.clicked.connect(self._edit.clear)
        clr.hide()
        self._clr = clr
        h.addWidget(clr)

        self._results: list = []
        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._do_search)

        self._dropdown = QListWidget(self)
        self._dropdown.setWindowFlags(Qt.WindowType.Popup)
        self._dropdown.setStyleSheet(
            f"QListWidget{{background:{_S.BG_SECONDARY};"
            f"border:1px solid {_S.BORDER_FOCUS};color:{_S.TEXT_PRIMARY};"
            f"font-size:12px;outline:none;}}"
            f"QListWidget::item{{padding:5px 12px;height:26px;}}"
            f"QListWidget::item:selected{{background:{_S.BG_SELECTED};color:white;}}"
            f"QListWidget::item:hover{{background:{_S.BG_HOVER};}}"
        )
        self._dropdown.itemClicked.connect(self._on_pick)
        self._dropdown.hide()

    def focus(self):
        self._edit.setFocus()
        self._edit.selectAll()

    def _on_change(self, text: str):
        self._clr.setVisible(bool(text))
        if text.strip():
            self._timer.start(180)
        else:
            self._dropdown.hide()

    def _do_search(self):
        q = self._edit.text().strip()
        if not q:
            return
        self._results = _eft_db.search(q)
        if not self._results:
            self._dropdown.hide()
            return
        self._dropdown.clear()
        for key, name, otype in self._results:
            it = QListWidgetItem(f"  {name}  ·  {otype}  ·  {key}")
            it.setData(Qt.ItemDataRole.UserRole, key)
            self._dropdown.addItem(it)
        pos = self._edit.mapToGlobal(self._edit.rect().bottomLeft())
        self._dropdown.move(pos)
        self._dropdown.resize(
            self._edit.width() + 40, min(len(self._results) * 30 + 4, 300)
        )
        self._dropdown.show()

    def _on_enter(self):
        if self._results:
            self._dropdown.hide()
            self.item_chosen.emit(self._results[0][0])

    def _on_pick(self, item: QListWidgetItem):
        self._dropdown.hide()
        self.item_chosen.emit(item.data(Qt.ItemDataRole.UserRole))


# ── Главная страница ───────────────────────────────────────────────────────────

class EftPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background:{_S.BG_PRIMARY};")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Поисковая строка ───────────────────────────────────────────────
        self._search = _SearchBar()
        root.addWidget(self._search)

        # ── Три панели ─────────────────────────────────────────────────────
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet(
            f"QSplitter::handle{{background:{_S.BORDER};width:1px;}}"
        )
        self._explorer   = ExplorerPanel()
        self._inspector  = InspectorPanel()
        self._references = ReferencesPanel()

        splitter.addWidget(self._explorer)
        splitter.addWidget(self._inspector)
        splitter.addWidget(self._references)
        splitter.setSizes([220, 820, 260])
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(2, False)
        root.addWidget(splitter, 1)

        # ── Статус-строка ──────────────────────────────────────────────────
        status = QWidget()
        status.setFixedHeight(22)
        status.setStyleSheet(
            f"background:{_S.BG_PANEL};border-top:1px solid {_S.BORDER};"
        )
        sh = QHBoxLayout(status)
        sh.setContentsMargins(8, 0, 8, 0)
        self._status_lbl = QLabel(
            f"Предметов: {len(_eft_db.ITEMS)}   "
            f"Ботов: {len(_eft_db.BOTS)}   "
            f"Трейдеров: {len(_eft_db.TRADERS)}   "
            f"Квестов: {len(_eft_db.QUESTS)}"
        )
        self._status_lbl.setStyleSheet(
            f"color:{_S.TEXT_DIM};font-size:10px;background:transparent;"
        )
        sh.addWidget(self._status_lbl)
        sh.addStretch()
        self._sel_lbl = QLabel()
        self._sel_lbl.setStyleSheet(
            f"color:{_S.TEXT_DIM};font-size:10px;background:transparent;"
        )
        sh.addWidget(self._sel_lbl)
        root.addWidget(status)

        # ── Сигналы ────────────────────────────────────────────────────────
        self._explorer.item_selected.connect(self._on_select)
        self._search.item_chosen.connect(self._on_navigate)
        self._references.navigate_to.connect(self._on_navigate)

        from PyQt6.QtGui import QShortcut, QKeySequence
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self._search.focus)

        # Стартовый выбор
        self._on_select("AKS-74U")
        self._explorer.select_key("AKS-74U")

    # ──────────────────────────────────────────────────────────────────────────

    def _on_select(self, key: str):
        data = _eft_db.ALL_DATA.get(key, {})
        self._inspector.load(key)
        self._references.load(key)
        name  = data.get("_name", key)
        dtype = data.get("_type", "")
        self._sel_lbl.setText(f"{dtype.upper()}  ·  {name}")

    def _on_navigate(self, key: str):
        if key and key in _eft_db.ALL_DATA:
            self._on_select(key)
            self._explorer.select_key(key)
