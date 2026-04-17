import os
import torch
from datetime import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QFrame, QStackedWidget, 
    QScrollArea, QStatusBar, QDialog, QMessageBox,
    QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon, QPixmap

from ui.style_premium import PREMIUM_QSS
from ui.theme_manager import ThemeManager
from ui.onboarding import OnboardingDialog
from ui.data_panel import DataPanel
from ui.model_panel import ModelPanel
from ui.evaluation_panel import EvaluationPanel
from ui.training_panel import TrainingPanel
from ui.log_panel import LogPanel
from ui.plots_panel import PlotsPanel


# ─────────────────────────────────────────────────────────────────────────────
class HeaderBar(QFrame):
    """Refined Top application header."""

    def __init__(self, icon_path: str, parent=None):
        super().__init__(parent)
        self.setObjectName("headerBar")
        self.setFixedHeight(70)

        ly = QHBoxLayout(self)
        ly.setContentsMargins(30, 0, 30, 0)
        ly.setSpacing(16)

        # ── Logo ──────────────────────────────────────────────────────────────
        logo = QLabel()
        if os.path.exists(icon_path):
            px = QPixmap(icon_path).scaled(
                40, 40,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            logo.setPixmap(px)

        # ── Brand ─────────────────────────────────────────────────────────────
        brand = QVBoxLayout()
        brand.setSpacing(0)
        title = QLabel("AxoLexis")
        title.setObjectName("titleLabel")
        sub = QLabel("SHAHAD TRAINER")
        sub.setObjectName("subtitleLabel")
        brand.addWidget(title)
        brand.addWidget(sub)

        ly.addWidget(logo)
        ly.addLayout(brand)
        ly.addStretch()

        # ── Device pill ───────────────────────────────────────────────────────
        self._device_pill = QLabel("Detecting...")
        self._device_pill.setObjectName("devicePill")
        self._device_pill.setFixedHeight(32)
        self._device_pill.setStyleSheet("""
            background-color: rgba(99, 102, 241, 0.1);
            color: #818CF8;
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 16px;
            padding: 4px 16px;
            font-size: 8.5pt;
            font-weight: 700;
        """)
        ly.addWidget(self._device_pill)

        # ── Theme Toggle ──────────────────────────────────────────────────────
        self.btn_theme = QPushButton()
        self.btn_theme.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_theme.setFixedSize(40, 40)
        self.btn_theme.setStyleSheet("border-radius: 20px; font-size: 14pt; background: transparent;")
        self._update_theme_icon()
        ly.addWidget(self.btn_theme)

    def _update_theme_icon(self):
        tm = ThemeManager()
        icon = "\U0001f31e" if tm.is_dark else "\U0001f319"
        self.btn_theme.setText(icon)

    def set_device(self, text: str):
        self._device_pill.setText(text.upper())


# ─────────────────────────────────────────────────────────────────────────────
class StepperBar(QFrame):
    """Progressive stepper for task flow."""

    sig_step_changed = pyqtSignal(int)

    STEPS = ["WELCOME", "DATASET", "PARAMETERS", "EVALUATION", "TRAINING"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("stepperBar")
        self.setFixedHeight(80)

        ly = QHBoxLayout(self)
        ly.setContentsMargins(0, 0, 0, 0)
        ly.setSpacing(10)
        ly.addStretch()

        self.buttons: list[QPushButton] = []
        for i, name in enumerate(self.STEPS):
            btn = QPushButton(f"{i}. {name}")
            btn.setObjectName("stepButtonActive" if i == 0 else "stepButton")
            btn.setCheckable(True)
            btn.setChecked(i == 0)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, idx=i: self._on_clicked(idx))
            ly.addWidget(btn)
            self.buttons.append(btn)

            if i < len(self.STEPS) - 1:
                arrow = QLabel("→")
                arrow.setStyleSheet("color: #334155; font-size: 12pt; margin: 0 5px;")
                ly.addWidget(arrow)

        ly.addStretch()

    def _on_clicked(self, index: int):
        for i, btn in enumerate(self.buttons):
            active = (i == index)
            btn.setObjectName("stepButtonActive" if active else "stepButton")
            btn.setChecked(active)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        self.sig_step_changed.emit(index)

    def set_active(self, index: int):
        self._on_clicked(index)


# ─────────────────────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AxoLexis — SHAHAD Trainer")
        self.setMinimumSize(1300, 850)
        
        # Apply premium theme
        self.setStyleSheet(PREMIUM_QSS)

        self._icon_path = os.path.join(os.path.dirname(__file__), "resources", "icon.png")
        if os.path.exists(self._icon_path):
            self.setWindowIcon(QIcon(self._icon_path))

        self._build_ui()
        self._connect_signals()
        self._setup_timers()
        self._detect_and_set_hardware()

        if OnboardingDialog.should_show():
            QTimer.singleShot(500, self._show_onboarding)

    def _build_ui(self):
        self.central = QWidget()
        self.setCentralWidget(self.central)
        root_ly = QVBoxLayout(self.central)
        root_ly.setContentsMargins(0, 0, 0, 0)
        root_ly.setSpacing(0)

        # ── Header ────────────────────────────────────────────────────────────
        self._header = HeaderBar(self._icon_path)
        root_ly.addWidget(self._header)

        # ── Stepper ───────────────────────────────────────────────────────────
        self._stepper = StepperBar()
        root_ly.addWidget(self._stepper)

        # ── Stacked Widget ────────────────────────────────────────────────────
        self._stack = QStackedWidget()
        root_ly.addWidget(self._stack, 1)

        # Panels
        self.data_panel = DataPanel()
        self.model_panel = ModelPanel()
        self.evaluation_panel = EvaluationPanel()
        self.training_panel = TrainingPanel()
        self.log_panel = LogPanel()
        self.plots_panel = PlotsPanel()

        self._init_pages()

        self._stepper.sig_step_changed.connect(self._stack.setCurrentIndex)

        # Status Bar
        sb = QStatusBar()
        self._sb_version = QLabel("   AxoLexis v3.1 Premium Edition")
        self._sb_time = QLabel("")
        sb.addWidget(self._sb_version)
        sb.addPermanentWidget(self._sb_time)
        self.setStatusBar(sb)

    def _init_pages(self):
        # Page 0: Welcome
        self._stack.addWidget(self._make_welcome_page())
        # Page 1: Dataset
        self._stack.addWidget(self._make_wizard_page(self.data_panel, "Dataset Setup", "BACK: Welcome", "NEXT: Configuration", 0, 2))
        # Page 2: Model Config
        self._stack.addWidget(self._make_wizard_page(self.model_panel, "Model Parameters", "BACK: Dataset", "NEXT: Evaluation", 1, 3))
        # Page 3: Evaluation
        self._stack.addWidget(self._make_wizard_page(self.evaluation_panel, "Evaluation Settings", "BACK: Parameters", "NEXT: Training Center", 2, 4))
        # Page 4: Training Center
        self._stack.addWidget(self._make_training_page())

    def _make_welcome_page(self) -> QWidget:
        page = QWidget()
        ly = QVBoxLayout(page)
        ly.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ly.setSpacing(30)

        welcome_card = QFrame()
        welcome_card.setObjectName("glassPanel")
        welcome_card.setFixedWidth(700)
        wly = QVBoxLayout(welcome_card)
        wly.setContentsMargins(40, 40, 40, 40)
        wly.setSpacing(20)

        icon_lbl = QLabel("🚀")
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet("font-size: 48pt; background: transparent;")
        
        title = QLabel("Welcome to AxoLexis")
        title.setObjectName("welcomeHeader")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        sub = QLabel("Professional SHAHAD AI training environment redesigned for precision and clarity.")
        sub.setObjectName("welcomeSub")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setWordWrap(True)

        btn_start = QPushButton("START NEW TRAINING PROJECT")
        btn_start.setObjectName("btnPrimary")
        btn_start.setFixedHeight(50)
        btn_start.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_start.clicked.connect(lambda: self._set_page(1))

        wly.addWidget(icon_lbl)
        wly.addWidget(title)
        wly.addWidget(sub)
        wly.addSpacing(20)
        wly.addWidget(btn_start)

        ly.addStretch()
        ly.addWidget(welcome_card)
        ly.addStretch()
        return page

    def _make_wizard_page(self, panel, title, back_text, next_text, back_idx, next_idx) -> QWidget:
        page = QWidget()
        outer_ly = QVBoxLayout(page)
        outer_ly.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        content = QWidget()
        ly = QVBoxLayout(content)
        ly.setContentsMargins(40, 40, 40, 40)
        ly.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        inner = QWidget()
        inner.setFixedWidth(900)
        ily = QVBoxLayout(inner)
        ily.setSpacing(30)

        # Page Title
        lbl_title = QLabel(title.upper())
        lbl_title.setStyleSheet("font-size: 14pt; font-weight: 800; color: #818CF8; letter-spacing: 2px;")
        ily.addWidget(lbl_title)

        ily.addWidget(panel)

        # Nav Buttons
        nav = QHBoxLayout()
        btn_back = QPushButton(back_text)
        btn_back.setMinimumWidth(150)
        btn_back.clicked.connect(lambda: self._set_page(back_idx))
        
        btn_next = QPushButton(next_text)
        btn_next.setObjectName("btnPrimary")
        btn_next.setMinimumWidth(200)
        btn_next.clicked.connect(lambda: self._handle_next(next_idx))

        nav.addWidget(btn_back)
        nav.addStretch()
        nav.addWidget(btn_next)
        ily.addLayout(nav)

        ly.addWidget(inner)
        scroll.setWidget(content)
        outer_ly.addWidget(scroll)
        return page

    def _make_training_page(self) -> QWidget:
        page = QWidget()
        ly = QVBoxLayout(page)
        ly.setContentsMargins(30, 20, 30, 20)
        ly.setSpacing(20)

        # Metrics Row
        metric_strip = self._build_metric_strip()
        ly.addWidget(metric_strip)

        # Main Layout: Controls Left, Plots Right
        mid = QHBoxLayout()
        mid.setSpacing(20)

        self.training_panel.setFixedWidth(400)
        mid.addWidget(self.training_panel)
        mid.addWidget(self.plots_panel, 1)

        ly.addLayout(mid, 1)

        # Log toggle / bottom bar
        footer = QHBoxLayout()
        btn_logs = QPushButton("VIEW SYSTEM LOGS")
        btn_logs.setObjectName("btnSecondary")
        btn_logs.clicked.connect(self._show_logs_dialog)
        
        btn_back = QPushButton("← BACK TO SETUP")
        btn_back.clicked.connect(lambda: self._set_page(3))

        footer.addWidget(btn_back)
        footer.addStretch()
        footer.addWidget(btn_logs)
        ly.addLayout(footer)

        return page

    def _show_logs_dialog(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("System Console Logs")
        dlg.setMinimumSize(900, 600)
        dlg_ly = QVBoxLayout(dlg)
        dlg_ly.addWidget(self.log_panel)
        dlg.exec()

    def _build_metric_strip(self) -> QFrame:
        container = QFrame()
        container.setObjectName("headerBar") # Reuse glass header style
        container.setFixedHeight(120)
        container.setStyleSheet("border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.05);")

        ly = QHBoxLayout(container)
        ly.setContentsMargins(20, 10, 20, 10)
        ly.setSpacing(15)

        metrics = [
            ("STEP", "---", "#94A3B8"),
            ("LOSS", "0.000", "#F87171"),
            ("ACCURACY", "0.0%", "#34D399"),
            ("L-RATE", "0.0e-0", "#60A5FA"),
            ("TIME", "0:00:00", "#A78BFA"),
        ]

        self._metric_labels = {}
        for name, init, color in metrics:
            card = QFrame()
            card.setObjectName("metricCard")
            cly = QVBoxLayout(card)
            cly.setContentsMargins(12, 12, 12, 12)
            
            lbl_name = QLabel(name)
            lbl_name.setObjectName("metricLabel")
            
            lbl_val = QLabel(init)
            lbl_val.setObjectName("metricValue")
            lbl_val.setStyleSheet(f"color: {color};")
            
            cly.addWidget(lbl_name)
            cly.addWidget(lbl_val)
            ly.addWidget(card, 1)
            self._metric_labels[name.lower()] = lbl_val

        return container

    def _set_page(self, index: int):
        self._stack.setCurrentIndex(index)
        self._stepper.set_active(index)

    def _handle_next(self, idx):
        # Validation logic
        if idx == 2: # Dataset -> Model
            valid, msg = self.data_panel.validate_config()
            if not valid:
                QMessageBox.warning(self, "Dataset Error", msg)
                return
        elif idx == 4: # Evaluation -> Training
            valid, msg = self.model_panel.validate_config(self.data_panel.train_path, self.data_panel.data_format)
            if not valid:
                QMessageBox.warning(self, "Model Error", msg)
                return
        
        self._set_page(idx)

    def _connect_signals(self):
        tp = self.training_panel
        tp.set_data_panel(self.data_panel)
        tp.set_model_panel(self.model_panel)
        tp.set_evaluation_panel(self.evaluation_panel)
        self.model_panel.set_data_panel(self.data_panel)

        tp.sig_step.connect(self._on_step_metrics)
        tp.sig_step.connect(self.plots_panel.on_step)
        tp.sig_started.connect(self._on_train_started)
        tp.sig_finished.connect(self._on_train_finished)
        tp.sig_log.connect(self.log_panel.append_log)

        self._header.btn_theme.clicked.connect(self._toggle_theme)

        # Wiring logic between panels
        self.data_panel.sig_format_changed.connect(self.model_panel.set_data_format)
        self.model_panel.sig_task_changed.connect(self.evaluation_panel.set_task)
        self.model_panel.sig_task_changed.connect(self.data_panel.set_task)

    def _toggle_theme(self):
        ThemeManager().toggle(QApplication.instance())
        self._header._update_theme_icon()

    def _detect_and_set_hardware(self):
        device = "CPU"
        if torch.cuda.is_available():
            device = torch.cuda.get_device_name(0)
        self._header.set_device(device)

    def _setup_timers(self):
        self._clock = QTimer(self)
        self._clock.timeout.connect(lambda: self._sb_time.setText(datetime.now().strftime("%H:%M:%S")))
        self._clock.start(1000)

    def _on_train_started(self):
        self._set_page(4)
        self.plots_panel.reset()

    def _on_train_finished(self, msg):
        QMessageBox.information(self, "Training Complete", msg)

    def _on_step_metrics(self, info: dict):
        if "step" in info: self._metric_labels["step"].setText(str(info["step"]))
        if "loss/total" in info: self._metric_labels["loss"].setText(f"{info['loss/total']:.4f}")
        if "val/accuracy" in info: self._metric_labels["accuracy"].setText(f"{info['val/accuracy']*100:.1f}%")
        if "lr" in info: self._metric_labels["l-rate"].setText(f"{info['lr']:.1e}")

    def _show_onboarding(self):
        dlg = OnboardingDialog(self)
        dlg.exec()
