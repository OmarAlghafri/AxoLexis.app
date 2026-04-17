"""
ThemeManager — Singleton for dual Light/Dark theme management.
Handles QSS loading, application, persistence, and signals.
"""

from PyQt6.QtCore import QObject, pyqtSignal, QSettings
from PyQt6.QtWidgets import QApplication


class ThemeManager(QObject):
    """Singleton that manages the application theme (Dark / Light)."""

    theme_changed = pyqtSignal(str)  # emits "dark" or "light"

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # Initialize the base class immediately
            QObject.__init__(cls._instance)
            # Setup singleton variables
            cls._instance._settings = QSettings("AxoLexis", "AxoLexisTrainer")
            cls._instance._current = cls._instance._settings.value("theme", "dark", type=str)
        return cls._instance

    def __init__(self):
        # Initialization is handled entirely within __new__ to avoid PyQt constructor conflicts.
        pass

    # ── Public API ────────────────────────────────────────────────────────────
    @property
    def current_theme(self) -> str:
        return self._current

    @property
    def is_dark(self) -> bool:
        return self._current == "dark"

    def apply(self, app: QApplication):
        """Load the current theme QSS and apply it to the application."""
        from ui.style_premium import PREMIUM_QSS
        from ui.style_light import LIGHT_QSS
        qss = PREMIUM_QSS if self._current == "dark" else LIGHT_QSS
        app.setStyleSheet(qss)
        self.theme_changed.emit(self._current)

    def toggle(self, app: QApplication):
        """Switch between dark and light themes."""
        self._current = "light" if self._current == "dark" else "dark"
        self._settings.setValue("theme", self._current)
        self.apply(app)

    def set_theme(self, name: str, app: QApplication):
        """Explicitly set a theme by name ('dark' or 'light')."""
        if name not in ("dark", "light"):
            return
        self._current = name
        self._settings.setValue("theme", name)
        self.apply(app)
