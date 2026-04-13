"""
Lasso Selection Tool - Freehand and polygon selection
"""
import numpy as np
import cv2
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QSlider, 
                                QComboBox, QGroupBox, QRadioButton, QButtonGroup)
from PySide6.QtCore import Qt
from typing import List, Tuple

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.plugin_base import ToolPlugin
from src.selection_manager import SelectionMode


class LassoSelectionTool(ToolPlugin):
    """Lasso selection tool with multiple modes"""
    
    def __init__(self):
        super().__init__()
        self.name = "Lasso Select"
        self.version = "1.0.0"
        self.description = "Freehand and polygon selection"
        self.icon_path = None
        
        # Tool state
        self.points: List[Tuple[int, int]] = []
        self.is_selecting = False
        
        # Settings
        self.feather = 0
        self.selection_mode = SelectionMode.NEW
        self.lasso_type = "free"  # "free", "polygon", "magnetic"
        
    def get_name(self) -> str:
        return self.name
    
    def get_icon(self) -> str:
        return self.icon_path or ""
    
    def get_settings_widget(self) -> QWidget:
        """Return settings widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Lasso Type
        type_group = QGroupBox("Lasso Type")
        type_layout = QVBoxLayout()
        
        self.type_button_group = QButtonGroup()
        
        free_radio = QRadioButton("Free Lasso")
        free_radio.setChecked(True)
        free_radio.toggled.connect(lambda: self.on_type_changed("free"))
        self.type_button_group.addButton(free_radio)
        
        poly_radio = QRadioButton("Polygon Lasso")
        poly_radio.toggled.connect(lambda: self.on_type_changed("polygon"))
        self.type_button_group.addButton(poly_radio)
        
        magnetic_radio = QRadioButton("Magnetic Lasso")
        magnetic_radio.toggled.connect(lambda: self.on_type_changed("magnetic"))
        self.type_button_group.addButton(magnetic_radio)
        
        type_layout.addWidget(free_radio)
        type_layout.addWidget(poly_radio)
        type_layout.addWidget(magnetic_radio)
        type_group.setLayout(type_layout)
        
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
        feather_label = QLabel("Feather:")
        self.feather_slider = QSlider(Qt.Horizontal)
        self.feather_slider.setRange(0, 50)
        self.feather_slider.setValue(self.feather)
        self.feather_slider.valueChanged.connect(self.on_feather_changed)
        self.feather_value_label = QLabel(str(self.feather))
        
        layout.addWidget(type_group)
        layout.addWidget(mode_group)
        layout.addWidget(feather_label)
        layout.addWidget(self.feather_slider)
        layout.addWidget(self.feather_value_label)
        layout.addStretch()
        
        return widget
    
    def on_type_changed(self, lasso_type: str):
        self.lasso_type = lasso_type
        self.points.clear()
    
    def on_mode_changed(self, index: int):
        self.selection_mode = self.mode_combo.itemData(index)
    
    def on_feather_changed(self, value: int):
        self.feather = value
        self.feather_value_label.setText(str(value))
    
    def execute(self, image: np.ndarray, **kwargs) -> np.ndarray:
        return image
    
    def on_mouse_press(self, x: int, y: int, image: np.ndarray) -> np.ndarray:
        """Start lasso selection"""
        if self.lasso_type == "polygon":
            # Add point for polygon
            self.points.append((x, y))
            # Don't draw on canvas - just track points
        else:
            # Free or magnetic lasso
            self.is_selecting = True
            self.points = [(x, y)]
        return None
    
    def on_mouse_move(self, x: int, y: int, image: np.ndarray) -> np.ndarray:
        """Update lasso selection"""
        if self.lasso_type == "free" and self.is_selecting:
            # Add point to free lasso
            self.points.append((x, y))
            # Show preview during selection
            result = image.copy()
            if len(self.points) > 1:
                pts = np.array(self.points, dtype=np.int32)
                cv2.polylines(result, [pts], False, (255, 0, 255), 2)
            return result
        elif self.lasso_type == "polygon" and self.points:
            # Show preview for polygon
            result = image.copy()
            # Draw existing points and lines
            for i, pt in enumerate(self.points):
                cv2.circle(result, pt, 3, (255, 0, 255), -1)
                if i > 0:
                    cv2.line(result, self.points[i-1], pt, (255, 0, 255), 2)
            # Draw preview line to cursor
            if self.points:
                cv2.line(result, self.points[-1], (x, y), (255, 0, 255), 1)
            return result
        return None
    
    def on_mouse_release(self, x: int, y: int, image: np.ndarray) -> np.ndarray:
        """Finish lasso selection"""
        if self.lasso_type == "free" and self.is_selecting:
            self.is_selecting = False
            # Close the lasso
            if len(self.points) > 2:
                return image
        
        # Polygon lasso continues until double-click or Enter key
        return None
    
    def finish_polygon(self):
        """Finish polygon lasso (called externally)"""
        if self.lasso_type == "polygon" and len(self.points) > 2:
            return True
        return False
    
    def get_selection_points(self):
        """Get lasso points for external use"""
        if len(self.points) > 2:
            return self.points.copy()
        return None
    
    def clear_points(self):
        """Clear current points"""
        self.points.clear()
