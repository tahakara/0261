"""
Shape Tool - Draw geometric shapes (rectangle, circle, line, arrow, polygon)
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QColorDialog, QSpinBox
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
import cv2
import numpy as np


class ShapeTool:
    """Tool for drawing shapes on images"""
    
    def __init__(self):
        self.shape_type = "rectangle"  # rectangle, circle, line, arrow, ellipse, polygon
        self.color = (0, 0, 255)  # BGR - Red default
        self.thickness = 2
        self.filled = False
        
    def draw_shape(self, image, start_point, end_point):
        """
        Draw shape on image
        
        Args:
            image: BGR image
            start_point: (x, y) tuple
            end_point: (x, y) tuple
            
        Returns:
            Modified image
        """
        result = image.copy()
        
        if self.shape_type == "rectangle":
            result = self._draw_rectangle(result, start_point, end_point)
        elif self.shape_type == "circle":
            result = self._draw_circle(result, start_point, end_point)
        elif self.shape_type == "line":
            result = self._draw_line(result, start_point, end_point)
        elif self.shape_type == "arrow":
            result = self._draw_arrow(result, start_point, end_point)
        elif self.shape_type == "ellipse":
            result = self._draw_ellipse(result, start_point, end_point)
        elif self.shape_type == "triangle":
            result = self._draw_triangle(result, start_point, end_point)
        
        return result
    
    def _draw_rectangle(self, image, start, end):
        """Draw rectangle"""
        thickness = -1 if self.filled else self.thickness
        cv2.rectangle(image, start, end, self.color, thickness)
        return image
    
    def _draw_circle(self, image, center, edge):
        """Draw circle"""
        radius = int(np.sqrt((edge[0] - center[0])**2 + (edge[1] - center[1])**2))
        thickness = -1 if self.filled else self.thickness
        cv2.circle(image, center, radius, self.color, thickness)
        return image
    
    def _draw_line(self, image, start, end):
        """Draw line"""
        cv2.line(image, start, end, self.color, self.thickness)
        return image
    
    def _draw_arrow(self, image, start, end):
        """Draw arrow"""
        cv2.arrowedLine(image, start, end, self.color, self.thickness, tipLength=0.3)
        return image
    
    def _draw_ellipse(self, image, center, edge):
        """Draw ellipse"""
        axes = (abs(edge[0] - center[0]), abs(edge[1] - center[1]))
        thickness = -1 if self.filled else self.thickness
        cv2.ellipse(image, center, axes, 0, 0, 360, self.color, thickness)
        return image
    
    def _draw_triangle(self, image, start, end):
        """Draw triangle"""
        # Calculate third point
        mid_x = (start[0] + end[0]) // 2
        points = np.array([start, end, (mid_x, start[1])], np.int32)
        points = points.reshape((-1, 1, 2))
        
        if self.filled:
            cv2.fillPoly(image, [points], self.color)
        else:
            cv2.polylines(image, [points], True, self.color, self.thickness)
        
        return image


class ShapeToolPanel(QWidget):
    """Panel for shape tool settings"""
    
    shape_changed = Signal(str)  # shape_type
    color_changed = Signal(tuple)  # BGR color
    thickness_changed = Signal(int)
    filled_changed = Signal(bool)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        
        # Shape type selection
        shape_layout = QHBoxLayout()
        shape_layout.addWidget(QLabel("Şekil:"))
        self.shape_combo = QComboBox()
        self.shape_combo.addItem("Dikdörtgen", "rectangle")
        self.shape_combo.addItem("Daire", "circle")
        self.shape_combo.addItem("Çizgi", "line")
        self.shape_combo.addItem("Ok", "arrow")
        self.shape_combo.addItem("Elips", "ellipse")
        self.shape_combo.addItem("Üçgen", "triangle")
        self.shape_combo.currentIndexChanged.connect(self.on_shape_changed)
        shape_layout.addWidget(self.shape_combo)
        layout.addLayout(shape_layout)
        
        # Color selection
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Renk:"))
        self.color_btn = QPushButton("Renk Seç")
        self.color_btn.clicked.connect(self.on_color_clicked)
        self.color_preview = QWidget()
        self.color_preview.setFixedSize(30, 30)
        self.color_preview.setStyleSheet("background-color: red;")
        color_layout.addWidget(self.color_btn)
        color_layout.addWidget(self.color_preview)
        layout.addLayout(color_layout)
        
        # Thickness
        thickness_layout = QHBoxLayout()
        thickness_layout.addWidget(QLabel("Kalınlık:"))
        self.thickness_spin = QSpinBox()
        self.thickness_spin.setRange(1, 20)
        self.thickness_spin.setValue(2)
        self.thickness_spin.valueChanged.connect(self.on_thickness_changed)
        thickness_layout.addWidget(self.thickness_spin)
        layout.addLayout(thickness_layout)
        
        # Filled checkbox
        from PySide6.QtWidgets import QCheckBox
        self.filled_check = QCheckBox("Dolu")
        self.filled_check.stateChanged.connect(self.on_filled_changed)
        layout.addWidget(self.filled_check)
        
        layout.addStretch()
        
        # Store current color (BGR)
        self.current_color = (0, 0, 255)  # Red
        
    def on_shape_changed(self):
        """Handle shape type change"""
        shape_type = self.shape_combo.currentData()
        self.shape_changed.emit(shape_type)
        
        # Disable filled for line and arrow
        if shape_type in ["line", "arrow"]:
            self.filled_check.setEnabled(False)
            self.filled_check.setChecked(False)
        else:
            self.filled_check.setEnabled(True)
    
    def on_color_clicked(self):
        """Handle color button click"""
        # Convert BGR to RGB for QColor
        r, g, b = self.current_color[2], self.current_color[1], self.current_color[0]
        initial_color = QColor(r, g, b)
        
        color = QColorDialog.getColor(initial_color, self, "Renk Seç")
        
        if color.isValid():
            # Convert RGB to BGR
            self.current_color = (color.blue(), color.green(), color.red())
            self.color_preview.setStyleSheet(f"background-color: rgb({color.red()}, {color.green()}, {color.blue()});")
            self.color_changed.emit(self.current_color)
    
    def on_thickness_changed(self, value):
        """Handle thickness change"""
        self.thickness_changed.emit(value)
    
    def on_filled_changed(self, state):
        """Handle filled checkbox change"""
        self.filled_changed.emit(state == Qt.Checked)
