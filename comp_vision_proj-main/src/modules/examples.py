"""
Example modules - Demonstrates how to create modules for the editor.
"""

from typing import Optional
import numpy as np
import cv2
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QSlider, QPushButton, QComboBox
)
from PySide6.QtCore import Qt, Signal

from ..core.module_base import ModuleBase, ModuleCategory


class SliderControl(QWidget):
    """Reusable slider control with label and value display."""
    
    value_changed = Signal(int)
    
    def __init__(self, label: str, min_val: int, max_val: int, 
                 default: int, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(4)
        
        # Header with label and value
        header = QHBoxLayout()
        
        self._label = QLabel(label)
        self._label.setStyleSheet("color: #cccccc; font-size: 11px;")
        header.addWidget(self._label)
        
        self._value_label = QLabel(str(default))
        self._value_label.setStyleSheet("color: #0078d4; font-size: 11px; font-weight: bold;")
        self._value_label.setAlignment(Qt.AlignRight)
        header.addWidget(self._value_label)
        
        layout.addLayout(header)
        
        # Slider
        self._slider = QSlider(Qt.Horizontal)
        self._slider.setRange(min_val, max_val)
        self._slider.setValue(default)
        self._slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: #3c3c3c;
                height: 6px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #0078d4;
                width: 14px;
                height: 14px;
                margin: -4px 0;
                border-radius: 7px;
            }
            QSlider::sub-page:horizontal {
                background: #0078d4;
                border-radius: 3px;
            }
        """)
        self._slider.valueChanged.connect(self._on_value_changed)
        layout.addWidget(self._slider)
    
    def _on_value_changed(self, value: int):
        self._value_label.setText(str(value))
        self.value_changed.emit(value)
    
    @property
    def value(self) -> int:
        return self._slider.value()
    
    def set_value(self, value: int):
        self._slider.setValue(value)


class BrightnessModule(ModuleBase):
    """
    Brightness adjustment module.
    Demonstrates a simple slider-based effect.
    """
    
    def __init__(self):
        super().__init__()
        self._brightness = 0
        self._widget: Optional[QWidget] = None
    
    @property
    def name(self) -> str:
        return "Brightness"
    
    @property
    def description(self) -> str:
        return "Adjust the brightness of the image"
    
    @property
    def category(self) -> ModuleCategory:
        return ModuleCategory.ADJUSTMENT
    
    @property
    def supports_image(self) -> bool:
        return True
    
    @property
    def supports_video(self) -> bool:
        return True
    
    def get_settings_widget(self) -> QWidget:
        if self._widget is None:
            self._widget = QWidget()
            layout = QVBoxLayout(self._widget)
            layout.setContentsMargins(12, 12, 12, 12)
            layout.setSpacing(12)
            
            # Brightness slider
            self._slider = SliderControl("Brightness", -100, 100, 0)
            self._slider.value_changed.connect(self._on_brightness_changed)
            layout.addWidget(self._slider)
            
            # Reset button
            reset_btn = QPushButton("Reset")
            reset_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3c3c3c;
                    color: #cccccc;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background-color: #4a4a4a;
                }
            """)
            reset_btn.clicked.connect(lambda: self._slider.set_value(0))
            layout.addWidget(reset_btn)
            
            layout.addStretch()
        
        return self._widget
    
    def _on_brightness_changed(self, value: int):
        self._brightness = value
    
    def apply(self, image: np.ndarray, **params) -> np.ndarray:
        brightness = params.get('brightness', self._brightness)
        
        if brightness == 0:
            return image
        
        # Convert to float for calculation
        result = image.astype(np.float32)
        result = result + brightness
        result = np.clip(result, 0, 255).astype(np.uint8)
        
        return result
    
    def get_default_params(self):
        return {'brightness': 0}


class ContrastModule(ModuleBase):
    """
    Contrast adjustment module.
    """
    
    def __init__(self):
        super().__init__()
        self._contrast = 1.0
        self._widget: Optional[QWidget] = None
    
    @property
    def name(self) -> str:
        return "Contrast"
    
    @property
    def description(self) -> str:
        return "Adjust the contrast of the image"
    
    @property
    def category(self) -> ModuleCategory:
        return ModuleCategory.ADJUSTMENT
    
    @property
    def supports_image(self) -> bool:
        return True
    
    @property
    def supports_video(self) -> bool:
        return True
    
    def get_settings_widget(self) -> QWidget:
        if self._widget is None:
            self._widget = QWidget()
            layout = QVBoxLayout(self._widget)
            layout.setContentsMargins(12, 12, 12, 12)
            layout.setSpacing(12)
            
            # Contrast slider (50 = 1.0, range 0-100 maps to 0.0-2.0)
            self._slider = SliderControl("Contrast", 0, 200, 100)
            self._slider.value_changed.connect(self._on_contrast_changed)
            layout.addWidget(self._slider)
            
            # Reset button
            reset_btn = QPushButton("Reset")
            reset_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3c3c3c;
                    color: #cccccc;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background-color: #4a4a4a;
                }
            """)
            reset_btn.clicked.connect(lambda: self._slider.set_value(100))
            layout.addWidget(reset_btn)
            
            layout.addStretch()
        
        return self._widget
    
    def _on_contrast_changed(self, value: int):
        self._contrast = value / 100.0
    
    def apply(self, image: np.ndarray, **params) -> np.ndarray:
        contrast = params.get('contrast', self._contrast)
        
        if contrast == 1.0:
            return image
        
        # Apply contrast
        result = image.astype(np.float32)
        result = (result - 127.5) * contrast + 127.5
        result = np.clip(result, 0, 255).astype(np.uint8)
        
        return result
    
    def get_default_params(self):
        return {'contrast': 1.0}


class BlurModule(ModuleBase):
    """
    Blur filter module.
    Demonstrates different blur types.
    """
    
    def __init__(self):
        super().__init__()
        self._blur_type = "gaussian"
        self._kernel_size = 5
        self._widget: Optional[QWidget] = None
    
    @property
    def name(self) -> str:
        return "Blur"
    
    @property
    def description(self) -> str:
        return "Apply various blur effects to the image"
    
    @property
    def category(self) -> ModuleCategory:
        return ModuleCategory.FILTER
    
    @property
    def supports_image(self) -> bool:
        return True
    
    @property
    def supports_video(self) -> bool:
        return True
    
    def get_settings_widget(self) -> QWidget:
        if self._widget is None:
            self._widget = QWidget()
            layout = QVBoxLayout(self._widget)
            layout.setContentsMargins(12, 12, 12, 12)
            layout.setSpacing(12)
            
            # Blur type selector
            type_layout = QHBoxLayout()
            type_label = QLabel("Type:")
            type_label.setStyleSheet("color: #cccccc; font-size: 11px;")
            type_layout.addWidget(type_label)
            
            self._type_combo = QComboBox()
            self._type_combo.addItems(["Gaussian", "Box", "Median", "Bilateral"])
            self._type_combo.setStyleSheet("""
                QComboBox {
                    background-color: #3c3c3c;
                    color: #cccccc;
                    border: 1px solid #4a4a4a;
                    border-radius: 4px;
                    padding: 6px 10px;
                }
                QComboBox:hover {
                    border-color: #5a5a5a;
                }
                QComboBox::drop-down {
                    border: none;
                }
            """)
            self._type_combo.currentTextChanged.connect(self._on_type_changed)
            type_layout.addWidget(self._type_combo)
            layout.addLayout(type_layout)
            
            # Kernel size slider
            self._slider = SliderControl("Strength", 1, 31, 5)
            self._slider.value_changed.connect(self._on_kernel_changed)
            layout.addWidget(self._slider)
            
            # Note about odd values
            note = QLabel("Note: Only odd values are used")
            note.setStyleSheet("color: #666666; font-size: 10px;")
            layout.addWidget(note)
            
            # Reset button
            reset_btn = QPushButton("Reset")
            reset_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3c3c3c;
                    color: #cccccc;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background-color: #4a4a4a;
                }
            """)
            reset_btn.clicked.connect(self._reset)
            layout.addWidget(reset_btn)
            
            layout.addStretch()
        
        return self._widget
    
    def _on_type_changed(self, text: str):
        self._blur_type = text.lower()
    
    def _on_kernel_changed(self, value: int):
        # Ensure odd value
        self._kernel_size = value if value % 2 == 1 else value + 1
    
    def _reset(self):
        self._type_combo.setCurrentIndex(0)
        self._slider.set_value(5)
    
    def apply(self, image: np.ndarray, **params) -> np.ndarray:
        blur_type = params.get('blur_type', self._blur_type)
        kernel_size = params.get('kernel_size', self._kernel_size)
        
        # Ensure odd kernel size
        if kernel_size % 2 == 0:
            kernel_size += 1
        
        if kernel_size <= 1:
            return image
        
        # Apply blur based on type
        if blur_type == "gaussian":
            return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
        elif blur_type == "box":
            return cv2.blur(image, (kernel_size, kernel_size))
        elif blur_type == "median":
            return cv2.medianBlur(image, kernel_size)
        elif blur_type == "bilateral":
            return cv2.bilateralFilter(image, kernel_size, 75, 75)
        
        return image
    
    def get_default_params(self):
        return {'blur_type': 'gaussian', 'kernel_size': 5}
