"""
Bucket Fill Tool - Flood fill aracı
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


class BucketFillTool(ToolPlugin):
    """Bucket fill (flood fill) aracı - Tıklanan bölgeyi doldurur"""
    
    def __init__(self):
        super().__init__()
        self.name = "Kova Dolgusu"
        self.version = "1.0.0"
        self.description = "Tıklanan bölgeyi benzer renklerle doldurur"
        self.icon_path = None
        
        # Settings
        self.fill_color = (255, 255, 255)  # BGR - Beyaz
        self.tolerance = 10  # 0-255 arası tolerans
        self.is_drawing = False
        
    def get_name(self) -> str:
        return self.name
    
    def get_icon(self) -> str:
        return self.icon_path or ""
    
    def get_settings_widget(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Color picker
        color_label = QLabel("Dolgu Rengi:")
        self.color_button = QPushButton()
        self.color_button.setFixedHeight(30)
        self.update_color_button()
        self.color_button.clicked.connect(self.on_color_picker)
        
        # Tolerance slider
        tolerance_label = QLabel("Tolerans (Benzerlik):")
        self.tolerance_slider = QSlider(Qt.Horizontal)
        self.tolerance_slider.setRange(0, 100)
        self.tolerance_slider.setValue(self.tolerance)
        self.tolerance_slider.valueChanged.connect(self.on_tolerance_changed)
        
        self.tolerance_value_label = QLabel(f"{self.tolerance}")
        
        # Info
        info_label = QLabel("Tıklayarak benzer renkli bölgeyi doldurun.\nSeçim varsa sadece seçili alanda çalışır.")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #888; font-size: 10px;")
        
        layout.addWidget(color_label)
        layout.addWidget(self.color_button)
        layout.addWidget(tolerance_label)
        layout.addWidget(self.tolerance_slider)
        layout.addWidget(self.tolerance_value_label)
        layout.addWidget(info_label)
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
    
    def on_tolerance_changed(self, value: int):
        self.tolerance = value
        self.tolerance_value_label.setText(f"{value}")
    
    def on_mouse_press(self, x: int, y: int, image: np.ndarray) -> np.ndarray:
        """Flood fill işlemini başlat"""
        if x < 0 or y < 0 or y >= image.shape[0] or x >= image.shape[1]:
            return image
        
        result = image.copy()
        h, w = image.shape[:2]
        
        # Mask oluştur (flood fill için)
        # Flood fill mask boyutu image boyutundan 2 piksel daha büyük olmalı (OpenCV requirement)
        mask = np.zeros((h + 2, w + 2), dtype=np.uint8)
        
        # Flood fill flags
        connectivity = 4  # 4-way connectivity (yukarı, aşağı, sağ, sol)
        flags = connectivity | cv2.FLOODFILL_FIXED_RANGE | (255 << 8)
        
        # Tolerans değerini OpenCV formatına çevir
        lo_diff = (self.tolerance, self.tolerance, self.tolerance)
        up_diff = (self.tolerance, self.tolerance, self.tolerance)
        
        try:
            # Flood fill uygula
            num_filled = cv2.floodFill(
                result,
                mask,
                (x, y),
                self.fill_color,
                lo_diff,
                up_diff,
                flags
            )
            
            # Note: Selection desteği için editor_window.py'da handle edilecek
            # Çünkü bu plugin selection_manager'a erişemiyor
            
        except Exception as e:
            print(f"Flood fill error: {e}")
        
        return result
    
    def on_mouse_move(self, x: int, y: int, image: np.ndarray) -> np.ndarray:
        """Mouse hareketi - hiçbir şey yapma"""
        return None
    
    def on_mouse_release(self, x: int, y: int, image: np.ndarray) -> np.ndarray:
        """Mouse bırakma - hiçbir şey yapma"""
        return None
