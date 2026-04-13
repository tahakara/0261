"""
Sharpen Filter Plugin - Example filter plugin
"""
import numpy as np
import cv2
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider
from PySide6.QtCore import Qt

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.plugin_base import FilterPlugin as BaseFilterPlugin


class SharpenFilter(BaseFilterPlugin):
    """Sharpen filter using unsharp masking"""
    
    def __init__(self):
        super().__init__()
        self.name = "Sharpen"
        self.version = "1.0.0"
        self.description = "Sharpen the image"
        self.icon_path = None
        
        # Filter settings
        self.strength = 2.0  # 0.0 to 5.0
        
    def get_name(self) -> str:
        return self.name
    
    def get_icon(self) -> str:
        return self.icon_path or ""
    
    def get_settings_widget(self) -> QWidget:
        """Return settings widget for sharpen configuration"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Strength slider
        strength_label = QLabel("Strength:")
        self.strength_slider = QSlider(Qt.Horizontal)
        self.strength_slider.setRange(0, 500)
        self.strength_slider.setValue(int(self.strength * 100))
        self.strength_slider.valueChanged.connect(self.on_strength_changed)
        
        self.strength_value_label = QLabel(f"{self.strength:.2f}")
        
        layout.addWidget(strength_label)
        layout.addWidget(self.strength_slider)
        layout.addWidget(self.strength_value_label)
        layout.addStretch()
        
        return widget
    
    def on_strength_changed(self, value: int):
        """Handle strength change"""
        self.strength = value / 100.0
        self.strength_value_label.setText(f"{self.strength:.2f}")
    
    def apply_filter(self, image: np.ndarray, **params) -> np.ndarray:
        """Apply sharpen filter using unsharp masking"""
        # Create a Gaussian blur
        blurred = cv2.GaussianBlur(image, (0, 0), 3)
        
        # Unsharp masking
        result = cv2.addWeighted(image, 1.0 + self.strength, blurred, -self.strength, 0)
        
        return result
