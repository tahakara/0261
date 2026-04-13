"""
Layer Management System - Sophisticated layer handling
"""
from typing import Optional, List
from dataclasses import dataclass
from enum import Enum
import numpy as np
import cv2
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                                QListWidget, QListWidgetItem, QLabel, QSlider,
                                QComboBox, QCheckBox, QMenu)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QPixmap, QImage


class BlendMode(Enum):
    """Layer blending modes"""
    NORMAL = "Normal"
    MULTIPLY = "Multiply"
    SCREEN = "Screen"
    OVERLAY = "Overlay"
    ADD = "Add"
    SUBTRACT = "Subtract"


@dataclass
class Layer:
    """Represents a single layer in the layer stack"""
    name: str
    image: np.ndarray
    visible: bool = True
    opacity: float = 1.0  # 0.0 to 1.0
    blend_mode: BlendMode = BlendMode.NORMAL
    locked: bool = False
    thumbnail: Optional[QPixmap] = None
    
    # Transform properties
    x_offset: int = 0
    y_offset: int = 0
    scale_x: float = 1.0
    scale_y: float = 1.0
    rotation: float = 0.0  # degrees
    
    def get_transformed_image(self) -> np.ndarray:
        """Apply transform to image"""
        result = self.image.copy()
        h, w = result.shape[:2]
        has_alpha = len(result.shape) == 3 and result.shape[2] == 4
        
        # Apply scale
        if self.scale_x != 1.0 or self.scale_y != 1.0:
            new_w = int(w * self.scale_x)
            new_h = int(h * self.scale_y)
            if new_w > 0 and new_h > 0:
                result = cv2.resize(result, (new_w, new_h))
                h, w = result.shape[:2]
        
        # Apply rotation
        if self.rotation != 0.0:
            center = (w // 2, h // 2)
            matrix = cv2.getRotationMatrix2D(center, self.rotation, 1.0)
            # Calculate new bounding box
            cos = abs(matrix[0, 0])
            sin = abs(matrix[0, 1])
            new_w = int((h * sin) + (w * cos))
            new_h = int((h * cos) + (w * sin))
            # Adjust translation
            matrix[0, 2] += (new_w / 2) - center[0]
            matrix[1, 2] += (new_h / 2) - center[1]
            
            # Use transparent border for images with alpha channel
            if has_alpha:
                border_value = (0, 0, 0, 0)  # Transparent
            else:
                border_value = (255, 255, 255)  # White
            
            result = cv2.warpAffine(result, matrix, (new_w, new_h), 
                                   borderMode=cv2.BORDER_CONSTANT, borderValue=border_value)
        
        return result
    
    def get_thumbnail(self, size=(64, 64)) -> QPixmap:
        """Generate thumbnail for the layer"""
        if self.thumbnail is None:
            # Resize image for thumbnail
            h, w = self.image.shape[:2]
            aspect = w / h
            if aspect > 1:
                new_w, new_h = size[0], int(size[0] / aspect)
            else:
                new_w, new_h = int(size[1] * aspect), size[1]
            
            thumb = cv2.resize(self.image, (new_w, new_h))
            
            # Convert to QPixmap
            if len(thumb.shape) == 2:  # Grayscale
                thumb = cv2.cvtColor(thumb, cv2.COLOR_GRAY2RGB)
            else:
                thumb = cv2.cvtColor(thumb, cv2.COLOR_BGR2RGB)
            
            h, w, ch = thumb.shape
            bytes_per_line = ch * w
            qt_image = QImage(thumb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.thumbnail = QPixmap.fromImage(qt_image)
            
        return self.thumbnail


class LayerManager:
    """Manages the layer stack and compositing"""
    
    def __init__(self):
        self.layers: List[Layer] = []
        self.active_layer_index: int = 0
        self.canvas_size: Optional[tuple] = None  # (width, height)
        self._composite_cache: Optional[np.ndarray] = None
        self._cache_valid = False
        
    def add_layer(self, name: str, image: np.ndarray, index: Optional[int] = None) -> Layer:
        """Add a new layer to the stack"""
        layer = Layer(name=name, image=image.copy())
        
        # Update canvas size to fit largest layer
        h, w = image.shape[:2]
        if self.canvas_size is None:
            self.canvas_size = (w, h)
        else:
            current_w, current_h = self.canvas_size
            self.canvas_size = (max(current_w, w), max(current_h, h))
        
        if index is None:
            self.layers.append(layer)
            self.active_layer_index = len(self.layers) - 1
        else:
            self.layers.insert(index, layer)
            self.active_layer_index = index
        
        self._cache_valid = False
        return layer
    
    def remove_layer(self, index: int) -> bool:
        """Remove a layer from the stack"""
        if 0 <= index < len(self.layers):
            self.layers.pop(index)
            if self.active_layer_index >= len(self.layers):
                self.active_layer_index = max(0, len(self.layers) - 1)
            self._cache_valid = False
            return True
        return False
    
    def move_layer(self, from_index: int, to_index: int) -> bool:
        """Move a layer to a different position"""
        if 0 <= from_index < len(self.layers) and 0 <= to_index < len(self.layers):
            layer = self.layers.pop(from_index)
            self.layers.insert(to_index, layer)
            self.active_layer_index = to_index
            self._cache_valid = False
            return True
        return False
    
    def get_active_layer(self) -> Optional[Layer]:
        """Get the currently active layer"""
        if 0 <= self.active_layer_index < len(self.layers):
            return self.layers[self.active_layer_index]
        return None
    
    def set_active_layer(self, index: int):
        """Set the active layer"""
        if 0 <= index < len(self.layers):
            self.active_layer_index = index
    
    def composite_layers(self, force_refresh: bool = False) -> np.ndarray:
        """Composite all visible layers into a single image with caching"""
        if self._cache_valid and self._composite_cache is not None and not force_refresh:
            return self._composite_cache.copy()
        
        if not self.layers:
            if self.canvas_size:
                w, h = self.canvas_size
                result = np.ones((h, w, 3), dtype=np.uint8) * 255
            else:
                result = np.ones((512, 512, 3), dtype=np.uint8) * 255
            self._composite_cache = result
            self._cache_valid = True
            return result
        
        # Determine canvas size based on largest layer with transforms
        if self.canvas_size:
            canvas_w, canvas_h = self.canvas_size
        else:
            max_w, max_h = 0, 0
            for layer in self.layers:
                # Get transformed dimensions
                transformed = layer.get_transformed_image()
                h, w = transformed.shape[:2]
                # Consider offsets
                layer_right = w + layer.x_offset
                layer_bottom = h + layer.y_offset
                max_w = max(max_w, layer_right)
                max_h = max(max_h, layer_bottom)
            canvas_w, canvas_h = max(max_w, 512), max(max_h, 512)
        
        # Start with white background
        result = np.ones((canvas_h, canvas_w, 3), dtype=np.uint8) * 255
        
        for layer in self.layers:
            if not layer.visible:
                continue
            
            # Get transformed layer image
            layer_img = layer.get_transformed_image()
            
            # Place layer on canvas with offset
            h, w = layer_img.shape[:2]
            x, y = layer.x_offset, layer.y_offset
            
            # Calculate placement bounds
            x1 = max(0, x)
            y1 = max(0, y)
            x2 = min(canvas_w, x + w)
            y2 = min(canvas_h, y + h)
            
            # Calculate source bounds
            src_x1 = max(0, -x)
            src_y1 = max(0, -y)
            src_x2 = src_x1 + (x2 - x1)
            src_y2 = src_y1 + (y2 - y1)
            
            if x2 > x1 and y2 > y1:
                # Extract region to blend
                layer_region = layer_img[src_y1:src_y2, src_x1:src_x2]
                
                # Convert grayscale to BGR if needed (alpha channel handled in blend)
                if len(layer_region.shape) == 2:
                    layer_region = cv2.cvtColor(layer_region, cv2.COLOR_GRAY2BGR)
                # If 4 channels (BGRA), keep it - blend function will handle alpha
                
                canvas_region = result[y1:y2, x1:x2]
                blended = self._blend_layers(canvas_region, layer_region, layer.blend_mode, layer.opacity)
                result[y1:y2, x1:x2] = blended
        
        self._composite_cache = result.copy()
        self._cache_valid = True
        return result
    
    def _blend_layers(self, base: np.ndarray, overlay: np.ndarray, 
                     blend_mode: BlendMode, opacity: float) -> np.ndarray:
        """Blend two layers together with alpha channel support"""
        # Check if overlay has alpha channel (4 channels)
        has_alpha = len(overlay.shape) == 3 and overlay.shape[2] == 4
        
        if has_alpha:
            # Extract alpha channel before resizing
            overlay_rgb = overlay[:, :, :3]
            alpha_channel = overlay[:, :, 3]
        else:
            overlay_rgb = overlay
            alpha_channel = None
        
        # Ensure same size (resize RGB only)
        if base.shape[:2] != overlay_rgb.shape[:2]:
            overlay_rgb = cv2.resize(overlay_rgb, (base.shape[1], base.shape[0]))
            if alpha_channel is not None:
                alpha_channel = cv2.resize(alpha_channel, (base.shape[1], base.shape[0]))
        
        # Calculate alpha values
        if has_alpha and alpha_channel is not None:
            alpha = alpha_channel.astype(float) / 255.0
        else:
            # No alpha channel, use full opacity
            alpha = np.ones((overlay_rgb.shape[0], overlay_rgb.shape[1]), dtype=float)
        
        # Apply layer opacity to alpha
        alpha = alpha * opacity
        
        # Ensure base is 3-channel BGR
        if len(base.shape) == 2:
            base = cv2.cvtColor(base, cv2.COLOR_GRAY2BGR)
        
        # Ensure overlay_rgb is 3-channel BGR
        if len(overlay_rgb.shape) == 2:
            overlay_rgb = cv2.cvtColor(overlay_rgb, cv2.COLOR_GRAY2BGR)
        
        # Convert to float for blending
        base_float = base.astype(float) / 255.0
        overlay_float = overlay_rgb.astype(float) / 255.0
        
        # Expand alpha to 3 channels for broadcasting
        alpha_3ch = np.stack([alpha, alpha, alpha], axis=2)
        
        if blend_mode == BlendMode.NORMAL:
            result = base_float * (1 - alpha_3ch) + overlay_float * alpha_3ch
            
        elif blend_mode == BlendMode.MULTIPLY:
            blended = base_float * overlay_float
            result = base_float * (1 - alpha_3ch) + blended * alpha_3ch
            
        elif blend_mode == BlendMode.SCREEN:
            blended = 1 - (1 - base_float) * (1 - overlay_float)
            result = base_float * (1 - alpha_3ch) + blended * alpha_3ch
            
        elif blend_mode == BlendMode.OVERLAY:
            mask = base_float < 0.5
            blended = np.where(mask, 2 * base_float * overlay_float,
                            1 - 2 * (1 - base_float) * (1 - overlay_float))
            result = base_float * (1 - alpha_3ch) + blended * alpha_3ch
            
        elif blend_mode == BlendMode.ADD:
            result = np.clip(base_float + overlay_float * alpha_3ch, 0, 1)
            
        elif blend_mode == BlendMode.SUBTRACT:
            result = np.clip(base_float - overlay_float * alpha_3ch, 0, 1)
        else:
            result = base_float
        
        return (result * 255).astype(np.uint8)
        
        return (result * 255).astype(np.uint8)


class LayerPanel(QWidget):
    """UI Panel for layer management"""
    
    layer_changed = Signal()
    active_layer_changed = Signal(int)
    
    def __init__(self, layer_manager: LayerManager):
        super().__init__()
        self.layer_manager = layer_manager
        self.setup_ui()
        self.apply_styles()
        
    def setup_ui(self):
        """Setup the layer panel UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Title
        title = QLabel("Layers")
        title.setObjectName("panelTitle")
        layout.addWidget(title)
        
        # Layer controls
        controls_layout = QHBoxLayout()
        
        self.add_layer_btn = QPushButton("+")
        self.add_layer_btn.setToolTip("Add Layer")
        self.add_layer_btn.setFixedSize(30, 30)
        self.add_layer_btn.clicked.connect(self.on_add_layer)
        
        self.remove_layer_btn = QPushButton("-")
        self.remove_layer_btn.setToolTip("Remove Layer")
        self.remove_layer_btn.setFixedSize(30, 30)
        self.remove_layer_btn.clicked.connect(self.on_remove_layer)
        
        self.move_up_btn = QPushButton("↑")
        self.move_up_btn.setToolTip("Move Layer Up")
        self.move_up_btn.setFixedSize(30, 30)
        self.move_up_btn.clicked.connect(self.on_move_up)
        
        self.move_down_btn = QPushButton("↓")
        self.move_down_btn.setToolTip("Move Layer Down")
        self.move_down_btn.setFixedSize(30, 30)
        self.move_down_btn.clicked.connect(self.on_move_down)
        
        controls_layout.addWidget(self.add_layer_btn)
        controls_layout.addWidget(self.remove_layer_btn)
        controls_layout.addWidget(self.move_up_btn)
        controls_layout.addWidget(self.move_down_btn)
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        # Layer list
        self.layer_list = QListWidget()
        self.layer_list.setSelectionMode(QListWidget.SingleSelection)
        self.layer_list.currentRowChanged.connect(self.on_layer_selected)
        layout.addWidget(self.layer_list)
        
        # Layer properties
        props_layout = QVBoxLayout()
        
        # Opacity slider
        opacity_label = QLabel("Opacity:")
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.valueChanged.connect(self.on_opacity_changed)
        
        # Blend mode
        blend_label = QLabel("Blend Mode:")
        self.blend_mode_combo = QComboBox()
        for mode in BlendMode:
            self.blend_mode_combo.addItem(mode.value)
        self.blend_mode_combo.currentTextChanged.connect(self.on_blend_mode_changed)
        
        # Visibility checkbox
        self.visible_checkbox = QCheckBox("Visible")
        self.visible_checkbox.setChecked(True)
        self.visible_checkbox.stateChanged.connect(self.on_visibility_changed)
        
        props_layout.addWidget(opacity_label)
        props_layout.addWidget(self.opacity_slider)
        props_layout.addWidget(blend_label)
        props_layout.addWidget(self.blend_mode_combo)
        props_layout.addWidget(self.visible_checkbox)
        
        # Transform controls
        transform_label = QLabel("Transform:")
        transform_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        props_layout.addWidget(transform_label)
        
        # Scale controls
        scale_layout = QHBoxLayout()
        scale_layout.addWidget(QLabel("Scale:"))
        self.scale_slider = QSlider(Qt.Horizontal)
        self.scale_slider.setRange(10, 300)  # 10% to 300%
        self.scale_slider.setValue(100)
        self.scale_slider.valueChanged.connect(self.on_scale_changed)
        self.scale_label = QLabel("100%")
        scale_layout.addWidget(self.scale_slider)
        scale_layout.addWidget(self.scale_label)
        props_layout.addLayout(scale_layout)
        
        # Rotation controls
        rotation_layout = QHBoxLayout()
        rotation_layout.addWidget(QLabel("Rotate:"))
        self.rotation_slider = QSlider(Qt.Horizontal)
        self.rotation_slider.setRange(-180, 180)
        self.rotation_slider.setValue(0)
        self.rotation_slider.valueChanged.connect(self.on_rotation_changed)
        self.rotation_label = QLabel("0°")
        rotation_layout.addWidget(self.rotation_slider)
        rotation_layout.addWidget(self.rotation_label)
        props_layout.addLayout(rotation_layout)
        
        # Reset transform button
        self.reset_transform_btn = QPushButton("Reset Transform")
        self.reset_transform_btn.clicked.connect(self.on_reset_transform)
        props_layout.addWidget(self.reset_transform_btn)
        
        layout.addLayout(props_layout)
        
    def refresh_layer_list(self):
        """Refresh the layer list display"""
        self.layer_list.clear()
        
        for i, layer in enumerate(reversed(self.layer_manager.layers)):
            actual_index = len(self.layer_manager.layers) - 1 - i
            item = QListWidgetItem()
            item.setText(f"{layer.name} {'🔒' if layer.locked else ''}")
            
            # Add thumbnail
            thumbnail = layer.get_thumbnail()
            item.setIcon(QIcon(thumbnail))
            
            self.layer_list.addItem(item)
            
            if actual_index == self.layer_manager.active_layer_index:
                self.layer_list.setCurrentRow(i)
    
    def on_layer_selected(self, row: int):
        """Handle layer selection"""
        if row >= 0:
            actual_index = len(self.layer_manager.layers) - 1 - row
            self.layer_manager.set_active_layer(actual_index)
            self.update_properties()
            self.active_layer_changed.emit(actual_index)
    
    def on_add_layer(self):
        """Handle add layer button"""
        # Create a blank white layer
        if self.layer_manager.layers:
            ref_layer = self.layer_manager.layers[0]
            h, w = ref_layer.image.shape[:2]
        else:
            h, w = 512, 512
            
        blank = np.ones((h, w, 3), dtype=np.uint8) * 255
        self.layer_manager.add_layer(f"Layer {len(self.layer_manager.layers) + 1}", blank)
        self.refresh_layer_list()
        self.layer_changed.emit()
    
    def on_remove_layer(self):
        """Handle remove layer button"""
        if len(self.layer_manager.layers) > 1:
            current_row = self.layer_list.currentRow()
            if current_row >= 0:
                actual_index = len(self.layer_manager.layers) - 1 - current_row
                self.layer_manager.remove_layer(actual_index)
                self.refresh_layer_list()
                self.layer_changed.emit()
    
    def on_move_up(self):
        """Move selected layer up"""
        current_row = self.layer_list.currentRow()
        if current_row > 0:
            actual_index = len(self.layer_manager.layers) - 1 - current_row
            if actual_index < len(self.layer_manager.layers) - 1:
                self.layer_manager.move_layer(actual_index, actual_index + 1)
                self.refresh_layer_list()
                self.layer_changed.emit()
    
    def on_move_down(self):
        """Move selected layer down"""
        current_row = self.layer_list.currentRow()
        if current_row < self.layer_list.count() - 1:
            actual_index = len(self.layer_manager.layers) - 1 - current_row
            if actual_index > 0:
                self.layer_manager.move_layer(actual_index, actual_index - 1)
                self.refresh_layer_list()
                self.layer_changed.emit()
    
    def on_opacity_changed(self, value: int):
        """Handle opacity slider change"""
        layer = self.layer_manager.get_active_layer()
        if layer:
            layer.opacity = value / 100.0
            self.layer_changed.emit()
    
    def on_blend_mode_changed(self, text: str):
        """Handle blend mode change"""
        layer = self.layer_manager.get_active_layer()
        if layer:
            for mode in BlendMode:
                if mode.value == text:
                    layer.blend_mode = mode
                    break
            self.layer_changed.emit()
    
    def on_visibility_changed(self, state: int):
        """Handle visibility checkbox change"""
        layer = self.layer_manager.get_active_layer()
        if layer:
            layer.visible = (state == Qt.Checked)
            self.layer_changed.emit()
    
    def on_scale_changed(self, value: int):
        """Handle scale slider change"""
        layer = self.layer_manager.get_active_layer()
        if layer:
            scale = value / 100.0
            layer.scale_x = scale
            layer.scale_y = scale
            self.scale_label.setText(f"{value}%")
            self.layer_manager._cache_valid = False
            self.layer_changed.emit()
    
    def on_rotation_changed(self, value: int):
        """Handle rotation slider change"""
        layer = self.layer_manager.get_active_layer()
        if layer:
            layer.rotation = float(value)
            self.rotation_label.setText(f"{value}°")
            self.layer_manager._cache_valid = False
            self.layer_changed.emit()
    
    def on_reset_transform(self):
        """Reset transform to default"""
        layer = self.layer_manager.get_active_layer()
        if layer:
            layer.scale_x = 1.0
            layer.scale_y = 1.0
            layer.rotation = 0.0
            layer.x_offset = 0
            layer.y_offset = 0
            
            self.scale_slider.blockSignals(True)
            self.rotation_slider.blockSignals(True)
            self.scale_slider.setValue(100)
            self.rotation_slider.setValue(0)
            self.scale_label.setText("100%")
            self.rotation_label.setText("0°")
            self.scale_slider.blockSignals(False)
            self.rotation_slider.blockSignals(False)
            
            self.layer_manager._cache_valid = False
            self.layer_changed.emit()
    
    def update_properties(self):
        """Update property widgets based on active layer"""
        layer = self.layer_manager.get_active_layer()
        if layer:
            self.opacity_slider.blockSignals(True)
            self.blend_mode_combo.blockSignals(True)
            self.visible_checkbox.blockSignals(True)
            self.scale_slider.blockSignals(True)
            self.rotation_slider.blockSignals(True)
            
            self.opacity_slider.setValue(int(layer.opacity * 100))
            self.blend_mode_combo.setCurrentText(layer.blend_mode.value)
            self.visible_checkbox.setChecked(layer.visible)
            self.scale_slider.setValue(int(layer.scale_x * 100))
            self.rotation_slider.setValue(int(layer.rotation))
            self.scale_label.setText(f"{int(layer.scale_x * 100)}%")
            self.rotation_label.setText(f"{int(layer.rotation)}°")
            
            self.opacity_slider.blockSignals(False)
            self.blend_mode_combo.blockSignals(False)
            self.visible_checkbox.blockSignals(False)
            self.scale_slider.blockSignals(False)
            self.rotation_slider.blockSignals(False)
    
    def apply_styles(self):
        """Apply stylesheet"""
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #e0e0e0;
            }
            
            #panelTitle {
                font-size: 12px;
                font-weight: bold;
                padding: 5px;
            }
            
            QPushButton {
                background-color: #3a3a3a;
                border: 1px solid #505050;
                border-radius: 3px;
                padding: 5px;
                color: #e0e0e0;
            }
            
            QPushButton:hover {
                background-color: #4a4a4a;
            }
            
            QPushButton:pressed {
                background-color: #2a2a2a;
            }
            
            QListWidget {
                background-color: #1e1e1e;
                border: 1px solid #3a3a3a;
                border-radius: 3px;
            }
            
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #2b2b2b;
            }
            
            QListWidget::item:selected {
                background-color: #0078d4;
            }
            
            QSlider::groove:horizontal {
                height: 4px;
                background: #3a3a3a;
                border-radius: 2px;
            }
            
            QSlider::handle:horizontal {
                background: #0078d4;
                width: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }
            
            QComboBox {
                background-color: #3a3a3a;
                border: 1px solid #505050;
                border-radius: 3px;
                padding: 3px 5px;
            }
            
            QComboBox:hover {
                border: 1px solid #0078d4;
            }
            
            QComboBox::drop-down {
                border: none;
            }
            
            QCheckBox {
                spacing: 5px;
            }
            
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #505050;
                border-radius: 3px;
                background-color: #3a3a3a;
            }
            
            QCheckBox::indicator:checked {
                background-color: #0078d4;
            }
        """)
