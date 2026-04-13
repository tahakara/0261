"""
Brightness Adjustment Plugin - Example adjustment plugin
"""
import numpy as np
import cv2
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider, QPushButton
from PySide6.QtCore import Qt

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.plugin_base import AdjustmentPlugin as BaseAdjustmentPlugin


class BrightnessAdjustment(BaseAdjustmentPlugin):
    """Adjust image brightness"""
    
    def __init__(self):
        super().__init__()
        self.name = "Brightness"
        self.version = "1.0.0"
        self.description = "Adjust image brightness"
        self.icon_path = None
        
        # Adjustment settings
        self.brightness = 0  # -100 to 100
        
    def get_name(self) -> str:
        return self.name
    
    def get_icon(self) -> str:
        return self.icon_path or ""
    
    def get_settings_widget(self) -> QWidget:
        """Return settings widget for brightness configuration"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Brightness slider
        brightness_label = QLabel("Brightness:")
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(-255, 255)
        self.brightness_slider.setValue(self.brightness)
        self.brightness_slider.valueChanged.connect(self.on_brightness_changed)
        
        self.brightness_value_label = QLabel(str(self.brightness))
        
        # Reset button
        reset_button = QPushButton("Reset")
        reset_button.clicked.connect(self.on_reset)
        
        layout.addWidget(brightness_label)
        layout.addWidget(self.brightness_slider)
        layout.addWidget(self.brightness_value_label)
        layout.addWidget(reset_button)
        layout.addStretch()
        
        return widget
    
    def on_brightness_changed(self, value: int):
        """Handle brightness change"""
        self.brightness = value
        self.brightness_value_label.setText(str(value))
    
    def on_reset(self):
        """Reset brightness to default"""
        self.brightness_slider.setValue(0)
    
    def apply_adjustment(self, image: np.ndarray, **params) -> np.ndarray:
        """Apply brightness adjustment to the image"""
        if self.brightness == 0:
            return image
        
        # Convert to HSV for proper brightness adjustment
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
        
        # Adjust V (brightness) channel
        hsv[:, :, 2] = hsv[:, :, 2] + self.brightness
        
        # Clip values to valid range
        hsv[:, :, 2] = np.clip(hsv[:, :, 2], 0, 255)
        
        # Convert back to BGR
        result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
        
        return result
