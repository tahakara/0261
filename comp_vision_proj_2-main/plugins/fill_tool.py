"""
Fill Tool - Doldurma aracı
"""
import numpy as np
import cv2
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QColorDialog
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.plugin_base import ToolPlugin


class FillTool(ToolPlugin):
    """Doldurma aracı"""
    
    def __init__(self):
        super().__init__()
        self.name = "Doldur"
        self.version = "1.0.0"
        self.description = "Seçili alanı renkle doldur"
        self.icon_path = None
        
        self.fill_color = (255, 255, 255)  # BGR - Beyaz
        
    def get_name(self) -> str:
        return self.name
    
    def get_icon(self) -> str:
        return self.icon_path or ""
    
    def get_settings_widget(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        color_label = QLabel("Dolgu Rengi:")
        self.color_button = QPushButton()
        self.color_button.setFixedHeight(30)
        self.update_color_button()
        self.color_button.clicked.connect(self.on_color_picker)
        
        layout.addWidget(color_label)
        layout.addWidget(self.color_button)
        layout.addStretch()
        
        return widget
    
    def on_color_picker(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.fill_color = (color.blue(), color.green(), color.red())
            self.update_color_button()
    
    def update_color_button(self):
        r, g, b = self.fill_color[2], self.fill_color[1], self.fill_color[0]
        self.color_button.setStyleSheet(f"background-color: rgb({r}, {g}, {b}); border: 2px solid #505050;")
    
    def execute(self, image: np.ndarray, **kwargs) -> np.ndarray:
        """Alanı doldur"""
        result = np.full_like(image, self.fill_color)
        return result
