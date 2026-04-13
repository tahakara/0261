"""
Main window - The primary application window.
"""

from typing import Optional
from pathlib import Path
import numpy as np
import cv2

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QFileDialog, QMessageBox, QApplication, QSplitter
)
from PySide6.QtCore import Qt, QRect, QTimer, QThread, QObject, Signal
from PySide6.QtGui import QKeySequence, QShortcut

from ..core.project import Project, EditorMode
from ..core.module_base import ModuleBase
from ..modules import ModuleLoader
from .mode_selector import ModeSelectorDialog
from .canvas import CanvasWidget
from .video_panel import VideoPanel
from .sidebar_left import LeftSidebar
from .sidebar_right import RightSidebar
from .toolbar import TopToolbar
from .statusbar import InfoStatusBar


class MainWindow(QMainWindow):
    """
    Main application window.
    Contains all UI components and manages the overall application state.
    """
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Image/Video Editor")
        self.setMinimumSize(1200, 800)
        
        # Set dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
        """)
        
        # Initialize project (mode will be set after selection)
        self._project: Optional[Project] = None
        self._current_module: Optional[ModuleBase] = None
        # Simple in-memory clipboard for image regions
        self._clipboard_image = None
        
        # Load modules
        self._module_loader = ModuleLoader()
        
        # Setup UI
        self._setup_ui()
        self._setup_shortcuts()
        self._connect_signals()
        
        # Show mode selector on startup
        QTimer.singleShot(100, self._show_mode_selector)
    
    def _setup_ui(self):
        """Setup the UI components."""
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Top toolbar
        self._toolbar = TopToolbar()
        self.addToolBar(self._toolbar)
        
        # Main content area with splitters
        self._content_splitter = QSplitter(Qt.Horizontal)
        self._content_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #3c3c3c;
                width: 4px;
            }
            QSplitter::handle:hover {
                background-color: #0078d4;
            }
        """)
        
        # Left sidebar (modules/tools)
        self._left_sidebar = LeftSidebar()
        self._content_splitter.addWidget(self._left_sidebar)
        
        # Center stack: Image canvas and Video panel
        from PySide6.QtWidgets import QStackedWidget
        self._center_stack = QStackedWidget()
        self._canvas = CanvasWidget()
        self._video_panel = VideoPanel()
        self._center_stack.addWidget(self._canvas)      # index 0: image
        self._center_stack.addWidget(self._video_panel) # index 1: video
        self._content_splitter.addWidget(self._center_stack)
        
        # Right sidebar (settings + layers)
        self._right_sidebar = RightSidebar()
        self._content_splitter.addWidget(self._right_sidebar)
        
        # Set splitter sizes (left: 220, center: stretch, right: 280)
        self._content_splitter.setSizes([220, 700, 280])
        self._content_splitter.setStretchFactor(0, 0)
        self._content_splitter.setStretchFactor(1, 1)
        self._content_splitter.setStretchFactor(2, 0)

        main_layout.addWidget(self._content_splitter)
        
        # Status bar (bottom)
        self._statusbar = InfoStatusBar()
        self.setStatusBar(self._statusbar)
    
    def _setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        # Already handled by toolbar actions, but add some extras
        
        # Zoom shortcuts
        QShortcut(QKeySequence(Qt.CTRL | Qt.Key_Plus), self, self._canvas.zoom_in)
        QShortcut(QKeySequence(Qt.CTRL | Qt.Key_Minus), self, self._canvas.zoom_out)
        QShortcut(QKeySequence(Qt.CTRL | Qt.Key_0), self, self._canvas.actual_size)
        QShortcut(QKeySequence(Qt.CTRL | Qt.Key_1), self, self._canvas.fit_to_view)
        # Clipboard and edit shortcuts
        QShortcut(QKeySequence(Qt.CTRL | Qt.Key_X), self, self._cut_selection)
        QShortcut(QKeySequence(Qt.CTRL | Qt.Key_C), self, self._copy_selection)
        QShortcut(QKeySequence(Qt.Key_Delete), self, self._delete_selection)
        # Selection tool shortcuts: R = Rect, L = Lasso, B = Brush
        QShortcut(QKeySequence(Qt.Key_R), self, lambda: (self._canvas.canvas.set_selection_mode('rect'), self._statusbar.showMessage('Selection: Rect')))
        QShortcut(QKeySequence(Qt.Key_L), self, lambda: (self._canvas.canvas.set_selection_mode('lasso'), self._statusbar.showMessage('Selection: Lasso')))
        QShortcut(QKeySequence(Qt.Key_B), self, lambda: (self._canvas.canvas.set_selection_mode('brush'), self._statusbar.showMessage('Selection: Brush')))
    
    def _connect_signals(self):
        """Connect all signals."""
        
        # Toolbar signals
        self._toolbar.new_requested.connect(self._on_new)
        self._toolbar.open_requested.connect(self._on_open)
        self._toolbar.save_requested.connect(self._on_save)
        self._toolbar.save_as_requested.connect(self._on_save_as)
        self._toolbar.export_requested.connect(self._on_export)
        
        self._toolbar.undo_requested.connect(self._on_undo)
        self._toolbar.redo_requested.connect(self._on_redo)
        
        self._toolbar.zoom_in_requested.connect(self._canvas.zoom_in)
        self._toolbar.zoom_out_requested.connect(self._canvas.zoom_out)
        self._toolbar.fit_to_view_requested.connect(self._canvas.fit_to_view)
        self._toolbar.actual_size_requested.connect(self._canvas.actual_size)
        self._toolbar.zoom_changed.connect(self._on_toolbar_zoom_changed)
        
        self._toolbar.mode_change_requested.connect(self._show_mode_selector)
        self._toolbar.selection_mode_changed.connect(self._on_selection_mode_changed)
        self._toolbar.paint_mode_toggled.connect(self._on_paint_mode_toggled)
        self._toolbar.paint_color_changed.connect(self._on_paint_color_changed)
        
        # Canvas signals
        self._canvas.mouse_position.connect(self._on_cursor_moved)
        self._canvas.selection_changed.connect(self._on_selection_changed)
        self._canvas.zoom_changed.connect(self._on_zoom_changed)
        self._canvas.mouse_pressed.connect(self._on_canvas_mouse_pressed)
        self._canvas.mouse_moved.connect(self._on_canvas_mouse_moved)
        self._canvas.mouse_released.connect(self._on_canvas_mouse_released)
        self._canvas.key_pressed.connect(self._on_canvas_key_pressed)
        self._canvas.paint_stroke.connect(self._on_paint_stroke)
        self._canvas.fill_at_point.connect(self._on_fill_at_point)
        
        # Left sidebar signals
        self._left_sidebar.module_selected.connect(self._on_module_selected)

        # Wire selection settings clear/brush signals from right sidebar when available
        try:
            sel_panel = self._right_sidebar._selection_panel
            sel_panel.clear_requested.connect(self._canvas.clear_selection)
            sel_panel.brush_radius_changed.connect(lambda v: self._canvas.canvas.set_brush_radius(v))
            sel_panel.brush_softness_changed.connect(lambda v: self._canvas.canvas.set_brush_softness(v))
            sel_panel.brush_transparency_changed.connect(lambda v: self._canvas.canvas.set_brush_transparency(v))
            sel_panel.brush_step_changed.connect(lambda v: self._canvas.canvas.set_brush_step(v))
        except Exception:
            pass
        
        # Right sidebar signals
        self._right_sidebar.layer_selected.connect(self._on_layer_selected)
        self._right_sidebar.layer_add_requested.connect(self._on_add_layer)
        self._right_sidebar.layer_delete_requested.connect(self._on_delete_layer)
        self._right_sidebar.layer_duplicate_requested.connect(self._on_duplicate_layer)
        self._right_sidebar.layer_rename_requested.connect(self._on_rename_layer)
        self._right_sidebar.layer_move_up_requested.connect(self._on_move_layer_up)
        self._right_sidebar.layer_move_down_requested.connect(self._on_move_layer_down)
        self._right_sidebar.layer_visibility_changed.connect(self._on_layer_visibility_changed)
        self._right_sidebar.layer_merge_requested.connect(self._on_merge_layer)
        # Apply module from settings panel
        self._right_sidebar.apply_requested.connect(self._on_apply_module)

        # Surface video errors to status bar
        try:
            self._video_panel.error_signal.connect(lambda msg: self._statusbar.showMessage(msg, 5000))
        except Exception:
            pass

        # Overlay panel signals -> Video panel provider (video mode)
        try:
            self._right_sidebar.overlay_selected.connect(self._video_panel.set_active_overlay)
            self._right_sidebar.overlay_visibility_changed.connect(lambda i, v: self._video_panel.set_overlay_visibility(i, v))
            self._right_sidebar.overlay_add_requested.connect(self._video_panel._on_overlay_add)
            self._right_sidebar.overlay_delete_requested.connect(self._video_panel.remove_overlay)
            self._right_sidebar.overlay_move_up_requested.connect(self._video_panel.move_overlay_up)
            self._right_sidebar.overlay_move_down_requested.connect(self._video_panel.move_overlay_down)
            self._right_sidebar.overlay_rename_requested.connect(self._video_panel.rename_overlay)
        except Exception:
            pass
    
    def _show_mode_selector(self):
        """Show the mode selection dialog."""
        dialog = ModeSelectorDialog(self)
        dialog.mode_selected.connect(self._on_mode_selected)
        
        if dialog.exec() != ModeSelectorDialog.Accepted:
            # If canceled and no project exists, use default image mode
            if self._project is None:
                self._on_mode_selected(EditorMode.IMAGE)
    
    def _on_mode_selected(self, mode: EditorMode):
        """Handle mode selection."""
        # Create or update project
        if self._project is None:
            self._project = Project(mode)
            self._project.new_project()
            self._right_sidebar.set_layer_manager(self._project.layer_manager)
            
            # Pass project reference to right sidebar
            self._right_sidebar.set_project(self._project)
            
            # Connect project signals
            self._project.project_changed.connect(self._on_project_changed)
            self._project.canvas_size_changed.connect(self._on_canvas_size_changed)
        else:
            self._project.set_mode(mode)
        
        # Update UI for mode
        self._toolbar.set_mode(mode)
        self._statusbar.set_mode(mode)
        
        # Load modules for this mode
        self._load_modules_for_mode(mode)
        
        # Switch center stack + sidebars according to mode
        if mode == EditorMode.IMAGE:
            self._center_stack.setCurrentIndex(0)
            # ensure video resources are stopped
            try:
                self._video_panel.deactivate()
            except Exception:
                pass
            self._update_canvas()
            # Show sidebars in image mode
            try:
                self._left_sidebar.setVisible(True)
                self._right_sidebar.setVisible(True)
                self._content_splitter.setSizes([220, max(600, self.width()-500), 280])
            except Exception:
                pass
        else:
            self._center_stack.setCurrentIndex(1)
            try:
                self._video_panel.activate()
                # Do not auto-start camera; user can start manually
            except Exception:
                pass
            # In video mode, canvas updates are not used
            # Hide left sidebar; show right sidebar for overlays
            try:
                self._left_sidebar.setVisible(False)
                self._right_sidebar.setVisible(True)
                # Give space mostly to center
                self._content_splitter.setSizes([0, max(800, self.width()-300), 300])
                # Show overlay panel in right sidebar
                self._right_sidebar.show_overlay_panel(self._video_panel)
            except Exception:
                pass
        
        # Update window title
        mode_str = "Image" if mode == EditorMode.IMAGE else "Video"
        self.setWindowTitle(f"{mode_str} Editor - Untitled")
    
    def _load_modules_for_mode(self, mode: EditorMode):
        """Load modules appropriate for the current mode."""
        self._left_sidebar.clear_modules()
        
        modules = self._module_loader.get_modules_for_mode(mode)
        for module in modules:
            self._left_sidebar.add_module(module)
    
    def _update_canvas(self):
        """Update the canvas display from project.

        If `active_only` is True, show only the active layer image to speed up
        layer switching (avoids re-flattening full composite).
        """
        def _do_updates(display_image: 'np.ndarray'):
            if display_image is not None:
                self._canvas.set_image(display_image)

            # Update status bar
            w, h = self._project.canvas_size
            self._statusbar.set_dimensions(w, h)
            self._toolbar.set_canvas_size(w, h)

            # Update layer info
            layer_count = self._project.layer_manager.layer_count
            active = self._project.layer_manager.active_index + 1
            self._statusbar.set_layer_info(active, layer_count)

            # Update undo/redo state
            self._toolbar.set_undo_enabled(self._project.can_undo())
            self._toolbar.set_redo_enabled(self._project.can_redo())

        if self._project is None or self._project.mode == EditorMode.VIDEO:
            return

        # Default behavior: full composite
        image = self._project.get_composite_image()
        _do_updates(image)
    
    def _on_project_changed(self):
        """Handle project changes."""
        self._update_canvas()
        
        # Update window title
        title = self._project.file_path.stem if self._project.file_path else "Untitled"
        modified = "*" if self._project.is_modified else ""
        mode_str = "Image" if self._project.mode == EditorMode.IMAGE else "Video"
        self.setWindowTitle(f"{mode_str} Editor - {title}{modified}")
    
    def _on_canvas_size_changed(self, width: int, height: int):
        """Handle canvas size change."""
        self._statusbar.set_dimensions(width, height)
        self._toolbar.set_canvas_size(width, height)
    
    # File operations
    def _on_new(self):
        """Create a new project."""
        if self._project and self._project.is_modified:
            reply = QMessageBox.question(
                self, "Unsaved Changes",
                "Do you want to save changes before creating a new project?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            if reply == QMessageBox.Save:
                self._on_save()
            elif reply == QMessageBox.Cancel:
                return
        
        self._project.new_project()
        self._update_canvas()
    
    def _on_open(self):
        """Open a file."""
        if self._project.mode == EditorMode.IMAGE:
            filters = "Images (*.png *.jpg *.jpeg *.bmp *.tiff *.webp);;All Files (*)"
        else:
            filters = "Videos (*.mp4 *.avi *.mov *.mkv *.webm);;All Files (*)"
        
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", filters)
        
        if file_path:
            if self._project.mode == EditorMode.IMAGE:
                self._project.load_image(file_path)
            else:
                self._project.load_video(file_path)
            
            self._update_canvas()
            self._canvas.fit_to_view()
    
    def _on_save(self):
        """Save the current project."""
        if self._project.file_path:
            self._project.save_image()
        else:
            self._on_save_as()
    
    def _on_save_as(self):
        """Save with a new filename."""
        filters = "PNG (*.png);;JPEG (*.jpg);;BMP (*.bmp);;All Files (*)"
        file_path, _ = QFileDialog.getSaveFileName(self, "Save As", "", filters)
        
        if file_path:
            self._project.save_image(file_path)
    
    def _on_export(self):
        """Export the project."""
        self._on_save_as()  # For now, same as save as
    
    # Edit operations
    def _on_undo(self):
        """Undo last operation."""
        if self._project:
            self._project.undo()
    
    def _on_redo(self):
        """Redo last undone operation."""
        if self._project:
            self._project.redo()
    
    # Canvas event handlers
    def _on_cursor_moved(self, x: int, y: int):
        """Handle cursor movement on canvas."""
        self._statusbar.set_cursor_position(x, y)
        
        # Get color at cursor
        image = self._canvas.get_image()
        if image is not None and 0 <= y < image.shape[0] and 0 <= x < image.shape[1]:
            if image.shape[2] == 4:
                b, g, r, a = image[y, x]
                self._statusbar.set_color_at_cursor(r, g, b, a)
            else:
                b, g, r = image[y, x]
                self._statusbar.set_color_at_cursor(r, g, b)
        else:
            self._statusbar.clear_color()
    
    def _on_selection_changed(self, rect: QRect):
        """Handle selection change."""
        self._statusbar.set_selection(rect if not rect.isEmpty() else None)
    
    def _on_zoom_changed(self, zoom: float):
        """Handle zoom change."""
        self._statusbar.set_zoom(zoom)
        self._toolbar.set_zoom(zoom)
    
    def _on_toolbar_zoom_changed(self, percentage: int):
        """Handle zoom change from toolbar."""
        self._canvas.set_zoom(percentage / 100.0)
    
    def _on_canvas_mouse_pressed(self, x: int, y: int, button: int):
        """Forward mouse press to active module."""
        # Check for Alt+Click to apply module directly at cursor position (brush mode)
        from PySide6.QtCore import Qt as QtCore
        app = QApplication.instance()
        if app and button == 1:  # Left click
            modifiers = app.keyboardModifiers()
            if modifiers & QtCore.AltModifier:
                # Alt+Click: apply module at cursor position
                if self._current_module and self._project:
                    self._on_apply_module_at_cursor(x, y)
                    return
        
        if self._current_module:
            self._current_module.on_canvas_mouse_press(x, y, button)
        
        # If project and active layer exists, check whether click hits non-transparent pixel
        if self._project and self._project.layer_manager.active_layer:
            layer = self._project.layer_manager.active_layer
            if layer.image is not None:
                lx, ly = layer.position if hasattr(layer, 'position') else (0, 0)
                rel_x = x - lx
                rel_y = y - ly
                h, w = layer.image.shape[:2]
                if 0 <= rel_x < w and 0 <= rel_y < h:
                    # check alpha channel if present
                    if layer.has_alpha:
                        a = layer.image[rel_y, rel_x, 3]
                        if a > 0:
                            # show transform handles for the active layer
                            from PySide6.QtCore import QRect
                            rect = QRect(lx, ly, w, h)
                            self._canvas.canvas.set_transform_rect(rect)
                            return
                    else:
                        # no alpha - treat as hit
                        from PySide6.QtCore import QRect
                        rect = QRect(lx, ly, w, h)
                        self._canvas.canvas.set_transform_rect(rect)
                        return

        # otherwise clear transform rect
        self._canvas.canvas.set_transform_rect(None)
    
    def _on_canvas_mouse_moved(self, x: int, y: int):
        """Forward mouse move to active module."""
        if self._current_module:
            self._current_module.on_canvas_mouse_move(x, y)
    
    def _on_canvas_mouse_released(self, x: int, y: int, button: int):
        """Forward mouse release to active module."""
        if self._current_module:
            self._current_module.on_canvas_mouse_release(x, y, button)
    
    def _on_canvas_key_pressed(self, key: int):
        """Forward key press to active module."""
        if self._current_module:
            self._current_module.on_canvas_key_press(key)

    def _on_apply_module_at_cursor(self, x: int, y: int):
        """Apply module at cursor position using brush radius as region."""
        if self._project is None or self._current_module is None:
            return
        
        layer, idx = self._get_active_layer_and_index()
        if layer is None or layer.image is None:
            return
        
        # Get brush radius from canvas
        brush_radius = self._canvas.canvas._brush_radius
        
        # Create circular mask region at cursor position
        h_img, w_img = layer.image.shape[:2]
        
        # Calculate bounding box for the brush circle
        x0 = max(0, x - brush_radius)
        y0 = max(0, y - brush_radius)
        x1 = min(w_img, x + brush_radius)
        y1 = min(h_img, y + brush_radius)
        
        w = x1 - x0
        h = y1 - y0
        
        if w <= 0 or h <= 0:
            return
        
        # Create circular mask for this region
        mask_crop = np.zeros((h, w), dtype='uint8')
        cv2.circle(mask_crop, (x - x0, y - y0), brush_radius, 255, -1)
        
        # Save undo state
        self._project.save_state()
        prev_active = self._project.layer_manager.active_index
        
        # Extract region
        target_image = layer.image[y0:y1, x0:x1].copy()
        
        # Show progress
        try:
            self._statusbar.show_progress("Applying...")
            QApplication.setOverrideCursor(Qt.WaitCursor)
            self._canvas.canvas.show_processing_overlay("Applying...")
        except Exception:
            pass
        
        # Apply module in worker thread
        class _ApplyWorker(QObject):
            finished = Signal(object)
            error = Signal(str)
            
            def __init__(self, module, img, params, mask):
                super().__init__()
                self.module = module
                self.img = img
                self.params = params
                self.mask = mask
            
            def run(self):
                try:
                    res = self.module.apply(self.img, **self.params)
                    if res.shape != self.img.shape:
                        res = cv2.resize(res, (self.img.shape[1], self.img.shape[0]), interpolation=cv2.INTER_LINEAR)
                    self.finished.emit(res)
                except Exception as ex:
                    self.error.emit(str(ex))
        
        worker = _ApplyWorker(self._current_module, target_image, {}, mask_crop)
        thread = QThread()
        worker.moveToThread(thread)
        
        def _on_worker_finished(result):
            try:
                # Write back only masked pixels
                region = layer.image[y0:y1, x0:x1]
                if region.ndim == 3 and result.ndim == 3:
                    mask_bool = mask_crop > 0
                    region[mask_bool] = result[mask_bool]
                else:
                    region[mask_crop > 0] = result[mask_crop > 0]
                layer.image[y0:y1, x0:x1] = region
                
                self._project.layer_manager.layer_changed.emit(idx)
                if prev_active is not None and 0 <= prev_active < self._project.layer_manager.layer_count:
                    self._project.layer_manager.set_active_layer(prev_active)
                self._update_canvas()
            except Exception as e:
                QMessageBox.warning(self, "Apply Error", f"Error applying result: {e}")
            finally:
                try:
                    self._statusbar.hide_progress()
                    self._canvas.canvas.hide_processing_overlay()
                    QApplication.restoreOverrideCursor()
                except Exception:
                    pass
                worker.deleteLater()
                thread.quit()
        
        def _on_worker_error(msg):
            QMessageBox.warning(self, "Apply Error", f"Error applying module: {msg}")
            try:
                self._statusbar.hide_progress()
                self._canvas.canvas.hide_processing_overlay()
                QApplication.restoreOverrideCursor()
            except Exception:
                pass
            worker.deleteLater()
            thread.quit()
        
        worker.finished.connect(_on_worker_finished)
        worker.error.connect(_on_worker_error)
        thread.started.connect(worker.run)
        thread.start()

    def _on_apply_module(self):
        """Apply the currently selected module to the active layer or selection."""
        if self._project is None or self._current_module is None:
            return

        layer, idx = self._get_active_layer_and_index()
        if layer is None or layer.image is None:
            return

        # Get selection from canvas (in image coordinates)
        sel = self._canvas.selection
        sel_mask = None
        try:
            sel_mask = self._canvas.canvas.get_selection_mask()
        except Exception:
            sel_mask = None

        # Save undo state
        self._project.save_state()
        # Preserve active layer index so we don't change selection after apply
        prev_active = self._project.layer_manager.active_index

        # Use module's current settings/state; do not override with defaults here.
        params = {}

        # Prepare the image/region to process (do minimal copies here)
        try:
            if sel_mask is not None and sel_mask.any():
                ys, xs = np.where(sel_mask)
                y0, y1 = int(ys.min()), int(ys.max())
                x0, x1 = int(xs.min()), int(xs.max())
                x, y, w, h = x0, y0, x1 - x0 + 1, y1 - y0 + 1
                h_img, w_img = layer.image.shape[:2]
                x = max(0, min(x, w_img - 1))
                y = max(0, min(y, h_img - 1))
                w = max(0, min(w, w_img - x))
                h = max(0, min(h, h_img - y))
                if w == 0 or h == 0:
                    return

                target_image = layer.image[y:y+h, x:x+w].copy()
                mask_crop = sel_mask[y:y+h, x:x+w].copy()
                is_region = True
                region_coords = (x, y, w, h)
            elif sel and not sel.isEmpty():
                x, y, w, h = sel.x(), sel.y(), sel.width(), sel.height()
                h_img, w_img = layer.image.shape[:2]
                x = max(0, min(x, w_img - 1))
                y = max(0, min(y, h_img - 1))
                w = max(0, min(w, w_img - x))
                h = max(0, min(h, h_img - y))
                if w == 0 or h == 0:
                    return

                target_image = layer.image[y:y+h, x:x+w].copy()
                mask_crop = None
                is_region = True
                region_coords = (x, y, w, h)
            else:
                target_image = layer.image.copy()
                mask_crop = None
                is_region = False
                region_coords = None
        except Exception as e:
            QMessageBox.warning(self, "Apply Error", f"Error preparing region: {e}")
            return

        # Show progress indicator
        try:
            self._statusbar.show_progress("Applying...")
            # show overlay and busy cursor
            try:
                QApplication.setOverrideCursor(Qt.WaitCursor)
            except Exception:
                pass
            try:
                self._canvas.canvas.show_processing_overlay("Applying...")
            except Exception:
                pass
        except Exception:
            pass

        # Worker to run module.apply in background
        class _ApplyWorker(QObject):
            finished = Signal(object)
            error = Signal(str)

            def __init__(self, module, img, params, is_region, region_coords, layer_shape, mask=None):
                super().__init__()
                self.module = module
                self.img = img
                self.params = params
                self.is_region = is_region
                self.region_coords = region_coords
                self.layer_shape = layer_shape
                self.mask = mask

            def run(self):
                try:
                    res = self.module.apply(self.img, **self.params)

                    # Ensure result is resized to target dimensions while still in worker thread
                    if self.is_region and self.region_coords:
                        _, _, w, h = self.region_coords[0], self.region_coords[1], self.region_coords[2], self.region_coords[3]
                        if res.shape[:2] != (h, w):
                            res = cv2.resize(res, (w, h), interpolation=cv2.INTER_LINEAR)
                    else:
                        # whole layer
                        if self.layer_shape is not None and res.shape != self.layer_shape:
                            res = cv2.resize(res, (self.layer_shape[1], self.layer_shape[0]), interpolation=cv2.INTER_LINEAR)

                    self.finished.emit(res)
                except Exception as ex:
                    # Ensure any exception is propagated so UI can clean up
                    self.error.emit(str(ex))

        # Create worker and thread
        # Provide worker with information so it can finalize result in its thread
        layer_shape = layer.image.shape if layer.image is not None else None
        worker = _ApplyWorker(self._current_module, target_image, params, is_region, region_coords, layer_shape, mask=(mask_crop if 'mask_crop' in locals() else None))
        thread = QThread()
        worker.moveToThread(thread)

        def _on_worker_finished(result):
            # Ensure result shape matches and write back to layer
            try:
                if is_region and region_coords:
                    x, y, w, h = region_coords
                    if result.shape[:2] != (h, w):
                        result = cv2.resize(result, (w, h), interpolation=cv2.INTER_LINEAR)
                    # If a mask was used, only write masked pixels
                    try:
                        mask_used = mask_crop if 'mask_crop' in locals() else None
                    except Exception:
                        mask_used = None

                    if mask_used is not None:
                        region = layer.image[y:y+h, x:x+w]
                        # region and result are (h,w,c) or (h,w)
                        if region.ndim == 3 and result.ndim == 3:
                            region[mask_used] = result[mask_used]
                        else:
                            region[mask_used] = result[mask_used]
                        layer.image[y:y+h, x:x+w] = region
                    else:
                        layer.image[y:y+h, x:x+w] = result
                else:
                    if result.shape != layer.image.shape:
                        result = cv2.resize(result, (layer.image.shape[1], layer.image.shape[0]), interpolation=cv2.INTER_LINEAR)
                    layer.image = result

                self._project.layer_manager.layer_changed.emit(idx)
                # restore previous active layer (if still valid)
                try:
                    if prev_active is not None and 0 <= prev_active < self._project.layer_manager.layer_count:
                        self._project.layer_manager.set_active_layer(prev_active)
                except Exception:
                    pass
                self._update_canvas()
            except Exception as e:
                QMessageBox.warning(self, "Apply Error", f"Error applying result: {e}")
            finally:
                try:
                    self._statusbar.hide_progress()
                except Exception:
                    pass
                try:
                    self._canvas.canvas.hide_processing_overlay()
                except Exception:
                    pass
                try:
                    QApplication.restoreOverrideCursor()
                except Exception:
                    pass
                # Clean up without blocking main thread
                worker.deleteLater()
                thread.quit()

        def _on_worker_error(msg):
            QMessageBox.warning(self, "Apply Error", f"Error applying module: {msg}")
            try:
                self._statusbar.hide_progress()
                self._canvas.canvas.hide_processing_overlay()
                QApplication.restoreOverrideCursor()
            except Exception:
                pass
            worker.deleteLater()
            thread.quit()

        # Connect worker signals and start the background thread
        worker.finished.connect(_on_worker_finished)
        worker.error.connect(_on_worker_error)
        thread.started.connect(worker.run)
        thread.start()

    def _on_rename_layer(self, visual_index: int):
        """Prompt for a new layer name and apply it."""
        if not self._project:
            return
        actual_index = self._project.layer_manager.layer_count - 1 - visual_index
        layer = self._project.layer_manager.get_layer(actual_index)
        if layer is None:
            return

        from PySide6.QtWidgets import QInputDialog
        new_name, ok = QInputDialog.getText(self, "Rename Layer", "New name:", text=layer.name)
        if ok and new_name:
            layer.name = new_name
            self._project.layer_manager.layer_changed.emit(actual_index)
            self._update_canvas()

    def _get_active_layer_and_index(self):
        if not self._project:
            return None, -1
        lm = self._project.layer_manager
        idx = lm.active_index
        return lm.active_layer, idx

    def _copy_selection(self):
        """Copy selected region from active layer to clipboard (in-memory)."""
        layer, idx = self._get_active_layer_and_index()
        if layer is None or layer.image is None:
            return

        sel = self._canvas.selection
        if sel is None or sel.isEmpty():
            return

        x, y, w, h = sel.x(), sel.y(), sel.width(), sel.height()
        h_img, w_img = layer.image.shape[:2]
        # Clamp
        x = max(0, min(x, w_img - 1))
        y = max(0, min(y, h_img - 1))
        w = max(0, min(w, w_img - x))
        h = max(0, min(h, h_img - y))

        if w == 0 or h == 0:
            return

        self._clipboard_image = layer.image[y:y+h, x:x+w].copy()

    def _cut_selection(self):
        """Cut selected region (copy then clear area to transparent)."""
        layer, idx = self._get_active_layer_and_index()
        if layer is None or layer.image is None:
            return

        sel = self._canvas.selection
        if sel is None or sel.isEmpty():
            return

        x, y, w, h = sel.x(), sel.y(), sel.width(), sel.height()
        h_img, w_img = layer.image.shape[:2]
        x = max(0, min(x, w_img - 1))
        y = max(0, min(y, h_img - 1))
        w = max(0, min(w, w_img - x))
        h = max(0, min(h, h_img - y))
        if w == 0 or h == 0:
            return

        # Save undo
        self._project.save_state()

        # Copy
        self._clipboard_image = layer.image[y:y+h, x:x+w].copy()

        # Make region transparent
        if layer.has_alpha:
            layer.image[y:y+h, x:x+w, :3] = 0
            layer.image[y:y+h, x:x+w, 3] = 0
        else:
            # add alpha and then clear
            from ..utils.image_utils import ImageUtils
            layer.image = ImageUtils.add_alpha_channel(layer.image)
            layer.image[y:y+h, x:x+w, :3] = 0
            layer.image[y:y+h, x:x+w, 3] = 0

        # notify
        self._project.layer_manager.layer_changed.emit(idx)
        self._update_canvas()

    def _delete_selection(self):
        """Delete selected region (no copy)."""
        layer, idx = self._get_active_layer_and_index()
        if layer is None or layer.image is None:
            return

        sel = self._canvas.selection
        if sel is None or sel.isEmpty():
            return

        x, y, w, h = sel.x(), sel.y(), sel.width(), sel.height()
        h_img, w_img = layer.image.shape[:2]
        x = max(0, min(x, w_img - 1))
        y = max(0, min(y, h_img - 1))
        w = max(0, min(w, w_img - x))
        h = max(0, min(h, h_img - y))
        if w == 0 or h == 0:
            return

        self._project.save_state()

        if layer.has_alpha:
            layer.image[y:y+h, x:x+w, :3] = 0
            layer.image[y:y+h, x:x+w, 3] = 0
        else:
            from ..utils.image_utils import ImageUtils
            layer.image = ImageUtils.add_alpha_channel(layer.image)
            layer.image[y:y+h, x:x+w, :3] = 0
            layer.image[y:y+h, x:x+w, 3] = 0

        self._project.layer_manager.layer_changed.emit(idx)
        self._update_canvas()
    
    # Module handling
    def _on_module_selected(self, module: ModuleBase):
        """Handle module selection."""
        # Deactivate previous module
        if self._current_module:
            self._current_module.deactivate()

        # Check if this is the "None" module - if so, clear module selection
        if module.name == "None":
            self._current_module = None
            self._right_sidebar.set_module(None)
            return

        # Activate new module
        self._current_module = module
        module.activate()

        # Update right sidebar with module settings
        self._right_sidebar.set_module(module)

    def _on_selection_mode_changed(self, mode: str):
        """Handle selection mode changes from toolbar."""
        try:
            # set canvas mode
            self._canvas.canvas.set_selection_mode(mode)
            # show selection config on right sidebar
            self._right_sidebar.show_selection_settings(mode)
            
            # Auto-enable paint mode for pen, erase, and fill tools
            if mode in ['pen', 'erase', 'fill']:
                if not self._canvas.canvas._paint_mode:
                    # Enable paint mode via toolbar
                    self._toolbar._paint_toggle.setChecked(True)
                self._statusbar.showMessage(f"{mode.capitalize()} tool selected (Paint mode)")
            else:
                # notify statusbar
                self._statusbar.showMessage(f"Selection mode: {mode}")
        except Exception:
            pass
    
    def _on_paint_mode_toggled(self, enabled: bool):
        """Handle paint mode toggle."""
        try:
            self._canvas.canvas.set_paint_mode(enabled)
            if enabled:
                self._statusbar.showMessage("Paint mode: ON - Draw directly on layer")
            else:
                self._statusbar.showMessage("Paint mode: OFF - Selection mode")
        except Exception:
            pass
    
    def _on_paint_color_changed(self, r: int, g: int, b: int):
        """Handle paint color change."""
        try:
            self._canvas.canvas.set_paint_color(r, g, b)
            self._statusbar.showMessage(f"Paint color: RGB({r}, {g}, {b})")
        except Exception:
            pass
    
    def _on_paint_stroke(self, x: int, y: int, r: int, g: int, b: int, radius: int, softness: int, transparency: int, mode: int):
        """Handle paint stroke on active layer.
        mode: 0=brush, 1=pen (hard edge), 2=erase
        """
        # If no project, create a default blank canvas
        if self._project is None:
            from ..core.project import EditorMode
            self._on_mode_selected(EditorMode.IMAGE)
            # Create a blank white canvas
            blank_canvas = np.ones((600, 800, 3), dtype=np.uint8) * 255
            self._project.load_image(blank_canvas)
            self._update_canvas()
        
        layer, idx = self._get_active_layer_and_index()
        if layer is None or layer.image is None:
            return
        
        h_img, w_img = layer.image.shape[:2]
        if x < 0 or x >= w_img or y < 0 or y >= h_img:
            return
        
        # Create circular brush mask
        brush_size = radius * 2 + 1
        temp_mask = np.zeros((brush_size, brush_size), dtype='uint8')
        cv2.circle(temp_mask, (radius, radius), radius, 255, -1)
        
        # Apply softness (Gaussian blur) only for brush mode (not pen)
        if mode == 0 and softness > 0:  # brush mode
            kernel_size = max(3, int(radius * softness / 100.0))
            if kernel_size % 2 == 0:
                kernel_size += 1
            temp_mask = cv2.GaussianBlur(temp_mask, (kernel_size, kernel_size), 0)
        
        # Calculate alpha from transparency (0 = opaque, 100 = transparent)
        alpha = 1.0 - (transparency / 100.0)
        
        # Calculate brush bounds on image
        x0 = max(0, x - radius)
        y0 = max(0, y - radius)
        x1 = min(w_img, x + radius + 1)
        y1 = min(h_img, y + radius + 1)
        
        # Calculate corresponding mask region
        mx0 = radius - (x - x0)
        my0 = radius - (y - y0)
        mx1 = mx0 + (x1 - x0)
        my1 = my0 + (y1 - y0)
        
        if x1 <= x0 or y1 <= y0:
            return
        
        # Get mask region
        mask_region = temp_mask[my0:my1, mx0:mx1].astype(np.float32) / 255.0 * alpha
        
        # Get image region (make a copy to modify)
        img_region = layer.image[y0:y1, x0:x1].copy()
        
        if mode == 2:  # erase mode
            # Erase by setting to white (or could make transparent if using alpha channel)
            erase_color = np.array([255, 255, 255], dtype=np.uint8)  # White
            if img_region.ndim == 3 and img_region.shape[2] == 3:
                for c in range(3):
                    img_region[:, :, c] = (img_region[:, :, c] * (1 - mask_region) + erase_color[c] * mask_region).astype(np.uint8)
        else:  # brush or pen mode
            # Blend color onto image
            paint_color = np.array([b, g, r], dtype=np.uint8)  # BGR for OpenCV
            if img_region.ndim == 3 and img_region.shape[2] == 3:
                for c in range(3):
                    img_region[:, :, c] = (img_region[:, :, c] * (1 - mask_region) + paint_color[c] * mask_region).astype(np.uint8)
        
        # Write the modified region back to the layer
        layer.image[y0:y1, x0:x1] = img_region
        
        # Update layer and refresh
        self._project.layer_manager.layer_changed.emit(idx)
        self._update_canvas()
    
    def _on_fill_at_point(self, x: int, y: int, r: int, g: int, b: int):
        """Handle flood fill at a point."""
        # If no project, create a default blank canvas
        if self._project is None:
            from ..core.project import EditorMode
            self._on_mode_selected(EditorMode.IMAGE)
            # Create a blank white canvas
            blank_canvas = np.ones((600, 800, 3), dtype=np.uint8) * 255
            self._project.load_image(blank_canvas)
            self._update_canvas()
        
        layer, idx = self._get_active_layer_and_index()
        if layer is None or layer.image is None:
            return
        
        h_img, w_img = layer.image.shape[:2]
        if x < 0 or x >= w_img or y < 0 or y >= h_img:
            return
        
        # Ensure image has 3 channels (BGR) for floodFill
        # layer.image is RGB, convert to BGR for OpenCV
        if len(layer.image.shape) == 2:
            # Grayscale - convert to BGR
            work_img = cv2.cvtColor(layer.image, cv2.COLOR_GRAY2BGR)
        elif layer.image.shape[2] == 4:
            # RGBA - convert to BGR
            work_img = cv2.cvtColor(layer.image, cv2.COLOR_RGBA2BGR)
        elif layer.image.shape[2] == 3:
            # RGB - convert to BGR
            work_img = cv2.cvtColor(layer.image, cv2.COLOR_RGB2BGR)
        else:
            return  # Unsupported format
        
        # Get target color at click point
        target_color = work_img[y, x].copy()
        fill_color = np.array([b, g, r], dtype=np.uint8)  # BGR
        
        # Check if already same color
        if np.array_equal(target_color, fill_color):
            return
        
        # Create mask for flood fill
        mask = np.zeros((h_img + 2, w_img + 2), dtype=np.uint8)
        
        # Perform flood fill
        cv2.floodFill(work_img, mask, (x, y), fill_color.tolist())
        
        # Convert back to original format (RGB)
        if len(layer.image.shape) == 2:
            layer.image[:] = cv2.cvtColor(work_img, cv2.COLOR_BGR2GRAY)
        elif layer.image.shape[2] == 4:
            # Convert BGR to RGB, preserve alpha channel
            layer.image[:, :, :3] = cv2.cvtColor(work_img, cv2.COLOR_BGR2RGB)
        else:
            # Convert BGR back to RGB
            layer.image[:] = cv2.cvtColor(work_img, cv2.COLOR_BGR2RGB)
        
        # Update layer and refresh (preserve active layer selection)
        active_idx = self._project.layer_manager.active_index
        self._project.layer_manager.layer_changed.emit(idx)
        self._project.layer_manager.set_active_layer(active_idx)
        self._update_canvas()

    def _on_layer_selected(self, visual_index: int):
        """Handle layer selection."""
        if self._project:
            # Convert visual index to actual index
            actual_index = self._project.layer_manager.layer_count - 1 - visual_index
            self._project.layer_manager.set_active_layer(actual_index)
            # Fast update: show active layer image directly to avoid full composite
            layer = self._project.layer_manager.get_layer(actual_index)
            if layer and layer.image is not None:
                self._canvas.set_image(layer.image)
            # Update layer info and keep other UI in sync
            layer_count = self._project.layer_manager.layer_count
            active = self._project.layer_manager.active_index + 1
            self._statusbar.set_layer_info(active, layer_count)
            self._toolbar.set_undo_enabled(self._project.can_undo())
            self._toolbar.set_redo_enabled(self._project.can_redo())
            # Clear any transform overlay when changing layers
            self._canvas.canvas.set_transform_rect(None)

    def _on_add_layer(self):
        """Add a new layer."""
        if self._project:
            self._project.save_state()
            self._project.layer_manager.create_layer(f"Layer {self._project.layer_manager.layer_count + 1}")
            self._update_canvas()

    def _on_delete_layer(self, visual_index: int):
        """Delete a layer."""
        if self._project and self._project.layer_manager.layer_count > 1:
            self._project.save_state()
            actual_index = self._project.layer_manager.layer_count - 1 - visual_index
            self._project.layer_manager.remove_layer(actual_index)
            self._update_canvas()

    def _on_duplicate_layer(self, visual_index: int):
        """Duplicate a layer."""
        if self._project:
            self._project.save_state()
            actual_index = self._project.layer_manager.layer_count - 1 - visual_index
            self._project.layer_manager.duplicate_layer(actual_index)
            self._update_canvas()

    def _on_move_layer_up(self, visual_index: int):
        """Move layer up in the stack."""
        if self._project and visual_index > 0:
            self._project.save_state()
            actual_from = self._project.layer_manager.layer_count - 1 - visual_index
            actual_to = actual_from + 1
            self._project.layer_manager.move_layer(actual_from, actual_to)
            self._update_canvas()

    def _on_move_layer_down(self, visual_index: int):
        """Move layer down in the stack."""
        if self._project:
            actual_from = self._project.layer_manager.layer_count - 1 - visual_index
            if actual_from > 0:
                self._project.save_state()
                self._project.layer_manager.move_layer(actual_from, actual_from - 1)
                self._update_canvas()

    def _on_layer_visibility_changed(self, index: int, visible: bool):
        """Handle layer visibility change."""
        self._update_canvas()

    def _on_merge_layer(self, visual_index: int):
        """Handle merge down or merge all depending on visual_index.

        If visual_index == -1 -> merge all layers.
        Otherwise, merge the selected layer down into the one below it.
        """
        if not self._project:
            return

        lm = self._project.layer_manager
        if visual_index == -1:
            # Merge all
            self._project.save_state()
            lm.merge_all()
            self._update_canvas()
        else:
            # Convert visual index to actual index
            actual_index = lm.layer_count - 1 - visual_index
            if actual_index <= 0:
                return
            self._project.save_state()
            lm.merge_down(actual_index)
            self._update_canvas()
