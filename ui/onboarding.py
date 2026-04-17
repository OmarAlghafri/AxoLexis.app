"""
Onboarding Dialog — AxoLexis SHAHAD Trainer
Multi-step welcome guide shown on first launch.
Can be re-opened via the ? help button.
"""

import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFrame, QWidget, QStackedWidget, QGraphicsDropShadowEffect,
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSettings, QSize
from PyQt6.QtGui import QColor, QFont, QIcon, QPixmap


# ── Step data ─────────────────────────────────────────────────────────────────
STEPS = [
    {
        "icon": "",
        "title": "Welcome to AxoLexis",
        "subtitle": "SHAHAD Model Training Studio",
        "body": (
            "AxoLexis is a <b>professional desktop trainer</b> for the SHAHAD AI model — "
            "a powerful, multi-task deep learning architecture.\n\n"
            "Train classification, language models, detection, and segmentation tasks "
            "from a single unified interface — no code required."
        ),
    },
    {
        "icon": "",
        "title": "Step 1: Load Your Data",
        "subtitle": "Flexible data ingestion",
        "body": (
            "Navigate to the <b>Setup &amp; Config</b> tab to select your dataset.\n\n"
            "• <b>Training Data</b> — CSV, NumPy arrays, or image folders\n"
            "• <b>Validation Data</b> — optional holdout set for evaluation\n"
            "• <b>Format</b> — choose Auto-detect or specify manually\n"
            "• <b>Output Dir</b> — where checkpoints will be saved"
        ),
    },
    {
        "icon": "",
        "title": "Step 2: Configure the Model",
        "subtitle": "Hyper-parameter tuning",
        "body": (
            "In the same <b>Setup &amp; Config</b> view, you'll find the Model &amp; Hyper-Parameters section.\n\n"
            "• Choose a <b>Model Tier</b>: nano → base → large → xl\n"
            "• Set <b>Epochs</b>, <b>Batch Size</b>, <b>Learning Rate</b>\n"
            "• Enable <b>LoRA</b> (low-rank adapters) for efficient fine-tuning\n"
            "• Toggle <b>RL / Adversarial / MTL</b> training modes"
        ),
    },
    {
        "icon": "",
        "title": "Step 3: Start Training",
        "subtitle": "Real-time monitoring",
        "body": (
            "Switch to the <b>Training &amp; Status</b> tab and hit <b> Start Training</b>.\n\n"
            "• <b>Training Charts</b> — live loss, accuracy, LR, and grad-norm plots\n"
            "• <b>Live Metrics</b> — check the status bar for device info and current step\n"
            "• <b>Console Log</b> — check the Console Logs tab for detailed events\n"
            "• Use <b> Stop</b> to safely interrupt training at any time"
        ),
    },
    {
        "icon": "",
        "title": "Step 4: Save &amp; Export",
        "subtitle": "Persist your trained model",
        "body": (
            "After training completes, the <b>Save Model…</b> button activates.\n\n"
            "• Export as a <b>.pt / .pth</b> PyTorch checkpoint\n"
            "• Checkpoints auto-save to your configured Output Dir\n"
            "• Re-open a previous training session by reloading the checkpoint\n\n"
            "You can revisit this guide anytime via the <b>?</b> button in the toolbar."
        ),
    },
]


# ── Step Page Widget ───────────────────────────────────────────────────────────
class StepPage(QWidget):
    def __init__(self, data: dict, parent=None):
        super().__init__(parent)
        self._build(data)

    def _build(self, data):
        ly = QVBoxLayout(self)
        ly.setContentsMargins(40, 30, 40, 20)
        ly.setSpacing(0)

        # Icon
        icon_lbl = QLabel(data["icon"])
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet("font-size: 52pt; background: transparent; margin-bottom: 4px;")

        # Title
        title_lbl = QLabel(data["title"])
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_lbl.setWordWrap(True)
        title_lbl.setStyleSheet(
            "font-size: 18pt; font-weight: 800; color: #f1f5f9; "
            "background: transparent; margin-top: 8px;"
        )

        # Subtitle badge
        sub_lbl = QLabel(data["subtitle"])
        sub_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub_lbl.setStyleSheet(
            "font-size: 8pt; font-weight: 700; color: #38bdf8; "
            "background: rgba(14, 165, 233, 0.12); border-radius: 10px; "
            "padding: 4px 14px; letter-spacing: 1.5px; margin-top: 4px;"
        )

        # Divider
        div = QFrame()
        div.setFrameShape(QFrame.Shape.HLine)
        div.setStyleSheet("color: #1e2235; margin: 16px 0;")

        # Body text
        body_lbl = QLabel(data["body"])
        body_lbl.setWordWrap(True)
        body_lbl.setTextFormat(Qt.TextFormat.RichText)
        body_lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        body_lbl.setStyleSheet(
            "font-size: 10pt; color: #94a3b8; line-height: 1.7; "
            "background: transparent;"
        )

        ly.addStretch(1)
        ly.addWidget(icon_lbl)
        ly.addSpacing(6)
        ly.addWidget(title_lbl)
        ly.addSpacing(6)
        ly.addWidget(sub_lbl, 0, Qt.AlignmentFlag.AlignCenter)
        ly.addWidget(div)
        ly.addWidget(body_lbl)
        ly.addStretch(2)


# ── Dot Indicator ─────────────────────────────────────────────────────────────
class DotIndicator(QWidget):
    def __init__(self, count: int, parent=None):
        super().__init__(parent)
        self._count = count
        self._current = 0
        self._dots: list[QLabel] = []
        self._build()

    def _build(self):
        ly = QHBoxLayout(self)
        ly.setContentsMargins(0, 0, 0, 0)
        ly.setSpacing(8)
        ly.addStretch()
        for _ in range(self._count):
            dot = QLabel("●")
            dot.setStyleSheet("font-size: 8pt; color: #1e2235;")
            ly.addWidget(dot)
            self._dots.append(dot)
        ly.addStretch()
        self._refresh()

    def set_current(self, idx: int):
        self._current = idx
        self._refresh()

    def _refresh(self):
        for i, dot in enumerate(self._dots):
            if i == self._current:
                dot.setStyleSheet("font-size: 10pt; color: #38bdf8;")
            else:
                dot.setStyleSheet("font-size: 8pt; color: #1e2235;")


# ── Main Onboarding Dialog ─────────────────────────────────────────────────────
class OnboardingDialog(QDialog):
    SETTINGS_KEY = "onboarding/completed"

    def __init__(self, parent=None, force_show: bool = False):
        super().__init__(parent)
        self._current = 0
        self.setWindowTitle("Welcome to AxoLexis")
        self.setModal(True)
        self.setFixedSize(600, 520)
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._build()
        self._go_to(0)

    @staticmethod
    def should_show() -> bool:
        settings = QSettings("AxoLexis", "Trainer")
        return not settings.value(OnboardingDialog.SETTINGS_KEY, False, type=bool)

    def _mark_completed(self):
        settings = QSettings("AxoLexis", "Trainer")
        settings.setValue(OnboardingDialog.SETTINGS_KEY, True)

    # ── Build UI ──────────────────────────────────────────────────────────────
    def _build(self):
        # Outer layout (for drop shadow)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 20, 20, 20)

        # Container
        self._container = QFrame()
        self._container.setObjectName("onboardContainer")
        self._container.setStyleSheet("""
            QFrame#onboardContainer {
                background-color: #0d0f18;
                border: 1px solid #1e2235;
                border-radius: 20px;
            }
        """)

        # Shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(60)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 200))
        self._container.setGraphicsEffect(shadow)

        container_ly = QVBoxLayout(self._container)
        container_ly.setContentsMargins(0, 0, 0, 0)
        container_ly.setSpacing(0)

        # Accent top bar
        top_bar = QFrame()
        top_bar.setFixedHeight(4)
        top_bar.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #0369a1, stop:0.5 #38bdf8, stop:1 #7c3aed);
            border-radius: 0;
            border-top-left-radius: 20px;
            border-top-right-radius: 20px;
        """)
        container_ly.addWidget(top_bar)

        # ── Stacked pages ──
        self._stack = QStackedWidget()
        for step_data in STEPS:
            self._stack.addWidget(StepPage(step_data))
        container_ly.addWidget(self._stack, 1)

        # ── Dot indicator ──
        self._dots = DotIndicator(len(STEPS))
        container_ly.addWidget(self._dots)

        # ── Footer buttons ──
        footer = QWidget()
        footer.setStyleSheet("background: transparent;")
        foot_ly = QHBoxLayout(footer)
        foot_ly.setContentsMargins(32, 12, 32, 24)
        foot_ly.setSpacing(10)

        self._btn_skip = QPushButton("Skip")
        self._btn_skip.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #475569;
                border: none;
                font-size: 9pt;
                padding: 8px 16px;
            }
            QPushButton:hover { color: #94a3b8; }
        """)
        self._btn_skip.setCursor(Qt.CursorShape.PointingHandCursor)

        self._btn_prev = QPushButton("← Back")
        self._btn_prev.setStyleSheet("""
            QPushButton {
                background-color: #151929;
                color: #94a3b8;
                border: 1px solid #1e2235;
                border-radius: 9px;
                padding: 9px 20px;
                font-size: 9pt;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #1e2538;
                color: #e2e8f0;
            }
        """)
        self._btn_prev.setCursor(Qt.CursorShape.PointingHandCursor)

        self._btn_next = QPushButton("Next →")
        self._btn_next.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0369a1, stop:1 #38bdf8);
                color: #ffffff;
                border: none;
                border-radius: 9px;
                padding: 9px 28px;
                font-size: 9pt;
                font-weight: 700;
                min-width: 110px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0284c7, stop:1 #7dd3fc);
            }
        """)
        self._btn_next.setCursor(Qt.CursorShape.PointingHandCursor)

        foot_ly.addWidget(self._btn_skip)
        foot_ly.addStretch()
        foot_ly.addWidget(self._btn_prev)
        foot_ly.addWidget(self._btn_next)

        container_ly.addWidget(footer)
        outer.addWidget(self._container)

        # ── Connect ──
        self._btn_next.clicked.connect(self._next)
        self._btn_prev.clicked.connect(self._prev)
        self._btn_skip.clicked.connect(self._finish)

    # ── Navigation ────────────────────────────────────────────────────────────
    def _go_to(self, idx: int):
        self._current = idx
        self._stack.setCurrentIndex(idx)
        self._dots.set_current(idx)

        last = idx == len(STEPS) - 1
        first = idx == 0

        self._btn_prev.setVisible(not first)
        self._btn_skip.setText("Skip" if not last else "")
        self._btn_skip.setVisible(not last)
        self._btn_next.setText("Get Started " if last else "Next →")
        self._btn_next.setStyleSheet(self._btn_next.styleSheet())  # force repaint

    def _next(self):
        if self._current < len(STEPS) - 1:
            self._go_to(self._current + 1)
        else:
            self._finish()

    def _prev(self):
        if self._current > 0:
            self._go_to(self._current - 1)

    def _finish(self):
        self._mark_completed()
        self.accept()
