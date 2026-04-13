"""
Gradient Tool - Seçili alana gradient uygula
"""
import numpy as np
import cv2
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QColorDialog
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.plugin_base import ToolPlugin


class GradientTool(ToolPlugin):
    """Gradient geçiş aracı"""
    
    def __init__(self):
        super().__init__()
        self.name = "Gradient"
        self.version = "1.0.0"
        self.description = "Seçili alana gradient uygula"
        self.icon_path = None
        
        # Settings
        self.color1 = (0, 0, 255)  # BGR - Kırmızı
        self.color2 = (255, 255, 255)  # BGR - Beyaz
        self.gradient_type = "linear"  # linear, radial
        
    def get_name(self) -> str:
        return self.name
    
    def get_icon(self) -> str:
        return self.icon_path or ""
    
    def get_settings_widget(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Gradient türü
        type_label = QLabel("Gradient Türü:")
        self.type_combo = QComboBox()
        self.type_combo.addItem("Doğrusal", "linear")
        self.type_combo.addItem("Dairesel", "radial")
        self.type_combo.currentIndexChanged.connect(self.on_type_changed)
        
        # Renk 1
        color1_label = QLabel("Başlangıç Rengi:")
        self.color1_button = QPushButton()
        self.color1_button.setFixedHeight(30)
        self.update_color1_button()
        self.color1_button.clicked.connect(self.on_color1_picker)
        
        # Renk 2
        color2_label = QLabel("Bitiş Rengi:")
        self.color2_button = QPushButton()
        self.color2_button.setFixedHeight(30)
        self.update_color2_button()
        self.color2_button.clicked.connect(self.on_color2_picker)
        
        layout.addWidget(type_label)
        layout.addWidget(self.type_combo)
        layout.addWidget(color1_label)
        layout.addWidget(self.color1_button)
        layout.addWidget(color2_label)
        layout.addWidget(self.color2_button)
        layout.addStretch()
        
        return widget
    
    def on_type_changed(self, index: int):
        self.gradient_type = self.type_combo.itemData(index)
    
    def on_color1_picker(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.color1 = (color.blue(), color.green(), color.red())
            self.update_color1_button()
    
    def on_color2_picker(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.color2 = (color.blue(), color.green(), color.red())
            self.update_color2_button()
    
    def update_color1_button(self):
        r, g, b = self.color1[2], self.color1[1], self.color1[0]
        self.color1_button.setStyleSheet(f"background-color: rgb({r}, {g}, {b}); border: 2px solid #505050;")
    
    def update_color2_button(self):
        r, g, b = self.color2[2], self.color2[1], self.color2[0]
        self.color2_button.setStyleSheet(f"background-color: rgb({r}, {g}, {b}); border: 2px solid #505050;")
    
    def execute(self, image: np.ndarray, **kwargs) -> np.ndarray:
        """Gradient uygula"""
        h, w = image.shape[:2]
        
        if self.gradient_type == "linear":
            gradient = self.create_linear_gradient(h, w)
        else:
            gradient = self.create_radial_gradient(h, w)
        
        return gradient
    
    def create_linear_gradient(self, h: int, w: int) -> np.ndarray:
        """Doğrusal gradient"""
        result = np.zeros((h, w, 3), dtype=np.uint8)
        
        for i in range(h):
            ratio = i / h
            color = tuple(int(self.color1[c] * (1 - ratio) + self.color2[c] * ratio) for c in range(3))
            result[i, :] = color
        
        return result
    
    def create_radial_gradient(self, h: int, w: int) -> np.ndarray:
        """Dairesel gradient"""
        result = np.zeros((h, w, 3), dtype=np.uint8)
        center_x, center_y = w // 2, h // 2
        max_dist = np.sqrt(center_x**2 + center_y**2)
        
        for y in range(h):
            for x in range(w):
                dist = np.sqrt((x - center_x)**2 + (y - center_y)**2)
                ratio = min(dist / max_dist, 1.0)
                color = tuple(int(self.color1[c] * (1 - ratio) + self.color2[c] * ratio) for c in range(3))
                result[y, x] = color
        
        return result
