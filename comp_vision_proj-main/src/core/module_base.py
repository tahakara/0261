"""
Base class for all modules (effects and tools).
All modules should inherit from ModuleBase.
"""

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Optional, Dict, Any, List
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QIcon
import numpy as np


class ModuleCategory(Enum):
    """Categories for organizing modules in the sidebar."""
    TOOL = auto()           # Selection, brush, eraser, etc.
    ADJUSTMENT = auto()     # Brightness, contrast, levels, etc.
    FILTER = auto()         # Blur, sharpen, noise, etc.
    EFFECT = auto()         # Artistic effects
    TRANSFORM = auto()      # Rotate, scale, crop, etc.
    COLOR = auto()          # Color correction, grading
    VIDEO = auto()          # Video-specific tools
    OTHER = auto()


class ModuleBase(ABC):
    """
    Abstract base class for all editor modules.
    
    To create a new module:
    1. Create a new class inheriting from ModuleBase
    2. Implement all abstract methods
    3. Place the file in src/modules/
    4. The module will be automatically discovered and loaded
    
    Example:
        class BrightnessModule(ModuleBase):
            @property
            def name(self) -> str:
                return "Brightness"
            
            @property
            def category(self) -> ModuleCategory:
                return ModuleCategory.ADJUSTMENT
            
            def get_settings_widget(self) -> QWidget:
                # Return widget with brightness slider
                pass
            
            def apply(self, image: np.ndarray, **params) -> np.ndarray:
                # Apply brightness adjustment
                pass
    """
    
    def __init__(self):
        self._is_active = False
        self._settings_widget: Optional[QWidget] = None
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the display name of the module."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Return a brief description of what the module does."""
        pass
    
    @property
    @abstractmethod
    def category(self) -> ModuleCategory:
        """Return the category this module belongs to."""
        pass
    
    @property
    def icon(self) -> Optional[QIcon]:
        """Return an optional icon for the module."""
        return None
    
    @property
    def supports_image(self) -> bool:
        """Return True if this module supports image editing."""
        return True
    
    @property
    def supports_video(self) -> bool:
        """Return True if this module supports video editing."""
        return False
    
    @property
    def is_active(self) -> bool:
        """Return True if this module is currently active."""
        return self._is_active
    
    def activate(self):
        """Called when the module is activated/selected."""
        self._is_active = True
        self.on_activate()
    
    def deactivate(self):
        """Called when the module is deactivated."""
        self._is_active = False
        self.on_deactivate()
    
    def on_activate(self):
        """Override to perform actions when module is activated."""
        pass
    
    def on_deactivate(self):
        """Override to perform actions when module is deactivated."""
        pass
    
    @abstractmethod
    def get_settings_widget(self) -> Optional[QWidget]:
        """
        Return a widget containing the module's settings/controls.
        This widget will be displayed in the right sidebar.
        Return None if no settings are needed.
        """
        pass
    
    @abstractmethod
    def apply(self, image: np.ndarray, **params) -> np.ndarray:
        """
        Apply the module's effect to the image.
        
        Args:
            image: Input image as numpy array (BGR format from OpenCV)
            **params: Additional parameters specific to the module
            
        Returns:
            Processed image as numpy array
        """
        pass
    
    def apply_to_frame(self, frame: np.ndarray, frame_index: int, **params) -> np.ndarray:
        """
        Apply the module's effect to a video frame.
        Override this for video-specific processing.
        
        Args:
            frame: Input frame as numpy array
            frame_index: Index of the frame in the video
            **params: Additional parameters
            
        Returns:
            Processed frame as numpy array
        """
        return self.apply(frame, **params)
    
    def get_default_params(self) -> Dict[str, Any]:
        """Return default parameters for this module."""
        return {}
    
    def validate_params(self, params: Dict[str, Any]) -> bool:
        """Validate the given parameters. Return True if valid."""
        return True
    
    def get_preview(self, image: np.ndarray, **params) -> np.ndarray:
        """
        Generate a preview of the effect (can be lower quality for speed).
        Override for custom preview behavior.
        """
        return self.apply(image, **params)
    
    def on_canvas_mouse_press(self, x: int, y: int, button: int):
        """Handle mouse press on canvas. Override for interactive tools."""
        pass
    
    def on_canvas_mouse_move(self, x: int, y: int):
        """Handle mouse move on canvas. Override for interactive tools."""
        pass
    
    def on_canvas_mouse_release(self, x: int, y: int, button: int):
        """Handle mouse release on canvas. Override for interactive tools."""
        pass
    
    def on_canvas_key_press(self, key: int):
        """Handle key press. Override for keyboard shortcuts."""
        pass
