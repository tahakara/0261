"""
Bottom status bar - Shows cursor position, selection info, image dimensions, etc.
"""

from typing import Optional
from PySide6.QtWidgets import (
    QStatusBar, QWidget, QHBoxLayout, QLabel, 
    QFrame, QProgressBar
)
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QFont

from ..core.project import EditorMode


class StatusSection(QFrame):
    """A section in the status bar with label and value."""
    
    def __init__(self, label: str, value: str = "", parent=None):
        super().__init__(parent)
        
        self.setStyleSheet("""
            StatusSection {
                background-color: transparent;
                border-right: 1px solid #3c3c3c;
                padding: 0 8px;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(6)
        
        self._label = QLabel(label)
        self._label.setStyleSheet("color: #888888; font-size: 11px;")
        layout.addWidget(self._label)
        
        self._value = QLabel(value)
        self._value.setStyleSheet("color: #cccccc; font-size: 11px; font-weight: bold;")
        layout.addWidget(self._value)
    
    def set_value(self, value: str):
        """Update the value text."""
        self._value.setText(value)
    
    def set_label(self, label: str):
        """Update the label text."""
        self._label.setText(label)


class InfoStatusBar(QStatusBar):
    """
    Status bar at the bottom of the window.
    Shows cursor position, selection info, zoom level, etc.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setStyleSheet("""
            QStatusBar {
                background-color: #252526;
                border-top: 1px solid #3c3c3c;
                color: #cccccc;
                min-height: 28px;
            }
            QStatusBar::item {
                border: none;
            }
        """)
        
        # Mode indicator
        self._mode_section = StatusSection("Mode:", "Image")
        self.addWidget(self._mode_section)
        
        # Cursor position
        self._cursor_section = StatusSection("Cursor:", "0, 0")
        self.addWidget(self._cursor_section)
        
        # Selection info
        self._selection_section = StatusSection("Selection:", "None")
        self.addWidget(self._selection_section)
        
        # Image dimensions
        self._dimensions_section = StatusSection("Size:", "800 × 600")
        self.addWidget(self._dimensions_section)
        
        # Color at cursor
        self._color_section = StatusSection("Color:", "---")
        self.addWidget(self._color_section)
        
        # Zoom level
        self._zoom_section = StatusSection("Zoom:", "100%")
        self.addWidget(self._zoom_section)
        
        # Spacer to push permanent widgets to right
        spacer = QWidget()
        spacer.setMinimumWidth(1)
        self.addWidget(spacer, 1)
        
        # Layer info (permanent, right side)
        self._layer_section = StatusSection("Layer:", "1/1")
        self.addPermanentWidget(self._layer_section)
        
        # Memory usage (permanent, right side)
        self._memory_section = StatusSection("Memory:", "0 MB")
        self.addPermanentWidget(self._memory_section)
        
        # Progress bar for long operations (hidden by default)
        self._progress = QProgressBar()
        self._progress.setFixedWidth(150)
        self._progress.setTextVisible(True)
        self._progress.setStyleSheet("""
            QProgressBar {
                background-color: #3c3c3c;
                border: none;
                border-radius: 4px;
                text-align: center;
                color: white;
                font-size: 10px;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 4px;
            }
        """)
        self._progress.hide()
        self.addPermanentWidget(self._progress)
        
        # Video-specific sections (hidden in image mode)
        self._frame_section = StatusSection("Frame:", "0/0")
        self._frame_section.hide()
        self.addWidget(self._frame_section)
        
        self._time_section = StatusSection("Time:", "00:00:00")
        self._time_section.hide()
        self.addWidget(self._time_section)
        
        self._fps_section = StatusSection("FPS:", "30")
        self._fps_section.hide()
        self.addWidget(self._fps_section)
    
    def set_mode(self, mode: EditorMode):
        """Set editor mode and update visibility of mode-specific sections."""
        if mode == EditorMode.IMAGE:
            self._mode_section.set_value("Image")
            self._frame_section.hide()
            self._time_section.hide()
            self._fps_section.hide()
        else:
            self._mode_section.set_value("Video")
            self._frame_section.show()
            self._time_section.show()
            self._fps_section.show()
    
    def set_cursor_position(self, x: int, y: int):
        """Update cursor position display."""
        self._cursor_section.set_value(f"{x}, {y}")
    
    def set_selection(self, rect: Optional[QRect]):
        """Update selection info."""
        if rect is None or rect.isEmpty():
            self._selection_section.set_value("None")
        else:
            w, h = rect.width(), rect.height()
            pixels = w * h
            self._selection_section.set_value(f"{w}×{h} ({pixels:,} px)")
    
    def set_dimensions(self, width: int, height: int):
        """Update image/canvas dimensions."""
        pixels = width * height
        self._dimensions_section.set_value(f"{width} × {height} ({pixels:,} px)")
    
    def set_color_at_cursor(self, r: int, g: int, b: int, a: int = 255):
        """Update color at cursor position."""
        self._color_section.set_value(f"R:{r} G:{g} B:{b}" + (f" A:{a}" if a < 255 else ""))
    
    def clear_color(self):
        """Clear color display."""
        self._color_section.set_value("---")
    
    def set_zoom(self, zoom: float):
        """Update zoom level display."""
        percentage = int(zoom * 100)
        self._zoom_section.set_value(f"{percentage}%")
    
    def set_layer_info(self, current: int, total: int):
        """Update layer info."""
        self._layer_section.set_value(f"{current}/{total}")
    
    def set_memory_usage(self, mb: float):
        """Update memory usage display."""
        self._memory_section.set_value(f"{mb:.1f} MB")
    
    # Video-specific methods
    def set_frame_info(self, current: int, total: int):
        """Update frame info (video mode)."""
        self._frame_section.set_value(f"{current}/{total}")
    
    def set_time(self, seconds: float):
        """Update time display (video mode)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        self._time_section.set_value(f"{hours:02d}:{minutes:02d}:{secs:02d}")
    
    def set_fps(self, fps: float):
        """Update FPS display (video mode)."""
        self._fps_section.set_value(f"{fps:.1f}")
    
    # Progress bar methods
    def show_progress(self, text: str = "Processing..."):
        """Show progress bar."""
        self._progress.setFormat(text + " %p%")
        self._progress.setValue(0)
        self._progress.show()
    
    def set_progress(self, value: int):
        """Update progress value (0-100)."""
        self._progress.setValue(value)
    
    def hide_progress(self):
        """Hide progress bar."""
        self._progress.hide()
