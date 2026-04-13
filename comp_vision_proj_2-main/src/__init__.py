"""
Vision Editor - Plugin-Based Image and Video Processing Software
"""
__version__ = "1.0.0"
__author__ = "Vision Editor Team"

from src.plugin_base import PluginBase, ToolPlugin, EffectPlugin, FilterPlugin, AdjustmentPlugin
from src.plugin_manager import PluginManager
from src.layer_manager import LayerManager, LayerPanel, Layer
from src.canvas import ImageCanvas
from src.editor_window import EditorWindow
from src.launcher_window import LauncherWindow

__all__ = [
    "PluginBase",
    "ToolPlugin",
    "EffectPlugin",
    "FilterPlugin",
    "AdjustmentPlugin",
    "PluginManager",
    "LayerManager",
    "LayerPanel",
    "Layer",
    "ImageCanvas",
    "EditorWindow",
    "LauncherWindow",
]
