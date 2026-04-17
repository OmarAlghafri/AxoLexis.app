"""
Training Panel — start/stop controls, phase selector, progress bar, save model.
Redesigned: gradient Start button, better spacing, cleaner layout.
"""

import os
from PyQt6.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QProgressBar, QComboBox, QFileDialog, QFrame,
    QMessageBox,
)
from PyQt6.QtCore import Qt, pyqtSignal

from training.trainer_thread import TrainerThread
from ui.model_panel import ConfigValidationDialog


class TrainingPanel(QGroupBox):
    # Signals forwarded to MainWindow
    sig_step     = pyqtSignal(dict)
    sig_log      = pyqtSignal(str, str)
    sig_started  = pyqtSignal()
    sig_finished = pyqtSignal(str)
    sig_device   = pyqtSignal(str)
    sig_step_num = pyqtSignal(int)

    def __init__(self):
        super().__init__(" Training Controls")
        self._data_panel  = None
        self._model_panel = None
        self._evaluation_panel = None
        self._thread: TrainerThread | None = None
        self._build()

    def set_data_panel(self, p):  self._data_panel = p
    def set_model_panel(self, p): self._model_panel = p
    def set_evaluation_panel(self, p): self._evaluation_panel = p

    # ──────────────────────────────────────────────────────────────────────────
    def _build(self):
        ly = QVBoxLayout(self)
        ly.setSpacing(25)
        ly.setContentsMargins(24, 32, 24, 24)

        prog_card = QFrame()
        prog_card.setObjectName("glassPanel")
        prog_ly = QVBoxLayout(prog_card)
        prog_ly.setSpacing(15)
        
        prog_hdr = QLabel("LIVE PROGRESS")
        prog_hdr.setObjectName("fieldLabel")
        prog_ly.addWidget(prog_hdr)
        
        self._progress = QProgressBar()
        self._progress.setFixedHeight(12)
        self._progress.setRange(0, 100); self._progress.setValue(0)
        self._progress.setTextVisible(False)
        prog_ly.addWidget(self._progress)
        
        self._status_lbl = QLabel("Ready to start training.")
        self._status_lbl.setStyleSheet("color: #94A3B8; font-size: 9pt;")
        prog_ly.addWidget(self._status_lbl)
        
        ly.addWidget(prog_card)

        # ── Action Grid ──
        ctrl_ly = QHBoxLayout()
        ctrl_ly.setSpacing(12)
        
        self._btn_start = QPushButton("START PIPELINE")
        self._btn_start.setObjectName("btnStart")
        self._btn_start.setFixedHeight(50)
        self._btn_start.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self._btn_stop = QPushButton("HALT")
        self._btn_stop.setObjectName("btnStop")
        self._btn_stop.setFixedWidth(100)
        self._btn_stop.setFixedHeight(50)
        self._btn_stop.setEnabled(False)
        self._btn_stop.setCursor(Qt.CursorShape.PointingHandCursor)
        
        ctrl_ly.addWidget(self._btn_stop)
        ctrl_ly.addWidget(self._btn_start, 1)
        ly.addLayout(ctrl_ly)

        self._btn_save = QPushButton("SAVE MODEL CHECKPOINT")
        self._btn_save.setObjectName("btnSave")
        self._btn_save.setFixedHeight(45)
        self._btn_save.setEnabled(False)
        self._btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        ly.addWidget(self._btn_save)

        ly.addStretch()

        # ── Connect ───────────────────────────────────────────────────────────
        self._btn_start.clicked.connect(self._start)
        self._btn_stop.clicked.connect(self._stop)
        self._btn_save.clicked.connect(self._save_model)

    def _lbl(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName("fieldLabel")
        return lbl

    def _divider(self) -> QFrame:
        d = QFrame()
        d.setFrameShape(QFrame.Shape.HLine)
        d.setStyleSheet("color: #1E2040; max-height: 1px; margin: 2px 0;")
        return d

    # ──────────────────────────────────────────────────────────────────────────
    def _start(self):
        if self._thread and self._thread.isRunning():
            return

        # 1) Basic compatibility validation
        if self._model_panel:
            train_path = self._data_panel.train_path if self._data_panel else ""
            data_format = self._data_panel.data_format if self._data_panel else "Synthetic (demo)"
            is_valid, msg = self._model_panel.validate_config(train_path, data_format)
            if not is_valid:
                QMessageBox.warning(self, "Invalid Configuration", msg)
                return

        # 2) SHADA-aware configuration validation (automatic before training)
        if self._model_panel:
            from models.config_validator import validate_config
            
            cfg = self._model_panel.get_config()
            dataset_info = self._model_panel._get_dataset_info(train_path, data_format)
            hardware_info = {
                "device": "cuda",
                "vram_gb": self._model_panel._vram_gb,
                "gpu_name": "",
            }
            
            alerts = validate_config(cfg, dataset_info, hardware_info)

            # Check for critical issues
            critical = [a for a in alerts if a["level"] == "CRITICAL"]
            if critical:
                warnings = [a for a in alerts if a["level"] == "WARNING"]
                infos = [a for a in alerts if a["level"] == "INFO"]

                dialog = ConfigValidationDialog(self, model_panel=self._model_panel)
                dialog.show_results(critical, warnings, infos)

                # Block training on critical issues
                QMessageBox.critical(
                    self,
                    "Training Blocked",
                    f"Training cannot start due to {len(critical)} critical configuration issue(s).\n\n"
                    "Please fix the issues shown in the validation dialog and try again."
                )
                return

            # Show warnings but allow user to proceed
            warnings = [a for a in alerts if a["level"] == "WARNING"]
            if warnings:
                infos = [a for a in alerts if a["level"] == "INFO"]

                dialog = ConfigValidationDialog(self, model_panel=self._model_panel)
                dialog.show_results(critical, warnings, infos)
                
                # Ask user if they want to proceed
                proceed = QMessageBox.question(
                    self,
                    "Configuration Warnings",
                    f"Found {len(warnings)} warning(s) in your configuration.\n\n"
                    "Do you want to proceed with training anyway?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if proceed != QMessageBox.StandardButton.Yes:
                    return

        # 3) Start training
        cfg = self._model_panel.get_config() if self._model_panel else {}
        cfg["output_dir"]  = self._data_panel.output_dir  if self._data_panel else "./shahad_output"
        cfg["train_path"]  = self._data_panel.train_path  if self._data_panel else ""
        cfg["val_path"]    = self._data_panel.val_path    if self._data_panel else ""
        cfg["data_format"] = self._data_panel.data_format if self._data_panel else "Synthetic (demo)"
        cfg["phase"]       = cfg.get("phase", "full_pipeline")

        # Collection evaluation configuration
        if self._evaluation_panel:
            cfg["eval_config"] = self._evaluation_panel.get_config()

        self._thread = TrainerThread(cfg)
        self._thread.sig_step.connect(self._on_step)
        self._thread.sig_log.connect(self.sig_log)
        self._thread.sig_finished.connect(self._on_finished)
        self._thread.sig_device.connect(self.sig_device)
        self._thread.sig_progress.connect(self._on_progress)
        self._thread.sig_config_alerts.connect(self._on_config_alerts)

        self._thread.start()
        self._btn_start.setEnabled(False)
        self._btn_stop.setEnabled(True)
        self._btn_save.setEnabled(False)
        self._progress.setFormat("Training...  %p%")
        self.sig_started.emit()

    def _on_config_alerts(self, alerts: list):
        """Handle configuration alerts emitted from trainer thread."""
        # Alerts are already shown in trainer thread, but we can log them
        for alert in alerts:
            if alert["level"] == "WARNING":
                self.sig_log.emit(f"[CONFIG WARNING] {alert['parameter']}: {alert['message']}", "warn")
            elif alert["level"] == "INFO":
                self.sig_log.emit(f"[CONFIG INFO] {alert['parameter']}: {alert['message']}", "info")

    def _stop(self):
        if self._thread:
            self._thread.request_stop()
            self.sig_log.emit("[WARN] Stop requested — finishing current step...", "warn")

    def _on_progress(self, value: int):
        self._progress.setValue(value)

    def _on_step(self, info: dict):
        self.sig_step.emit(info)
        self.sig_step_num.emit(info.get("step", 0))

    def _on_finished(self, msg: str):
        self._btn_start.setEnabled(True)
        self._btn_stop.setEnabled(False)
        self._btn_save.setEnabled(True)
        self._progress.setValue(100)
        self._progress.setFormat("  Complete")
        self.sig_finished.emit(msg)

    def _save_model(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Model Checkpoint", "./model.pt",
            "PyTorch checkpoint (*.pt *.pth);;All files (*)",
        )
        if path and self._thread:
            self._thread.save_checkpoint(path)
            self.sig_log.emit(f"[INFO] Model saved -> {path}", "success")
