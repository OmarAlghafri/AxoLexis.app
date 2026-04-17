"""
Evaluation Panel — select testing metrics and post-training benchmarks.
Redesigned: dynamic metric filtering based on task, glass card aesthetic.
"""

import os
from PyQt6.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout, QLabel,
    QCheckBox, QFrame, QScrollArea, QWidget, QFormLayout
)
from PyQt6.QtCore import Qt


class EvaluationPanel(QGroupBox):
    def __init__(self):
        super().__init__(" Post-Training Evaluation")
        self.setObjectName("evaluationPanel")
        self._current_task = ""
        self._build()

    def _build(self):
        ly = QVBoxLayout(self)
        ly.setSpacing(24)
        ly.setContentsMargins(24, 32, 24, 24)

        # ── Intro ──
        intro = QLabel("Configure post-training benchmarking and automated reporting.")
        intro.setStyleSheet("color: #94A3B8; font-size: 9pt;")
        ly.addWidget(intro)

        # ── Metrics Card ──
        card = QFrame()
        card.setObjectName("glassPanel")
        card_ly = QVBoxLayout(card)
        card_ly.setSpacing(15)
        
        hdr = QLabel("METRIC SELECTION")
        hdr.setObjectName("fieldLabel")
        card_ly.addWidget(hdr)
        
        self._metrics_ly = QVBoxLayout()
        self._metrics_ly.setSpacing(12)
        
        # Common Metrics
        self._cb_loss = self._add_metric("Final Validation Loss", True)
        self._cb_time = self._add_metric("Inference Latency Benchmark", True)

        # Classification Metrics
        self._cb_acc = self._add_metric("Accuracy (Top-1 / Top-5)", True)
        self._cb_f1 = self._add_metric("F1-Score & Precision/Recall", True)
        self._cb_confusion = self._add_metric("Confusion Matrix Export", False)

        # Detection Metrics
        self._cb_map = self._add_metric("mAP (mean Average Precision)", False)
        self._cb_iou = self._add_metric("IoU (Intersection over Union)", False)

        # Language Metrics
        self._cb_ppl = self._add_metric("Perplexity (PPL)", False)
        self._cb_bleu = self._add_metric("BLEU / ROUGE Score", False)

        # Segmentation Metrics
        self._cb_dice = self._add_metric("Dice Coefficient", False)
        
        card_ly.addLayout(self._metrics_ly)
        ly.addWidget(card)

        # ── Reporting ──
        report_card = QFrame()
        report_card.setObjectName("glassPanel")
        report_ly = QVBoxLayout(report_card)
        report_ly.setSpacing(12)
        
        rep_hdr = QLabel("REPORTING & EXPORT")
        rep_hdr.setObjectName("fieldLabel")
        report_ly.addWidget(rep_hdr)
        
        self._cb_save_json = QCheckBox("Export results to evaluation_report.json")
        self._cb_save_json.setChecked(True)
        self._cb_save_plots = QCheckBox("Save evaluation plots (PDF/PNG)")
        self._cb_save_plots.setChecked(True)
        
        report_ly.addWidget(self._cb_save_json)
        report_ly.addWidget(self._cb_save_plots)
        
        ly.addWidget(report_card)
        ly.addStretch()

    def _add_metric(self, name: str, checked: bool = False) -> QCheckBox:
        cb = QCheckBox(name)
        cb.setChecked(checked)
        cb.setStyleSheet("color: #94A3B8;")
        self._metrics_ly.addWidget(cb)
        return cb

    def _field_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName("fieldLabel")
        return lbl

    def _divider(self) -> QFrame:
        d = QFrame()
        d.setFrameShape(QFrame.Shape.HLine)
        d.setStyleSheet("color: #1E2040; max-height: 1px; margin: 4px 0;")
        return d

    # ── Public API ────────────────────────────────────────────────────────────
    def set_task(self, task: str):
        self._current_task = task.lower()
        
        # Reset visibility
        self._cb_acc.setVisible("classification" in self._current_task)
        self._cb_f1.setVisible("classification" in self._current_task)
        self._cb_confusion.setVisible("classification" in self._current_task)
        
        self._cb_map.setVisible("detection" in self._current_task)
        self._cb_iou.setVisible("detection" in self._current_task)
        
        self._cb_ppl.setVisible("lm" in self._current_task or "language" in self._current_task)
        self._cb_bleu.setVisible("lm" in self._current_task or "language" in self._current_task)
        
        self._cb_dice.setVisible("segmentation" in self._current_task)

        # Update defaults based on task
        if "classification" in self._current_task:
            self._cb_acc.setChecked(True)
            self._cb_f1.setChecked(True)
        elif "detection" in self._current_task:
            self._cb_map.setChecked(True)
            self._cb_iou.setChecked(True)
        elif "lm" in self._current_task:
            self._cb_ppl.setChecked(True)

    def get_config(self) -> dict:
        return {
            "eval_loss": self._cb_loss.isChecked(),
            "eval_latency": self._cb_time.isChecked(),
            "eval_accuracy": self._cb_acc.isChecked(),
            "eval_f1": self._cb_f1.isChecked(),
            "eval_confusion": self._cb_confusion.isChecked(),
            "eval_map": self._cb_map.isChecked(),
            "eval_iou": self._cb_iou.isChecked(),
            "eval_ppl": self._cb_ppl.isChecked(),
            "eval_bleu": self._cb_bleu.isChecked(),
            "eval_dice": self._cb_dice.isChecked(),
            "save_json": self._cb_save_json.isChecked(),
            "save_plots": self._cb_save_plots.isChecked(),
        }
