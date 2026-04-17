"""
Log Panel — coloured console output for training events.
Redesigned: terminal-style container, color-coded level badges, improved toolbar.
"""

from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QPlainTextEdit, QLabel, QFileDialog, QFrame,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextCharFormat, QColor, QTextCursor, QFont


LEVEL_COLORS = {
    "info":    "#94A3D0",
    "success": "#3EE8B5",
    "warn":    "#FFCB6B",
    "error":   "#FF6B8A",
    "debug":   "#4A4F7A",
}

LEVEL_TAGS = {
    "info":    "INFO",
    "success": "DONE",
    "warn":    "WARN",
    "error":   "ERR!",
    "debug":   "DBG",
}


class LogPanel(QWidget):
    def __init__(self):
        super().__init__()
        self._entries: list[tuple[str, str]] = []
        self._build()

    def _build(self):
        ly = QVBoxLayout(self)
        ly.setContentsMargins(0, 0, 0, 0)
        ly.setSpacing(10)

        # ── Toolbar ──────────────────────────────────────────────────────────
        toolbar = QFrame()
        toolbar.setStyleSheet(
            "background: transparent; border: none;"
        )
        tb_ly = QHBoxLayout(toolbar)
        tb_ly.setContentsMargins(4, 0, 4, 0)
        tb_ly.setSpacing(8)

        title_lbl = QLabel("  Console Log")
        title_lbl.setObjectName("fieldLabel")

        tb_ly.addWidget(title_lbl)
        tb_ly.addStretch()

        self._count_lbl = QLabel("0 lines")
        self._count_lbl.setStyleSheet("color: #3A3F70; font-size: 8pt; background: transparent;")
        tb_ly.addWidget(self._count_lbl)

        btn_export = QPushButton("  Export")
        btn_export.setMinimumWidth(80)
        btn_export.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_export.setToolTip("Save console log to a .txt file.")
        btn_export.clicked.connect(self._export_log)

        btn_clear = QPushButton("Clear")
        btn_clear.setMinimumWidth(66)
        btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_clear.setToolTip("Clear all console output.")
        btn_clear.clicked.connect(self._clear)

        tb_ly.addWidget(btn_export)
        tb_ly.addWidget(btn_clear)
        ly.addWidget(toolbar)

        # ── Log area ─────────────────────────────────────────────────────────
        self._log = QPlainTextEdit()
        self._log.setReadOnly(True)
        self._log.setMaximumBlockCount(5000)
        font = QFont("Cascadia Code", 9)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self._log.setFont(font)
        ly.addWidget(self._log, 1)

    # ──────────────────────────────────────────────────────────────────────────
    def _clear(self):
        self._log.clear()
        self._entries.clear()
        self._count_lbl.setText("0 lines")

    def _export_log(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Log", "training_log.txt", "Text files (*.txt);;All files (*)"
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                for msg, _ in self._entries:
                    f.write(msg + "\n")

    # ──────────────────────────────────────────────────────────────────────────
    def append_log(self, message: str, level: str = "info"):
        ts = datetime.now().strftime("%H:%M:%S")
        tag = LEVEL_TAGS.get(level, "INFO")
        color = LEVEL_COLORS.get(level, LEVEL_COLORS["info"])

        stamped = f"[{ts}] [{tag}]  {message}"
        self._entries.append((stamped, level))

        self._log.appendHtml(
            f'<span style="color:#3A3F70; font-family:Cascadia Code,Consolas,monospace; font-size:9pt;">[{ts}] </span>'
            f'<span style="color:{color}; font-weight:bold; font-family:Cascadia Code,Consolas,monospace; font-size:9pt;">[{tag}]</span>'
            f'<span style="color:{color}; font-family:Cascadia Code,Consolas,monospace; font-size:9pt;">  {message}</span>'
        )

        sb = self._log.verticalScrollBar()
        sb.setValue(sb.maximum())
        self._count_lbl.setText(f"{len(self._entries)} lines")
