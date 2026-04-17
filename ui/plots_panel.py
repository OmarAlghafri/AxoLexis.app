"""
Plots Panel — real-time training charts using pyqtgraph.
Premium design with glassmorphism and theme integration.
"""

import collections
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QGridLayout, QFrame, QGraphicsDropShadowEffect, QApplication
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from ui.theme_manager import ThemeManager

try:
    import pyqtgraph as pg
    # Set default config to prevent flashes before theme applies
    pg.setConfigOption("background", "transparent")
    pg.setConfigOption("foreground", "#D4D4D8")
    pg.setConfigOptions(antialias=True, enableExperimental=True)
    _HAS_PG = True
except ImportError:
    _HAS_PG = False

# Premium gradient-inspired colors for plots
COLORS = {
    "loss":     "#F472B6",   # Pink - vibrant
    "val_loss": "#FBBF24",   # Amber - warm
    "acc":      "#34D399",   # Emerald - fresh green
    "lr":       "#60A5FA",   # Sky blue - bright
    "gnorm":    "#A78BFA",   # Violet - soft purple
}
MAX_POINTS = 500


class PlotsPanel(QWidget):
    def __init__(self):
        super().__init__()
        self._step = 0
        self._data: dict = collections.defaultdict(list)
        self._steps_data: list = []
        self._build()

        ThemeManager().theme_changed.connect(self._on_theme_changed)

    # ──────────────────────────────────────────────────────────────────────────
    def _build(self):
        ly = QVBoxLayout(self)
        ly.setContentsMargins(0, 0, 0, 0)
        ly.setSpacing(12)

        if _HAS_PG:
            self._build_pg(ly)
            self._apply_theme_colors(ThemeManager().is_dark)
        else:
            self._build_fallback(ly)

    def _build_pg(self, parent_ly):
        grid = QGridLayout()
        grid.setSpacing(20)

        self._plots = []
        self._plot_containers = []

        def make_plot(title: str, ylabel: str, color: str):
            # Create container frame with glass effect
            container = QFrame()
            container.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 rgba(24, 24, 27, 0.4), stop:1 rgba(18, 18, 23, 0.6));
                    border: 1px solid rgba(255, 255, 255, 0.06);
                    border-radius: 12px;
                }
            """)
            container.setContentsMargins(12, 12, 12, 12)
            
            # Apply subtle shadow
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(20)
            shadow.setXOffset(0)
            shadow.setYOffset(4)
            shadow.setColor(QColor(0, 0, 0, 80))
            container.setGraphicsEffect(shadow)
            
            container_ly = QVBoxLayout(container)
            container_ly.setContentsMargins(0, 0, 0, 0)
            
            # Title label
            title_lbl = QLabel(title)
            title_lbl.setStyleSheet(f"""
                color: {color};
                font-size: 9.5pt;
                font-weight: 700;
                background: transparent;
                padding: 4px 0 8px 4px; /* Added top and left padding */
            """)
            container_ly.addWidget(title_lbl)
            
            # Create plot widget
            pw = pg.PlotWidget()
            pw.setMouseEnabled(x=False, y=False)
            pw.hideButtons()
            pw.setBackground('transparent')
            
            # Style axes
            pw.setLabel("left", ylabel, size="8.5pt", color="#71717A")
            pw.setLabel("bottom", "Step", size="8.5pt", color="#71717A")
            
            # Add to container
            container_ly.addWidget(pw)
            
            # Store references
            self._plots.append(pw)
            self._plot_containers.append(container)

            pen = pg.mkPen(color=color, width=3, antialias=True)
            curve = pw.plot(pen=pen, antialias=True)
            return container, pw, curve

        # Create the four plot containers
        self._container_loss, self._pw_loss,  self._c_loss  = make_plot("Training Loss",    "Loss",   COLORS["loss"])
        self._container_vacc, self._pw_vacc,  self._c_vacc  = make_plot("Validation Accuracy", "%",  COLORS["acc"])
        self._container_lr, self._pw_lr,    self._c_lr    = make_plot("Learning Rate",    "LR",     COLORS["lr"])
        self._container_gnorm, self._pw_gnorm, self._c_gnorm = make_plot("Gradient Norm",    "‖∇‖",    COLORS["gnorm"])

        # Val loss overlaid on loss plot (dashed line)
        pen2 = pg.mkPen(color=COLORS["val_loss"], width=2.5, style=Qt.PenStyle.DashLine, antialias=True)
        self._c_vloss = self._pw_loss.plot(pen=pen2, antialias=True)

        # Add containers to grid
        grid.addWidget(self._container_loss,  0, 0)
        grid.addWidget(self._container_vacc,  0, 1)
        grid.addWidget(self._container_lr,    1, 0)
        grid.addWidget(self._container_gnorm, 1, 1)
        parent_ly.addLayout(grid, 1)

        # ── Legend bar ────────────────────────────────────────────────────────
        self._legend_frame = QFrame()
        self._legend_frame.setObjectName("legendFrame")
        self._legend_frame.setFixedHeight(52)
        self._legend_frame.setStyleSheet("""
            QFrame#legendFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(24, 24, 27, 0.5), stop:1 rgba(18, 18, 23, 0.7));
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 12px;
            }
        """)
        leg_ly = QHBoxLayout(self._legend_frame)
        leg_ly.setContentsMargins(24, 0, 24, 0)
        leg_ly.setSpacing(20)

        legend_items = [
            ("Train Loss",COLORS["loss"],     "●"),
            ("Val Loss",  COLORS["val_loss"], "─"),
            ("Val Acc",   COLORS["acc"],      "●"),
            ("LR",        COLORS["lr"],       "●"),
            ("Grad Norm", COLORS["gnorm"],    "●"),
        ]

        self._legend_texts = []
        for label, color, sym in legend_items:
            item_ly = QHBoxLayout()
            item_ly.setSpacing(6)
            
            sym_lbl = QLabel(sym)
            sym_lbl.setStyleSheet(f"color: {color}; font-size: 14pt; font-weight: 800; background: transparent;")
            
            txt_lbl = QLabel(label)
            txt_lbl.setStyleSheet(f"color: #A1A1AA; font-size: 8.5pt; font-weight: 600; background: transparent;")
            self._legend_texts.append(txt_lbl)
            
            item_ly.addWidget(sym_lbl)
            item_ly.addWidget(txt_lbl)
            leg_ly.addLayout(item_ly)

        leg_ly.addStretch()
        parent_ly.addWidget(self._legend_frame)

    def _build_fallback(self, parent_ly):
        msg = QLabel(
            " pyqtgraph not installed\n\n"
            "pip install pyqtgraph\n\n"
            "Training metrics are still visible in the Console tab."
        )
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg.setObjectName("fallbackLabel")
        parent_ly.addWidget(msg)

    # ──────────────────────────────────────────────────────────────────────────
    def _on_theme_changed(self, theme: str):
        if _HAS_PG:
            self._apply_theme_colors(theme == "dark")

    def _apply_theme_colors(self, is_dark: bool):
        bg = "transparent"
        fg = "#D4D4D8" if is_dark else "#374151"
        grid_color = "rgba(255, 255, 255, 0.08)" if is_dark else "rgba(0, 0, 0, 0.08)"

        # Legend frame style
        leg_bg = "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(24, 24, 27, 0.5), stop:1 rgba(18, 18, 23, 0.7))" if is_dark else "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(249, 250, 251, 0.8), stop:1 rgba(243, 244, 246, 0.9))"
        leg_border = "rgba(255, 255, 255, 0.08)" if is_dark else "rgba(0, 0, 0, 0.1)"
        self._legend_frame.setStyleSheet(f"""
            QFrame#legendFrame {{
                background: {leg_bg};
                border: 1px solid {leg_border};
                border-radius: 12px;
            }}
        """)

        for lbl in self._legend_texts:
            lbl.setStyleSheet(f"color: {fg}; font-size: 8.5pt; font-weight: 600; background: transparent;")

        # Update pyqtgraph elements
        for pw in self._plots:
            pw.setBackground(bg)
            pw.showGrid(x=False, y=True, alpha=0.2 if is_dark else 0.3)
            
            # Style axes - use setPen for axis lines and tick marks
            axis_pen = pg.mkPen(color=fg, width=1)
            for axis_name in ("left", "bottom"):
                ax = pw.getAxis(axis_name)
                ax.setPen(axis_pen)

    # ──────────────────────────────────────────────────────────────────────────
    def on_step(self, info: dict):
        if not _HAS_PG:
            return

        self._step += 1
        s = self._step
        self._steps_data.append(s)

        if len(self._steps_data) > MAX_POINTS:
            self._steps_data.pop(0)

        def push(key, value):
            arr = self._data[key]
            arr.append(value)
            if len(arr) > MAX_POINTS:
                arr.pop(0)

        loss = info.get("loss/total", info.get("ssl/total_ssl"))
        if loss is not None:
            push("loss", loss)
            self._c_loss.setData(
                self._steps_data[-len(self._data["loss"]):],
                self._data["loss"],
            )

        vloss = info.get("val/loss")
        if vloss is not None:
            push("vloss", vloss)
            self._c_vloss.setData(
                self._steps_data[-len(self._data["vloss"]):],
                self._data["vloss"],
            )

        acc = info.get("val/accuracy")
        if acc is not None:
            push("acc", acc * 100)
            self._c_vacc.setData(
                self._steps_data[-len(self._data["acc"]):],
                self._data["acc"],
            )

        lr = info.get("lr")
        if lr is not None:
            push("lr", lr)
            self._c_lr.setData(
                self._steps_data[-len(self._data["lr"]):],
                self._data["lr"],
            )

        gnorm = info.get("grad_norm")
        if gnorm is not None:
            push("gnorm", gnorm)
            self._c_gnorm.setData(
                self._steps_data[-len(self._data["gnorm"]):],
                self._data["gnorm"],
            )

    def reset(self):
        self._step = 0
        self._data.clear()
        self._steps_data.clear()
        if _HAS_PG:
            for c in [self._c_loss, self._c_vloss, self._c_vacc,
                      self._c_lr, self._c_gnorm]:
                c.setData([], [])
