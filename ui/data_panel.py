"""
Data Panel — file selection for CSV, Images, NPY datasets.
Redesigned: improved card layout, browse icons, better UX.
"""

import os
from PyQt6.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QFileDialog, QComboBox, QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal


class DataPanel(QGroupBox):
    sig_format_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__(" Dataset Configuration")
        self.setObjectName("dataPanel")
        self._build()
        self._fmt.currentTextChanged.connect(self.sig_format_changed.emit)

    def _build(self):
        ly = QVBoxLayout(self)
        ly.setSpacing(24)
        ly.setContentsMargins(24, 32, 24, 24)

        # ── Introduction ──
        intro = QLabel("Select the resources for your training pipeline.")
        intro.setStyleSheet("color: #94A3B8; font-size: 9pt; margin-bottom: 10px;")
        ly.addWidget(intro)

        # ── Training Data ──
        self._train_path = QLineEdit()
        ly.addLayout(self._create_field_section(
            "Training Dataset",
            "Select your primary dataset file or folder.",
            self._train_path,
            "Select file or folder (CSV, Images, NumPy)...",
            lambda: self._browse(self._train_path),
            is_file=True
        ))

        # ── Validation Data ──
        self._val_path = QLineEdit()
        ly.addLayout(self._create_field_section(
            "Validation Dataset (Optional)",
            "A separate set to evaluate accuracy during training.",
            self._val_path,
            "Optional holdout set...",
            lambda: self._browse(self._val_path),
            is_file=True
        ))

        # ── Format ──
        fmt_ly = QVBoxLayout()
        fmt_ly.setSpacing(8)
        fmt_title = QLabel("DATA FORMAT")
        fmt_title.setObjectName("fieldLabel")
        fmt_desc = QLabel("How should the files be parsed?")
        fmt_desc.setStyleSheet("color: #64748B; font-size: 8pt;")
        
        from PyQt6.QtWidgets import QListView
        self._fmt = QComboBox()
        self._fmt.setView(QListView())
        self._fmt.setFixedHeight(45)
        
        fmt_ly.addWidget(fmt_title)
        fmt_ly.addWidget(fmt_desc)
        fmt_ly.addWidget(self._fmt)
        ly.addLayout(fmt_ly)

        # ── Output ──
        self._out_path = QLineEdit("./shahad_output")
        ly.addLayout(self._create_field_section(
            "Export Directory",
            "Where to save checkpoints and training logs.",
            self._out_path,
            "Target folder...",
            lambda: self._browse_dir(self._out_path),
            is_file=False
        ))

        ly.addStretch()

    def _create_field_section(self, title, desc, edit, placeholder, callback, is_file=True):
        layout = QVBoxLayout()
        layout.setSpacing(8)
        
        lbl = QLabel(title.upper())
        lbl.setObjectName("fieldLabel")
        
        sub = QLabel(desc)
        sub.setStyleSheet("color: #64748B; font-size: 8pt;")
        
        row = QHBoxLayout()
        row.setSpacing(10)
        edit.setPlaceholderText(placeholder)
        edit.setFixedHeight(45)
        
        btn = QPushButton("📁" if is_file else "📂")
        btn.setObjectName("btnBrowse")
        btn.setFixedSize(45, 45)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(callback)
        
        row.addWidget(edit, 1)
        row.addWidget(btn)
        
        layout.addWidget(lbl)
        layout.addWidget(sub)
        layout.addLayout(row)
        return layout

    def _browse(self, target: QLineEdit):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Data File", "",
            "Standard Formats (*.csv *.json *.jsonl *.parquet *.npy *.npz *.png *.jpg *.jpeg *.txt);;"
            "Tabular (*.csv *.parquet);;"
            "JSON (*.json *.jsonl);;"
            "NumPy (*.npy *.npz);;"
            "Images (*.png *.jpg *.jpeg);;"
            "All files (*)",
        )
        if path:
            target.setText(path)

    def _browse_dir(self, target: QLineEdit):
        path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if path:
            target.setText(path)

    def validate_config(self) -> tuple[bool, str]:
        """Validate data configuration for path presence and basic format."""
        issues = []
        fmt = self.data_format
        train_path = self.train_path
        
        if not train_path and "synthetic" not in fmt.lower():
            issues.append("Please select a training dataset or use Synthetic (demo) format.")
        
        if train_path and not os.path.exists(train_path):
            issues.append(f"The selected path does not exist:\n{train_path}")

        if issues:
            return False, "Data Configuration Issues:\n• " + "\n• ".join(issues)
        return True, ""

    # ── Public API ────────────────────────────────────────────────────────────
    @property
    def train_path(self) -> str:
        return self._train_path.text().strip()

    @property
    def val_path(self) -> str:
        return self._val_path.text().strip()

    @property
    def data_format(self) -> str:
        return self._fmt.currentText()

    @property
    def output_dir(self) -> str:
        return self._out_path.text().strip() or "./shahad_output"

    def set_task(self, task: str):
        """Filter available data formats based on task."""
        self._current_task = task
        self._fmt.blockSignals(True)
        prev_text = self._fmt.currentText()
        self._fmt.clear()
        
        # Categorized formats
        cv_formats = ["Images (Folder)", "Images (CSV/Manifest)", "NumPy (.npy / .npz)"]
        nlp_formats = ["CSV (Text / Labels)", "JSON / JSONL", "Parquet (.parquet)", "Text Files (.txt folder)"]
        special_formats = ["COCO JSON (Detection)", "Medical (DICOM/NIfTI)"]
        demo_formats = ["Synthetic (demo)"]
        
        allowed = demo_formats.copy()
        
        if "Classification" in task:
            # Classification can be CV or NLP
            allowed += cv_formats + nlp_formats
        elif "Language Modeling" in task:
            # Language modeling is mostly NLP
            allowed += nlp_formats
        elif "Object Detection" in task:
            allowed += ["Images (Folder)", "COCO JSON (Detection)", "NumPy (.npy / .npz)"]
        elif "Image Segmentation" in task:
            allowed += ["Images (Folder)", "Medical (DICOM/NIfTI)", "NumPy (.npy / .npz)"]
            
        self._fmt.addItems(allowed)
        
        # Try to restore previous selection
        idx = self._fmt.findText(prev_text)
        if idx >= 0:
            self._fmt.setCurrentIndex(idx)
        else:
            self._fmt.setCurrentIndex(0)
            
        self._fmt.blockSignals(False)
