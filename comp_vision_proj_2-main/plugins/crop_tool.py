"""
Crop Tool - Kırpma aracı
"""
import numpy as np
import cv2
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.plugin_base import ToolPlugin


class CropTool(ToolPlugin):
    """Kırpma aracı - Seçili alanı keser"""
    
    def __init__(self):
        super().__init__()
        self.name = "Kırp"
        self.version = "1.0.0"
        self.description = "Seçili alanı kırp"
        self.icon_path = None
        
    def get_name(self) -> str:
        return self.name
    
    def get_icon(self) -> str:
        return self.icon_path or ""
    
    def get_settings_widget(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        info_label = QLabel("Önce alan seçin, sonra Apply'a tıklayın.\nSadece seçili alan kalacaktır.")
        info_label.setWordWrap(True)
        
        layout.addWidget(info_label)
        layout.addStretch()
        
        return widget
    
    def execute(self, image: np.ndarray, **kwargs) -> np.ndarray:
        """Crop işlemi selection manager tarafından yapılacak"""
        return image
