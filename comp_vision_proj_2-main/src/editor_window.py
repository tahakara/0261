"""
Main Editor Window - Professional image and video editor interface
"""
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                                QToolBar, QMenuBar, QMenu, QStatusBar, QLabel,
                                QScrollArea, QFileDialog, QMessageBox, QDockWidget,
                                QToolButton, QSplitter)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QAction, QIcon, QKeySequence, QActionGroup
import numpy as np
import cv2
from pathlib import Path

from src.canvas import ImageCanvas
from src.layer_manager import LayerManager, LayerPanel
from src.plugin_manager import PluginManager
from src.plugin_base import PluginType
from src.selection_manager import SelectionManager, SelectionMode
from src.apply_effect_widget import ApplyEffectWidget
from src.video_system import VideoSystem
from src.video_control_panel import VideoControlPanel
from src.overlay_manager import OverlayManager
from src.overlay_panel import OverlayPanel


class EditorWindow(QMainWindow):
    """
    Main editor window with plugin-based architecture
    Inspired by Adobe Photoshop/Premiere UI/UX
    """
    
    def __init__(self, mode: str = "image"):
        super().__init__()
        
        self.mode = mode  # "image" or "video"
        self.current_file = None
        self.is_modified = False
        
        # Initialize managers
        self.layer_manager = LayerManager()
        self.plugin_manager = PluginManager(plugin_directory="plugins")
        self.selection_manager = None  # Will be initialized when image is loaded
        
        # Video system (for video mode)
        self.video_system = None
        self.overlay_manager = None
        if mode == "video":
            self.overlay_manager = OverlayManager()
            self.video_system = VideoSystem()
            self.video_system.overlay_manager = self.overlay_manager
            self.video_system.frame_ready.connect(self.on_video_frame_ready)
            self.video_system.recording_status_changed.connect(self.on_recording_status_changed)
        
        # Active plugin
        self.active_plugin = None
        self.active_effect_plugin = None  # For effects that need Apply button
        
        # Selection tools action group (for mutual exclusivity)
        self.selection_action_group = None
        
        # Overlay interaction state
        self.dragging_overlay = False
        self.resizing_overlay = False
        self.selected_overlay_id = None
        self.drag_start_pos = None
        self.resize_start_pos = None
        self.resize_start_size = None
        
        # Setup UI
        self.setWindowTitle(f"Görsel Düzenleyici - {mode.capitalize()} Modu")
        self.setGeometry(100, 100, 1400, 900)
        self.setup_ui()
        self.apply_styles()
        
        # Load plugins
        self.load_plugins()
        
    def setup_ui(self):
        """Setup the main editor UI"""
        # Create central widget with canvas
        self.canvas = ImageCanvas()
        self.canvas.mouse_pressed.connect(self.on_canvas_mouse_pressed)
        self.canvas.mouse_moved.connect(self.on_canvas_mouse_moved)
        self.canvas.mouse_released.connect(self.on_canvas_mouse_released)
        self.canvas.mouse_double_clicked.connect(self.on_canvas_double_clicked)
        self.canvas.zoom_changed.connect(self.on_zoom_changed)
        
        # For video mode, disable scrollbars and set fixed view
        if self.mode == "video":
            self.canvas.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.canvas.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            from PySide6.QtWidgets import QGraphicsView
            self.canvas.setDragMode(QGraphicsView.NoDrag)
        
        self.setCentralWidget(self.canvas)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        self.create_toolbar()
        
        # Create status bar
        self.create_status_bar()
        
        # Create left sidebar (Toolbox) - only for image mode
        if self.mode == "image":
            self.create_toolbox()
        
        # Create right sidebar (Tool Settings + Layers)
        self.create_right_sidebar()
        
    def create_menu_bar(self):
        """Create the top menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("▣ Dosya")
        
        new_action = QAction("+ Yeni", self)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self.on_new)
        file_menu.addAction(new_action)
        
        open_action = QAction("◈ Aç", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.on_open)
        file_menu.addAction(open_action)
        
        save_action = QAction("▼ Kaydet", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.on_save)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("▽ Farklı Kaydet...", self)
        save_as_action.setShortcut(QKeySequence.SaveAs)
        save_as_action.triggered.connect(self.on_save_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("× Çıkış", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("✎ Düzenle")
        
        undo_action = QAction("↺ Geri Al", self)
        undo_action.setShortcut(QKeySequence.Undo)
        undo_action.setEnabled(False)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("↻ Yinele", self)
        redo_action.setShortcut(QKeySequence.Redo)
        redo_action.setEnabled(False)
        edit_menu.addAction(redo_action)
        
        # View menu
        view_menu = menubar.addMenu("◉ Görünüm")
        
        zoom_in_action = QAction("⊕ Yakınlaştır", self)
        zoom_in_action.setShortcut(QKeySequence.ZoomIn)
        zoom_in_action.triggered.connect(self.canvas.zoom_in)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("⊖ Uzaklaştır", self)
        zoom_out_action.setShortcut(QKeySequence.ZoomOut)
        zoom_out_action.triggered.connect(self.canvas.zoom_out)
        view_menu.addAction(zoom_out_action)
        
        fit_action = QAction("▦ Pencereye Sığdır", self)
        fit_action.setShortcut("Ctrl+0")
        fit_action.triggered.connect(self.canvas.fit_to_window)
        view_menu.addAction(fit_action)
        
        reset_action = QAction("🔄 Görünümü Sıfırla", self)
        reset_action.setShortcut("Ctrl+R")
        reset_action.triggered.connect(self.canvas.reset_view)
        view_menu.addAction(reset_action)
        
        # Plugins menu
        plugins_menu = menubar.addMenu("🔌 Eklentiler")
        
        reload_action = QAction("🔄 Eklentileri Yeniden Yükle", self)
        reload_action.triggered.connect(self.load_plugins)
        plugins_menu.addAction(reload_action)
        
        # Help menu
        help_menu = menubar.addMenu("❓ Yardım")
        
        about_action = QAction("ℹ️ Hakkında", self)
        about_action.triggered.connect(self.on_about)
        help_menu.addAction(about_action)
        
    def create_toolbar(self):
        """Create the main toolbar"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setMovable(False)
        self.addToolBar(Qt.TopToolBarArea, toolbar)
        
        # New
        new_btn = QAction("+ Yeni", self)
        new_btn.setToolTip("Yeni proje oluştur")
        new_btn.triggered.connect(self.on_new)
        toolbar.addAction(new_btn)
        
        # Open
        open_btn = QAction("◈ Aç", self)
        open_btn.setToolTip("Resim/video aç")
        open_btn.triggered.connect(self.on_open)
        toolbar.addAction(open_btn)
        
        # Save
        save_btn = QAction("▼ Kaydet", self)
        save_btn.setToolTip("Mevcut çalışmayı kaydet")
        save_btn.triggered.connect(self.on_save)
        toolbar.addAction(save_btn)
        
        toolbar.addSeparator()
        
        # Zoom controls
        zoom_in_btn = QAction("⊕ Yakınlaştır", self)
        zoom_in_btn.triggered.connect(self.canvas.zoom_in)
        toolbar.addAction(zoom_in_btn)
        
        zoom_out_btn = QAction("⊖ Uzaklaştır", self)
        zoom_out_btn.triggered.connect(self.canvas.zoom_out)
        toolbar.addAction(zoom_out_btn)
        
        fit_btn = QAction("▦ Sığdır", self)
        fit_btn.triggered.connect(self.canvas.fit_to_window)
        toolbar.addAction(fit_btn)
        
        toolbar.addSeparator()
        
        # Selection Tools Section
        toolbar.addWidget(QLabel(" ◎ Seçim: "))
        
        # Create action group for exclusive selection tools
        from PySide6.QtGui import QActionGroup
        self.selection_action_group = QActionGroup(self)
        self.selection_action_group.setExclusive(True)
        
        # These will be populated when plugins load
        self.selection_toolbar = toolbar
        
    def create_status_bar(self):
        """Create the status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Current tool label
        self.tool_label = QLabel("⚒ Araç: Yok")
        self.status_bar.addWidget(self.tool_label)
        
        self.status_bar.addWidget(QLabel("|"))
        
        # Zoom level label
        self.zoom_label = QLabel("⊕ Zoom: %100")
        self.status_bar.addWidget(self.zoom_label)
        
        self.status_bar.addWidget(QLabel("|"))
        
        # Mouse position label
        self.position_label = QLabel("⊙ Konum: (0, 0)")
        self.status_bar.addWidget(self.position_label)
        
        self.status_bar.addWidget(QLabel("|"))
        
        # Image info label
        self.info_label = QLabel("▭ Resim yüklenmedi")
        self.status_bar.addPermanentWidget(self.info_label)
        
    def create_toolbox(self):
        """Create the left sidebar toolbox for plugins"""
        self.toolbox_dock = QDockWidget("Toolbox", self)
        self.toolbox_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        toolbox_widget = QWidget()
        toolbox_layout = QVBoxLayout(toolbox_widget)
        toolbox_layout.setContentsMargins(5, 5, 5, 5)
        toolbox_layout.setSpacing(10)
        
        # Title
        title = QLabel("▣ Araçlar")
        title.setObjectName("panelTitle")
        toolbox_layout.addWidget(title)
        
        # Create scroll area for tool sections
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Container for all sections
        sections_widget = QWidget()
        sections_layout = QVBoxLayout(sections_widget)
        sections_layout.setSpacing(15)
        sections_layout.setAlignment(Qt.AlignTop)
        
        # Drawing Tools Section
        drawing_section = QLabel("✎ ÇİZİM ARAÇLARI")
        drawing_section.setObjectName("sectionTitle")
        sections_layout.addWidget(drawing_section)
        
        self.drawing_tool_buttons_layout = QVBoxLayout()
        self.drawing_tool_buttons_layout.setSpacing(2)
        sections_layout.addLayout(self.drawing_tool_buttons_layout)
        
        # Separator
        separator2 = QLabel("━" * 30)
        separator2.setAlignment(Qt.AlignCenter)
        separator2.setStyleSheet("color: #3a3a3a;")
        sections_layout.addWidget(separator2)
        
        # Effects Section (require selection)
        effects_section = QLabel("★ EFEKTLERİ (Seçim Gerekli)")
        effects_section.setObjectName("sectionTitle")
        sections_layout.addWidget(effects_section)
        
        self.effect_buttons_layout = QVBoxLayout()
        self.effect_buttons_layout.setSpacing(2)
        sections_layout.addLayout(self.effect_buttons_layout)
        
        scroll_area.setWidget(sections_widget)
        toolbox_layout.addWidget(scroll_area)
        
        self.toolbox_dock.setWidget(toolbox_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.toolbox_dock)
        
    def create_right_sidebar(self):
        """Create the right sidebar with tool settings and layer panel"""
        self.right_dock = QDockWidget("Properties", self)
        self.right_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        
        # For video mode, show video controls and layers panel
        if self.mode == "video":
            # Create scroll area for controls
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            
            # Container widget for scrollable content
            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(5, 5, 5, 5)
            container_layout.setSpacing(10)
            
            # Video controls
            self.video_control_panel = VideoControlPanel()
            
            # Connect signals
            self.video_control_panel.camera_toggle_requested.connect(self.on_camera_toggle)
            self.video_control_panel.recording_toggle_requested.connect(self.on_recording_toggle)
            self.video_control_panel.snapshot_requested.connect(self.on_snapshot)
            
            self.video_control_panel.brightness_changed.connect(lambda v: self.video_system.set_brightness(v))
            self.video_control_panel.heat_changed.connect(lambda v: self.video_system.set_heat_effect(v))
            self.video_control_panel.denoise_changed.connect(lambda v: self.video_system.set_denoise_strength(v))
            self.video_control_panel.noise_changed.connect(lambda v: self.video_system.set_noise_strength(v))
            self.video_control_panel.rgb_changed.connect(lambda r, g, b: self.video_system.set_rgb_adjustments(r, g, b))
            
            # Face detection signals
            self.video_control_panel.face_detection_toggled.connect(lambda e: setattr(self.video_system.face_detection, 'enabled', e))
            self.video_control_panel.face_blur_toggled.connect(lambda e: setattr(self.video_system.face_detection, 'blur_faces', e))
            self.video_control_panel.face_boxes_toggled.connect(lambda e: setattr(self.video_system.face_detection, 'show_boxes', e))
            self.video_control_panel.face_numbers_toggled.connect(lambda e: setattr(self.video_system.face_detection, 'show_numbers', e))
            self.video_control_panel.face_blur_strength_changed.connect(lambda v: self.video_system.face_detection.set_blur_strength(v))
            self.video_control_panel.face_sentiment_toggled.connect(lambda e: setattr(self.video_system.face_sentiment, 'enabled', e))
            self.video_control_panel.face_sentiment_emoji_toggled.connect(lambda e: setattr(self.video_system.face_sentiment, 'show_emoji', e))
            
            # Color filter signal
            self.video_control_panel.color_filter_changed.connect(lambda f, i: self.video_system.set_color_filter(f, i))
            
            # Recording duration signal
            self.video_system.recording_duration_updated.connect(self.video_control_panel.update_recording_duration)
            
            container_layout.addWidget(self.video_control_panel)
            
            # Overlay panel
            self.overlay_panel = OverlayPanel(self.overlay_manager)
            
            # Connect overlay signals
            self.overlay_panel.add_text_overlay_requested.connect(self.on_add_text_overlay)
            self.overlay_panel.add_image_overlay_requested.connect(self.on_add_image_overlay)
            self.overlay_panel.add_video_overlay_requested.connect(self.on_add_video_overlay)
            self.overlay_panel.remove_overlay_requested.connect(self.on_remove_overlay)
            self.overlay_panel.overlay_selected.connect(self.on_overlay_selected)
            self.overlay_panel.opacity_changed.connect(lambda id, o: self.overlay_manager.update_overlay_opacity(id, o))
            self.overlay_panel.keycolor_changed.connect(lambda id, e, c, t: self.overlay_manager.set_overlay_keycolor(id, e, c, t))
            self.overlay_panel.overlay_name_changed.connect(lambda id, n: self.overlay_manager.update_overlay_name(id, n))
            
            container_layout.addWidget(self.overlay_panel)
            container_layout.addStretch()
            
            scroll_area.setWidget(container)
            right_layout.addWidget(scroll_area)
        else:
            # Image mode: show both tool settings and layers with splitter
            # Create splitter for tool settings and layers
            splitter = QSplitter(Qt.Vertical)
            
            # Tool settings panel (top half)
            self.tool_settings_widget = QWidget()
            tool_settings_layout = QVBoxLayout(self.tool_settings_widget)
            tool_settings_layout.setContentsMargins(5, 5, 5, 5)
            
            settings_title = QLabel("Tool Settings")
            settings_title.setObjectName("panelTitle")
            tool_settings_layout.addWidget(settings_title)
            
            # Dynamic settings container
            self.dynamic_settings_widget = QWidget()
            self.dynamic_settings_layout = QVBoxLayout(self.dynamic_settings_widget)
            self.dynamic_settings_layout.setAlignment(Qt.AlignTop)
            tool_settings_layout.addWidget(self.dynamic_settings_widget)
            
            # Apply Effect Widget (for effects that need selection)
            self.apply_widget = ApplyEffectWidget()
            self.apply_widget.apply_requested.connect(self.on_apply_effect)
            tool_settings_layout.addWidget(self.apply_widget)
            
            tool_settings_layout.addStretch()
            
            splitter.addWidget(self.tool_settings_widget)
            
            # Layer panel (bottom half)
            self.layer_panel = LayerPanel(self.layer_manager)
            self.layer_panel.layer_changed.connect(self.on_layer_changed)
            self.layer_panel.active_layer_changed.connect(self.on_active_layer_changed)
            
            splitter.addWidget(self.layer_panel)
            
            # Set splitter sizes (equal split)
            splitter.setSizes([300, 300])
            
            right_layout.addWidget(splitter)
        
        self.right_dock.setWidget(right_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.right_dock)
        
    def load_plugins(self):
        """Load all plugins and populate the toolbox"""
        count = self.plugin_manager.load_all_plugins()
        self.status_bar.showMessage(f"{count} eklenti yüklendi", 3000)
        
        # Skip plugin UI setup for video mode (no toolbox)
        if self.mode == "video":
            return
        
        # Clear existing tool buttons (only in image mode)
        for layout in [self.drawing_tool_buttons_layout, self.effect_buttons_layout]:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        
        # Categorize plugins
        plugins = self.plugin_manager.get_all_plugins()
        for plugin in plugins:
            # Determine section based on plugin name and type
            plugin_name = plugin.get_name().lower()
            
            if 'select' in plugin_name or 'lasso' in plugin_name or 'rectangle' in plugin_name or 'ellipse' in plugin_name:
                # Selection tools - Add to TOP TOOLBAR
                btn = QAction(plugin.get_name(), self)
                btn.setToolTip(plugin.description)
                btn.setCheckable(True)
                btn.triggered.connect(lambda checked, p=plugin: self.on_plugin_selected(p))
                
                # Add to action group for mutual exclusivity
                if self.selection_action_group:
                    self.selection_action_group.addAction(btn)
                
                self.selection_toolbar.addAction(btn)
            elif plugin.plugin_type == PluginType.TOOL or 'brush' in plugin_name or 'draw' in plugin_name:
                # Drawing tools (don't need selection)
                btn = QToolButton()
                btn.setText(plugin.get_name())
                btn.setToolTip(plugin.description)
                btn.setCheckable(True)
                btn.setFixedHeight(32)
                btn.clicked.connect(lambda checked, p=plugin: self.on_plugin_selected(p))
                self.drawing_tool_buttons_layout.addWidget(btn)
            else:
                # Effects (need selection)
                btn = QToolButton()
                btn.setText(plugin.get_name())
                btn.setToolTip(plugin.description)
                btn.setCheckable(True)
                btn.setFixedHeight(32)
                btn.clicked.connect(lambda checked, p=plugin: self.on_plugin_selected(p))
                self.effect_buttons_layout.addWidget(btn)
            
    def on_plugin_selected(self, plugin):
        """Handle plugin selection"""
        plugin_name = plugin.get_name().lower()
        
        # Check if it's an effect plugin (needs selection)
        is_effect = not ('select' in plugin_name or 'lasso' in plugin_name or 
                        'rectangle' in plugin_name or 'ellipse' in plugin_name or
                        plugin.plugin_type == PluginType.TOOL or 'brush' in plugin_name)
        
        if is_effect:
            self.active_effect_plugin = plugin
            self.apply_widget.set_enabled(True, "Configure settings and click Apply")
            
            # Update apply button based on selection status
            if self.selection_manager and self.selection_manager.has_selection:
                self.apply_widget.set_selection_status(True)
            else:
                self.apply_widget.set_selection_status(False)
        else:
            self.active_plugin = plugin
            self.active_effect_plugin = None
            self.apply_widget.set_enabled(False)
            
            # Set brush cursor if it's a brush tool
            if 'brush' in plugin_name:
                if hasattr(plugin, 'brush_size'):
                    plugin.parent_canvas = self.canvas
                    self.canvas.set_brush_cursor(plugin.brush_size, True)
            else:
                self.canvas.set_brush_cursor(0, False)
        
        self.tool_label.setText(f"⚒ Araç: {plugin.get_name()}")
        
        # Clear current tool settings
        while self.dynamic_settings_layout.count():
            child = self.dynamic_settings_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Load plugin settings widget
        settings_widget = plugin.get_settings_widget()
        if settings_widget:
            self.dynamic_settings_layout.addWidget(settings_widget)
        else:
            no_settings = QLabel("No settings available")
            no_settings.setAlignment(Qt.AlignCenter)
            self.dynamic_settings_layout.addWidget(no_settings)
        
        # Uncheck other buttons in toolbox sections (selection tools are in toolbar now)
        for layout in [self.drawing_tool_buttons_layout, self.effect_buttons_layout]:
            for i in range(layout.count()):
                btn = layout.itemAt(i).widget()
                if btn and isinstance(btn, QToolButton):
                    if self.plugin_manager.get_plugin(btn.text()) != plugin:
                        btn.setChecked(False)
        
        # Uncheck selection tools in action group (they handle themselves via QActionGroup)
    
    def on_apply_effect(self):
        """Apply effect to selected area"""
        if not self.active_effect_plugin:
            self.apply_widget.finish_applying(False, "Hiçbir efekt seçilmedi")
            return
        
        if not self.selection_manager or not self.selection_manager.has_selection:
            self.apply_widget.finish_applying(False, "Aktif seçim yok")
            return
        
        layer = self.layer_manager.get_active_layer()
        if not layer:
            self.apply_widget.finish_applying(False, "Aktif katman yok")
            return
        
        try:
            # Check for special tools (gradient, fill, crop, cutout)
            plugin_name = self.active_effect_plugin.get_name().lower()
            
            if 'gradient' in plugin_name:
                # Apply gradient to selected area
                gradient = self.active_effect_plugin.execute(layer.image)
                result = self.selection_manager.apply_to_image(layer.image, gradient)
                layer.image = result
                layer.thumbnail = None
                self.on_layer_changed()
                self.apply_widget.finish_applying(True, "Gradient başarıyla uygulandı!")
            
            elif 'doldur' in plugin_name or 'fill' in plugin_name:
                # Fill selected area
                fill = self.active_effect_plugin.execute(layer.image)
                result = self.selection_manager.apply_to_image(layer.image, fill)
                layer.image = result
                layer.thumbnail = None
                self.on_layer_changed()
                self.apply_widget.finish_applying(True, "Alan başarıyla dolduruldu!")
            
            elif 'kırp' in plugin_name or 'crop' in plugin_name:
                # Crop to selection
                result = self.selection_manager.crop_to_selection(layer.image)
                if result is not None:
                    layer.image = result
                    layer.thumbnail = None
                    self.selection_manager.clear_selection()
                    self.on_layer_changed()
                    self.apply_widget.finish_applying(True, "Resim başarıyla kırpıldı!")
                else:
                    self.apply_widget.finish_applying(False, "Kırpma başarısız")
            
            elif 'kesme' in plugin_name or 'cutout' in plugin_name:
                # Cutout mask - keep selection, make rest white
                result = self.selection_manager.cutout_mask(layer.image)
                if result is not None:
                    layer.image = result
                    layer.thumbnail = None
                    self.on_layer_changed()
                    self.apply_widget.finish_applying(True, "Kesme maskesi uygulandı!")
                else:
                    self.apply_widget.finish_applying(False, "Kesme maskesi başarısız")
            
            else:
                # Regular effect
                processed = self.active_effect_plugin.execute(layer.image)
                result = self.selection_manager.apply_to_image(layer.image, processed)
                layer.image = result
                layer.thumbnail = None
                self.on_layer_changed()
                self.apply_widget.finish_applying(True, "Efekt başarıyla uygulandı!")
        
        except Exception as e:
            self.apply_widget.finish_applying(False, f"Hata: {str(e)}")
    
    def on_new(self):
        """Create a new blank canvas"""
        # Create blank white image
        blank = np.ones((512, 512, 3), dtype=np.uint8) * 255
        self.layer_manager.layers.clear()
        self.layer_manager.add_layer("Background", blank)
        self.canvas.load_image(blank)
        self.layer_panel.refresh_layer_list()
        self.current_file = None
        self.is_modified = False
        self.update_window_title()
        
        # Initialize selection manager
        h, w = blank.shape[:2]
        self.selection_manager = SelectionManager((w, h))
        
    def on_open(self):
        """Open an image or video file"""
        file_filter = "Image Files (*.png *.jpg *.jpeg *.bmp *.tiff);;Video Files (*.mp4 *.avi *.mov);;All Files (*.*)"
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", file_filter)
        
        if file_path:
            # Load image with alpha channel support (for PNG transparency)
            image = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
            if image is not None:
                # If no layers exist, clear and add as background
                if len(self.layer_manager.layers) == 0:
                    # Convert BGRA to BGR for background layer (no transparency on background)
                    if len(image.shape) == 3 and image.shape[2] == 4:
                        bg_image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
                    else:
                        bg_image = image
                    self.layer_manager.add_layer("Background", bg_image)
                    
                    # Initialize selection manager
                    h, w = bg_image.shape[:2]
                    self.selection_manager = SelectionManager((w, h))
                else:
                    # Add as new layer (keep alpha channel if present)
                    layer_name = Path(file_path).stem
                    # If image doesn't have alpha but has 3 channels, keep as is
                    # If it has alpha (4 channels), keep the alpha
                    self.layer_manager.add_layer(layer_name, image)
                
                # Update canvas with composite
                composite = self.layer_manager.composite_layers()
                self.canvas.load_image(composite)
                self.layer_panel.refresh_layer_list()
                self.current_file = file_path
                self.is_modified = False
                self.update_window_title()
                # Show info for the original image (not composite)
                display_img = image if len(self.layer_manager.layers) == 1 else composite
                self.update_image_info(display_img)
            else:
                QMessageBox.warning(self, "Error", f"Could not open file: {file_path}")
    
    def on_save(self):
        """Save the current work"""
        if self.current_file:
            self.save_file(self.current_file)
        else:
            self.on_save_as()
    
    def on_save_as(self):
        """Save the current work as a new file"""
        file_filter = "PNG Image (*.png);;JPEG Image (*.jpg);;BMP Image (*.bmp);;All Files (*.*)"
        file_path, _ = QFileDialog.getSaveFileName(self, "Save As", "", file_filter)
        
        if file_path:
            self.save_file(file_path)
    
    def save_file(self, file_path: str):
        """Save the composited image to file"""
        composite = self.layer_manager.composite_layers()
        if cv2.imwrite(file_path, composite):
            self.current_file = file_path
            self.is_modified = False
            self.update_window_title()
            self.status_bar.showMessage(f"Saved: {file_path}", 3000)
        else:
            QMessageBox.warning(self, "Error", f"Could not save file: {file_path}")
    
    def on_layer_changed(self):
        """Handle layer changes"""
        # Invalidate cache and get fresh composite
        self.layer_manager._cache_valid = False
        composite = self.layer_manager.composite_layers()
        self.canvas.update_image(composite)
        self.is_modified = True
        self.update_window_title()
    
    def on_active_layer_changed(self, index: int):
        """Handle active layer change"""
        pass
    
    def on_canvas_mouse_pressed(self, x: int, y: int):
        """Handle canvas mouse press"""
        # In video mode, check for overlay interaction
        if self.mode == "video" and self.overlay_manager:
            overlay_id = self.overlay_manager.get_overlay_at_position((x, y))
            if overlay_id is not None:
                self.selected_overlay_id = overlay_id
                overlay = self.overlay_manager.get_overlay(overlay_id)
                
                # Check if clicking near corner (resize) or center (move)
                ox, oy = overlay.position
                w, h = overlay.size
                
                # Check corners for resize (10px tolerance)
                corners = [
                    (ox + w, oy + h),  # Bottom-right
                ]
                
                for cx, cy in corners:
                    if abs(x - cx) < 10 and abs(y - cy) < 10:
                        self.resizing_overlay = True
                        self.resize_start_pos = (x, y)
                        self.resize_start_size = (w, h)
                        return
                        
                # Otherwise, start dragging
                self.dragging_overlay = True
                self.drag_start_pos = (x - ox, y - oy)  # Offset within overlay
                return
        
        # Original plugin handling for image mode
        if self.active_plugin:
            layer = self.layer_manager.get_active_layer()
            if layer and hasattr(self.active_plugin, 'on_mouse_press'):
                result = self.active_plugin.on_mouse_press(x, y, layer.image)
                if result is not None:
                    # Check if it's bucket fill and there's a selection
                    plugin_name = self.active_plugin.get_name().lower()
                    if 'kova' in plugin_name or 'bucket' in plugin_name or 'fill' in plugin_name:
                        # If selection exists, apply only to selected area
                        if self.selection_manager and self.selection_manager.has_selection:
                            # Keep only the filled pixels that are within selection
                            result = self.selection_manager.apply_to_image(layer.image, result)
                    
                    layer.image = result
                    # Don't show selection overlay for drawing tools
                    self.layer_manager._cache_valid = False
                    composite = self.layer_manager.composite_layers()
                    self.canvas.update_image(composite)
                    self.is_modified = True
    
    def on_canvas_mouse_moved(self, x: int, y: int):
        """Handle canvas mouse move"""
        self.position_label.setText(f"⊙ Konum: ({x}, {y})")
        
        # In video mode, handle overlay dragging/resizing
        if self.mode == "video" and self.overlay_manager:
            if self.dragging_overlay and self.selected_overlay_id is not None:
                # Calculate new position
                new_x = x - self.drag_start_pos[0]
                new_y = y - self.drag_start_pos[1]
                self.overlay_manager.update_overlay_position(self.selected_overlay_id, (new_x, new_y))
                return
                
            elif self.resizing_overlay and self.selected_overlay_id is not None:
                # Calculate new size
                overlay = self.overlay_manager.get_overlay(self.selected_overlay_id)
                ox, oy = overlay.position
                
                new_width = max(50, x - ox)
                new_height = max(50, y - oy)
                self.overlay_manager.update_overlay_size(self.selected_overlay_id, (new_width, new_height))
                return
        
        # Original plugin handling
        if self.active_plugin:
            layer = self.layer_manager.get_active_layer()
            if layer and hasattr(self.active_plugin, 'on_mouse_move'):
                result = self.active_plugin.on_mouse_move(x, y, layer.image)
                if result is not None:
                    # For selection tools, show preview
                    # For drawing tools, update directly
                    plugin_name = self.active_plugin.get_name().lower()
                    if 'select' in plugin_name or 'lasso' in plugin_name:
                        # Selection tool preview
                        self.canvas.update_image(result)
                    else:
                        # Drawing tool - update layer
                        layer.image = result
                        self.layer_manager._cache_valid = False
                        composite = self.layer_manager.composite_layers()
                        self.canvas.update_image(composite)
    
    def on_canvas_mouse_released(self, x: int, y: int):
        """Handle canvas mouse release"""
        # In video mode, stop overlay interaction
        if self.mode == "video":
            self.dragging_overlay = False
            self.resizing_overlay = False
            self.drag_start_pos = None
            self.resize_start_pos = None
            self.resize_start_size = None
        
        # Original plugin handling
        if self.active_plugin:
            # Check if it's a selection tool
            plugin_name = self.active_plugin.get_name().lower()
            is_selection_tool = ('select' in plugin_name or 'lasso' in plugin_name)
            
            if is_selection_tool and self.selection_manager:
                # Handle selection tool completion
                if hasattr(self.active_plugin, 'get_selection_bounds'):
                    bounds = self.active_plugin.get_selection_bounds()
                    if bounds:
                        x1, y1, x2, y2 = bounds
                        mode = getattr(self.active_plugin, 'selection_mode', SelectionMode.NEW)
                        feather = getattr(self.active_plugin, 'feather', 0)
                        self.selection_manager.create_rectangle_selection(x1, y1, x2, y2, feather, mode)
                        
                        # Clear canvas preview and show selection overlay
                        layer = self.layer_manager.get_active_layer()
                        if layer:
                            self.show_selection_overlay(layer.image)
                        
                        # Update apply button
                        if self.active_effect_plugin:
                            self.apply_widget.set_selection_status(True)
                
                elif hasattr(self.active_plugin, 'get_selection_params'):
                    params = self.active_plugin.get_selection_params()
                    if params:
                        center_x, center_y, radius_x, radius_y = params
                        mode = getattr(self.active_plugin, 'selection_mode', SelectionMode.NEW)
                        feather = getattr(self.active_plugin, 'feather', 0)
                        self.selection_manager.create_ellipse_selection(
                            center_x, center_y, radius_x, radius_y, feather, mode)
                        
                        # Clear canvas preview and show selection overlay
                        layer = self.layer_manager.get_active_layer()
                        if layer:
                            self.show_selection_overlay(layer.image)
                        
                        # Update apply button
                        if self.active_effect_plugin:
                            self.apply_widget.set_selection_status(True)
                
                elif hasattr(self.active_plugin, 'get_selection_points'):
                    # For polygon mode, only create selection if explicitly finalized
                    # For free mode, create on mouse release
                    lasso_type = getattr(self.active_plugin, 'lasso_type', 'free')
                    
                    if lasso_type == 'polygon':
                        # Polygon mode: don't create selection on mouse release
                        # Selection is created when user finishes polygon (double-click or Enter)
                        pass
                    else:
                        # Free mode: create selection on mouse release
                        points = self.active_plugin.get_selection_points()
                        if points and len(points) > 2:
                            mode = getattr(self.active_plugin, 'selection_mode', SelectionMode.NEW)
                            feather = getattr(self.active_plugin, 'feather', 0)
                            self.selection_manager.create_lasso_selection(points, feather, mode)
                            
                            # Clear canvas preview and restore original image
                            layer = self.layer_manager.get_active_layer()
                            if layer:
                                self.show_selection_overlay(layer.image)
                            
                            # Update apply button
                            if self.active_effect_plugin:
                                self.apply_widget.set_selection_status(True)
                            
                            # Clear points for next selection
                            if hasattr(self.active_plugin, 'clear_points'):
                                self.active_plugin.clear_points()
            
            # Regular tool handling (non-selection tools like brush)
            layer = self.layer_manager.get_active_layer()
            if layer and hasattr(self.active_plugin, 'on_mouse_release'):
                result = self.active_plugin.on_mouse_release(x, y, layer.image)
                if result is not None:
                    layer.image = result
                    # Update without selection overlay
                    self.layer_manager._cache_valid = False
                    composite = self.layer_manager.composite_layers()
                    self.canvas.update_image(composite)
                    self.is_modified = True
    
    def on_canvas_double_clicked(self, x: int, y: int):
        """Handle canvas double-click (finalize polygon)"""
        if self.active_plugin:
            plugin_name = self.active_plugin.get_name().lower()
            is_lasso = 'lasso' in plugin_name
            
            if is_lasso and self.selection_manager:
                lasso_type = getattr(self.active_plugin, 'lasso_type', 'free')
                
                if lasso_type == 'polygon':
                    # Finalize polygon selection
                    points = self.active_plugin.get_selection_points()
                    if points and len(points) > 2:
                        mode = getattr(self.active_plugin, 'selection_mode', SelectionMode.NEW)
                        feather = getattr(self.active_plugin, 'feather', 0)
                        self.selection_manager.create_lasso_selection(points, feather, mode)
                        
                        # Clear canvas preview and show selection overlay
                        layer = self.layer_manager.get_active_layer()
                        if layer:
                            self.show_selection_overlay(layer.image)
                        
                        # Update apply button
                        if self.active_effect_plugin:
                            self.apply_widget.set_selection_status(True)
                        
                        # Clear points for next selection
                        if hasattr(self.active_plugin, 'clear_points'):
                            self.active_plugin.clear_points()
                        
                        self.status_bar.showMessage("Polygon selection completed", 2000)
    
    def on_zoom_changed(self, zoom: float):
        """Handle zoom level change"""
        self.zoom_label.setText(f"Zoom: {int(zoom * 100)}%")
    
    def show_selection_overlay(self, base_image: np.ndarray):
        """Show selection with visual overlay"""
        if not self.selection_manager or not self.selection_manager.has_selection:
            # Show composite of all layers
            composite = self.layer_manager.composite_layers()
            self.canvas.update_image(composite)
            return
        
        # Get composite image
        composite = self.layer_manager.composite_layers()
        
        # Get selection overlay based on composite size
        overlay = self.selection_manager.get_selection_overlay(composite.shape[:2])
        if overlay is None:
            self.canvas.update_image(composite)
            return
        
        # Blend overlay with composite
        result = composite.copy()
        if len(result.shape) == 2:
            result = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)
        
        # Add alpha channel if needed
        if result.shape[2] == 3:
            result = cv2.cvtColor(result, cv2.COLOR_BGR2BGRA)
        
        # Blend overlay
        alpha = overlay[:, :, 3] / 255.0
        for c in range(3):
            result[:, :, c] = (alpha * overlay[:, :, c] + (1 - alpha) * result[:, :, c]).astype(np.uint8)
        
        # Convert back to BGR for display
        result = cv2.cvtColor(result, cv2.COLOR_BGRA2BGR)
        self.canvas.update_image(result)
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        if event.key() == Qt.Key_C and event.modifiers() == Qt.ControlModifier:
            # Copy selection (Ctrl+C)
            self.on_copy_selection()
        elif event.key() == Qt.Key_V and event.modifiers() == Qt.ControlModifier:
            # Paste selection (Ctrl+V)
            self.on_paste_selection()
        elif event.key() == Qt.Key_Delete or event.key() == Qt.Key_Backspace:
            # Delete selection (Delete/Backspace)
            self.on_delete_selection()
        elif event.key() == Qt.Key_D and event.modifiers() == Qt.ControlModifier:
            # Deselect (Ctrl+D)
            self.on_deselect()
        else:
            super().keyPressEvent(event)
    
    def on_copy_selection(self):
        """Copy selected area to clipboard"""
        if not self.selection_manager or not self.selection_manager.has_selection:
            self.status_bar.showMessage("Kopyalanacak seçim yok", 2000)
            return
        
        layer = self.layer_manager.get_active_layer()
        if not layer:
            return
        
        if self.selection_manager.copy_selection(layer.image):
            self.status_bar.showMessage("Seçim panoya kopyalandı", 2000)
        else:
            self.status_bar.showMessage("Kopyalama başarısız", 2000)
    
    def on_paste_selection(self):
        """Paste clipboard image"""
        if not self.selection_manager or self.selection_manager.clipboard_image is None:
            self.status_bar.showMessage("Pano boş", 2000)
            return
        
        layer = self.layer_manager.get_active_layer()
        if not layer:
            return
        
        # Paste at top-left corner for now
        result = self.selection_manager.paste_selection(layer.image, 10, 10)
        if result is not None:
            layer.image = result
            self.on_layer_changed()
            self.status_bar.showMessage("Panodan yapıştırıldı", 2000)
        else:
            self.status_bar.showMessage("Yapıştırma başarısız", 2000)
    
    def on_delete_selection(self):
        """Delete selected area (fill with white)"""
        if not self.selection_manager or not self.selection_manager.has_selection:
            self.status_bar.showMessage("Silinecek seçim yok", 2000)
            return
        
        layer = self.layer_manager.get_active_layer()
        if not layer:
            return
        
        result = self.selection_manager.delete_selection(layer.image)
        if result is not None:
            layer.image = result
            self.on_layer_changed()
            self.show_selection_overlay(layer.image)
            self.status_bar.showMessage("Seçim silindi", 2000)
        else:
            self.status_bar.showMessage("Silme başarısız", 2000)
    
    def on_deselect(self):
        """Clear current selection"""
        if self.selection_manager:
            self.selection_manager.clear_selection()
            layer = self.layer_manager.get_active_layer()
            if layer:
                self.canvas.load_image(layer.image)
            self.status_bar.showMessage("Seçim kaldırıldı", 2000)
    
    def update_window_title(self):
        """Update the window title"""
        title = "Görsel Düzenleyici"
        if self.current_file:
            title += f" - {Path(self.current_file).name}"
        if self.is_modified:
            title += " *"
        self.setWindowTitle(title)
    
    def update_image_info(self, image: np.ndarray):
        """Update image information in status bar"""
        if image is not None:
            h, w = image.shape[:2]
            channels = image.shape[2] if len(image.shape) > 2 else 1
            self.info_label.setText(f"▭ Boyut: {w}x{h} | Kanallar: {channels}")
        else:
            self.info_label.setText("▭ Resim yüklenmedi")
    
    def on_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "Görsel Düzenleyici Hakkında",
            "Görsel Düzenleyici v1.0.0\n\n"
            "Profesyonel Resim & Video İşleme Yazılımı\n"
            "Python, PySide6 ve OpenCV ile geliştirildi\n\n"
            "✨ Eklenti Tabanlı Mimari ile Genişletilebilir"
        )
    
    def apply_styles(self):
        """Apply stylesheet to the editor"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            
            QMenuBar {
                background-color: #2b2b2b;
                color: #e0e0e0;
                border-bottom: 1px solid #1e1e1e;
            }
            
            QMenuBar::item:selected {
                background-color: #3a3a3a;
            }
            
            QMenu {
                background-color: #2b2b2b;
                color: #e0e0e0;
                border: 1px solid #3a3a3a;
            }
            
            QMenu::item:selected {
                background-color: #0078d4;
            }
            
            QToolBar {
                background-color: #2b2b2b;
                border: none;
                spacing: 3px;
                padding: 3px;
            }
            
            QToolButton {
                background-color: #3a3a3a;
                color: #e0e0e0;
                border: 1px solid #505050;
                border-radius: 3px;
                padding: 5px;
                min-width: 40px;
            }
            
            QToolButton:hover {
                background-color: #4a4a4a;
                border: 1px solid #0078d4;
            }
            
            QToolButton:checked {
                background-color: #0078d4;
                border: 1px solid #0078d4;
            }
            
            QToolButton:pressed {
                background-color: #005a9e;
            }
            
            QStatusBar {
                background-color: #1e1e1e;
                color: #b0b0b0;
                border-top: 1px solid #3a3a3a;
            }
            
            QDockWidget {
                color: #e0e0e0;
                titlebar-close-icon: url(close.png);
                titlebar-normal-icon: url(float.png);
            }
            
            QDockWidget::title {
                background-color: #2b2b2b;
                padding: 5px;
                border-bottom: 1px solid #3a3a3a;
            }
            
            #panelTitle {
                font-size: 12px;
                font-weight: bold;
                padding: 5px;
                color: #e0e0e0;
            }
            
            #sectionTitle {
                font-size: 10px;
                font-weight: bold;
                color: #0078d4;
                padding: 3px;
                letter-spacing: 1px;
            }
            
            QLabel {
                color: #e0e0e0;
            }
            
            QScrollArea {
                border: none;
                background-color: #2b2b2b;
            }
        """)
    
    def on_camera_toggle(self, start):
        """Handle camera toggle"""
        if start:
            if self.video_system.start_camera():
                self.status_bar.showMessage("Kamera açıldı", 2000)
                # Clear canvas first
                self.canvas.scene.clear()
                self.canvas.image_item = None
            else:
                self.status_bar.showMessage("Kamera açılamadı!", 3000)
                self.video_control_panel.camera_btn.setChecked(False)
        else:
            self.video_system.stop_camera()
            self.status_bar.showMessage("Kamera kapatıldı", 2000)
            # Clear canvas
            self.canvas.scene.clear()
            self.canvas.image_item = None
    
    def on_recording_toggle(self):
        """Handle recording toggle"""
        if not self.video_system.is_recording:
            # Start recording - ask for output path
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Video Kaydet",
                "",
                "Video Files (*.mp4 *.avi *.mov *.mkv)"
            )
            
            if file_path:
                # Get selected format from control panel
                video_format = self.video_control_panel.get_selected_format()
                
                if self.video_system.start_recording(file_path, video_format):
                    self.status_bar.showMessage("Kayıt başladı", 2000)
                else:
                    self.status_bar.showMessage("Kayıt başlatılamadı!", 3000)
                    self.video_control_panel.set_recording_status(False)
        else:
            # Stop recording
            output_path = self.video_system.stop_recording()
            if output_path:
                self.status_bar.showMessage(f"Kayıt tamamlandı: {output_path}", 5000)
    
    def on_snapshot(self):
        """Handle snapshot request"""
        snapshot = self.video_system.take_snapshot()
        if snapshot is None:
            self.status_bar.showMessage("Snapshot alınamadı!", 3000)
            return
        
        # Ask for save location
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Snapshot Kaydet",
            "",
            "Image Files (*.png *.jpg *.jpeg)"
        )
        
        if file_path:
            cv2.imwrite(file_path, snapshot)
            self.status_bar.showMessage(f"Snapshot kaydedildi: {file_path}", 5000)
    
    def on_video_frame_ready(self, frame):
        """Handle new video frame"""
        # Add REC indicator if recording
        display_frame = frame.copy()
        
        if self.video_system.is_recording:
            # Add red circle and REC text
            cv2.circle(display_frame, (30, 30), 10, (0, 0, 255), -1)
            cv2.putText(display_frame, "REC", (50, 40), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # Display frame on canvas
        # Use load_image for first frame to fit view, update_image for subsequent frames
        if self.canvas.image_item is None:
            self.canvas.load_image(display_frame)
        else:
            self.canvas.update_image(display_frame)
    
    def on_recording_status_changed(self, is_recording):
        """Handle recording status change"""
        # Update UI if needed
        pass
    
    def on_add_text_overlay(self, text, font_size, color, font_family, name):
        """Handle add text overlay"""
        # Add at center of screen
        if self.video_system.current_frame is not None:
            h, w = self.video_system.current_frame.shape[:2]
            position = (w // 4, h // 2)
        else:
            position = (100, 100)
            
        overlay_id = self.overlay_manager.add_text_overlay(text, position, font_size, color, font_family, name)
        if overlay_id:
            self.status_bar.showMessage(f"Text overlay eklendi: {text}", 2000)
            
    def on_add_image_overlay(self, image_path, name):
        """Handle add image overlay"""
        # Add at top-left with default size
        position = (50, 50)
        size = (200, 200)  # Default size
        
        overlay_id = self.overlay_manager.add_image_overlay(image_path, position, size, name)
        if overlay_id:
            self.status_bar.showMessage(f"Resim overlay eklendi", 2000)
        else:
            self.status_bar.showMessage("Resim yüklenemedi!", 3000)
            
    def on_add_video_overlay(self, video_path, name):
        """Handle add video overlay"""
        # Add at top-left with default size
        position = (50, 50)
        size = (200, 150)  # Default size
        
        overlay_id = self.overlay_manager.add_video_overlay(video_path, position, size, name)
        if overlay_id:
            self.status_bar.showMessage(f"Video overlay eklendi", 2000)
        else:
            self.status_bar.showMessage("Video yüklenemedi!", 3000)
            
    def on_remove_overlay(self, overlay_id):
        """Handle remove overlay"""
        self.overlay_manager.remove_overlay(overlay_id)
        self.status_bar.showMessage("Overlay silindi", 2000)
        
    def on_overlay_selected(self, overlay_id):
        """Handle overlay selection"""
        self.selected_overlay_id = overlay_id
