"""
Bulge/Pinch Effect - Şişirme/Sıkıştırma efekti
"""
import numpy as np
import cv2
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider
from PySide6.QtCore import Qt

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.plugin_base import EffectPlugin


class BulgeEffect(EffectPlugin):
    """Bulge/Pinch efekti"""
    
    def __init__(self):
        super().__init__()
        self.name = "Şişir/Sıkıştır"
        self.version = "1.0.0"
        self.description = "Seçili alanı şişir veya sıkıştır"
        self.icon_path = None
        self.real_time_preview = False
        
        self.strength = 0  # -100 to 100
        
    def get_name(self) -> str:
        return self.name
    
    def get_icon(self) -> str:
        return self.icon_path or ""
    
    def get_settings_widget(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        strength_label = QLabel("Güç (-100: Sıkıştır, +100: Şişir):")
        self.strength_slider = QSlider(Qt.Horizontal)
        self.strength_slider.setRange(-100, 100)
        self.strength_slider.setValue(self.strength)
        self.strength_slider.valueChanged.connect(self.on_strength_changed)
        
        self.strength_value_label = QLabel(str(self.strength))
        
        layout.addWidget(strength_label)
        layout.addWidget(self.strength_slider)
        layout.addWidget(self.strength_value_label)
        layout.addStretch()
        
        return widget
    
    def on_strength_changed(self, value: int):
        self.strength = value
        self.strength_value_label.setText(str(value))
    
    def apply_effect(self, image: np.ndarray, **params) -> np.ndarray:
        """Bulge/Pinch uygula"""
        if self.strength == 0:
            return image
        
        h, w = image.shape[:2]
        center_x, center_y = w // 2, h // 2
        radius = min(w, h) // 2
        
        # Create mesh grid
        y, x = np.mgrid[0:h, 0:w]
        
        # Calculate distance from center
        dx = x - center_x
        dy = y - center_y
        distance = np.sqrt(dx**2 + dy**2)
        
        # Apply bulge/pinch transformation
        mask = distance < radius
        factor = 1.0 + (self.strength / 100.0)
        
        # Calculate new coordinates
        new_distance = distance.copy()
        new_distance[mask] = distance[mask] * (1.0 - (distance[mask] / radius) * (1.0 - factor))
        
        # Calculate new positions
        angle = np.arctan2(dy, dx)
        map_x = (center_x + new_distance * np.cos(angle)).astype(np.float32)
        map_y = (center_y + new_distance * np.sin(angle)).astype(np.float32)
        
        # Apply remap
        result = cv2.remap(image, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        
        return result
