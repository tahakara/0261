# Developer Guide - Vision Editor

## Getting Started with Development

### Setting Up Development Environment

1. **Clone the repository**
```bash
git clone <repository-url>
cd comp_vision_proj
```

2. **Create virtual environment (recommended)**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
python main.py
```

---

## Project Structure

```
comp_vision_proj/
├── main.py                          # Application entry point
├── requirements.txt                 # Python dependencies
├── config.ini                       # Configuration file
├── .gitignore                       # Git ignore rules
│
├── README.md                        # Project overview
├── QUICKSTART.md                    # Quick start guide
├── ARCHITECTURE.md                  # Architecture documentation
├── DEVELOPER_GUIDE.md              # This file
│
├── src/                            # Core source code
│   ├── __init__.py                 # Package initialization
│   ├── launcher_window.py          # Welcome/launcher screen
│   ├── editor_window.py            # Main editor window
│   ├── canvas.py                   # Canvas rendering system
│   ├── layer_manager.py            # Layer management
│   ├── plugin_base.py              # Plugin base classes
│   └── plugin_manager.py           # Plugin loading/management
│
├── plugins/                        # Plugin directory
│   ├── __init__.py
│   ├── brush_tool.py               # Brush tool plugin
│   ├── blur_effect.py              # Blur effect plugin
│   ├── brightness_adjustment.py    # Brightness plugin
│   └── sharpen_filter.py           # Sharpen filter plugin
│
└── assets/                         # Static assets (icons, images)
```

---

## Core Components Deep Dive

### 1. Main Application (main.py)

**Responsibilities:**
- Initialize Qt application
- Show launcher window
- Handle mode selection
- Create and show editor window

**Key Methods:**
- `run()`: Start application event loop
- `on_mode_selected(mode)`: Handle editor mode selection

### 2. Launcher Window (launcher_window.py)

**Responsibilities:**
- Display welcome screen
- Mode selection UI
- Emit signals for mode selection

**Key Signals:**
- `mode_selected(str)`: Emitted when user selects mode

**Customization Points:**
- `apply_styles()`: Modify appearance
- `_create_mode_button()`: Change button design

### 3. Editor Window (editor_window.py)

**Responsibilities:**
- Main editing interface
- Menu and toolbar management
- Plugin coordination
- File operations
- Canvas and panel integration

**Key Methods:**
- `setup_ui()`: Initialize UI components
- `load_plugins()`: Load and populate plugin buttons
- `on_plugin_selected(plugin)`: Handle plugin activation
- `on_layer_changed()`: Update canvas when layers change

**Customization Points:**
- `create_menu_bar()`: Add menu items
- `create_toolbar()`: Add toolbar actions
- `apply_styles()`: Change theme

### 4. Canvas (canvas.py)

**Responsibilities:**
- High-performance image rendering
- Zoom and pan functionality
- Mouse event handling
- OpenCV ↔ QPixmap conversion

**Key Methods:**
- `load_image(image)`: Load new image
- `update_image(image)`: Update displayed image
- `numpy_to_pixmap(image)`: Convert OpenCV to Qt
- `zoom_in()`, `zoom_out()`: Zoom controls

**Signals:**
- `mouse_pressed(int, int)`: Mouse press with coordinates
- `mouse_moved(int, int)`: Mouse move with coordinates
- `mouse_released(int, int)`: Mouse release with coordinates
- `zoom_changed(float)`: Zoom level changed

### 5. Layer Manager (layer_manager.py)

**Responsibilities:**
- Layer stack management
- Layer compositing
- Blend mode implementation
- Layer properties management

**Key Classes:**
- `Layer`: Data class for layer properties
- `LayerManager`: Layer stack management
- `LayerPanel`: UI for layer management
- `BlendMode`: Enum for blend modes

**Key Methods:**
- `add_layer()`: Add new layer
- `remove_layer()`: Remove layer
- `composite_layers()`: Composite all layers
- `_blend_layers()`: Blend two layers

### 6. Plugin System (plugin_base.py, plugin_manager.py)

**Base Classes:**
- `PluginBase`: Abstract base for all plugins
- `ToolPlugin`: Interactive tools
- `EffectPlugin`: Image effects
- `FilterPlugin`: Image filters
- `AdjustmentPlugin`: Image adjustments

**Plugin Manager Methods:**
- `discover_plugins()`: Find plugin files
- `load_plugin()`: Load single plugin
- `load_all_plugins()`: Load all plugins
- `get_plugin()`: Get plugin by name
- `get_plugins_by_type()`: Get plugins by type

---

## Creating Plugins

### Plugin Development Workflow

1. **Choose Plugin Type**
   - ToolPlugin: Interactive tools (brush, selection)
   - EffectPlugin: Effects (blur, sharpen)
   - FilterPlugin: Filters (color grading)
   - AdjustmentPlugin: Adjustments (brightness, contrast)

2. **Create Plugin File**
   - Place in `plugins/` directory
   - Name: `<plugin_name>.py`

3. **Implement Required Methods**
   - `get_name()`: Return plugin name
   - `get_icon()`: Return icon path (optional)
   - `get_settings_widget()`: Return settings UI
   - `execute()` or type-specific method

4. **Test Plugin**
   - Restart application
   - Or use "Plugins → Reload Plugins"

### Example: Creating an Effect Plugin

```python
# plugins/my_effect.py
import numpy as np
import cv2
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider
from PySide6.QtCore import Qt

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.plugin_base import EffectPlugin


class MyEffect(EffectPlugin):
    def __init__(self):
        super().__init__()
        self.name = "My Effect"
        self.version = "1.0.0"
        self.description = "My custom effect"
        self.icon_path = None
        self.strength = 50
        
    def get_name(self) -> str:
        return self.name
    
    def get_icon(self) -> str:
        return self.icon_path or ""
    
    def get_settings_widget(self) -> QWidget:
        """Create settings UI"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Add controls
        label = QLabel("Strength:")
        slider = QSlider(Qt.Horizontal)
        slider.setRange(0, 100)
        slider.setValue(self.strength)
        slider.valueChanged.connect(self.on_strength_changed)
        
        layout.addWidget(label)
        layout.addWidget(slider)
        layout.addStretch()
        
        return widget
    
    def on_strength_changed(self, value: int):
        self.strength = value
    
    def apply_effect(self, image: np.ndarray, **params) -> np.ndarray:
        """Apply effect to image"""
        # Your image processing code here
        result = image.copy()
        
        # Example: Adjust intensity
        factor = self.strength / 50.0
        result = cv2.convertScaleAbs(image, alpha=factor, beta=0)
        
        return result
```

### Example: Creating a Tool Plugin

```python
# plugins/my_tool.py
import numpy as np
import cv2
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.plugin_base import ToolPlugin


class MyTool(ToolPlugin):
    def __init__(self):
        super().__init__()
        self.name = "My Tool"
        self.version = "1.0.0"
        self.description = "My custom tool"
        
        # Tool state
        self.is_active = False
        
    def get_name(self) -> str:
        return self.name
    
    def get_icon(self) -> str:
        return ""
    
    def get_settings_widget(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel("My Tool Settings"))
        return widget
    
    def execute(self, image: np.ndarray, **kwargs) -> np.ndarray:
        return image
    
    def on_mouse_press(self, x: int, y: int, image: np.ndarray) -> np.ndarray:
        """Handle mouse press"""
        self.is_active = True
        result = image.copy()
        # Draw at click position
        cv2.circle(result, (x, y), 5, (255, 0, 0), -1)
        return result
    
    def on_mouse_move(self, x: int, y: int, image: np.ndarray) -> np.ndarray:
        """Handle mouse move"""
        if self.is_active:
            result = image.copy()
            cv2.circle(result, (x, y), 5, (255, 0, 0), -1)
            return result
        return None
    
    def on_mouse_release(self, x: int, y: int, image: np.ndarray) -> np.ndarray:
        """Handle mouse release"""
        self.is_active = False
        return None
```

---

## Best Practices

### Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings to classes and methods
- Keep functions small and focused

### Plugin Development
- Always inherit from appropriate base class
- Handle errors gracefully
- Test with various image sizes
- Clean up resources properly
- Document plugin parameters

### Performance
- Use numpy vectorized operations
- Avoid unnecessary image copies
- Cache computed results when possible
- Profile performance-critical code

### UI Development
- Keep UI responsive
- Use Qt signals/slots for communication
- Apply consistent styling
- Provide meaningful tooltips

---

## Testing

### Manual Testing Checklist

**Basic Functionality:**
- [ ] Application launches successfully
- [ ] Mode selection works
- [ ] File operations (New, Open, Save)
- [ ] Canvas zoom/pan works
- [ ] Layers can be added/removed
- [ ] Plugins load correctly

**Plugin Testing:**
- [ ] Plugin appears in toolbox
- [ ] Plugin settings display correctly
- [ ] Plugin executes without errors
- [ ] Results appear on canvas
- [ ] Multiple plugins work together

**Layer Testing:**
- [ ] Layers composite correctly
- [ ] Blend modes work as expected
- [ ] Opacity adjustment works
- [ ] Layer reordering works
- [ ] Layer visibility toggles

### Automated Testing (Future)

```python
# Example test structure
import unittest
from src.layer_manager import LayerManager
import numpy as np

class TestLayerManager(unittest.TestCase):
    def setUp(self):
        self.manager = LayerManager()
        
    def test_add_layer(self):
        img = np.ones((100, 100, 3), dtype=np.uint8) * 255
        layer = self.manager.add_layer("Test", img)
        self.assertEqual(len(self.manager.layers), 1)
        self.assertEqual(layer.name, "Test")
        
    def test_composite(self):
        img1 = np.ones((100, 100, 3), dtype=np.uint8) * 255
        img2 = np.ones((100, 100, 3), dtype=np.uint8) * 128
        
        self.manager.add_layer("Layer1", img1)
        self.manager.add_layer("Layer2", img2)
        
        result = self.manager.composite_layers()
        self.assertIsNotNone(result)
        self.assertEqual(result.shape, (100, 100, 3))
```

---

## Debugging

### Common Issues

**Plugin Not Loading:**
- Check file location (must be in `plugins/` directory)
- Verify syntax errors
- Ensure class inherits from plugin base
- Check `__init__` method

**Image Not Displaying:**
- Verify image format (OpenCV BGR)
- Check image dimensions
- Ensure numpy array type is uint8
- Look for conversion errors

**Performance Issues:**
- Profile with cProfile
- Check for excessive copying
- Look for inefficient loops
- Monitor memory usage

### Debug Mode

Add debug prints in key locations:

```python
# In plugin
def apply_effect(self, image, **params):
    print(f"[DEBUG] Applying {self.name}")
    print(f"[DEBUG] Image shape: {image.shape}")
    print(f"[DEBUG] Parameters: {params}")
    
    result = self.process(image)
    
    print(f"[DEBUG] Result shape: {result.shape}")
    return result
```

---

## Contributing

### Contribution Workflow

1. **Fork the repository**
2. **Create feature branch**
   ```bash
   git checkout -b feature/my-feature
   ```
3. **Make changes**
   - Add features/fixes
   - Test thoroughly
   - Update documentation
4. **Commit changes**
   ```bash
   git add .
   git commit -m "Add: My feature description"
   ```
5. **Push to fork**
   ```bash
   git push origin feature/my-feature
   ```
6. **Create pull request**

### Commit Message Guidelines

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Prefix with type: Add, Fix, Update, Remove, Refactor
- Keep first line under 50 characters
- Add detailed description if needed

Examples:
- `Add: Gaussian blur effect plugin`
- `Fix: Layer opacity not applying correctly`
- `Update: Improve canvas rendering performance`
- `Remove: Deprecated blend mode`

---

## Advanced Topics

### Adding New Blend Modes

1. Add to `BlendMode` enum in [layer_manager.py](layer_manager.py):
```python
class BlendMode(Enum):
    # ... existing modes
    LIGHTEN = "Lighten"
```

2. Implement in `_blend_layers()`:
```python
elif blend_mode == BlendMode.LIGHTEN:
    result = np.maximum(base_float, overlay_float)
    result = base_float * (1 - opacity) + result * opacity
```

### Adding Configuration Support

Read from `config.ini`:
```python
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

default_width = config.getint('Canvas', 'default_width')
```

### Adding Keyboard Shortcuts

In `editor_window.py`:
```python
# In create_menu_bar or similar
my_action = QAction("My Action", self)
my_action.setShortcut("Ctrl+M")
my_action.triggered.connect(self.on_my_action)
```

---

## Resources

### Documentation
- [PySide6 Docs](https://doc.qt.io/qtforpython/)
- [OpenCV Docs](https://docs.opencv.org/)
- [NumPy Docs](https://numpy.org/doc/)

### Tutorials
- Qt Graphics View Framework
- OpenCV Image Processing
- Python Plugin Systems

### Tools
- Qt Designer for UI mockups
- cProfile for performance profiling
- pytest for unit testing

---

## Support

- **Issues**: Report bugs and feature requests
- **Discussions**: Ask questions and share ideas
- **Documentation**: Help improve documentation
- **Code Review**: Review pull requests

---

**Happy Coding!** 🚀
