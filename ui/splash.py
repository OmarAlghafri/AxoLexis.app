"""
Modern Splash Screen — AxoLexis SHAHAD Trainer
Redesigned: elegant violet gradient, soft fade-in animation, cleaner progress bar.
"""

import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QProgressBar, QLabel, 
    QFrame, QGraphicsDropShadowEffect, QGraphicsOpacityEffect
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPixmap, QColor


class ModernSplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(760, 560)
        
        self._init_ui()
        self._center()

        # Fade in animation
        self.setWindowOpacity(0.0)
        self._fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self._fade_anim.setDuration(800)
        self._fade_anim.setStartValue(0.0)
        self._fade_anim.setEndValue(1.0)
        self._fade_anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        self._fade_anim.start()

    def _init_ui(self):
        self.container = QFrame(self)
        self.container.setObjectName("splashContainer")
        self.container.setFixedSize(700, 500)
        
        # Super soft multi-layered shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(60)
        shadow.setXOffset(0)
        shadow.setYOffset(20)
        shadow.setColor(QColor(0, 0, 0, 160))
        self.container.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Content Wrapper ──
        content = QWidget()
        content_ly = QVBoxLayout(content)
        content_ly.setContentsMargins(50, 60, 50, 50)
        content_ly.setSpacing(15)

        # ── Logo ──
        icon_path = os.path.join(os.path.dirname(__file__), "resources", "icon.png")
        self.logo_label = QLabel()
        pixmap = QPixmap(icon_path)
        if not pixmap.isNull():
            self.logo_label.setPixmap(
                pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            )
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Soft logo glow
        logo_glow = QGraphicsDropShadowEffect(self)
        logo_glow.setBlurRadius(80)
        logo_glow.setColor(QColor(108, 92, 231, 140)) # Violet glow
        logo_glow.setOffset(0, 0)
        self.logo_label.setGraphicsEffect(logo_glow)
        
        # ── Typography ──
        self.title_label = QLabel("AXOLEXIS")
        self.title_label.setStyleSheet("""
            font-size: 44pt; 
            font-weight: 900; 
            color: #FFFFFF; 
            letter-spacing: 8px;
            background: transparent;
        """)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.subtitle_label = QLabel("SHAHAD MODEL TRAINING STUDIO")
        self.subtitle_label.setStyleSheet("""
            font-size: 11pt; 
            color: #A5B4FF; 
            font-weight: 700;
            letter-spacing: 4px;
            background: transparent;
            margin-top: -12px;
        """)
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        content_ly.addStretch()
        content_ly.addWidget(self.logo_label)
        content_ly.addSpacing(25)
        content_ly.addWidget(self.title_label)
        content_ly.addWidget(self.subtitle_label)
        content_ly.addStretch()

        # ── Progress Section ──
        progress_container = QWidget()
        progress_ly = QVBoxLayout(progress_container)
        progress_ly.setContentsMargins(60, 0, 60, 0)
        progress_ly.setSpacing(12)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(6)
        
        # Custom stylesheet just for splash (independent of main theme)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: rgba(255, 255, 255, 0.1);
                border: none;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #6C5CE7, stop:0.5 #4FACFE, stop:1 #3EE8B5);
                border-radius: 3px;
            }
        """)

        self.status_label = QLabel("INITIALIZING ENGINE...")
        self.status_label.setStyleSheet("""
            font-size: 8.5pt; 
            color: #C8CBFF; 
            font-weight: 700;
            letter-spacing: 2px;
            background: transparent;
        """)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        progress_ly.addWidget(self.progress_bar)
        progress_ly.addWidget(self.status_label)
        
        content_ly.addWidget(progress_container)
        content_ly.addSpacing(10)

        layout.addWidget(content)

        # Deep violent space background
        self.container.setStyleSheet("""
            QFrame#splashContainer {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #0A0B14, stop:1 #14152A);
                border: 1px solid rgba(124, 111, 255, 0.2);
                border-radius: 30px;
            }
        """)
        
        self.container.move(30, 30)

    def _center(self):
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def update_progress(self, value: int, message: str = None):
        self.progress_bar.setValue(value)
        if message:
            self.status_label.setText(message.upper())
        self.repaint()
