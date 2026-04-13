"""
Plugin Manager - Handles dynamic loading and management of plugins
"""
import os
import sys
import importlib.util
import inspect
from typing import Dict, List, Type, Optional
from pathlib import Path
from src.plugin_base import PluginBase, PluginType, ToolPlugin, EffectPlugin, FilterPlugin, AdjustmentPlugin


class PluginManager:
    """Manages plugin discovery, loading, and lifecycle"""
    
    def __init__(self, plugin_directory: str = "plugins"):
        self.plugin_directory = Path(plugin_directory)
        self.plugins: Dict[str, PluginBase] = {}
        self.plugin_classes: Dict[str, Type[PluginBase]] = {}
        
    def discover_plugins(self) -> List[str]:
        """
        Discover all plugins in the plugin directory
        
        Returns:
            List of discovered plugin module names
        """
        discovered = []
        
        if not self.plugin_directory.exists():
            print(f"Plugin directory '{self.plugin_directory}' does not exist")
            return discovered
        
        # Look for Python files in plugin directory and subdirectories
        for plugin_file in self.plugin_directory.rglob("*.py"):
            if plugin_file.name.startswith("__"):
                continue
                
            module_name = plugin_file.stem
            discovered.append(str(plugin_file))
            
        return discovered
    
    def load_plugin(self, plugin_path: str) -> Optional[PluginBase]:
        """
        Load a single plugin from file path
        
        Args:
            plugin_path: Path to plugin Python file
            
        Returns:
            Instantiated plugin or None if loading failed
        """
        try:
            # Load the module dynamically
            spec = importlib.util.spec_from_file_location(
                f"plugin_{Path(plugin_path).stem}", 
                plugin_path
            )
            if spec is None or spec.loader is None:
                print(f"Failed to load plugin spec: {plugin_path}")
                return None
                
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)
            
            # Define base classes to exclude
            base_classes = (PluginBase, ToolPlugin, EffectPlugin, FilterPlugin, AdjustmentPlugin)
            
            # Find PluginBase subclasses in the module
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                
                # Check if it's a class and a subclass of PluginBase
                # Exclude abstract base classes and check if it's not abstract
                if (isinstance(attr, type) and 
                    issubclass(attr, PluginBase) and 
                    attr not in base_classes and
                    not inspect.isabstract(attr)):
                    
                    # Instantiate the plugin
                    plugin_instance = attr()
                    plugin_name = plugin_instance.get_name()
                    
                    # Store both class and instance
                    self.plugin_classes[plugin_name] = attr
                    self.plugins[plugin_name] = plugin_instance
                    
                    print(f"Loaded plugin: {plugin_name} ({plugin_instance.plugin_type})")
                    return plugin_instance
                    
        except Exception as e:
            print(f"Error loading plugin {plugin_path}: {str(e)}")
            
        return None
    
    def load_all_plugins(self) -> int:
        """
        Discover and load all plugins
        
        Returns:
            Number of successfully loaded plugins
        """
        discovered = self.discover_plugins()
        loaded_count = 0
        
        for plugin_path in discovered:
            if self.load_plugin(plugin_path):
                loaded_count += 1
                
        print(f"Loaded {loaded_count} plugins from {len(discovered)} discovered")
        return loaded_count
    
    def get_plugin(self, plugin_name: str) -> Optional[PluginBase]:
        """Get a plugin instance by name"""
        return self.plugins.get(plugin_name)
    
    def get_plugins_by_type(self, plugin_type: str) -> List[PluginBase]:
        """Get all plugins of a specific type"""
        return [
            plugin for plugin in self.plugins.values()
            if plugin.plugin_type == plugin_type
        ]
    
    def get_all_plugins(self) -> List[PluginBase]:
        """Get all loaded plugins"""
        return list(self.plugins.values())
    
    def reload_plugin(self, plugin_name: str) -> bool:
        """Reload a specific plugin"""
        if plugin_name not in self.plugins:
            print(f"Plugin '{plugin_name}' not found")
            return False
            
        # Find the plugin file and reload it
        for plugin_path in self.discover_plugins():
            plugin = self.load_plugin(plugin_path)
            if plugin and plugin.get_name() == plugin_name:
                print(f"Reloaded plugin: {plugin_name}")
                return True
                
        return False
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin"""
        if plugin_name in self.plugins:
            del self.plugins[plugin_name]
            if plugin_name in self.plugin_classes:
                del self.plugin_classes[plugin_name]
            print(f"Unloaded plugin: {plugin_name}")
            return True
        return False
    
    def get_plugin_info(self) -> List[Dict]:
        """Get information about all loaded plugins"""
        return [plugin.get_metadata() for plugin in self.plugins.values()]
