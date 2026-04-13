"""
Ellipse Selection Tool - Select elliptical areas
"""
import numpy as np
import cv2
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QSlider, 
                                QComboBox, QGroupBox)
from PySide6.QtCore import Qt

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.plugin_base import ToolPlugin
from src.selection_manager import SelectionMode


class EllipseSelectionTool(ToolPlugin):
    """Ellipse selection tool"""
    
    def __init__(self):
        super().__init__()
        self.name = "Ellipse Select"
        self.version = "1.0.0"
        self.description = "Select elliptical areas"
        self.icon_path = None
        
        # Tool state
        self.start_point = None
        self.current_point = None
        self.is_selecting = False
        
        # Settings
        self.feather = 0
        self.selection_mode = SelectionMode.NEW
        
    def get_name(self) -> str:
        return self.name
    
    def get_icon(self) -> str:
        return self.icon_path or ""
    
    def get_settings_widget(self) -> QWidget:
        """Return settings widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Selection Mode
        mode_group = QGroupBox("Selection Mode")
        mode_layout = QVBoxLayout()
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItem("New Selection", SelectionMode.NEW)
        self.mode_combo.addItem("Add to Selection", SelectionMode.ADD)
        self.mode_combo.addItem("Remove from Selection", SelectionMode.SUBTRACT)
        self.mode_combo.addItem("Intersect", SelectionMode.INTERSECT)
        self.mode_combo.setCurrentIndex(0)  # Default: New Selection
        self.mode_combo.currentIndexChanged.connect(self.on_mode_changed)
        mode_layout.addWidget(self.mode_combo)
        mode_group.setLayout(mode_layout)
        
        # Feather
        feather_label = QLabel("Feather (Softness):")
        self.feather_slider = QSlider(Qt.Horizontal)
        self.feather_slider.setRange(0, 50)
        self.feather_slider.setValue(self.feather)
        self.feather_slider.valueChanged.connect(self.on_feather_changed)
        self.feather_value_label = QLabel(str(self.feather))
        
        layout.addWidget(mode_group)
        layout.addWidget(feather_label)
        layout.addWidget(self.feather_slider)
        layout.addWidget(self.feather_value_label)
        layout.addStretch()
        
        return widget
    
    def on_mode_changed(self, index: int):
        self.selection_mode = self.mode_combo.itemData(index)
    
    def on_feather_changed(self, value: int):
        self.feather = value
        self.feather_value_label.setText(str(value))
    
    def execute(self, image: np.ndarray, **kwargs) -> np.ndarray:
        return image
    
    def on_mouse_press(self, x: int, y: int, image: np.ndarray) -> np.ndarray:
        """Start ellipse selection"""
        self.start_point = (x, y)
        self.current_point = (x, y)
        self.is_selecting = True
        # Don't draw on canvas - just track selection
        return None
    
    def on_mouse_move(self, x: int, y: int, image: np.ndarray) -> np.ndarray:
        """Update ellipse preview"""
        if self.is_selecting and self.start_point:
            self.current_point = (x, y)
            # Show preview during selection
            result = image.copy()
            
            center_x = (self.start_point[0] + x) // 2
            center_y = (self.start_point[1] + y) // 2
            radius_x = abs(x - self.start_point[0]) // 2
            radius_y = abs(y - self.start_point[1]) // 2
            
            if radius_x > 0 and radius_y > 0:
                cv2.ellipse(result, (center_x, center_y), (radius_x, radius_y), 
                           0, 0, 360, (255, 0, 255), 2)
            return result
        return None
    
    def on_mouse_release(self, x: int, y: int, image: np.ndarray) -> np.ndarray:
        """Finish ellipse selection"""
        if self.is_selecting and self.start_point:
            self.current_point = (x, y)
            self.is_selecting = False
            # Don't return modified image - let editor window handle the selection
        return None
    
    def get_selection_params(self):
        """Get ellipse parameters for external use"""
        if self.start_point and self.current_point:
            center_x = (self.start_point[0] + self.current_point[0]) // 2
            center_y = (self.start_point[1] + self.current_point[1]) // 2
            radius_x = abs(self.current_point[0] - self.start_point[0]) // 2
            radius_y = abs(self.current_point[1] - self.start_point[1]) // 2
            
            # Ensure minimum radius
            if radius_x < 1:
                radius_x = 1
            if radius_y < 1:
                radius_y = 1
            
            return (center_x, center_y, radius_x, radius_y)
        return None
