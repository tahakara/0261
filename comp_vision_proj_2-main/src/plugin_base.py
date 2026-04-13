"""
Base Plugin Architecture for Image and Video Editor
Defines abstract base classes for all plugins
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from PySide6.QtWidgets import QWidget
import numpy as np


class PluginType:
    """Plugin type enumeration"""
    TOOL = "tool"
    EFFECT = "effect"
    FILTER = "filter"
    ADJUSTMENT = "adjustment"


class PluginBase(ABC):
    """Abstract base class for all plugins"""
    
    def __init__(self):
        self.name: str = "Base Plugin"
        self.version: str = "1.0.0"
        self.description: str = ""
        self.icon_path: Optional[str] = None
        self.plugin_type: str = PluginType.TOOL
        self.enabled: bool = True
        
    @abstractmethod
    def get_name(self) -> str:
        """Returns the plugin name"""
        pass
    
    @abstractmethod
    def get_icon(self) -> str:
        """Returns the path to plugin icon"""
        pass
    
    @abstractmethod
    def get_settings_widget(self) -> Optional[QWidget]:
        """Returns a QWidget for plugin settings UI"""
        pass
    
    @abstractmethod
    def execute(self, image: np.ndarray, **kwargs) -> np.ndarray:
        """
        Execute the plugin operation on the image
        
        Args:
            image: OpenCV image (numpy array)
            **kwargs: Additional parameters
            
        Returns:
            Processed image as numpy array
        """
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """Returns plugin metadata"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "type": self.plugin_type,
            "enabled": self.enabled
        }


class ToolPlugin(PluginBase):
    """Base class for tool plugins (brush, selection, etc.)"""
    
    def __init__(self):
        super().__init__()
        self.plugin_type = PluginType.TOOL
        self.cursor_icon: Optional[str] = None
        
    @abstractmethod
    def on_mouse_press(self, x: int, y: int, image: np.ndarray) -> np.ndarray:
        """Handle mouse press event"""
        pass
    
    @abstractmethod
    def on_mouse_move(self, x: int, y: int, image: np.ndarray) -> np.ndarray:
        """Handle mouse move event"""
        pass
    
    @abstractmethod
    def on_mouse_release(self, x: int, y: int, image: np.ndarray) -> np.ndarray:
        """Handle mouse release event"""
        pass


class EffectPlugin(PluginBase):
    """Base class for effect plugins (blur, sharpen, etc.)"""
    
    def __init__(self):
        super().__init__()
        self.plugin_type = PluginType.EFFECT
        self.real_time_preview: bool = True
        
    @abstractmethod
    def apply_effect(self, image: np.ndarray, **params) -> np.ndarray:
        """Apply effect to the image"""
        pass
    
    def execute(self, image: np.ndarray, **kwargs) -> np.ndarray:
        """Execute wraps apply_effect"""
        return self.apply_effect(image, **kwargs)


class FilterPlugin(PluginBase):
    """Base class for filter plugins (color filters, etc.)"""
    
    def __init__(self):
        super().__init__()
        self.plugin_type = PluginType.FILTER
        
    @abstractmethod
    def apply_filter(self, image: np.ndarray, **params) -> np.ndarray:
        """Apply filter to the image"""
        pass
    
    def execute(self, image: np.ndarray, **kwargs) -> np.ndarray:
        """Execute wraps apply_filter"""
        return self.apply_filter(image, **kwargs)


class AdjustmentPlugin(PluginBase):
    """Base class for adjustment plugins (brightness, contrast, etc.)"""
    
    def __init__(self):
        super().__init__()
        self.plugin_type = PluginType.ADJUSTMENT
        
    @abstractmethod
    def apply_adjustment(self, image: np.ndarray, **params) -> np.ndarray:
        """Apply adjustment to the image"""
        pass
    
    def execute(self, image: np.ndarray, **kwargs) -> np.ndarray:
        """Execute wraps apply_adjustment"""
        return self.apply_adjustment(image, **kwargs)
