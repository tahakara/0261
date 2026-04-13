# Vision Editor
### Plugin-Based Modular Image and Video Processing Software

A professional-grade image and video editor built with Python, PySide6, and OpenCV, featuring a robust plugin architecture for extensibility and advanced computer vision capabilities. UI/UX inspired by Adobe Photoshop and Premiere.

---

## 🚀 Features

### Core Architecture
- **Plugin-Based System**: Dynamically load and manage tools, effects, filters, and adjustments
- **Dual Mode**: Switch between Image Editor and Video Editor modes
- **Professional UI**: Dark theme with intuitive layout inspired by industry-standard tools
- **High Performance**: Optimized rendering with QGraphicsView and OpenCV

### Image Editor Mode
#### User Interface
- **Top Bar**: Menu bar (File, Edit, View, Plugins, Help) and toolbar with quick actions
- **Left Sidebar (Toolbox)**: Dynamically populated with loaded plugins
- **Right Sidebar**: 
  - **Tool Settings Panel** (Top): Dynamic settings that change based on active plugin
  - **Layer Management Panel** (Bottom): Sophisticated layer system with full controls
- **Center Canvas**: High-performance QGraphicsView-based workspace with zoom/pan

#### Layer System
- Multiple layer support with thumbnails
- Layer visibility toggle
- Opacity control (0-100%)
- Blend modes: Normal, Multiply, Screen, Overlay, Add, Subtract
- Layer reordering (move up/down)
- Layer locking
- Real-time compositing

#### Plugin Types
1. **Tool Plugins**: Interactive tools (e.g., Brush, Selection, Shapes)
2. **Effect Plugins**: Image effects (e.g., Blur, Sharpen)
3. **Filter Plugins**: Color and style filters
4. **Adjustment Plugins**: Image adjustments (e.g., Brightness, Contrast)

#### Shape Drawing Tool
- **Shapes**: Rectangle, Circle, Line, Arrow, Ellipse, Triangle
- **Customization**: Color selection, thickness control, filled/outlined options
- **Real-time Preview**: See shapes as you draw them

### Video Editor Mode
#### Camera & Recording
- **Live Camera Feed**: Real-time camera capture with adjustable FPS
- **Recording**: 
  - Multiple format support (MP4, AVI, MOV, MKV)
  - Codec selection (H.264, MJPEG, X264)
  - Duration timer display during recording
  - REC indicator overlay
- **Snapshot**: Capture still frames from live feed

#### Video Effects
- **Basic Adjustments**:
  - Brightness control (-100 to +100)
  - Heat/Warm effect (0-100%)
  - Denoise strength (0-10)
  - Noise addition (0-100%)
  
- **RGB Channel Control**:
  - Independent Red, Green, Blue channel adjustments (-100 to +100)
  - Real-time color correction

#### Face Detection & Analysis
- **Face Detection** (Haar Cascade):
  - Automatic face detection
  - Bounding boxes with numbering
  - Adjustable blur strength (1-49, odd numbers only)
  - Face-specific blur effect
  
- **Sentiment Analysis**:
  - Real-time emotion detection (Happy, Sad, Neutral)
  - Visual emoji indicators on frame
  - Toggle emoji display
  - Adaptive thresholds for accurate detection

#### Color Filters
Nine artistic filters with adjustable intensity (0-100%):
1. **Sepia**: Classic warm vintage tone
2. **Grayscale**: Black and white conversion
3. **Negative**: Inverted colors
4. **Vintage**: Aged photo effect
5. **Cool Tone**: Blue-tinted cool effect
6. **Warm Tone**: Orange-tinted warm effect
7. **High Contrast**: CLAHE adaptive contrast
8. **Vibrant**: Enhanced saturation
9. **Black & White**: Binary threshold effect

#### Video Overlay System
- **Text Overlays**:
  - 7 OpenCV font families (HERSHEY_SIMPLEX, DUPLEX, COMPLEX, etc.)
  - Custom text, size, color, position
  - Opacity control (0-100%)
  - Named overlays with default naming
  
- **Image Overlays**:
  - PNG/JPG support with alpha channel
  - Position and size control
  - Chroma key (green screen) support
  - Adjustable keycolor tolerance
  
- **Video Overlays**:
  - Play videos as overlays
  - Looping playback
  - Position and size control
  - Chroma key support
  
- **Overlay Management**:
  - Name and rename overlays
  - Selection with visual frame and resize handles
  - Click to select, click outside to deselect
  - Real-time updates
  - List view with overlay names

---

## 📦 Installation

### Requirements
- Python 3.9 or higher
- pip package manager

### Setup

1. **Clone or download the project**
```bash
cd comp_vision_proj
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

---

## 🎯 Usage

### Running the Application

```bash
python main.py
```

### Workflow

#### Image Editor Mode
1. **Launch Screen**: Select "Image Editor" mode
2. **Main Editor**: 
   - Create new project or open existing image
   - Select tools from the left sidebar
   - Adjust tool settings in the top-right panel
   - Manage layers in the bottom-right panel
   - Use canvas controls: zoom, pan, fit to window
   - Draw shapes with customizable colors and styles

#### Video Editor Mode
1. **Launch Screen**: Select "Video Editor" mode
2. **Camera Setup**:
   - Click "Kamerayı Aç" to start camera feed
   - Adjust video effects in real-time
   
3. **Face Detection & Analysis**:
   - Enable "Yüz Tanıma Aktif" for face detection
   - Toggle bounding boxes, numbering, blur
   - Enable "Duygu Analizi" for emotion detection
   - Adjust blur strength for privacy
   
4. **Apply Effects**:
   - Adjust brightness, heat, denoise, noise
   - Modify RGB channels individually
   - Select color filters with intensity control
   
5. **Add Overlays**:
   - Text: Enter text, choose font, color, size
   - Image: Browse and load PNG/JPG files
   - Video: Add video overlays with chroma key
   - Name overlays for organization
   - Click overlays to select and resize
   
6. **Recording**:
   - Select video format (MP4, AVI, MOV, MKV)
   - Click "Kaydı Başlat" to start recording
   - Monitor duration timer
   - Click "Kaydı Durdur" to stop and save
   
7. **Snapshot**:
   - Click "Snapshot Al" to capture current frame
   - Save as PNG/JPG

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | New Project |
| `Ctrl+O` | Open File |
| `Ctrl+S` | Save |
| `Ctrl+Shift+S` | Save As |
| `Ctrl++` | Zoom In |
| `Ctrl+-` | Zoom Out |
| `Ctrl+0` | Fit to Window |
| `Ctrl+R` | Reset View |
| `Ctrl+Q` | Quit |

---

## 🔌 Plugin Development

### Creating a New Plugin

Plugins are simple Python files placed in the `plugins/` directory. Here's how to create different plugin types:

#### 1. Tool Plugin Example

```python
from src.plugin_base import ToolPlugin
import numpy as np

class MyTool(ToolPlugin):
    def __init__(self):
        super().__init__()
        self.name = "My Tool"
        self.description = "Description of my tool"
        
    def get_name(self):
        return self.name
    
    def get_icon(self):
        return ""
    
    def get_settings_widget(self):
        # Return QWidget with tool settings
        return None
    
    def execute(self, image, **kwargs):
        return image
    
    def on_mouse_press(self, x, y, image):
        # Handle mouse press
        return image
    
    def on_mouse_move(self, x, y, image):
        # Handle mouse move
        return None
    
    def on_mouse_release(self, x, y, image):
        # Handle mouse release
        return None
```

#### 2. Effect Plugin Example

```python
from src.plugin_base import EffectPlugin
import cv2
import numpy as np

class MyEffect(EffectPlugin):
    def __init__(self):
        super().__init__()
        self.name = "My Effect"
        
    def get_name(self):
        return self.name
    
    def get_icon(self):
        return ""
    
    def get_settings_widget(self):
        # Return QWidget with effect settings
        return None
    
    def apply_effect(self, image, **params):
        # Process and return the image
        return image
```

### Plugin Base Classes

- `ToolPlugin`: For interactive tools (brush, selection, etc.)
- `EffectPlugin`: For image effects (blur, sharpen, etc.)
- `FilterPlugin`: For filters (color grading, etc.)
- `AdjustmentPlugin`: For adjustments (brightness, contrast, etc.)

---

## 📁 Project Structure

```
comp_vision_proj/
├── main.py                    # Application entry point
├── requirements.txt           # Dependencies
├── README.md                  # Documentation
├── .gitignore                 # Git ignore rules
│
├── src/                       # Source code
│   ├── __init__.py
│   ├── launcher_window.py     # Welcome screen with mode selection
│   ├── editor_window.py       # Main editor window (dual mode)
│   ├── canvas.py              # Canvas rendering system
│   ├── layer_manager.py       # Layer management system
│   ├── plugin_base.py         # Plugin base classes
│   ├── plugin_manager.py      # Plugin loader and manager
│   │
│   # Video Editor Components
│   ├── video_system.py        # Camera capture and video processing
│   ├── video_control_panel.py # Video effects and controls UI
│   ├── overlay_manager.py     # Text/image/video overlay system
│   ├── overlay_panel.py       # Overlay management UI
│   ├── face_detection.py      # Haar Cascade face detection
│   ├── face_sentiment.py      # Emotion analysis system
│   ├── color_filters.py       # 9 artistic color filters
│   │
│   # Image Editor Components
│   └── shape_tool.py          # Geometric shape drawing tool
│
├── plugins/                   # Plugin directory (dynamically loaded)
│   ├── brush_tool.py          # Brush tool
│   ├── blur_effect.py         # Blur effect
│   ├── brightness_adjustment.py  # Brightness adjustment
│   └── sharpen_filter.py      # Sharpen filter
│
├── output/                    # Recorded videos (gitignored)
├── snapshots/                 # Captured snapshots (gitignored)
└── assets/                    # Assets (icons, images, etc.)
```

---

## 🛠️ Technical Details

### Technologies Used
- **PySide6 6.6.1**: Modern Qt6 bindings for Python
- **OpenCV 4.8.1.78**: Computer vision and image processing
- **NumPy 1.26.2**: Numerical computing and array operations
- **Pillow 10.1.0**: Image format support

### Key Components

#### Video System
- Real-time camera capture with configurable FPS (25 fps default)
- Multi-format video encoding (mp4v, MJPEG, X264, H264)
- Effects pipeline: Face detection → Sentiment → RGB → Brightness → Heat → Denoise → Noise → Filters → Overlays
- QTimer-based frame processing with signal/slot architecture

#### Face Detection System
- Haar Cascade classifier (haarcascade_frontalface_default.xml)
- Configurable parameters: scale_factor=1.1, min_neighbors=5, min_size=(30,30)
- Gaussian blur with odd kernel sizes (1-49)
- Real-time face tracking with bounding boxes and numbering

#### Sentiment Analysis
- Heuristic-based emotion detection (Happy, Sad, Neutral)
- Analyzes mouth region variance and brightness
- Adaptive thresholds for balanced detection
- Visual feedback with emoji indicators

#### Overlay System
- Dataclass-based overlay management with unique IDs
- BGRA alpha blending for transparency
- Chroma key (green screen) with adjustable tolerance
- Selection system with visual frames and resize handles
- Real-time video overlay playback with looping

#### Color Filter System
- Static methods for filter application
- Intensity-based blending with cv2.addWeighted()
- CLAHE for adaptive histogram equalization
- HSV and LAB color space transformations

---

### Technologies
- **Python 3.9+**: Core language
- **PySide6**: Qt-based GUI framework
- **OpenCV**: Image and video processing
- **NumPy**: Numerical operations
- **Pillow**: Additional image support

### Architecture Highlights

#### Canvas Rendering
- Uses `QGraphicsView` and `QGraphicsScene` for high-performance rendering
- Efficient conversion from OpenCV Mat (numpy array) to QPixmap
- Smooth zooming and panning with mouse/trackpad
- Real-time updates without flickering

#### Layer System
- Layer compositing with multiple blend modes
- Alpha blending for opacity control
- Efficient thumbnail generation
- Non-destructive editing workflow

#### Plugin System
- Dynamic plugin discovery and loading
- Hot-reloading support
- Plugin metadata and versioning
- Automatic UI generation for plugin settings

---

## 🎨 Included Plugins

### Tools
1. **Brush Tool**: Paint on canvas with customizable size and color

### Effects
2. **Blur Effect**: Apply Gaussian blur with adjustable strength

### Adjustments
3. **Brightness**: Adjust image brightness (-100 to +100)

### Filters
4. **Sharpen**: Sharpen images using unsharp masking

---

## 🔧 Customization

### Themes
The application uses a dark theme by default. Modify stylesheets in:
- `launcher_window.py`: Launcher styling
- `editor_window.py`: Main editor styling
- `layer_manager.py`: Layer panel styling

### Adding Menus
Add new menu items in `editor_window.py` → `create_menu_bar()`

### Adding Toolbar Actions
Add toolbar buttons in `editor_window.py` → `create_toolbar()`

---

## 📝 Development Roadmap

- [ ] Undo/Redo system with history stack
- [ ] Selection tools (rectangular, elliptical, lasso)
- [ ] Text tool with font customization
- [ ] Gradient tool
- [ ] Clone stamp tool
- [ ] More blend modes
- [ ] Layer groups
- [ ] Layer effects (drop shadow, glow, etc.)
- [ ] Video timeline and keyframes
- [ ] Video effects and transitions
- [ ] Export presets for different formats
- [ ] Batch processing
- [ ] Scripting API for automation

---

## 🤝 Contributing

To contribute plugins or features:

1. Fork the repository
2. Create a feature branch
3. Add your plugin in the `plugins/` directory
4. Test thoroughly
5. Submit a pull request

---

## 📄 License

This project is provided as-is for educational and commercial purposes.

---

## 🙏 Acknowledgments

- UI/UX inspiration: Adobe Photoshop and Premiere Pro
- Built with love using Python and Qt
- OpenCV community for excellent documentation

---

## 📞 Support

For issues, questions, or feature requests, please open an issue in the repository.

---

**Vision Editor** - Professional Image and Video Processing Made Easy 🎨
