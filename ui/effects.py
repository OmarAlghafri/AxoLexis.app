"""
AxoLexis — Premium UI Effects Module
Smooth animations, shadows, and visual enhancements.
"""

from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PyQt6.QtWidgets import QGraphicsDropShadowEffect, QGraphicsOpacityEffect, QWidget, QListView
from PyQt6.QtGui import QColor


def apply_shadow(widget, blur_radius=30, x_offset=0, y_offset=8, color=(0, 0, 0, 160), opacity=0.4):
    """Apply a smooth drop shadow effect to any widget."""
    if widget.graphicsEffect():
        return
    
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(blur_radius)
    shadow.setXOffset(x_offset)
    shadow.setYOffset(y_offset)
    shadow.setColor(QColor(color[0], color[1], color[2], int(255 * opacity)))
    widget.setGraphicsEffect(shadow)


def apply_glow(widget, color=(99, 102, 241, 180), blur_radius=40):
    """Apply a colored glow effect (for accent elements)."""
    if widget.graphicsEffect():
        return
    
    glow = QGraphicsDropShadowEffect(widget)
    glow.setBlurRadius(blur_radius)
    glow.setXOffset(0)
    glow.setYOffset(0)
    glow.setColor(QColor(*color))
    widget.setGraphicsEffect(glow)


def add_dropdown_shadow(combo):
    """
    Ensures the ComboBox dropdown feels like a native Windows 11 menu.
    Uses QListView and ensures clean, solid rendering with system-compatible flags.
    """
    if not isinstance(combo.view(), QListView):
        view = QListView(combo)
        combo.setView(view)
        
    # Ensure the popup follows Windows style
    view = combo.view()
    popup = view.window()
    if popup:
        # No system NoDropShadow flag to allow native shadows if the OS supports it
        popup.setWindowFlags(popup.windowFlags() | Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        popup.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        popup.setAutoFillBackground(True)
        
        # Windows-like slight offset for clarity if needed, but ComboBox handles this mostly
        view.setSpacing(2) # Subtle spacing between items


def fade_in(widget, duration=400, delay=0):
    """Fade in a widget with smooth opacity animation."""
    widget.setWindowOpacity(0.0)
    
    fade_anim = QPropertyAnimation(widget, b"windowOpacity")
    fade_anim.setDuration(duration)
    fade_anim.setStartValue(0.0)
    fade_anim.setEndValue(1.0)
    fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    if delay > 0:
        QTimer.singleShot(delay, fade_anim.start)
    else:
        fade_anim.start()
    
    return fade_anim


def slide_in(widget, direction="left", duration=500, easing=QEasingCurve.Type.OutCubic):
    """Slide in a widget from a specified direction."""
    # Store original geometry
    original_pos = widget.pos()
    original_size = widget.size()
    
    # Set initial position off-screen
    if direction == "left":
        widget.move(-original_size.width(), original_pos.y())
    elif direction == "right":
        widget.move(original_pos.x() + original_size.width(), original_pos.y())
    elif direction == "top":
        widget.move(original_pos.x(), -original_size.height())
    elif direction == "bottom":
        widget.move(original_pos.x(), original_pos.y() + original_size.height())
    
    # Create position animation
    anim = QPropertyAnimation(widget, b"pos")
    anim.setDuration(duration)
    anim.setStartValue(widget.pos())
    anim.setEndValue(original_pos)
    anim.setEasingCurve(easing)
    anim.start()
    
    return anim


def pulse(widget, duration=1500, scale_factor=1.05):
    """Create a subtle pulse/scale animation on a widget."""
    original_size = widget.size()
    
    # Scale up
    scale_up = QPropertyAnimation(widget, b"minimumSize")
    scale_up.setDuration(duration // 2)
    scale_up.setStartValue(original_size)
    target_size = original_size * scale_factor
    scale_up.setEndValue(target_size.toSize())
    scale_up.setEasingCurve(QEasingCurve.Type.InOutQuad)
    
    # Scale down
    scale_down = QPropertyAnimation(widget, b"minimumSize")
    scale_down.setDuration(duration // 2)
    scale_down.setStartValue(target_size.toSize())
    scale_down.setEndValue(original_size)
    scale_down.setEasingCurve(QEasingCurve.Type.InOutQuad)
    
    scale_up.finished.connect(scale_down.start)
    scale_up.start()
    
    return scale_up


def hover_glow_effect(widget, base_color=(99, 102, 241, 0), hover_color=(99, 102, 241, 80)):
    """
    Create a hover glow effect by animating background color.
    Note: This requires the widget to have a stylesheet that supports color transitions.
    """
    def enter_event(e):
        widget.setStyleSheet(
            f"background-color: rgba({hover_color[0]}, {hover_color[1]}, {hover_color[2]}, {hover_color[3]});"
        )
    
    def leave_event(e):
        widget.setStyleSheet(
            f"background-color: rgba({base_color[0]}, {base_color[1]}, {base_color[2]}, {base_color[3]});"
        )
    
    # Store original enterEvent and leaveEvent
    original_enter = widget.enterEvent
    original_leave = widget.leaveEvent
    
    def patched_enter(e):
        enter_event(e)
        original_enter(e)
    
    def patched_leave(e):
        leave_event(e)
        original_leave(e)
    
    widget.enterEvent = patched_enter
    widget.leaveEvent = patched_leave


def add_gradient_background(widget, gradient_type="vertical", colors=None):
    """
    Apply a gradient background to a widget.
    gradient_type: 'vertical', 'horizontal', or 'diagonal'
    colors: list of (stop, color) tuples where color is (r, g, b) or (r, g, b, a)
    """
    if colors is None:
        colors = [
            (0.0, (99, 102, 241)),
            (0.5, (139, 92, 246)),
            (1.0, (168, 85, 247))
        ]
    
    if gradient_type == "vertical":
        gradient_str = "qlineargradient(x1:0, y1:0, x2:0, y2:1"
    elif gradient_type == "horizontal":
        gradient_str = "qlineargradient(x1:0, y1:0, x2:1, y2:0"
    elif gradient_type == "diagonal":
        gradient_str = "qlineargradient(x1:0, y1:0, x2:1, y2:1"
    else:
        gradient_str = "qlineargradient(x1:0, y1:0, x2:0, y2:1"
    
    color_stops = ", ".join([f"stop:{stop} rgba({r}, {g}, {b}, {a if len(color) > 3 else 255})" 
                             for stop, color in colors 
                             for r, g, b, a in [(color + (255,))[:4]]])
    
    gradient_str += f", {color_stops})"
    
    widget.setStyleSheet(f"background-color: {gradient_str};")


class AnimatedContainer(QWidget):
    """A container widget with built-in enter/exit animations."""
    
    def __init__(self, parent=None, animation_type="fade"):
        super().__init__(parent)
        self.animation_type = animation_type
        self._animations = []
    
    def showAnimated(self, animation_type=None):
        """Show the widget with an animation."""
        anim_type = animation_type or self.animation_type
        
        if anim_type == "fade":
            self.setWindowOpacity(0.0)
            self.show()
            anim = fade_in(self)
            self._animations.append(anim)
        elif anim_type == "slide_left":
            self.show()
            anim = slide_in(self, "left")
            self._animations.append(anim)
        elif anim_type == "slide_right":
            self.show()
            anim = slide_in(self, "right")
            self._animations.append(anim)
        else:
            self.show()
    
    def hideAnimated(self, animation_type=None):
        """Hide the widget with an animation."""
        anim_type = animation_type or self.animation_type
        
        if anim_type == "fade":
            anim = QPropertyAnimation(self, b"windowOpacity")
            anim.setDuration(300)
            anim.setStartValue(1.0)
            anim.setEndValue(0.0)
            anim.setEasingCurve(QEasingCurve.Type.InCubic)
            anim.finished.connect(self.hide)
            anim.start()
            self._animations.append(anim)
        else:
            self.hide()


def animate_value_change(label, old_value, new_value, duration=500, formatter=None):
    """
    Animate a numeric value change with a counting animation.
    """
    if formatter is None:
        formatter = lambda x: str(x)
    
    anim = QPropertyAnimation(label, b"minimumWidth")  # Dummy property for timing
    anim.setDuration(duration)
    anim.setStartValue(0)
    anim.setEndValue(100)
    anim.setEasingCurve(QEasingCurve.Type.OutQuad)
    
    start_time = QTimer()
    start_time.singleShot(0, lambda: None)  # Placeholder
    
    # Simple approach: just update the label
    label.setText(formatter(new_value))
    
    return anim


# Keep backward compatibility
apply_premium_shadow = apply_shadow
