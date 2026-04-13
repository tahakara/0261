"""
Blur Effect Plugin - Example effect plugin
"""
import numpy as np
import cv2
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider
from PySide6.QtCore import Qt

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.plugin_base import EffectPlugin


class BlurEffect(EffectPlugin):
    """Gaussian blur effect"""
    
    def __init__(self):
        super().__init__()
        self.name = "Blur Effect"
        self.version = "1.0.0"
        self.description = "Apply Gaussian blur to the image"
        self.icon_path = None
        self.real_time_preview = True
        
        # Effect settings
        self.blur_strength = 15
        
    def get_name(self) -> str:
        return self.name
    
    def get_icon(self) -> str:
        return self.icon_path or ""
    
    def get_settings_widget(self) -> QWidget:
        """Return settings widget for blur configuration"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Blur strength slider
        strength_label = QLabel("Blur Strength:")
        self.strength_slider = QSlider(Qt.Horizontal)
        self.strength_slider.setRange(1, 99)
        self.strength_slider.setValue(self.blur_strength)
        self.strength_slider.setSingleStep(2)  # Keep it odd
        self.strength_slider.valueChanged.connect(self.on_strength_changed)
        
        self.strength_value_label = QLabel(str(self.blur_strength))
        
        layout.addWidget(strength_label)
        layout.addWidget(self.strength_slider)
        layout.addWidget(self.strength_value_label)
        layout.addStretch()
        
        return widget
    
    def on_strength_changed(self, value: int):
        """Handle blur strength change"""
        # Ensure odd number for kernel size
        if value % 2 == 0:
            value += 1
        self.blur_strength = value
        self.strength_value_label.setText(str(value))
    
    def apply_effect(self, image: np.ndarray, **params) -> np.ndarray:
        """Apply Gaussian blur to the image"""
        kernel_size = self.blur_strength
        if kernel_size % 2 == 0:
            kernel_size += 1
        
        result = cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
        return result
