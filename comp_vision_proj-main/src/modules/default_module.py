"""
Default/None module - represents no module selected state.
"""

import numpy as np
from ..core.module_base import ModuleBase, ModuleCategory


class DefaultModule(ModuleBase):
    """
    A placeholder module that represents 'no module selected'.
    When this module is active, no effects are applied.
    """
    
    def __init__(self):
        super().__init__()
    
    @property
    def name(self) -> str:
        """Return the display name."""
        return "None"
    
    @property
    def description(self) -> str:
        """Return the description."""
        return "No module selected - clear current selection"
    
    @property
    def category(self) -> ModuleCategory:
        """Return the category."""
        return ModuleCategory.OTHER
    
    @property
    def supports_image(self) -> bool:
        """Support image mode."""
        return True
    
    @property
    def supports_video(self) -> bool:
        """Support video mode."""
        return True
    
    def apply(self, image: np.ndarray, **params) -> np.ndarray:
        """Return the image unchanged."""
        return image.copy()
    
    def get_default_params(self) -> dict:
        """No parameters needed."""
        return {}
    
    def get_settings_widget(self):
        """No settings widget for default module."""
        return None
