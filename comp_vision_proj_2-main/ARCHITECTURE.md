# Vision Editor - Architecture Documentation

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      Vision Editor                           │
│                    (main.py - Entry Point)                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│                  Launcher Window                            │
│              (launcher_window.py)                           │
│  ┌──────────────────┐     ┌──────────────────┐            │
│  │  Image Editor    │     │  Video Editor    │            │
│  │     Mode         │     │     Mode         │            │
│  └──────────────────┘     └──────────────────┘            │
└────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│                  Editor Window                              │
│               (editor_window.py)                            │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  Top Menu Bar & Toolbar                              │  │
│  │  (File, Edit, View, Plugins, Help)                  │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────┐  ┌──────────────────────┐  ┌────────────────┐  │
│  │      │  │                       │  │  Tool Settings │  │
│  │ Tool │  │   Canvas (Center)     │  │    Panel       │  │
│  │ Box  │  │                       │  │   (Dynamic)    │  │
│  │      │  │  ┌──────────────┐    │  ├────────────────┤  │
│  │Left  │  │  │ QGraphicsView│    │  │     Layer      │  │
│  │Side  │  │  │              │    │  │   Management   │  │
│  │bar   │  │  │   OpenCV     │    │  │     Panel      │  │
│  │      │  │  │   Rendering  │    │  │                │  │
│  │      │  │  └──────────────┘    │  │  (Layers List) │  │
│  └──────┘  └──────────────────────┘  └────────────────┘  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  Status Bar (Tool, Zoom, Position, Image Info)      │  │
│  └─────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
```

## Component Architecture

### 1. Core Components

#### Main Application (main.py)
- Entry point for the application
- Manages application lifecycle
- Coordinates between launcher and editor

#### Launcher Window (launcher_window.py)
- Welcome screen
- Mode selection (Image/Video)
- Smooth transition to editor

#### Editor Window (editor_window.py)
- Main editing interface
- Manages all UI panels
- Coordinates plugin system
- Handles file operations

### 2. Canvas System (canvas.py)

```
┌─────────────────────────────────────┐
│       ImageCanvas                   │
│   (QGraphicsView)                   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │    QGraphicsScene           │   │
│  │                             │   │
│  │  ┌─────────────────────┐   │   │
│  │  │ QGraphicsPixmapItem │   │   │
│  │  │  (OpenCV → QPixmap) │   │   │
│  │  └─────────────────────┘   │   │
│  └─────────────────────────────┘   │
│                                     │
│  Features:                          │
│  • High-performance rendering       │
│  • Zoom & Pan                       │
│  • Mouse event handling             │
│  • OpenCV Mat ↔ QPixmap conversion │
└─────────────────────────────────────┘
```

### 3. Layer System (layer_manager.py)

```
┌────────────────────────────────────────┐
│         Layer Manager                  │
│                                        │
│  Layer Stack (Top to Bottom):         │
│  ┌──────────────────────────────┐     │
│  │ Layer 3 (Visible, 80%)       │     │
│  ├──────────────────────────────┤     │
│  │ Layer 2 (Hidden, 100%)       │     │
│  ├──────────────────────────────┤     │
│  │ Layer 1 (Visible, 60%)       │     │
│  ├──────────────────────────────┤     │
│  │ Background (Visible, 100%)   │     │
│  └──────────────────────────────┘     │
│                                        │
│  Compositing Pipeline:                 │
│  1. Start with bottom layer            │
│  2. Apply blend mode & opacity         │
│  3. Composite with layer above         │
│  4. Repeat until top layer             │
│  5. Return final composited image      │
│                                        │
│  Layer Properties:                     │
│  • Name                                │
│  • Image (OpenCV Mat)                  │
│  • Visibility                          │
│  • Opacity (0-100%)                    │
│  • Blend Mode                          │
│  • Locked state                        │
│  • Thumbnail                           │
└────────────────────────────────────────┘
```

### 4. Plugin System Architecture

```
┌─────────────────────────────────────────────────────────┐
│               Plugin Manager                             │
│            (plugin_manager.py)                           │
│                                                          │
│  Functions:                                              │
│  • Discover plugins (scan plugins/ directory)           │
│  • Load plugins dynamically                             │
│  • Manage plugin lifecycle                              │
│  • Provide plugin metadata                              │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│               Plugin Base Classes                        │
│               (plugin_base.py)                           │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │         PluginBase (Abstract)                  │    │
│  │  • get_name()                                  │    │
│  │  • get_icon()                                  │    │
│  │  • get_settings_widget()                       │    │
│  │  • execute(image, **kwargs)                    │    │
│  └────────────────────────────────────────────────┘    │
│                      │                                   │
│       ┌──────────────┼──────────────┬──────────────┐   │
│       ▼              ▼              ▼              ▼   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│  │   Tool   │  │  Effect  │  │  Filter  │  │Adjustment│
│  │  Plugin  │  │  Plugin  │  │  Plugin  │  │  Plugin  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘
│                                                          │
└─────────────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│              Concrete Plugins                            │
│              (plugins/*.py)                              │
│                                                          │
│  • brush_tool.py          (ToolPlugin)                  │
│  • blur_effect.py         (EffectPlugin)                │
│  • sharpen_filter.py      (FilterPlugin)                │
│  • brightness_adjustment.py (AdjustmentPlugin)          │
│                                                          │
│  ... (Extensible - Add new plugins here)                │
└─────────────────────────────────────────────────────────┘
```

## Plugin Types & Interfaces

### ToolPlugin
Interactive tools that respond to mouse events.

**Methods:**
- `on_mouse_press(x, y, image) → image`
- `on_mouse_move(x, y, image) → image`
- `on_mouse_release(x, y, image) → image`

**Example:** Brush Tool, Selection Tool, Eraser

### EffectPlugin
Apply effects to images.

**Methods:**
- `apply_effect(image, **params) → image`

**Example:** Blur, Sharpen, Noise

### FilterPlugin
Apply filters to images.

**Methods:**
- `apply_filter(image, **params) → image`

**Example:** Color filters, Artistic filters

### AdjustmentPlugin
Adjust image properties.

**Methods:**
- `apply_adjustment(image, **params) → image`

**Example:** Brightness, Contrast, Saturation

## Data Flow

### Image Loading Flow
```
User selects "Open"
    ↓
QFileDialog → file_path
    ↓
cv2.imread(file_path) → OpenCV Mat (numpy array)
    ↓
LayerManager.add_layer("Background", image)
    ↓
Canvas.load_image(image)
    ↓
numpy_to_pixmap(image) → QPixmap
    ↓
QGraphicsPixmapItem.setPixmap(pixmap)
    ↓
Display on canvas
```

### Plugin Execution Flow
```
User selects plugin from toolbox
    ↓
EditorWindow.on_plugin_selected(plugin)
    ↓
Load plugin settings widget → Right panel
    ↓
User interacts with canvas/settings
    ↓
Plugin.execute(image, **params)
    ↓
LayerManager.get_active_layer() → Current layer
    ↓
Process image with plugin
    ↓
Update layer image
    ↓
LayerManager.composite_layers()
    ↓
Canvas.update_image(composite)
    ↓
Display updated image
```

### Layer Compositing Flow
```
LayerManager.composite_layers()
    ↓
Start with bottom layer (result = layer_0.image)
    ↓
For each layer above:
    │
    ├─ Check if visible
    │   ↓ (if yes)
    ├─ Apply blend mode
    │   ↓
    ├─ Apply opacity
    │   ↓
    └─ Composite: result = blend(result, layer.image)
    ↓
Return final composite
    ↓
Display on canvas
```

## Key Design Patterns

### 1. Plugin Pattern
- Abstract base classes define plugin interface
- Concrete plugins implement specific functionality
- Dynamic loading and hot-reloading support

### 2. Model-View-Controller (MVC)
- **Model**: LayerManager, PluginManager (data)
- **View**: Canvas, Panels (UI)
- **Controller**: EditorWindow (coordination)

### 3. Observer Pattern
- Qt Signals/Slots for event handling
- Layer changes trigger canvas updates
- Plugin selection updates settings panel

### 4. Strategy Pattern
- Different blend modes (strategies) for layer compositing
- Plugin types represent different processing strategies

## Performance Optimizations

### 1. Canvas Rendering
- QGraphicsView hardware acceleration
- Efficient QPixmap caching
- Viewport-based updates

### 2. Layer Compositing
- Only composite visible layers
- Cache composite result until layer changes
- Use numpy vectorized operations

### 3. Plugin System
- Lazy loading of plugins
- Plugin settings widgets created on-demand
- Efficient image copying (numpy views when possible)

## Extension Points

### Adding New Plugin Types
1. Create new base class in `plugin_base.py`
2. Define required methods
3. Update `PluginType` enum
4. Implement in plugins directory

### Adding New Blend Modes
1. Add to `BlendMode` enum in `layer_manager.py`
2. Implement blending algorithm in `_blend_layers()`
3. Add to UI combo box

### Adding New UI Panels
1. Create widget class
2. Add to `EditorWindow.setup_ui()`
3. Connect signals for data flow

## Dependencies Graph

```
main.py
  ├── launcher_window.py (PySide6)
  └── editor_window.py
        ├── canvas.py (PySide6, OpenCV, NumPy)
        ├── layer_manager.py (PySide6, OpenCV, NumPy)
        ├── plugin_manager.py
        │     └── plugin_base.py
        └── plugins/*.py
              └── plugin_base.py
```

## Security Considerations

1. **Plugin Sandboxing**: Plugins run in same process (trust required)
2. **File Operations**: Validate file paths and extensions
3. **Memory Management**: Proper cleanup of large images
4. **Error Handling**: Try-catch blocks in plugin loading

## Future Architecture Improvements

1. **Undo/Redo System**: Command pattern implementation
2. **Plugin Marketplace**: Remote plugin discovery and installation
3. **Multi-threading**: Background processing for heavy operations
4. **GPU Acceleration**: OpenCL/CUDA for image processing
5. **Plugin API Versioning**: Backward compatibility support
6. **Project Format**: Save/load entire projects with layers

---

This architecture provides a solid, extensible foundation for a professional image and video editor!
