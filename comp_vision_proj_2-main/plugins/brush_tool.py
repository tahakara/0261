"""
Brush Tool Plugin - Example tool plugin for painting
"""
import numpy as np
import cv2
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider, QPushButton, QColorDialog
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.plugin_base import ToolPlugin


class BrushTool(ToolPlugin):
    """Basic brush tool for painting"""
    
    def __init__(self):
        super().__init__()
        self.name = "Fırça"
        self.version = "1.0.0"
        self.description = "Tuval üzerinde fırça ile boyama"
        self.icon_path = None
        
        # Brush settings
        self.brush_size = 10
        self.brush_color = (0, 0, 255)  # BGR format (Red)
        self.is_drawing = False
        self.last_point = None
        self.parent_canvas = None  # Will be set by editor
        self.temp_image = None  # Temporary image for current stroke
        
    def get_name(self) -> str:
        return self.name
    
    def get_icon(self) -> str:
        return self.icon_path or ""
    
    def get_settings_widget(self) -> QWidget:
        """Return settings widget for brush configuration"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Brush size slider
        size_label = QLabel("Fırça Boyutu:")
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setRange(1, 100)
        self.size_slider.setValue(self.brush_size)
        self.size_slider.valueChanged.connect(self.on_size_changed)
        
        self.size_value_label = QLabel(str(self.brush_size))
        
        # Color picker button
        color_label = QLabel("Fırça Rengi:")
        self.color_button = QPushButton()
        self.color_button.setFixedHeight(30)
        self.update_color_button()
        self.color_button.clicked.connect(self.on_color_picker)
        
        layout.addWidget(size_label)
        layout.addWidget(self.size_slider)
        layout.addWidget(self.size_value_label)
        layout.addWidget(color_label)
        layout.addWidget(self.color_button)
        layout.addStretch()
        
        return widget
    
    def on_size_changed(self, value: int):
        """Handle brush size change"""
        self.brush_size = value
        self.size_value_label.setText(str(value))
        # Notify parent to update cursor
        if hasattr(self, 'parent_canvas'):
            self.parent_canvas.set_brush_cursor(value, True)
    
    def on_color_picker(self):
        """Open color picker dialog"""
        color = QColorDialog.getColor()
        if color.isValid():
            # Convert QColor to BGR
            self.brush_color = (color.blue(), color.green(), color.red())
            self.update_color_button()
    
    def update_color_button(self):
        """Update color button appearance"""
        r, g, b = self.brush_color[2], self.brush_color[1], self.brush_color[0]
        self.color_button.setStyleSheet(f"""
            QPushButton {{
                background-color: rgb({r}, {g}, {b});
                border: 2px solid #505050;
                border-radius: 3px;
            }}
            QPushButton:hover {{
                border: 2px solid #0078d4;
            }}
        """)
    
    def execute(self, image: np.ndarray, **kwargs) -> np.ndarray:
        """Not used for tool plugins"""
        return image
    
    def on_mouse_press(self, x: int, y: int, image: np.ndarray) -> np.ndarray:
        """Start drawing"""
        self.is_drawing = True
        self.last_point = (x, y)
        
        # Create a temporary image for this stroke
        self.temp_image = image.copy()
        
        # Draw a smooth circle at the click point with antialiasing
        cv2.circle(self.temp_image, (x, y), self.brush_size // 2, self.brush_color, -1, cv2.LINE_AA)
        
        return self.temp_image
    
    def on_mouse_move(self, x: int, y: int, image: np.ndarray) -> np.ndarray:
        """Continue drawing with smooth lines"""
        if self.is_drawing and self.last_point and self.temp_image is not None:
            # Draw smooth line with antialiasing and rounded caps
            cv2.line(self.temp_image, self.last_point, (x, y), 
                    self.brush_color, self.brush_size, cv2.LINE_AA)
            
            # Draw circles at both ends for smoother appearance
            cv2.circle(self.temp_image, (x, y), self.brush_size // 2, 
                      self.brush_color, -1, cv2.LINE_AA)
            
            self.last_point = (x, y)
            return self.temp_image
        return None
    
    def on_mouse_release(self, x: int, y: int, image: np.ndarray) -> np.ndarray:
        """Stop drawing and finalize the stroke"""
        if self.is_drawing and self.temp_image is not None:
            # Draw final line to release point
            if self.last_point:
                cv2.line(self.temp_image, self.last_point, (x, y), 
                        self.brush_color, self.brush_size, cv2.LINE_AA)
                cv2.circle(self.temp_image, (x, y), self.brush_size // 2, 
                          self.brush_color, -1, cv2.LINE_AA)
            
            result = self.temp_image
            self.temp_image = None
        else:
            result = None
        
        self.is_drawing = False
        self.last_point = None
        
        return result
