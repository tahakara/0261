# Quick Start Guide - Vision Editor

## Installation

1. **Install Python 3.9+** (if not already installed)
   - Download from: https://www.python.org/downloads/

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

```bash
python main.py
```

## First Steps

### 1. Select Editor Mode
- Choose **Image Editor** or **Video Editor** from the launcher

### 2. Create or Open a Project
- **New Project**: `File → New` or `Ctrl+N`
- **Open Image**: `File → Open` or `Ctrl+O`

### 3. Use Tools
- Click a tool from the **left sidebar** (Toolbox)
- Adjust settings in the **top-right panel**
- Draw/apply on the canvas

### 4. Manage Layers
- View layers in the **bottom-right panel**
- Add layers with the `+` button
- Adjust opacity and blend modes
- Toggle visibility with the checkbox

### 5. Apply Effects
- Select an effect plugin (Blur, Sharpen, etc.)
- Adjust parameters in tool settings
- Click on the canvas to apply

### 6. Save Your Work
- **Save**: `File → Save` or `Ctrl+S`
- **Save As**: `File → Save As` or `Ctrl+Shift+S`

## Canvas Controls

- **Zoom In/Out**: Mouse wheel or `Ctrl +/-`
- **Pan**: Middle mouse button drag or `Shift + drag`
- **Fit to Window**: `Ctrl+0`
- **Reset View**: `Ctrl+R`

## Tips

1. **Layer Workflow**: Create new layers for non-destructive editing
2. **Blend Modes**: Experiment with different blend modes for creative effects
3. **Tool Settings**: Always check the tool settings panel when switching tools
4. **Keyboard Shortcuts**: Learn shortcuts for faster workflow

## Example Workflow

### Basic Image Edit

1. Open an image (`Ctrl+O`)
2. Select **Brush Tool** from left sidebar
3. Adjust brush size and color in tool settings
4. Paint on the canvas
5. Add a new layer for more edits
6. Apply **Blur Effect** if needed
7. Save your work (`Ctrl+S`)

### Creating a Composite

1. Create new project (`Ctrl+N`)
2. Open base image
3. Add new layer (`+` button in layer panel)
4. Paint or import on new layer
5. Adjust layer opacity and blend mode
6. Experiment with different layer orders
7. Export final composite

## Troubleshooting

### Application won't start
- Ensure Python 3.9+ is installed
- Verify all dependencies are installed: `pip install -r requirements.txt`

### Plugins not loading
- Check that plugin files are in the `plugins/` directory
- Verify plugin files don't have syntax errors
- Use `Plugins → Reload Plugins` to reload

### Performance issues
- Close unused applications
- Work with smaller images for better performance
- Reduce number of layers if possible

## Creating Your First Plugin

Create a file in `plugins/` directory:

```python
# plugins/my_plugin.py
from src.plugin_base import EffectPlugin
import cv2

class MyPlugin(EffectPlugin):
    def __init__(self):
        super().__init__()
        self.name = "My Plugin"
        
    def get_name(self):
        return self.name
    
    def get_icon(self):
        return ""
    
    def get_settings_widget(self):
        return None
    
    def apply_effect(self, image, **params):
        # Your image processing here
        return image
```

Restart the app or use `Plugins → Reload Plugins`

---

**Happy Editing!** 🎨
