"""
Sponge/Saturate Effect - Renk doygunluğu efekti
"""
import numpy as np
import cv2
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider
from PySide6.QtCore import Qt

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.plugin_base import EffectPlugin


class SpongeEffect(EffectPlugin):
    """Renk doygunluğu efekti"""
    
    def __init__(self):
        super().__init__()
        self.name = "Renk Doygunluğu"
        self.version = "1.0.0"
        self.description = "Renk doygunluğunu ayarla"
        self.icon_path = None
        self.real_time_preview = True
        
        self.saturation = 100  # 0 to 200
        
    def get_name(self) -> str:
        return self.name
    
    def get_icon(self) -> str:
        return self.icon_path or ""
    
    def get_settings_widget(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        saturation_label = QLabel("Doygunluk (0: Gri, 100: Normal, 200: Çok Doygun):")
        self.saturation_slider = QSlider(Qt.Horizontal)
        self.saturation_slider.setRange(0, 200)
        self.saturation_slider.setValue(self.saturation)
        self.saturation_slider.valueChanged.connect(self.on_saturation_changed)
        
        self.saturation_value_label = QLabel(str(self.saturation))
        
        layout.addWidget(saturation_label)
        layout.addWidget(self.saturation_slider)
        layout.addWidget(self.saturation_value_label)
        layout.addStretch()
        
        return widget
    
    def on_saturation_changed(self, value: int):
        self.saturation = value
        self.saturation_value_label.setText(str(value))
    
    def apply_effect(self, image: np.ndarray, **params) -> np.ndarray:
        """Renk doygunluğunu ayarla"""
        # Convert to HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
        
        # Adjust saturation
        hsv[:, :, 1] = hsv[:, :, 1] * (self.saturation / 100.0)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 255)
        
        # Convert back to BGR
        result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
        
        return result
