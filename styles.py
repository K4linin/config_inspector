TITLE_BAR_BG   = "#354E68"   # same as sidebar — unified top/left colour
SIDEBAR_BG     = "#354E68"
SIDEBAR_ACTIVE = "#1E3347"
SIDEBAR_HOVER  = "#2A4058"

MAIN_BG        = "#F0F2F4"
CARD_BG        = "#FFFFFF"
CARD_BORDER    = "#DDDDDD"

TEXT_PRIMARY   = "#333333"
TEXT_SECONDARY = "#777777"
TEXT_HEADER    = "#555555"

ACCENT_GREEN   = "#5CB85C"
ACCENT_BLUE    = "#337AB7"
ACCENT_RED     = "#D9534F"
ACCENT_ORANGE  = "#F0AD4E"
ACCENT_GRAY    = "#888888"

BTN_PRIMARY_BG = "#2D6099"

TABLE_HEADER   = "#ECECEC"
TABLE_ALT      = "#F9F9F9"
TABLE_SELECTED = "#D6E4F7"

INPUT_BORDER   = "#CCCCCC"


def get_app_stylesheet():
    return f"""
    QWidget {{
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 12px;
        color: {TEXT_PRIMARY};
    }}

    /* ── Primary button ── */
    QPushButton#primaryBtn {{
        background: {BTN_PRIMARY_BG};
        color: white;
        border: none;
        padding: 6px 18px;
        border-radius: 3px;
        font-size: 13px;
    }}
    QPushButton#primaryBtn:hover  {{ background: #245080; }}
    QPushButton#primaryBtn:pressed {{ background: #1A3A60; }}

    /* ── Flat / default buttons ── */
    QPushButton {{
        background: #F5F5F5;
        border: 1px solid {INPUT_BORDER};
        padding: 4px 12px;
        border-radius: 2px;
        color: {TEXT_PRIMARY};
    }}
    QPushButton:hover  {{ background: #E8E8E8; }}
    QPushButton:pressed {{ background: #D5D5D5; }}

    /* ── Active filter button (blue) ── */
    QPushButton#activeBtn {{
        background: {ACCENT_BLUE};
        color: white;
        border: none;
        padding: 4px 12px;
        border-radius: 2px;
    }}

    /* ── Title bar buttons ── */
    QPushButton#titleBtn {{
        background: transparent;
        border: none;
        color: white;
        padding: 0 14px;
        font-size: 13px;
    }}
    QPushButton#titleBtn:hover  {{ background: rgba(255,255,255,30); }}
    QPushButton#closeBtn {{
        background: transparent;
        border: none;
        color: white;
        padding: 0 14px;
        font-size: 14px;
    }}
    QPushButton#closeBtn:hover  {{ background: #C42B1C; }}

    /* ── Nav (sidebar) tool buttons ── */
    QToolButton {{
        border: none;
        background: transparent;
        color: white;
        padding: 4px 2px 2px 2px;
        font-size: 10px;
    }}
    QToolButton:hover:!checked {{ background: {SIDEBAR_HOVER}; }}
    QToolButton:checked         {{ background: {SIDEBAR_ACTIVE}; }}

    /* ── Inputs ── */
    QLineEdit {{
        border: 1px solid {INPUT_BORDER};
        padding: 4px 6px;
        background: white;
        border-radius: 2px;
    }}
    QLineEdit:focus {{ border-color: {ACCENT_BLUE}; }}

    QComboBox {{
        border: 1px solid {INPUT_BORDER};
        padding: 4px 6px;
        background: white;
        border-radius: 2px;
        min-height: 24px;
    }}
    QComboBox:focus {{ border-color: {ACCENT_BLUE}; }}
    QComboBox::drop-down {{ border: none; width: 20px; }}
    QComboBox QAbstractItemView {{
        border: 1px solid {INPUT_BORDER};
        selection-background-color: {TABLE_SELECTED};
        selection-color: {TEXT_PRIMARY};
    }}

    /* ── Tree ── */
    QTreeWidget {{
        border: none;
        background: white;
        outline: none;
        show-decoration-selected: 1;
    }}
    QTreeWidget::item {{ height: 22px; padding-left: 2px; }}
    QTreeWidget::item:selected {{ background: {TABLE_SELECTED}; color: {TEXT_PRIMARY}; }}
    QTreeWidget::item:hover:!selected {{ background: #EAF2FF; }}

    /* ── Table ── */
    QTableWidget {{
        border: none;
        gridline-color: #EBEBEB;
        background: white;
        selection-background-color: {TABLE_SELECTED};
        selection-color: {TEXT_PRIMARY};
        alternate-background-color: {TABLE_ALT};
    }}
    QTableWidget::item {{ padding: 4px 6px; }}
    QHeaderView::section {{
        background: {TABLE_HEADER};
        border: none;
        border-right: 1px solid #D5D5D5;
        border-bottom: 2px solid #CCCCCC;
        padding: 5px 8px;
        font-weight: bold;
    }}

    /* ── Tabs ── */
    QTabWidget::pane {{
        border: none;
        border-top: 1px solid {CARD_BORDER};
        background: white;
    }}
    QTabBar::tab {{
        padding: 7px 18px;
        background: #F0F0F0;
        border: 1px solid {CARD_BORDER};
        border-bottom: none;
        margin-right: 2px;
        color: {TEXT_SECONDARY};
    }}
    QTabBar::tab:selected {{
        background: white;
        color: {TEXT_PRIMARY};
        border-top: 2px solid {ACCENT_BLUE};
    }}
    QTabBar::tab:hover:!selected {{ background: #E5E5E5; }}

    /* ── Scrollbars ── */
    QScrollBar:vertical   {{ width: 8px; background: transparent; }}
    QScrollBar:horizontal {{ height: 8px; background: transparent; }}
    QScrollBar::handle:vertical, QScrollBar::handle:horizontal {{
        background: #CCCCCC; border-radius: 4px; min-height: 20px; min-width: 20px;
    }}
    QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {{
        background: #AAAAAA;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ height:0; width:0; }}

    /* ── Progress bar ── */
    QProgressBar {{
        border: none;
        background: #E4E4E4;
        border-radius: 4px;
        max-height: 8px;
        text-align: right;
    }}
    QProgressBar::chunk {{ background: {ACCENT_BLUE}; border-radius: 4px; }}

    /* ── Splitter ── */
    QSplitter::handle:horizontal {{ background: {CARD_BORDER}; width: 1px; }}
    QSplitter::handle:vertical   {{ background: {CARD_BORDER}; height: 1px; }}

    /* ── Misc ── */
    QCheckBox {{
        spacing: 6px;
        background: transparent;
    }}
    QCheckBox::indicator {{
        width: 14px; height: 14px;
        border: 1px solid {INPUT_BORDER}; background: white; border-radius: 2px;
    }}
    QCheckBox::indicator:hover   {{ border-color: {ACCENT_BLUE}; }}
    QCheckBox::indicator:checked {{
        background: {ACCENT_BLUE}; border-color: {ACCENT_BLUE};
        image: none;
    }}
    QListWidget {{
        border: 1px solid {INPUT_BORDER}; background: white; outline: none;
    }}
    QListWidget::item {{ padding: 3px; }}
    QListWidget::item:selected {{ background: {TABLE_SELECTED}; color: {TEXT_PRIMARY}; }}

    QFrame#card {{
        background: white;
        border: 1px solid {CARD_BORDER};
        border-radius: 2px;
    }}
    """
