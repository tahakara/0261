"""
Cutout Mask - Seçili alanı kes ve arka planı şeffaf yap
"""
import numpy as np
import cv2
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.plugin_base import EffectPlugin


class CutoutMask(EffectPlugin):
    """Cutout mask efekti"""
    
    def __init__(self):
        super().__init__()
        self.name = "Kesme Maskesi"
        self.version = "1.0.0"
        self.description = "Seçili alanı kes, geri kalanı beyaz yap"
        self.icon_path = None
        self.real_time_preview = False
        
    def get_name(self) -> str:
        return self.name
    
    def get_icon(self) -> str:
        return self.icon_path or ""
    
    def get_settings_widget(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        info_label = QLabel("Seçili alanı korur, geri kalanını beyaz yapar.")
        info_label.setWordWrap(True)
        
        layout.addWidget(info_label)
        layout.addStretch()
        
        return widget
    
    def apply_effect(self, image: np.ndarray, **params) -> np.ndarray:
        """Cutout mask oluştur"""
        # Bu effect, selection manager tarafından özel işlenecek
        # Sadece seçili alan kalacak, geri kalan beyaz olacak
        result = np.ones_like(image) * 255
        return result
