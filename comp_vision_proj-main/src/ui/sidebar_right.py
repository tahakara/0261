"""
Right sidebar - Contains module settings panel and layer system.
"""

from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QFrame,
    QPushButton, QLabel, QSlider, QListWidget, QListWidgetItem,
    QSplitter, QToolButton, QComboBox, QCheckBox, QMenu,
    QSizePolicy, QStackedWidget, QSpinBox, QInputDialog
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QIcon, QAction

from ..core.module_base import ModuleBase
from ..core.layer import Layer, LayerManager, BlendMode


class ModuleSettingsPanel(QFrame):
    """
    Panel for displaying module-specific settings.
    The content changes based on the selected module.
    """
    
    # Signal emitted when user requests to apply the current module
    apply_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setStyleSheet("""
            ModuleSettingsPanel {
                background-color: #252526;
                border: none;
                border-bottom: 1px solid #3c3c3c;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QWidget()
        header.setStyleSheet("background-color: #2d2d2d;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(12, 8, 12, 8)
        
        self._title = QLabel("Module Settings")
        self._title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self._title.setStyleSheet("color: #ffffff;")
        header_layout.addWidget(self._title)
        header_layout.addStretch()

        # Apply button for applying module effects
        self._apply_btn = QPushButton("Apply")
        self._apply_btn.setFixedSize(80, 28)
        self._apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 4px 8px;
            }
            QPushButton:hover {
                background-color: #1084d8;
            }
        """)
        header_layout.addWidget(self._apply_btn)
        header_layout.addStretch()
        
        layout.addWidget(header)
        
        # Content area (stacked widget for different module settings)
        self._content_stack = QStackedWidget()
        self._content_stack.setStyleSheet("background-color: #252526;")
        
        # Default empty widget
        empty_widget = QWidget()
        empty_layout = QVBoxLayout(empty_widget)
        empty_label = QLabel("Select a module to see its settings")
        empty_label.setAlignment(Qt.AlignCenter)
        empty_label.setStyleSheet("color: #666666; padding: 20px;")
        empty_layout.addWidget(empty_label)
        empty_layout.addStretch()
        self._content_stack.addWidget(empty_widget)
        
        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #252526;
            }
        """)
        scroll.setWidget(self._content_stack)
        
        layout.addWidget(scroll)
        
        self._current_module: Optional[ModuleBase] = None
        # Connect internal button to emit apply_requested
        self._apply_btn.clicked.connect(lambda: self.apply_requested.emit())
    
    def set_module(self, module: Optional[ModuleBase]):
        """Set the current module and display its settings."""
        self._current_module = module
        
        if module is None:
            self._title.setText("Module Settings")
            self._content_stack.setCurrentIndex(0)
            return
        
        self._title.setText(f"{module.name} Settings")
        
        # Get or create settings widget for this module
        settings_widget = module.get_settings_widget()
        
        if settings_widget is None:
            self._content_stack.setCurrentIndex(0)
        else:
            # Check if widget already added
            index = -1
            for i in range(self._content_stack.count()):
                if self._content_stack.widget(i) == settings_widget:
                    index = i
                    break
            
            if index == -1:
                index = self._content_stack.addWidget(settings_widget)
            
            self._content_stack.setCurrentIndex(index)


class LayerListItem(QWidget):
    """Custom widget for layer list items."""
    
    visibility_changed = Signal(bool)
    
    def __init__(self, layer: Layer, parent=None):
        super().__init__(parent)
        self._layer = layer
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)
        
        # Visibility toggle
        self._visible_btn = QToolButton()
        self._visible_btn.setText("👁")
        self._visible_btn.setCheckable(True)
        self._visible_btn.setChecked(layer.visible)
        self._visible_btn.setFixedSize(24, 24)
        self._visible_btn.setStyleSheet("""
            QToolButton {
                background: transparent;
                border: none;
                font-size: 14px;
            }
            QToolButton:checked {
                color: #ffffff;
            }
            QToolButton:!checked {
                color: #666666;
            }
        """)
        self._visible_btn.toggled.connect(self._on_visibility_toggled)
        layout.addWidget(self._visible_btn)
        
        # Layer name
        self._name_label = QLabel(layer.name)
        self._name_label.setStyleSheet("color: #cccccc;")
        layout.addWidget(self._name_label)
        layout.addStretch()
        
        # Lock indicator
        if layer.locked:
            lock_label = QLabel("🔒")
            lock_label.setStyleSheet("font-size: 12px;")
            layout.addWidget(lock_label)
        
        # Add rename functionality to LayerListItem
        self._rename_btn = QToolButton()
        self._rename_btn.setText("✏️")
        self._rename_btn.setFixedSize(24, 24)
        self._rename_btn.setStyleSheet("""
            QToolButton {
                background: transparent;
                border: none;
                font-size: 14px;
            }
            QToolButton:hover {
                color: #ffffff;
            }
        """)
        self._rename_btn.clicked.connect(self._on_rename_clicked)
        layout.addWidget(self._rename_btn)
    
    @property
    def layer(self) -> Layer:
        return self._layer
    
    def _on_visibility_toggled(self, visible: bool):
        self._layer.visible = visible
        # Update visibility toggle to use closed eye icon when unchecked
        self._visible_btn.setText("👁" if self._layer.visible else "🙈")
        self.visibility_changed.emit(visible)
    
    def update_from_layer(self):
        """Update widget to reflect layer state."""
        self._name_label.setText(self._layer.name)
        self._visible_btn.setChecked(self._layer.visible)
    
    def _on_rename_clicked(self):
        new_name, ok = QInputDialog.getText(self, "Rename Layer", "Enter new layer name:")
        if ok and new_name.strip():
            self._layer.name = new_name.strip()
            self.update_from_layer()


class LayerPanel(QFrame):
    """
    Panel for managing layers.
    """
    
    layer_selected = Signal(int)  # layer index
    layer_visibility_changed = Signal(int, bool)  # index, visible
    layer_add_requested = Signal()
    layer_delete_requested = Signal(int)
    layer_duplicate_requested = Signal(int)
    layer_rename_requested = Signal(int)
    layer_merge_requested = Signal(int)
    layer_move_up_requested = Signal(int)
    layer_move_down_requested = Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setStyleSheet("""
            LayerPanel {
                background-color: #252526;
                border: none;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QWidget()
        header.setStyleSheet("background-color: #2d2d2d;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(12, 8, 8, 8)
        

        title = QLabel("Layers")

        title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        title.setStyleSheet("color: #ffffff;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        layout.addWidget(header)
        
        # Blend mode and opacity controls
        controls = QWidget()
        controls.setStyleSheet("background-color: #252526;")
        controls_layout = QVBoxLayout(controls)
        controls_layout.setContentsMargins(8, 8, 8, 8)
        controls_layout.setSpacing(6)
        
        # Blend mode
        blend_layout = QHBoxLayout()
        blend_label = QLabel("Blend:")
        blend_label.setStyleSheet("color: #888888; font-size: 11px;")
        blend_label.setFixedWidth(50)
        blend_layout.addWidget(blend_label)
        
        self._blend_combo = QComboBox()
        self._blend_combo.addItems([
            "Normal", "Multiply", "Screen", "Overlay",
            "Soft Light", "Hard Light", "Difference", "Add", "Subtract"
        ])
        self._blend_combo.setStyleSheet("""
            QComboBox {
                background-color: #3c3c3c;
                color: #cccccc;
                border: 1px solid #4a4a4a;
                border-radius: 4px;
                padding: 4px 8px;
            }
            QComboBox:hover {
                border-color: #5a5a5a;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
        """)
        blend_layout.addWidget(self._blend_combo)
        controls_layout.addLayout(blend_layout)
        
        # Opacity
        opacity_layout = QHBoxLayout()
        opacity_label = QLabel("Opacity:")
        opacity_label.setStyleSheet("color: #888888; font-size: 11px;")
        opacity_label.setFixedWidth(50)
        opacity_layout.addWidget(opacity_label)
        
        self._opacity_slider = QSlider(Qt.Horizontal)
        self._opacity_slider.setRange(0, 100)
        self._opacity_slider.setValue(100)
        self._opacity_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: #3c3c3c;
                height: 6px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #0078d4;
                width: 14px;
                height: 14px;
                margin: -4px 0;
                border-radius: 7px;
            }
            QSlider::sub-page:horizontal {
                background: #0078d4;
                border-radius: 3px;
            }
        """)
        opacity_layout.addWidget(self._opacity_slider)
        
        self._opacity_label = QLabel("100%")
        self._opacity_label.setStyleSheet("color: #cccccc; font-size: 11px;")
        self._opacity_label.setFixedWidth(35)
        self._opacity_slider.valueChanged.connect(
            lambda v: self._opacity_label.setText(f"{v}%")
        )
        opacity_layout.addWidget(self._opacity_label)
        controls_layout.addLayout(opacity_layout)
        
        layout.addWidget(controls)
        
        # Layer list
        self._layer_list = QListWidget()
        self._layer_list.setStyleSheet("""
            QListWidget {
                background-color: #1e1e1e;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
            }
            QListWidget::item {
                padding: 2px;
                border-bottom: 1px solid #2a2a2a;
            }
            QListWidget::item:selected {
                background-color: #0078d4;
            }
            QListWidget::item:hover:!selected {
                background-color: #2a2a2a;
            }
        """)
        self._layer_list.setDragDropMode(QListWidget.InternalMove)
        self._layer_list.currentRowChanged.connect(self.layer_selected)
        self._layer_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self._layer_list.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self._layer_list)
        
        # Layer action buttons
        buttons = QWidget()
        buttons_layout = QHBoxLayout(buttons)
        buttons_layout.setContentsMargins(8, 8, 8, 8)
        buttons_layout.setSpacing(4)
        
        btn_style = """
            QPushButton {
                background-color: #3c3c3c;
                color: #cccccc;
                border: none;
                border-radius: 4px;
                padding: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
            QPushButton:pressed {
                background-color: #2a2a2a;
            }
        """
        
        self._add_btn = QPushButton("➕")
        self._add_btn.setToolTip("Add Layer")
        self._add_btn.setFixedSize(32, 32)
        self._add_btn.setStyleSheet(btn_style)
        self._add_btn.clicked.connect(self.layer_add_requested)
        buttons_layout.addWidget(self._add_btn)
        
        self._delete_btn = QPushButton("🗑")
        self._delete_btn.setToolTip("Delete Layer")
        self._delete_btn.setFixedSize(32, 32)
        self._delete_btn.setStyleSheet(btn_style)
        self._delete_btn.clicked.connect(
            lambda: self.layer_delete_requested.emit(self._layer_list.currentRow())
        )
        buttons_layout.addWidget(self._delete_btn)
        
        self._duplicate_btn = QPushButton("📋")
        self._duplicate_btn.setToolTip("Duplicate Layer")
        self._duplicate_btn.setFixedSize(32, 32)
        self._duplicate_btn.setStyleSheet(btn_style)
        self._duplicate_btn.clicked.connect(
            lambda: self.layer_duplicate_requested.emit(self._layer_list.currentRow())
        )
        buttons_layout.addWidget(self._duplicate_btn)
        
        buttons_layout.addStretch()
        
        self._up_btn = QPushButton("⬆")
        self._up_btn.setToolTip("Move Up")
        self._up_btn.setFixedSize(32, 32)
        self._up_btn.setStyleSheet(btn_style)
        self._up_btn.clicked.connect(
            lambda: self.layer_move_up_requested.emit(self._layer_list.currentRow())
        )
        buttons_layout.addWidget(self._up_btn)
        
        self._down_btn = QPushButton("⬇")
        self._down_btn.setToolTip("Move Down")
        self._down_btn.setFixedSize(32, 32)
        self._down_btn.setStyleSheet(btn_style)
        self._down_btn.clicked.connect(
            lambda: self.layer_move_down_requested.emit(self._layer_list.currentRow())
        )
        buttons_layout.addWidget(self._down_btn)
        
        layout.addWidget(buttons)

    def set_layer_manager(self, manager: LayerManager):
        """Set the layer manager to display."""
        self._layer_manager: Optional[LayerManager] = manager

        # Connect signals
        manager.layer_added.connect(self._refresh_list)
        manager.layer_removed.connect(self._refresh_list)
        manager.layer_moved.connect(self._refresh_list)
        manager.layer_changed.connect(self._refresh_list)
        manager.active_layer_changed.connect(self._on_active_changed)

        self._refresh_list()

    def _refresh_list(self, *args):
        """Refresh the layer list."""
        if getattr(self, '_layer_manager', None) is None:
            return

        self._layer_list.clear()

        # Add layers in reverse order (top to bottom)
        for layer in reversed(self._layer_manager.layers):
            item = QListWidgetItem()
            item.setSizeHint(QSize(0, 36))

            widget = LayerListItem(layer)
            widget.visibility_changed.connect(
                lambda v, l=layer: self._on_visibility_changed(l, v)
            )

            self._layer_list.addItem(item)
            self._layer_list.setItemWidget(item, widget)

        # Select active layer
        if self._layer_manager.active_index >= 0:
            visual_index = self._layer_manager.layer_count - 1 - self._layer_manager.active_index
            self._layer_list.setCurrentRow(visual_index)

    def _on_active_changed(self, index: int):
        """Handle active layer change."""
        if self._layer_manager:
            visual_index = self._layer_manager.layer_count - 1 - index
            self._layer_list.setCurrentRow(visual_index)

    def _on_visibility_changed(self, layer: Layer, visible: bool):
        """Handle layer visibility change."""
        if self._layer_manager:
            index = self._layer_manager.layers.index(layer)
            self.layer_visibility_changed.emit(index, visible)

    def _show_context_menu(self, pos):
        """Show context menu for layer."""
        item = self._layer_list.itemAt(pos)
        if item is None:
            return

        row = self._layer_list.row(item)
        menu = QMenu(self)

        menu.addAction("Duplicate", lambda: self.layer_duplicate_requested.emit(row))
        menu.addAction("Delete", lambda: self.layer_delete_requested.emit(row))
        menu.addAction("Rename", lambda: self.layer_rename_requested.emit(row))
        menu.addSeparator()
        menu.addAction("Merge Down", lambda: self.layer_merge_requested.emit(row))
        menu.addAction("Merge All", lambda: self.layer_merge_requested.emit(-1))

        menu.exec(self._layer_list.mapToGlobal(pos))


class SelectionSettingsPanel(QFrame):
    """Panel for selection tool configuration."""

    clear_requested = Signal()
    brush_radius_changed = Signal(int)
    brush_softness_changed = Signal(int)
    brush_transparency_changed = Signal(int)
    brush_step_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            SelectionSettingsPanel {
                background-color: #252526;
                border: none;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)

        header = QWidget()
        header.setStyleSheet("background-color: #2d2d2d;")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(12,8,12,8)
        self._title = QLabel("Selection Settings")
        self._title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self._title.setStyleSheet("color: #ffffff;")
        hl.addWidget(self._title)
        hl.addStretch()
        layout.addWidget(header)

        content = QWidget()
        cl = QVBoxLayout(content)
        cl.setContentsMargins(8,8,8,8)
        cl.setSpacing(8)

        # Brush radius control
        self._brush_label = QLabel("Brush Radius:")
        self._brush_label.setStyleSheet("color: #cccccc;")
        cl.addWidget(self._brush_label)

        self._brush_spin = QSpinBox()
        self._brush_spin.setRange(1, 500)
        self._brush_spin.setValue(20)
        self._brush_spin.valueChanged.connect(self._on_brush_change)
        cl.addWidget(self._brush_spin)

        # Brush softness control
        self._softness_label = QLabel("Softness (0-100):")
        self._softness_label.setStyleSheet("color: #cccccc;")
        cl.addWidget(self._softness_label)

        self._softness_spin = QSpinBox()
        self._softness_spin.setRange(0, 100)
        self._softness_spin.setValue(0)
        self._softness_spin.valueChanged.connect(self._on_softness_change)
        cl.addWidget(self._softness_spin)

        # Brush transparency control
        self._transparency_label = QLabel("Transparency (0-100):")
        self._transparency_label.setStyleSheet("color: #cccccc;")
        cl.addWidget(self._transparency_label)

        self._transparency_spin = QSpinBox()
        self._transparency_spin.setRange(0, 100)
        self._transparency_spin.setValue(0)
        self._transparency_spin.valueChanged.connect(self._on_transparency_change)
        cl.addWidget(self._transparency_spin)

        # Brush step control
        self._step_label = QLabel("Step (1-100):")
        self._step_label.setStyleSheet("color: #cccccc;")
        cl.addWidget(self._step_label)

        self._step_spin = QSpinBox()
        self._step_spin.setRange(1, 100)
        self._step_spin.setValue(5)
        self._step_spin.valueChanged.connect(self._on_step_change)
        cl.addWidget(self._step_spin)

        # Clear selection button
        self._clear_btn = QPushButton("Clear Selection")
        self._clear_btn.setFixedHeight(28)
        self._clear_btn.clicked.connect(lambda: self.clear_requested.emit())
        cl.addWidget(self._clear_btn)

        cl.addStretch()
        layout.addWidget(content)

    def _on_brush_change(self, v: int):
        self.brush_radius_changed.emit(v)

    def _on_softness_change(self, v: int):
        self.brush_softness_changed.emit(v)

    def _on_transparency_change(self, v: int):
        self.brush_transparency_changed.emit(v)

    def _on_step_change(self, v: int):
        self.brush_step_changed.emit(v)


class RightSidebar(QSplitter):
    """
    Right sidebar containing module settings panel (top) and layer panel (bottom).
    """
    
    # Forward signals from layer panel
    layer_selected = Signal(int)
    layer_visibility_changed = Signal(int, bool)
    layer_add_requested = Signal()
    layer_delete_requested = Signal(int)
    layer_duplicate_requested = Signal(int)
    layer_merge_requested = Signal(int)
    layer_move_up_requested = Signal(int)
    layer_move_down_requested = Signal(int)
    
    # Forwarded apply request from settings panel
    apply_requested = Signal()
    # Forwarded rename request
    layer_rename_requested = Signal(int)

    # Overlay signals (video mode)
    overlay_selected = Signal(int)
    overlay_visibility_changed = Signal(int, bool)
    overlay_add_requested = Signal()
    overlay_delete_requested = Signal(int)
    overlay_move_up_requested = Signal(int)
    overlay_move_down_requested = Signal(int)
    overlay_rename_requested = Signal(int, str)

    def __init__(self, parent=None):
        super().__init__(Qt.Vertical, parent)
        
        self.setMinimumWidth(250)
        self.setMaximumWidth(350)
        self.setStyleSheet("""
            QSplitter {
                background-color: #252526;
                border-left: 1px solid #3c3c3c;
            }
            QSplitter::handle {
                background-color: #3c3c3c;
                height: 4px;
            }
            QSplitter::handle:hover {
                background-color: #0078d4;
            }
        """)
        
        # Settings stack (module settings or selection settings)
        self._settings_stack = QStackedWidget()
        self._module_panel = ModuleSettingsPanel()
        self._selection_panel = SelectionSettingsPanel()
        self._module_panel.apply_requested.connect(self.apply_requested)
        # selection panel signals
        self._selection_panel.clear_requested.connect(lambda: None)
        self._selection_panel.brush_radius_changed.connect(lambda v: None)
        self._settings_stack.addWidget(self._module_panel)
        self._settings_stack.addWidget(self._selection_panel)
        self.addWidget(self._settings_stack)
        
        # Bottom stack: layers or video overlays
        self._bottom_stack = QStackedWidget()
        self._layer_panel = LayerPanel()
        self._overlay_panel = VideoOverlayPanel()
        self._bottom_stack.addWidget(self._layer_panel)
        self._bottom_stack.addWidget(self._overlay_panel)
        self.addWidget(self._bottom_stack)
        
        # Forward signals (layers)
        self._layer_panel.layer_selected.connect(self.layer_selected)
        self._layer_panel.layer_visibility_changed.connect(self.layer_visibility_changed)
        self._layer_panel.layer_add_requested.connect(self.layer_add_requested)
        self._layer_panel.layer_delete_requested.connect(self.layer_delete_requested)
        self._layer_panel.layer_duplicate_requested.connect(self.layer_duplicate_requested)
        self._layer_panel.layer_rename_requested.connect(self.layer_rename_requested)
        self._layer_panel.layer_merge_requested.connect(self.layer_merge_requested)
        self._layer_panel.layer_move_up_requested.connect(self.layer_move_up_requested)
        self._layer_panel.layer_move_down_requested.connect(self.layer_move_down_requested)

        # Forward signals (video overlays)
        self._overlay_panel.overlay_selected.connect(lambda i: self.overlay_selected.emit(i))
        self._overlay_panel.overlay_visibility_changed.connect(lambda i,v: self.overlay_visibility_changed.emit(i, v))
        self._overlay_panel.overlay_add_requested.connect(lambda: self.overlay_add_requested.emit())
        self._overlay_panel.overlay_delete_requested.connect(lambda i: self.overlay_delete_requested.emit(i))
        self._overlay_panel.overlay_move_up_requested.connect(lambda i: self.overlay_move_up_requested.emit(i))
        self._overlay_panel.overlay_move_down_requested.connect(lambda i: self.overlay_move_down_requested.emit(i))
        self._overlay_panel.overlay_rename_requested.connect(lambda i,n: self.overlay_rename_requested.emit(i, n))
        
        # Set initial sizes (60% settings, 40% layers)
        self.setSizes([300, 200])

        # Initialize project reference
        self._project = None

        # Ensure _layer_manager is initialized before use
        if not hasattr(self, '_layer_manager'):
            self._layer_manager = None

    def set_project(self, project):
        """Set the project reference."""
        self._project = project
    
    def set_module(self, module: Optional[ModuleBase]):
        """Set the current module for settings panel."""
        # switch to module panel and set module
        self._settings_stack.setCurrentWidget(self._module_panel)
        self._module_panel.set_module(module)

    def show_selection_settings(self, mode: str):
        """Show selection settings for given mode (rect/lasso/brush)."""
        # configure selection panel title/content based on mode
        title = "Selection Settings"
        if mode == 'rect':
            title = "Rectangular Selection"
        elif mode == 'lasso':
            title = "Lasso Selection"
        elif mode == 'brush':
            title = "Brush Selection"
        self._selection_panel._title.setText(title)
        # show selection panel
        self._settings_stack.setCurrentWidget(self._selection_panel)
    
    def set_layer_manager(self, manager: LayerManager):
        """Set the layer manager for layer panel."""
        self._layer_panel.set_layer_manager(manager)

        # Connect opacity slider to update layer opacity
        self._layer_panel._opacity_slider.valueChanged.connect(self._on_opacity_change)

    def show_overlay_panel(self, overlays_provider):
        """Show video overlays panel and hook provider callbacks."""
        self._bottom_stack.setCurrentWidget(self._overlay_panel)
        try:
            self._overlay_panel.refresh(overlays_provider.get_overlays())
            overlays_provider.overlays_changed.connect(lambda: self._overlay_panel.refresh(overlays_provider.get_overlays()))
            self._overlays_provider = overlays_provider
        except Exception:
            pass

    def show_layer_panel(self):
        self._bottom_stack.setCurrentWidget(self._layer_panel)

    def _on_opacity_change(self, value):
        """Update the opacity of the active layer."""
        if self._project:
            layer, _ = self._project.layer_manager.active_layer, self._project.layer_manager.active_index
            if layer:
                # Directly update opacity without emitting layer_changed
                # Show loading indicator while applying opacity change
                self._show_loading_indicator("Applying opacity...")
                # Ensure opacity change applies to the correct layer
                active_layer = self._project.layer_manager.active_layer
                if layer == active_layer:
                    layer.opacity = value / 100.0
                    # Ensure all layers are rendered together
                    if self._layer_manager:
                        for layer in self._layer_manager.layers:
                            if layer.visible:
                                layer.render()  # Assuming render() is the method to draw the layer
                        self._layer_manager.layer_changed.emit(-1)  # Emit signal to refresh all layers
                self._hide_loading_indicator()

    def _show_loading_indicator(self, message: str):
        """Display a loading indicator with a message."""
        # Placeholder implementation for loading indicator
        # print(f"Loading: {message}")

    def _hide_loading_indicator(self):
        """Hide the loading indicator."""
        # Placeholder implementation for hiding loading indicator
        # print("Loading complete.")

    def change_layer(self, layer_index: int):
        """Change the active layer."""
        # Show loading indicator when changing or adding layers
        self._show_loading_indicator("Applying changes...")
        try:
            self._layer_manager.set_active_layer(layer_index)
        finally:
            self._hide_loading_indicator()

    def add_layer(self, new_layer: Layer):
        """Add a new layer."""
        # Show loading indicator when changing or adding layers
        self._show_loading_indicator("Applying changes...")
        try:
            self._layer_manager.add_layer(new_layer)
        finally:
            self._hide_loading_indicator()

        # Add functionality to hide or view all layers at once
        def toggle_all_layers_visibility(visible: bool):
            if self._layer_manager:
                for layer in self._layer_manager.layers:
                    layer.visible = visible
                self._layer_manager.layer_changed.emit(-1)  # Refresh all layers

        # Example usage: Call this function with True to show all layers, False to hide all layers
        toggle_all_layers_visibility(True)  # Show all layers
        toggle_all_layers_visibility(False)  # Hide all layers


class OverlayListItem(QWidget):
    """Minimal widget for a video overlay list item."""
    visibility_changed = Signal(bool)
    rename_requested = Signal(str)

    def __init__(self, name: str, visible: bool, parent=None):
        super().__init__(parent)
        self._name = name
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)
        self._visible_btn = QToolButton()
        self._visible_btn.setText("👁" if visible else "🙈")
        self._visible_btn.setCheckable(True)
        self._visible_btn.setChecked(visible)
        self._visible_btn.toggled.connect(self._on_vis)
        layout.addWidget(self._visible_btn)
        self._name_label = QLabel(name)
        self._name_label.setStyleSheet("color: #cccccc;")
        layout.addWidget(self._name_label)
        layout.addStretch()
        self._rename_btn = QToolButton()
        self._rename_btn.setText("✏️")
        self._rename_btn.clicked.connect(self._on_rename)
        layout.addWidget(self._rename_btn)

    def _on_vis(self, v: bool):
        self._visible_btn.setText("👁" if v else "🙈")
        self.visibility_changed.emit(v)

    def _on_rename(self):
        new_name, ok = QInputDialog.getText(self, "Rename Overlay", "New name:", text=self._name)
        if ok and new_name.strip():
            self._name = new_name.strip()
            self._name_label.setText(self._name)
            self.rename_requested.emit(self._name)


class VideoOverlayPanel(QFrame):
    """Panel for managing video overlays (on right sidebar)."""

    overlay_selected = Signal(int)
    overlay_visibility_changed = Signal(int, bool)
    overlay_add_requested = Signal()
    overlay_delete_requested = Signal(int)
    overlay_move_up_requested = Signal(int)
    overlay_move_down_requested = Signal(int)
    overlay_rename_requested = Signal(int, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            VideoOverlayPanel { background-color: #252526; border: none; }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)

        header = QWidget()
        header.setStyleSheet("background-color: #2d2d2d;")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(12,8,8,8)
        title = QLabel("Video Overlays")
        title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        title.setStyleSheet("color: #ffffff;")
        hl.addWidget(title)
        hl.addStretch()
        layout.addWidget(header)

        self._list = QListWidget()
        self._list.setStyleSheet("""
            QListWidget { background-color: #1e1e1e; border: 1px solid #3c3c3c; border-radius: 4px; }
            QListWidget::item { padding: 2px; border-bottom: 1px solid #2a2a2a; }
            QListWidget::item:selected { background-color: #0078d4; }
            QListWidget::item:hover:!selected { background-color: #2a2a2a; }
        """)
        self._list.currentRowChanged.connect(self.overlay_selected)
        layout.addWidget(self._list)

        buttons = QWidget()
        bl = QHBoxLayout(buttons)
        bl.setContentsMargins(8,8,8,8)
        bl.setSpacing(4)
        style = """
            QPushButton { background-color: #3c3c3c; color: #cccccc; border: none; border-radius: 4px; padding: 6px; font-size: 14px; }
            QPushButton:hover { background-color: #4a4a4a; }
            QPushButton:pressed { background-color: #2a2a2a; }
        """
        self._add_btn = QPushButton("➕"); self._add_btn.setStyleSheet(style); self._add_btn.setFixedSize(32,32)
        self._del_btn = QPushButton("🗑"); self._del_btn.setStyleSheet(style); self._del_btn.setFixedSize(32,32)
        self._up_btn  = QPushButton("⬆"); self._up_btn.setStyleSheet(style);  self._up_btn.setFixedSize(32,32)
        self._down_btn= QPushButton("⬇"); self._down_btn.setStyleSheet(style); self._down_btn.setFixedSize(32,32)
        bl.addWidget(self._add_btn); bl.addWidget(self._del_btn); bl.addStretch(); bl.addWidget(self._up_btn); bl.addWidget(self._down_btn)
        layout.addWidget(buttons)

        self._add_btn.clicked.connect(lambda: self.overlay_add_requested.emit())
        self._del_btn.clicked.connect(lambda: self.overlay_delete_requested.emit(self._list.currentRow()))
        self._up_btn.clicked.connect(lambda: self.overlay_move_up_requested.emit(self._list.currentRow()))
        self._down_btn.clicked.connect(lambda: self.overlay_move_down_requested.emit(self._list.currentRow()))

    def refresh(self, overlays: list):
        self._list.clear()
        for idx, ov in enumerate(overlays):
            item = QListWidgetItem()
            item.setSizeHint(QSize(0, 36))
            widget = OverlayListItem(ov.get('name', f'Overlay {idx+1}'), ov.get('visible', True))
            widget.visibility_changed.connect(lambda v, i=idx: self.overlay_visibility_changed.emit(i, v))
            widget.rename_requested.connect(lambda new_name, i=idx: self.overlay_rename_requested.emit(i, new_name))
            self._list.addItem(item)
            self._list.setItemWidget(item, widget)
