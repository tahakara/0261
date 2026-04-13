"""
Layer system for image/video editor.
Supports multiple layers with blending modes and opacity.
"""

from enum import Enum, auto
from typing import Optional, List, Callable
from dataclasses import dataclass, field
import numpy as np
import cv2
from PySide6.QtCore import QObject, Signal


class BlendMode(Enum):
    """Blending modes for layers."""
    NORMAL = auto()
    MULTIPLY = auto()
    SCREEN = auto()
    OVERLAY = auto()
    SOFT_LIGHT = auto()
    HARD_LIGHT = auto()
    DIFFERENCE = auto()
    ADD = auto()
    SUBTRACT = auto()


@dataclass
class Layer:
    """Represents a single layer in the editor."""
    
    name: str
    image: Optional[np.ndarray] = None
    visible: bool = True
    opacity: float = 1.0  # 0.0 to 1.0
    blend_mode: BlendMode = BlendMode.NORMAL
    locked: bool = False
    position: tuple = (0, 0)  # x, y offset
    
    _id: int = field(default_factory=lambda: id(object()))
    
    @property
    def id(self) -> int:
        return self._id
    
    @property
    def size(self) -> tuple:
        """Return (width, height) of the layer."""
        if self.image is not None:
            h, w = self.image.shape[:2]
            return (w, h)
        return (0, 0)
    
    @property
    def has_alpha(self) -> bool:
        """Check if layer has alpha channel."""
        if self.image is not None:
            return self.image.shape[2] == 4 if len(self.image.shape) == 3 else False
        return False
    
    def duplicate(self) -> 'Layer':
        """Create a copy of this layer."""
        return Layer(
            name=f"{self.name} (copy)",
            image=self.image.copy() if self.image is not None else None,
            visible=self.visible,
            opacity=self.opacity,
            blend_mode=self.blend_mode,
            locked=self.locked,
            position=self.position
        )
    
    def apply_opacity(self, image: np.ndarray) -> np.ndarray:
        """Apply layer opacity to image."""
        if self.opacity >= 1.0:
            return image
        return (image * self.opacity).astype(np.uint8)


class LayerManager(QObject):
    """
    Manages all layers in the project.
    Emits signals when layers change for UI updates.
    """
    
    # Signals
    layer_added = Signal(int)  # layer index
    layer_removed = Signal(int)  # layer index
    layer_moved = Signal(int, int)  # from_index, to_index
    layer_changed = Signal(int)  # layer index
    active_layer_changed = Signal(int)  # layer index
    layers_merged = Signal()
    
    def __init__(self):
        super().__init__()
        self._layers: List[Layer] = []
        self._active_index: int = -1
        self._canvas_size: tuple = (800, 600)  # default size
    
    @property
    def layers(self) -> List[Layer]:
        """Return list of all layers (bottom to top)."""
        return self._layers
    
    @property
    def layer_count(self) -> int:
        """Return number of layers."""
        return len(self._layers)
    
    @property
    def active_layer(self) -> Optional[Layer]:
        """Return the currently active layer."""
        if 0 <= self._active_index < len(self._layers):
            return self._layers[self._active_index]
        return None
    
    @property
    def active_index(self) -> int:
        """Return index of active layer."""
        return self._active_index
    
    @property
    def canvas_size(self) -> tuple:
        """Return (width, height) of canvas."""
        return self._canvas_size
    
    def set_canvas_size(self, width: int, height: int):
        """Set the canvas size."""
        old_w, old_h = self._canvas_size
        new_w, new_h = width, height
        if (new_w, new_h) == (old_w, old_h):
            return

        # Resize existing layer images to the new canvas size by placing them at their position
        for layer in self._layers:
            if layer.image is None:
                # create transparent image
                layer.image = np.zeros((new_h, new_w, 4), dtype=np.uint8)
                continue

            h, w = layer.image.shape[:2]
            # If sizes already match, continue
            if (w, h) == (new_w, new_h):
                continue

            # Create new transparent canvas
            new_img = np.zeros((new_h, new_w, 4), dtype=np.uint8)

            # Compute destination position using layer.position
            pos_x, pos_y = layer.position if hasattr(layer, 'position') else (0, 0)
            # Ensure positive positions
            pos_x = max(0, int(pos_x))
            pos_y = max(0, int(pos_y))

            # Determine region to copy
            copy_w = min(w, new_w - pos_x)
            copy_h = min(h, new_h - pos_y)
            if copy_w > 0 and copy_h > 0:
                new_img[pos_y:pos_y+copy_h, pos_x:pos_x+copy_w] = layer.image[0:copy_h, 0:copy_w]

            layer.image = new_img

        self._canvas_size = (new_w, new_h)
    
    def add_layer(self, layer: Layer, index: Optional[int] = None) -> int:
        """
        Add a layer at the specified index or on top.
        Returns the index where the layer was added.
        """
        if index is None:
            index = len(self._layers)
        
        self._layers.insert(index, layer)
        
        if self._active_index < 0:
            self._active_index = index
        elif index <= self._active_index:
            self._active_index += 1
            
        self.layer_added.emit(index)
        return index
    
    def create_layer(self, name: str = "New Layer", 
                     fill_color: Optional[tuple] = None) -> Layer:
        """Create and add a new empty layer."""
        w, h = self._canvas_size
        
        if fill_color:
            # Create BGRA image with fill color
            image = np.zeros((h, w, 4), dtype=np.uint8)
            image[:, :, 0] = fill_color[2]  # B
            image[:, :, 1] = fill_color[1]  # G
            image[:, :, 2] = fill_color[0]  # R
            image[:, :, 3] = fill_color[3] if len(fill_color) > 3 else 255  # A
        else:
            # Transparent layer
            image = np.zeros((h, w, 4), dtype=np.uint8)
        
        layer = Layer(name=name, image=image)
        self.add_layer(layer)
        return layer
    
    def remove_layer(self, index: int) -> Optional[Layer]:
        """Remove and return the layer at the specified index."""
        if not 0 <= index < len(self._layers):
            return None
        
        layer = self._layers.pop(index)
        
        if self._active_index >= len(self._layers):
            self._active_index = len(self._layers) - 1
        elif index < self._active_index:
            self._active_index -= 1
            
        self.layer_removed.emit(index)
        return layer
    
    def move_layer(self, from_index: int, to_index: int) -> bool:
        """Move a layer from one position to another."""
        if not (0 <= from_index < len(self._layers) and 
                0 <= to_index < len(self._layers)):
            return False
        
        layer = self._layers.pop(from_index)
        self._layers.insert(to_index, layer)
        
        # Update active index
        if self._active_index == from_index:
            self._active_index = to_index
        elif from_index < self._active_index <= to_index:
            self._active_index -= 1
        elif to_index <= self._active_index < from_index:
            self._active_index += 1
            
        self.layer_moved.emit(from_index, to_index)
        return True
    
    def set_active_layer(self, index: int) -> bool:
        """Set the active layer by index."""
        if 0 <= index < len(self._layers):
            self._active_index = index
            self.active_layer_changed.emit(index)
            return True
        return False
    
    def get_layer(self, index: int) -> Optional[Layer]:
        """Get layer by index."""
        if 0 <= index < len(self._layers):
            return self._layers[index]
        return None
    
    def get_layer_by_id(self, layer_id: int) -> Optional[Layer]:
        """Get layer by its unique ID."""
        for layer in self._layers:
            if layer.id == layer_id:
                return layer
        return None
    
    def duplicate_layer(self, index: int) -> Optional[Layer]:
        """Duplicate the layer at the specified index."""
        layer = self.get_layer(index)
        if layer:
            new_layer = layer.duplicate()
            self.add_layer(new_layer, index + 1)
            return new_layer
        return None
    
    def merge_down(self, index: int) -> bool:
        """Merge layer with the one below it."""
        if index <= 0 or index >= len(self._layers):
            return False
        
        upper = self._layers[index]
        lower = self._layers[index - 1]
        
        if upper.image is None or lower.image is None:
            return False
        
        # Simple alpha compositing
        merged = self._blend_layers(lower.image, upper.image, 
                                    upper.opacity, upper.blend_mode)
        lower.image = merged
        lower.name = f"{lower.name} + {upper.name}"
        
        self.remove_layer(index)
        self.layers_merged.emit()
        return True

    def merge_all(self) -> bool:
        """Merge all layers into a single layer (preserve canvas size).

        Returns True on success.
        """
        if not self._layers:
            return False

        # Use flatten (already optimized) to produce merged image
        merged = self.flatten()
        if merged is None:
            return False

        # Create new single layer with merged image
        merged_layer = Layer(name="Merged", image=merged)

        # Replace all layers with the merged one
        self._layers = [merged_layer]
        self._active_index = 0
        self.layers_merged.emit()
        return True
    
    def flatten(self) -> Optional[np.ndarray]:
        """Flatten all visible layers into a single image."""
        if not self._layers:
            return None

        w, h = self._canvas_size

        # Use float buffers for compositing to reduce repeated conversions
        result_rgb = np.zeros((h, w, 3), dtype=np.float32)
        result_alpha = np.zeros((h, w), dtype=np.float32)

        for layer in self._layers:
            if not layer.visible or layer.image is None:
                continue

            top = layer.image
            # Resize top to canvas if needed (rare)
            if top.shape[0] != h or top.shape[1] != w:
                top = cv2.resize(top, (w, h), interpolation=cv2.INTER_LINEAR)

            # Ensure top has 4 channels
            if top.shape[2] == 3:
                top = cv2.cvtColor(top, cv2.COLOR_BGR2BGRA)

            top_rgb = top[:, :, :3].astype(np.float32)
            top_alpha = (top[:, :, 3].astype(np.float32) / 255.0) * float(layer.opacity)

            # Skip fully transparent layer
            if np.all(top_alpha == 0):
                continue

            # Compute blended colors based on blend mode
            mode = layer.blend_mode
            if mode == BlendMode.NORMAL:
                blended = top_rgb
            elif mode == BlendMode.MULTIPLY:
                blended = (result_rgb * top_rgb) / 255.0
            elif mode == BlendMode.SCREEN:
                blended = 255.0 - ((255.0 - result_rgb) * (255.0 - top_rgb)) / 255.0
            elif mode == BlendMode.ADD:
                blended = np.minimum(result_rgb + top_rgb, 255.0)
            elif mode == BlendMode.SUBTRACT:
                blended = np.maximum(result_rgb - top_rgb, 0.0)
            else:
                # Fallback to normal for unimplemented modes
                blended = top_rgb

            # Alpha compositing (vectorized)
            top_a = top_alpha
            base_a = result_alpha

            out_a = top_a + base_a * (1.0 - top_a)
            # avoid division by zero
            out_a_safe = np.where(out_a > 0, out_a, 1.0)

            # Expand alpha dims for rgb ops
            top_a_exp = top_a[:, :, None]
            base_a_exp = base_a[:, :, None]
            out_a_exp = out_a_safe[:, :, None]

            out_rgb = (blended * top_a_exp + result_rgb * base_a_exp * (1.0 - top_a_exp)) / out_a_exp

            result_rgb = out_rgb
            result_alpha = out_a

        # Compose final uint8 image
        out = np.zeros((h, w, 4), dtype=np.uint8)
        out[:, :, :3] = np.clip(result_rgb, 0, 255).astype(np.uint8)
        out[:, :, 3] = np.clip(result_alpha * 255.0, 0, 255).astype(np.uint8)

        return out
    
    def _blend_layers(self, base: np.ndarray, top: np.ndarray,
                      opacity: float, mode: BlendMode) -> np.ndarray:
        """Blend two layers together."""
        # Ensure both images have alpha channel
        if base.shape[2] == 3:
            base = cv2.cvtColor(base, cv2.COLOR_BGR2BGRA)
        if top.shape[2] == 3:
            top = cv2.cvtColor(top, cv2.COLOR_BGR2BGRA)
        
        # Resize if necessary
        if base.shape[:2] != top.shape[:2]:
            top = cv2.resize(top, (base.shape[1], base.shape[0]))
        
        # Apply opacity
        top_alpha = top[:, :, 3:4].astype(float) / 255.0 * opacity
        base_alpha = base[:, :, 3:4].astype(float) / 255.0
        
        # Calculate blended colors based on blend mode
        top_rgb = top[:, :, :3].astype(float)
        base_rgb = base[:, :, :3].astype(float)
        
        if mode == BlendMode.NORMAL:
            blended = top_rgb
        elif mode == BlendMode.MULTIPLY:
            blended = (base_rgb * top_rgb) / 255.0
        elif mode == BlendMode.SCREEN:
            blended = 255.0 - ((255.0 - base_rgb) * (255.0 - top_rgb)) / 255.0
        elif mode == BlendMode.ADD:
            blended = np.minimum(base_rgb + top_rgb, 255.0)
        elif mode == BlendMode.SUBTRACT:
            blended = np.maximum(base_rgb - top_rgb, 0.0)
        else:
            blended = top_rgb
        
        # Alpha compositing
        out_alpha = top_alpha + base_alpha * (1 - top_alpha)
        out_alpha_safe = np.where(out_alpha > 0, out_alpha, 1)
        
        out_rgb = (blended * top_alpha + base_rgb * base_alpha * (1 - top_alpha)) / out_alpha_safe
        
        result = np.zeros_like(base)
        result[:, :, :3] = np.clip(out_rgb, 0, 255).astype(np.uint8)
        result[:, :, 3] = (out_alpha * 255).astype(np.uint8).squeeze()
        
        return result
    
    def clear(self):
        """Remove all layers."""
        self._layers.clear()
        self._active_index = -1
