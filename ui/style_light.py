"""Light theme QSS for AxoLexis — exported as LIGHT_QSS string."""

LIGHT_QSS = """
/* ═══════════════════════════════════════════════════════════════════════════
   AxoLexis — LIGHT Theme  |  Design: Crisp Violet + Soft White
   ═══════════════════════════════════════════════════════════════════════════ */

/* ── Base ── */
QMainWindow, QWidget {
    background-color: #F0F1FF;
    color: #1A1B35;
    font-family: "Inter", "Segoe UI", system-ui, sans-serif;
    font-size: 10pt;
}

QDialog {
    background-color: #F5F6FF;
    color: #1A1B35;
}

/* ── Header Bar ── */
QFrame#headerBar {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #FFFFFF, stop:1 #F5F6FF);
    border-bottom: 1px solid #DDE0FF;
}

/* ── Navigation Bar ── */
QFrame#navBar {
    background-color: #FFFFFF;
    border-bottom: 1px solid #E8EAFF;
}

QPushButton#navButton {
    background-color: transparent;
    color: #8B8FBE;
    border: none;
    border-radius: 8px;
    font-size: 10pt;
    font-weight: 600;
    padding: 8px 22px;
    letter-spacing: 0.5px;
}

QPushButton#navButton:hover {
    background-color: #EEEEFF;
    color: #5A5FBE;
}

QPushButton#navButtonActive {
    background-color: #EBEBFF;
    color: #5550D0;
    border: 1px solid #BBBEFF;
    border-radius: 10px;
    font-size: 10pt;
    font-weight: 700;
    padding: 8px 22px;
    letter-spacing: 0.5px;
}

/* ── General Labels ── */
QLabel {
    color: #5B5F8E;
    font-size: 9.5pt;
    background: transparent;
}

QLabel#titleLabel {
    font-size: 17pt;
    font-weight: 700;
    color: #1A1B35;
    letter-spacing: 0.3px;
}

QLabel#subtitleLabel {
    font-size: 8.5pt;
    color: #6C5CE7;
    font-weight: 600;
    letter-spacing: 1.5px;
}

QLabel#sectionLabel {
    font-size: 8pt;
    color: #9BA0D0;
    font-weight: 700;
    letter-spacing: 1.8px;
}

QLabel#metricValue {
    font-size: 22pt;
    font-weight: 800;
    color: #1A1B35;
    background: transparent;
}

QLabel#metricLabel {
    font-size: 7.5pt;
    color: #9BA0D0;
    font-weight: 600;
    letter-spacing: 1px;
    background: transparent;
}

QLabel#fieldLabel, QLabel#formRowLabel {
    font-size: 9.5pt;
    color: #2E3060;
    font-weight: 600;
    background: transparent;
    min-width: 130px;
}

/* ── Cards / Group Boxes ── */
QGroupBox {
    background-color: #FFFFFF;
    border: 1px solid #DDE0FF;
    border-radius: 14px;
    margin-top: 20px;
    padding: 18px 14px 14px 14px;
    color: #1A1B35;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 14px;
    top: -11px;
    padding: 3px 10px;
    color: #7C80C0;
    font-size: 9pt;
    font-weight: 600;
    background-color: #F5F6FF;
    border: 1px solid #DDE0FF;
    border-radius: 6px;
    letter-spacing: 0.5px;
}

/* ── Metric Cards ── */
QFrame#metricCard {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #FFFFFF, stop:1 #F5F6FF);
    border: 1px solid #DDE0FF;
    border-radius: 12px;
    padding: 12px;
}

/* ── Metric Strip ── */
QFrame#metricStrip {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #FFFFFF, stop:1 #F5F6FF);
    border: 1px solid #E0E2FF;
    border-radius: 14px;
}

/* ── Buttons ── */
QPushButton {
    background-color: #F0F1FF;
    color: #4550BB;
    border: 1px solid #C8CBFF;
    border-radius: 10px;
    padding: 7px 16px;
    font-size: 9.5pt;
    font-weight: 600;
    min-height: 32px;
}

QPushButton:hover {
    background-color: #E8EAFF;
    border-color: #9BA0E0;
    color: #2E36A0;
}

QPushButton:pressed {
    background-color: #DDDEFF;
    border-color: #6C5CE7;
    color: #5550D0;
}

QPushButton:disabled {
    background-color: #F5F5F5;
    color: #C0C4D0;
    border-color: #E5E8EE;
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
    background-color: #E5E8F0;
    color: #A0A8C0;
    border: 1px solid #DDE0EE;
}

/* ── Smart Config Buttons ── */
QPushButton#btnSmartConfig {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #6C5CE7, stop:1 #7B68EE);
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
        stop:0 #7D70FF, stop:1 #8B78EE);
}

QPushButton#btnValidate {
    background-color: #F0F4FF;
    color: #4F6B9A;
    font-weight: 600;
    border: 1px solid #C0D0E8;
    border-radius: 10px;
    padding: 10px 20px;
    font-size: 10pt;
}

QPushButton#btnValidate:hover {
    background-color: #E0E8FF;
    border-color: #4F6B9A;
    color: #3F5B8A;
}

/* ── Stop Button ── */
QPushButton#btnStop {
    background-color: #FFF0F3;
    color: #D63050;
    font-weight: 700;
    border: 1px solid #FFD0DA;
    border-radius: 10px;
    padding: 10px 20px;
    font-size: 10pt;
}

QPushButton#btnStop:hover {
    background-color: #FFE0E8;
    border-color: #D63050;
    color: #B02040;
}

QPushButton#btnStop:disabled {
    background-color: #FFF5F7;
    color: #DDB0BA;
    border-color: #FFE8EE;
}

/* ── Save Button ── */
QPushButton#btnSave {
    background-color: #F0FFF8;
    color: #00B894;
    font-weight: 600;
    border: 1px solid #B0EED8;
    border-radius: 10px;
    padding: 7px 16px;
}

QPushButton#btnSave:hover {
    background-color: #E0FFF2;
    border-color: #00B894;
    color: #009870;
}

QPushButton#btnSave:disabled {
    background-color: #F5F5F5;
    color: #B0C0BA;
    border-color: #E0EDE8;
}

/* ── Help / Onboarding Button ── */
QPushButton#btnHelp {
    background-color: transparent;
    color: #8B8FBE;
    border: 1px solid #C8CBFF;
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
    background-color: #EEEEFF;
    color: #5550D0;
    border-color: #9BA0E0;
}

/* ── Theme Toggle Button ── */
QPushButton#btnThemeToggle {
    background-color: transparent;
    color: #6C5CE7;
    border: 1px solid #C8CBFF;
    border-radius: 16px;
    font-size: 14pt;
    min-width: 36px;
    min-height: 36px;
    max-width: 36px;
    max-height: 36px;
    padding: 0;
}

QPushButton#btnThemeToggle:hover {
    background-color: #EEEEFF;
    border-color: #6C5CE7;
    color: #5550D0;
}

/* ── Browse Button ── */
QPushButton#btnBrowse {
    background-color: #F0F1FF;
    color: #6C5CE7;
    border: 1px solid #C8CBFF;
    border-radius: 8px;
    padding: 4px 10px;
    font-size: 12pt;
    min-width: 38px;
    min-height: 32px;
}

QPushButton#btnBrowse:hover {
    background-color: #E8EAFF;
    color: #5550D0;
    border-color: #9BA0E0;
}

/* ── Inputs ── */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: #FFFFFF;
    color: #2A2B50;
    border: 1px solid #C8CBFF;
    border-radius: 10px;
    padding: 7px 12px;
    selection-background-color: #C0C4FF;
    min-height: 34px;
    font-size: 9.5pt;
}

QLineEdit:hover, QSpinBox:hover, QDoubleSpinBox:hover, QComboBox:hover {
    border-color: #9BA0E0;
    background-color: #FAFAFF;
}

QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
    border: 1.5px solid #6C5CE7;
    background-color: #FFFFFF;
}

QLineEdit:read-only {
    background-color: #F5F6FF;
    color: #9BA0D0;
    border-color: #E0E2FF;
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
    border-top: 4px solid #8B8FBE;
    margin-right: 12px;
}

QComboBox:on::down-arrow {
    border-top: none;
    border-bottom: 4px solid #6C5CE7;
}

QComboBox QListView, QComboBox QAbstractItemView {
    background-color: #FFFFFF;
    border: 1px solid #D0D4E0;
    border-radius: 8px;
    padding: 5px;
    outline: none;
    font-size: 10pt;
    selection-background-color: transparent;
}

QComboBox QListView::item, QComboBox QAbstractItemView::item {
    padding: 8px 12px;
    min-height: 34px;
    border-radius: 5px;
    margin: 2px 4px;
    color: #4A4F80;
    background-color: transparent;
}

QComboBox QListView::item:selected, QComboBox QAbstractItemView::item:selected {
    background-color: #F0F2FF;
    color: #3530B0;
    border: 1px solid #DDE0FF;
}

QComboBox QListView::item:hover, QComboBox QAbstractItemView::item:hover {
    background-color: #F8F9FF;
    color: #2A2B50;
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
    background-color: #E8EAFF;
}

/* ── Separators ── */
QFrame[frameShape="4"], QFrame[frameShape="5"] {
    color: #DDE0FF;
    max-height: 1px;
}

/* ── Progress Bar ── */
QProgressBar {
    background-color: #EDF0FF;
    border: 1px solid #DDE0FF;
    border-radius: 8px;
    text-align: center;
    color: #4550BB;
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
    border: 1px solid #DDE0FF;
    border-radius: 12px;
    background-color: #FAFAFF;
    top: -1px;
}

QTabBar::tab {
    background-color: transparent;
    color: #9BA0D0;
    border: none;
    border-bottom: 2px solid transparent;
    padding: 10px 22px;
    margin-right: 2px;
    font-weight: 600;
    font-size: 10pt;
    min-width: 110px;
}

QTabBar::tab:selected {
    color: #5550D0;
    border-bottom: 2px solid #6C5CE7;
}

QTabBar::tab:hover:!selected {
    color: #7070C0;
    background-color: #F0F1FF;
    border-radius: 8px;
}

/* ── Sliders ── */
QSlider::groove:horizontal {
    height: 4px;
    background: #DDE0FF;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    background: #8B8FBE;
    border: 2px solid #C0C4FF;
    width: 16px;
    height: 16px;
    margin: -6px 0;
    border-radius: 8px;
}

QSlider::handle:horizontal:hover {
    background: #6C5CE7;
    border-color: #A0A5F0;
}

QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #6C5CE7, stop:1 #4FACFE);
    border-radius: 2px;
}

/* ── Text Area / Log ── */
QTextEdit, QPlainTextEdit {
    background-color: #0A0B12;
    color: #3EE8B5;
    border: 1px solid #1E2040;
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
    background: #C8CBFF;
    border-radius: 2px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: #9BA0E0;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }

QScrollBar:horizontal {
    background: transparent;
    height: 5px;
    margin: 0;
}

QScrollBar::handle:horizontal {
    background: #C8CBFF;
    border-radius: 2px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover { background: #9BA0E0; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

/* ── Checkbox ── */
QCheckBox {
    color: #3A3F70;
    spacing: 10px;
    font-size: 9.5pt;
    font-weight: 500;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1.5px solid #C0C4FF;
    border-radius: 5px;
    background: #FFFFFF;
}

QCheckBox::indicator:hover {
    border-color: #8B90D0;
    background: #F5F6FF;
}

QCheckBox::indicator:checked {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #6C5CE7, stop:1 #4FACFE);
    border-color: #6C5CE7;
}

/* ── ToolTip ── */
QToolTip {
    background-color: #FFFFFF;
    color: #2A2B50;
    border: 1px solid #C8CBFF;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 9pt;
    opacity: 240;
}

/* ── Status Bar ── */
QStatusBar {
    background-color: #F5F6FF;
    color: #9BA0D0;
    border-top: 1px solid #E0E2FF;
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

/* ── Splitter ── */
QSplitter::handle {
    background-color: #DDE0FF;
    width: 1px;
}
"""
