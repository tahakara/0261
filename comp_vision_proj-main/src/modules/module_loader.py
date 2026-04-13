"""
Module loader - Discovers and loads modules from the modules directory.
"""

from pathlib import Path
from typing import List, Dict, Type, Optional
import importlib
import inspect

from ..core.module_base import ModuleBase, ModuleCategory
from ..core.project import EditorMode


class ModuleLoader:
    """
    Discovers and loads modules from the modules directory.
    Modules are automatically discovered if they inherit from ModuleBase.
    """
    
    def __init__(self):
        self._modules: Dict[str, ModuleBase] = {}
        self._load_builtin_modules()
        self._discover_modules()
    
    def _load_builtin_modules(self):
        """Load built-in example modules."""
        # Import and instantiate built-in modules
        try:
            from .default_module import DefaultModule
            from .examples import BrightnessModule, ContrastModule, BlurModule
            
            # Add DefaultModule first
            default = DefaultModule()
            self._modules[default.name] = default
            
            for module_class in [BrightnessModule, ContrastModule, BlurModule]:
                instance = module_class()
                self._modules[instance.name] = instance
        except ImportError as e:
            print(f"Could not load built-in modules: {e}")
    
    def _discover_modules(self):
        """Discover modules in the modules directory."""
        modules_dir = Path(__file__).parent
        
        for path in modules_dir.glob("*.py"):
            if path.stem.startswith("_") or path.stem in ["module_loader", "examples"]:
                continue
            
            try:
                module_name = f"src.modules.{path.stem}"
                module = importlib.import_module(module_name)
                
                # Find classes that inherit from ModuleBase
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, ModuleBase) and obj is not ModuleBase:
                        instance = obj()
                        self._modules[instance.name] = instance
                        
            except Exception as e:
                print(f"Error loading module from {path}: {e}")
    
    def get_all_modules(self) -> List[ModuleBase]:
        """Get all loaded modules."""
        return list(self._modules.values())
    
    def get_modules_for_mode(self, mode: EditorMode) -> List[ModuleBase]:
        """Get modules appropriate for the given editor mode."""
        modules = []
        for module in self._modules.values():
            if mode == EditorMode.IMAGE and module.supports_image:
                modules.append(module)
            elif mode == EditorMode.VIDEO and module.supports_video:
                modules.append(module)
        
        # Sort by category and name
        modules.sort(key=lambda m: (m.category.value, m.name))
        return modules
    
    def get_modules_by_category(self, category: ModuleCategory) -> List[ModuleBase]:
        """Get all modules in a specific category."""
        return [m for m in self._modules.values() if m.category == category]
    
    def get_module(self, name: str) -> Optional[ModuleBase]:
        """Get a module by name."""
        return self._modules.get(name)
    
    def register_module(self, module: ModuleBase):
        """Manually register a module."""
        self._modules[module.name] = module
    
    def unregister_module(self, name: str):
        """Unregister a module by name."""
        if name in self._modules:
            del self._modules[name]
