"""Dark theme QSS for AxoLexis — exported as DARK_QSS string."""

DARK_QSS = """
/* ═══════════════════════════════════════════════════════════════════════════
   AxoLexis — DARK Theme  |  Design: Deep Violet Space + Glassmorphism
   ═══════════════════════════════════════════════════════════════════════════ */

/* ── Base ── */
QMainWindow, QWidget {
    background-color: #0A0B10;
    color: #E8E9FF;
    font-family: "Inter", "Segoe UI", system-ui, sans-serif;
    font-size: 10pt;
}

QDialog {
    background-color: #0E0F1A;
    color: #E8E9FF;
}

/* ── Header Bar ── */
QFrame#headerBar {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #0D0E1A, stop:1 #12132A);
    border-bottom: 1px solid #252640;
}

/* ── Navigation Bar ── */
QFrame#navBar {
    background-color: #0E0F1A;
    border-bottom: 1px solid #1E2040;
}

QPushButton#navButton {
    background-color: transparent;
    color: #4A4F7A;
    border: none;
    border-radius: 8px;
    font-size: 10pt;
    font-weight: 600;
    padding: 8px 22px;
    letter-spacing: 0.5px;
}

QPushButton#navButton:hover {
    background-color: #1A1D35;
    color: #9BA4FF;
}

QPushButton#navButtonActive {
    background-color: #1E2245;
    color: #A5B4FF;
    border: 1px solid #3D4285;
    border-radius: 10px;
    font-size: 10pt;
    font-weight: 700;
    padding: 8px 22px;
    letter-spacing: 0.5px;
}

/* ── General Labels ── */
QLabel {
    color: #B0B5E8;
    font-size: 9.5pt;
    background: transparent;
}

QLabel#titleLabel {
    font-size: 17pt;
    font-weight: 700;
    color: #F0F0FF;
    letter-spacing: 0.3px;
}

QLabel#subtitleLabel {
    font-size: 8.5pt;
    color: #7C6FFF;
    font-weight: 600;
    letter-spacing: 1.5px;
}

QLabel#sectionLabel {
    font-size: 8pt;
    color: #5559A0;
    font-weight: 700;
    letter-spacing: 1.8px;
}

QLabel#metricValue {
    font-size: 22pt;
    font-weight: 800;
    color: #F0F0FF;
    background: transparent;
}

QLabel#metricLabel {
    font-size: 7.5pt;
    color: #5559A0;
    font-weight: 600;
    letter-spacing: 1px;
    background: transparent;
}

QLabel#fieldLabel, QLabel#formRowLabel {
    font-size: 9.5pt;
    color: #CBD0FF;
    font-weight: 600;
    background: transparent;
    min-width: 130px;
}

/* ── Cards / Group Boxes ── */
QGroupBox {
    background-color: #11122A;
    border: 1px solid #252648;
    border-radius: 14px;
    margin-top: 20px;
    padding: 18px 14px 14px 14px;
    color: #E8E9FF;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 14px;
    top: -11px;
    padding: 3px 10px;
    color: #8B8FBE;
    font-size: 9pt;
    font-weight: 600;
    background-color: #181936;
    border: 1px solid #2D3060;
    border-radius: 6px;
    letter-spacing: 0.5px;
}

/* ── Metric Cards ── */
QFrame#metricCard {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #141530, stop:1 #0F1025);
    border: 1px solid #252648;
    border-radius: 12px;
    padding: 12px;
}

/* ── Metric Strip ── */
QFrame#metricStrip {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #0F1025, stop:1 #131430);
    border: 1px solid #1E2040;
    border-radius: 14px;
}

/* ── Buttons ── */
QPushButton {
    background-color: #1A1C38;
    color: #C8CBFF;
    border: 1px solid #2D3060;
    border-radius: 10px;
    padding: 7px 16px;
    font-size: 9.5pt;
    font-weight: 600;
    min-height: 32px;
}

QPushButton:hover {
    background-color: #252848;
    border-color: #4A4FBB;
    color: #FFFFFF;
}

QPushButton:pressed {
    background-color: #0F1025;
    border-color: #7C6FFF;
    color: #A5B4FF;
}

QPushButton:disabled {
    background-color: #111230;
    color: #2E325A;
    border-color: #1A1C38;
}

/* ── Start Button ── */
QPushButton#btnStart {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #6C5CE7, stop:1 #4FACFE);
    color: #FFFFFF;
    font-weight: 700;
    border: none;
    border-radius: 10px;
    padding: 10px 24px;
    font-size: 10.5pt;
    letter-spacing: 0.3px;
}

QPushButton#btnStart:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #7D70FF, stop:1 #5BBEFF);
}

QPushButton#btnStart:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #5A4BD0, stop:1 #3A90E0);
}

QPushButton#btnStart:disabled {
    background-color: #1A1D38;
    color: #3A3F70;
    border: 1px solid #252648;
}

/* ── Smart Config Buttons ── */
QPushButton#btnSmartConfig {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #5559A0, stop:1 #7B68EE);
    color: #FFFFFF;
    font-weight: 700;
    border: none;
    border-radius: 10px;
    padding: 10px 20px;
    font-size: 10pt;
    letter-spacing: 0.3px;
}

QPushButton#btnSmartConfig:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #6666bb, stop:1 #8B78EE);
}

QPushButton#btnValidate {
    background-color: #1A1D35;
    color: #55AADD;
    font-weight: 600;
    border: 1px solid #334466;
    border-radius: 10px;
    padding: 10px 20px;
    font-size: 10pt;
}

QPushButton#btnValidate:hover {
    background-color: #252845;
    border-color: #55AADD;
    color: #77CCFF;
}

/* ── Stop Button ── */
QPushButton#btnStop {
    background-color: #1A0F18;
    color: #FF6B8A;
    font-weight: 700;
    border: 1px solid #401025;
    border-radius: 10px;
    padding: 10px 20px;
    font-size: 10pt;
}

QPushButton#btnStop:hover {
    background-color: #291018;
    border-color: #FF6B8A;
    color: #FF8FA5;
}

QPushButton#btnStop:disabled {
    background-color: #110810;
    color: #2E1220;
    border-color: #1A0F18;
}

/* ── Save Button ── */
QPushButton#btnSave {
    background-color: #0F1F18;
    color: #3EE8B5;
    font-weight: 600;
    border: 1px solid #1A4030;
    border-radius: 10px;
    padding: 7px 16px;
}

QPushButton#btnSave:hover {
    background-color: #152A22;
    border-color: #3EE8B5;
    color: #5FFFC5;
}

QPushButton#btnSave:disabled {
    background-color: #0A1210;
    color: #1A3028;
    border-color: #0F1A15;
}

/* ── Help / Onboarding Button ── */
QPushButton#btnHelp {
    background-color: transparent;
    color: #4A4F7A;
    border: 1px solid #252648;
    border-radius: 16px;
    font-size: 11pt;
    font-weight: 700;
    min-width: 32px;
    min-height: 32px;
    max-width: 32px;
    max-height: 32px;
    padding: 0;
}

QPushButton#btnHelp:hover {
    background-color: #1A1D35;
    color: #A5B4FF;
    border-color: #4A4FBB;
}

/* ── Theme Toggle Button ── */
QPushButton#btnThemeToggle {
    background-color: transparent;
    color: #7C6FFF;
    border: 1px solid #2D2F60;
    border-radius: 16px;
    font-size: 14pt;
    min-width: 36px;
    min-height: 36px;
    max-width: 36px;
    max-height: 36px;
    padding: 0;
}

QPushButton#btnThemeToggle:hover {
    background-color: #1A1D40;
    border-color: #7C6FFF;
    color: #A5B4FF;
}

/* ── Browse Button ── */
QPushButton#btnBrowse {
    background-color: #1A1C38;
    color: #9BA4FF;
    border: 1px solid #2D3060;
    border-radius: 8px;
    padding: 4px 10px;
    font-size: 12pt;
    min-width: 38px;
    min-height: 32px;
}

QPushButton#btnBrowse:hover {
    background-color: #252848;
    color: #C5CAFF;
    border-color: #4A50BB;
}

/* ── Inputs ── */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: #0E0F22;
    color: #DDE0FF;
    border: 1px solid #252648;
    border-radius: 10px;
    padding: 7px 12px;
    selection-background-color: #4A4FBB;
    min-height: 34px;
    font-size: 9.5pt;
}

QLineEdit:hover, QSpinBox:hover, QDoubleSpinBox:hover, QComboBox:hover {
    border-color: #3D42AA;
    background-color: #111228;
}

QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
    border: 1.5px solid #7C6FFF;
    background-color: #0D0E20;
}

QLineEdit:read-only {
    background-color: #0A0B18;
    color: #5A5F90;
    border-color: #1A1C38;
}

/* ── ComboBox (Windows 11 Inspired) ── */
QComboBox::drop-down {
    border: none;
    width: 34px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 4px solid #8888AA;
    margin-right: 12px;
}

QComboBox:on::down-arrow {
    border-top: none;
    border-bottom: 4px solid #7C6FFF;
}

QComboBox QListView, QComboBox QAbstractItemView {
    background-color: #1E1F35;
    border: 1px solid #353650;
    border-radius: 8px;
    padding: 5px;
    outline: none;
    font-size: 10pt;
    selection-background-color: transparent; /* Handled by item style */
}

QComboBox QListView::item, QComboBox QAbstractItemView::item {
    padding: 8px 12px;
    min-height: 34px;
    border-radius: 5px;
    margin: 2px 4px;
    color: #DDE0FF;
    background-color: transparent;
}

QComboBox QListView::item:selected, QComboBox QAbstractItemView::item:selected {
    background-color: rgba(99, 102, 241, 0.15);
    color: #FFFFFF;
    border: 1px solid rgba(99, 102, 241, 0.3);
}

QComboBox QListView::item:hover, QComboBox QAbstractItemView::item:hover {
    background-color: rgba(255, 255, 255, 0.05);
    color: #FFFFFF;
}

/* ── SpinBox buttons ── */
QSpinBox::up-button, QDoubleSpinBox::up-button,
QSpinBox::down-button, QDoubleSpinBox::down-button {
    background-color: transparent;
    border: none;
    width: 22px;
    border-radius: 5px;
    margin: 2px;
}

QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
    background-color: #252848;
}

/* ── Separators ── */
QFrame[frameShape="4"], QFrame[frameShape="5"] {
    color: #1E2040;
    max-height: 1px;
}

/* ── Progress Bar ── */
QProgressBar {
    background-color: #0E0F22;
    border: 1px solid #1E2040;
    border-radius: 8px;
    text-align: center;
    color: #DDE0FF;
    font-size: 9pt;
    font-weight: 600;
    height: 20px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #6C5CE7, stop:1 #4FACFE);
    border-radius: 7px;
}

/* ── Tab Widget ── */
QTabWidget::pane {
    border: 1px solid #1E2040;
    border-radius: 12px;
    background-color: #0E0F22;
    top: -1px;
}

QTabBar::tab {
    background-color: transparent;
    color: #4A4F7A;
    border: none;
    border-bottom: 2px solid transparent;
    padding: 10px 22px;
    margin-right: 2px;
    font-weight: 600;
    font-size: 10pt;
    min-width: 110px;
}

QTabBar::tab:selected {
    color: #A5B4FF;
    border-bottom: 2px solid #7C6FFF;
}

QTabBar::tab:hover:!selected {
    color: #8890D0;
    background-color: #151630;
    border-radius: 8px;
}

/* ── Sliders ── */
QSlider::groove:horizontal {
    height: 4px;
    background: #1E2040;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    background: #B0B5E8;
    border: 2px solid #3D4080;
    width: 16px;
    height: 16px;
    margin: -6px 0;
    border-radius: 8px;
}

QSlider::handle:horizontal:hover {
    background: #FFFFFF;
    border-color: #7C6FFF;
}

QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #6C5CE7, stop:1 #4FACFE);
    border-radius: 2px;
}

/* ── Text Area / Log ── */
QTextEdit, QPlainTextEdit {
    background-color: #070810;
    color: #3EE8B5;
    border: 1px solid #151630;
    border-radius: 12px;
    font-family: "Cascadia Code", "Consolas", monospace;
    font-size: 9.5pt;
    padding: 12px;
    selection-background-color: #252848;
    selection-color: #F0F0FF;
}

/* ── Scroll Bars ── */
QScrollBar:vertical {
    background: transparent;
    width: 5px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #252648;
    border-radius: 2px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: #3D42AA;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }

QScrollBar:horizontal {
    background: transparent;
    height: 5px;
    margin: 0;
}

QScrollBar::handle:horizontal {
    background: #252648;
    border-radius: 2px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover { background: #3D42AA; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

/* ── Checkbox ── */
QCheckBox {
    color: #C0C4F0;
    spacing: 10px;
    font-size: 9.5pt;
    font-weight: 500;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1.5px solid #2D3070;
    border-radius: 5px;
    background: #0E0F22;
}

QCheckBox::indicator:hover {
    border-color: #5054A0;
    background: #141530;
}

QCheckBox::indicator:checked {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #7C6FFF, stop:1 #4FACFE);
    border-color: #6C5CE7;
}

/* ── ToolTip ── */
QToolTip {
    background-color: #141530;
    color: #DDE0FF;
    border: 1px solid #2D3070;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 9pt;
    opacity: 240;
}

/* ── Status Bar ── */
QStatusBar {
    background-color: #070810;
    color: #3A3F70;
    border-top: 1px solid #151630;
    font-size: 8pt;
    padding: 2px 12px;
}

QStatusBar::item {
    border: none;
}

/* ── Scroll Area ── */
QScrollArea {
    border: none;
    background: transparent;
}

/* ── Horizontal splitter handle ── */
QSplitter::handle {
    background-color: #1E2040;
    width: 1px;
}
"""
