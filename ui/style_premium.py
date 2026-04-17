"""Premium high-end Dark theme QSS for AxoLexis — exported as PREMIUM_QSS string."""

PREMIUM_QSS = """
/* ═══════════════════════════════════════════════════════════════════════════
   AxoLexis — PREMIUM DARK Theme  |  Design: Cybernetic Glassmorphism
   ═══════════════════════════════════════════════════════════════════════════ */

/* ── Base ── */
QMainWindow, QWidget {
    background-color: #05060A;
    color: #E2E8F0;
    font-family: "Outfit", "Inter", "Segoe UI", sans-serif;
    font-size: 10pt;
}

QLabel {
    background: transparent; /* Explicitly ensure no black background on labels */
}

/* ── Header Bar ── */
QFrame#headerBar {
    background: rgba(13, 14, 26, 0.7);
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

/* ── Stepper Navigation ── */
QFrame#stepperBar {
    background: transparent;
    border-bottom: 1px solid rgba(255, 255, 255, 0.03);
    padding: 10px;
}

QPushButton#stepButton {
    background-color: rgba(255, 255, 255, 0.03);
    color: #475569;
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 20px;
    font-size: 9pt;
    font-weight: 600;
    padding: 8px 24px;
    margin: 0 5px;
}

QPushButton#stepButtonActive {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #6366F1, stop:1 #A855F7);
    color: #FFFFFF;
    border: none;
    border-radius: 20px;
    font-size: 9pt;
    font-weight: 700;
    padding: 8px 24px;
    margin: 0 5px;
}

QPushButton#stepButton:hover:!checked {
    background-color: rgba(255, 255, 255, 0.08);
    color: #94A3B8;
}

/* ── Glass Containers ── */
QGroupBox, QFrame#glassPanel {
    background-color: rgba(15, 17, 26, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 20px;
}

QGroupBox {
    margin-top: 30px;
}

QGroupBox::title {
    subcontrol-origin: border;
    subcontrol-position: top left;
    left: 20px;
    top: -16px;
    padding: 6px 16px;
    color: #818CF8;
    font-size: 9pt;
    font-weight: 800;
    background-color: #05060A;
    border: 1px solid rgba(129, 140, 248, 0.5);
    border-radius: 8px;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    min-height: 28px;
}

/* ── Labels ── */
QLabel#titleLabel {
    font-size: 18pt;
    font-weight: 800;
    color: #F8FAFC;
    letter-spacing: -0.5px;
}

QLabel#subtitleLabel {
    font-size: 8pt;
    color: #818CF8;
    font-weight: 700;
    letter-spacing: 2px;
}

QLabel#fieldLabel {
    font-size: 8.5pt;
    color: #94A3B8;
    font-weight: 700;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    margin-bottom: 4px;
}

QLabel#welcomeHeader {
    font-size: 24pt;
    font-weight: 900;
    color: #FFFFFF;
    background: transparent;
}

QLabel#welcomeSub {
    font-size: 11pt;
    color: #94A3B8;
    line-height: 1.6;
}

/* ── Metric Cards ── */
QFrame#metricCard {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 14px;
    padding: 12px 14px; /* Reduced vertical padding */
}

QLabel#metricValue {
    font-size: 26pt;
    font-weight: 900;
    color: #F8FAFC;
    background: transparent;
    margin: 0;
    padding: 0;
}

QLabel#metricLabel {
    font-size: 7.5pt;
    color: #64748B;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}

/* ── Buttons ── */
QPushButton {
    background-color: rgba(255, 255, 255, 0.05);
    color: #CBD5E1;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 10px 20px;
    font-size: 9.5pt;
    font-weight: 600;
}

QPushButton:hover {
    background-color: rgba(255, 255, 255, 0.08);
    border-color: rgba(255, 255, 255, 0.2);
    color: #FFFFFF;
}

QPushButton#btnPrimary {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #4F46E5, stop:1 #06B6D4);
    color: #FFFFFF;
    border: none;
    font-weight: 700;
}

QPushButton#btnPrimary:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #6366F1, stop:1 #22D3EE);
}

QPushButton#btnSecondary {
    background: rgba(14, 165, 233, 0.1);
    color: #38BDF8;
    border: 1px solid rgba(14, 165, 233, 0.2);
}

QPushButton#btnSecondary:hover {
    background: rgba(14, 165, 233, 0.15);
    border-color: #38BDF8;
}

/* ── Inputs ── */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: rgba(0, 0, 0, 0.2);
    color: #F1F5F9;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 9.5pt;
}

QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
    border: 1px solid #6366F1;
    background-color: rgba(99, 102, 241, 0.05);
}

/* ── Progress ── */
QProgressBar {
    background-color: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 10px;
    text-align: center;
    color: #FFFFFF;
    font-weight: 700;
    height: 12px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #6366F1, stop:1 #EC4899);
    border-radius: 10px;
}

/* ── Scrollbars ── */
QScrollBar:vertical {
    background: transparent;
    width: 6px;
}

QScrollBar::handle:vertical {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 3px;
}

QScrollBar::handle:vertical:hover {
    background: rgba(255, 255, 255, 0.2);
}

/* ── Status Bar ── */
QStatusBar {
    background-color: #05060A;
    border-top: 1px solid rgba(255, 255, 255, 0.03);
    color: #475569;
}

QPushButton#btnStart {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #10B981, stop:1 #059669);
    color: white;
    border: none;
    border-radius: 12px;
    font-weight: 800;
    letter-spacing: 1.2px;
}
QPushButton#btnStart:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #34D399, stop:1 #10B981);
}
QPushButton#btnStart:pressed {
    background: #047857;
}

QPushButton#btnStop {
    background: rgba(239, 68, 68, 0.1);
    color: #EF4444;
    border: 1px solid rgba(239, 68, 68, 0.4);
    border-radius: 12px;
    font-weight: 700;
}
QPushButton#btnStop:hover {
    background: rgba(239, 68, 68, 0.2);
}
QPushButton#btnStop:disabled {
    color: #4B5563;
    border-color: rgba(75, 85, 99, 0.2);
    background: transparent;
}

QPushButton#btnSave {
    background: #1E293B;
    color: #94A3B8;
    border: 1px solid #334155;
    border-radius: 12px;
}
QPushButton#btnSave:hover {
    background: #334155;
    color: white;
}
"""
