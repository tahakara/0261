"""
Top toolbar - Contains file operations, edit tools, view controls.
"""

from PySide6.QtWidgets import (
    QToolBar, QWidget, QHBoxLayout, QPushButton,
    QLabel, QComboBox, QSpinBox, QMenu, QToolButton,
    QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QAction, QKeySequence

from ..core.project import EditorMode


class TopToolbar(QToolBar):
    """
    Main toolbar at the top of the window.
    Contains file operations, edit tools, and view controls.
    """
    
    # File operations
    new_requested = Signal()
    open_requested = Signal()
    save_requested = Signal()
    save_as_requested = Signal()
    export_requested = Signal()
    
    # Edit operations
    undo_requested = Signal()
    redo_requested = Signal()
    cut_requested = Signal()
    copy_requested = Signal()
    paste_requested = Signal()
    
    # View operations
    zoom_in_requested = Signal()
    zoom_out_requested = Signal()
    fit_to_view_requested = Signal()
    actual_size_requested = Signal()
    zoom_changed = Signal(int)  # zoom percentage
    
    # Mode
    mode_change_requested = Signal()
    # Selection tool
    selection_mode_changed = Signal(str)
    brush_radius_changed = Signal(int)
    # Paint mode
    paint_mode_toggled = Signal(bool)
    paint_color_changed = Signal(int, int, int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setMovable(False)
        self.setIconSize(QSize(20, 20))
        self.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        
        self.setStyleSheet("""
            QToolBar {
                background-color: #2d2d2d;
                border: none;
                border-bottom: 1px solid #3c3c3c;
                padding: 4px 8px;
                spacing: 4px;
            }
            QToolButton {
                background-color: transparent;
                color: #cccccc;
                border: none;
                border-radius: 4px;
                padding: 6px 10px;
                font-size: 12px;
            }
            QToolButton:hover {
                background-color: #3a3a3a;
            }
            QToolButton:pressed {
                background-color: #2a2a2a;
            }
            QToolButton:disabled {
                color: #666666;
            }
            QToolButton::menu-indicator {
                image: none;
            }
        """)
        
        self._mode = EditorMode.IMAGE
        self._setup_toolbar()
    
    def _setup_toolbar(self):
        """Setup toolbar items."""
        
        # Mode indicator
        self._mode_btn = QToolButton()
        self._mode_btn.setText("🖼️ Image Mode")
        self._mode_btn.setToolTip("Click to change editor mode")
        self._mode_btn.clicked.connect(self.mode_change_requested)
        self._mode_btn.setStyleSheet("""
            QToolButton {
                background-color: #0078d4;
                color: white;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QToolButton:hover {
                background-color: #1084d8;
            }
        """)
        self.addWidget(self._mode_btn)
        
        self.addSeparator()
        
        # File menu button
        file_btn = QToolButton()
        file_btn.setText("📁 File")
        file_btn.setPopupMode(QToolButton.InstantPopup)
        
        file_menu = QMenu(file_btn)
        file_menu.setStyleSheet("""
            QMenu {
                background-color: #2d2d2d;
                color: #cccccc;
                border: 1px solid #3c3c3c;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 24px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #0078d4;
            }
            QMenu::separator {
                height: 1px;
                background: #3c3c3c;
                margin: 4px 8px;
            }
        """)
        
        # Create QAction objects and connect to signals (signals are not callable)
        new_action = file_menu.addAction("New")
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(lambda checked=False: self.new_requested.emit())

        open_action = file_menu.addAction("Open...")
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(lambda checked=False: self.open_requested.emit())

        file_menu.addSeparator()

        save_action = file_menu.addAction("Save")
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(lambda checked=False: self.save_requested.emit())

        save_as_action = file_menu.addAction("Save As...")
        save_as_action.setShortcut(QKeySequence.SaveAs)
        save_as_action.triggered.connect(lambda checked=False: self.save_as_requested.emit())

        file_menu.addSeparator()

        export_action = file_menu.addAction("Export...")
        export_action.triggered.connect(lambda checked=False: self.export_requested.emit())
        
        file_btn.setMenu(file_menu)
        self.addWidget(file_btn)
        
        # Edit menu button
        edit_btn = QToolButton()
        edit_btn.setText("✏️ Edit")
        edit_btn.setPopupMode(QToolButton.InstantPopup)
        
        edit_menu = QMenu(edit_btn)
        edit_menu.setStyleSheet(file_menu.styleSheet())
        
        # Undo/Redo actions as QActions so we can enable/disable them
        self._undo_action = edit_menu.addAction("Undo")
        self._undo_action.setShortcut(QKeySequence.Undo)
        self._undo_action.triggered.connect(lambda checked=False: self.undo_requested.emit())

        self._redo_action = edit_menu.addAction("Redo")
        self._redo_action.setShortcut(QKeySequence.Redo)
        self._redo_action.triggered.connect(lambda checked=False: self.redo_requested.emit())

        edit_menu.addSeparator()

        cut_action = edit_menu.addAction("Cut")
        cut_action.setShortcut(QKeySequence.Cut)
        cut_action.triggered.connect(lambda checked=False: self.cut_requested.emit())

        copy_action = edit_menu.addAction("Copy")
        copy_action.setShortcut(QKeySequence.Copy)
        copy_action.triggered.connect(lambda checked=False: self.copy_requested.emit())

        paste_action = edit_menu.addAction("Paste")
        paste_action.setShortcut(QKeySequence.Paste)
        paste_action.triggered.connect(lambda checked=False: self.paste_requested.emit())
        
        edit_btn.setMenu(edit_menu)
        self.addWidget(edit_btn)
        
        self.addSeparator()
        
        # View controls
        view_label = QLabel("View:")
        view_label.setStyleSheet("color: #888888; padding: 0 8px;")
        self.addWidget(view_label)
        
        # Zoom controls
        zoom_out_btn = QToolButton()
        zoom_out_btn.setText("➖")
        zoom_out_btn.setToolTip("Zoom Out (Ctrl+-)")
        zoom_out_btn.clicked.connect(self.zoom_out_requested)
        self.addWidget(zoom_out_btn)
        
        self._zoom_combo = QComboBox()
        self._zoom_combo.setEditable(True)
        self._zoom_combo.addItems(["25%", "50%", "75%", "100%", "150%", "200%", "400%"])
        self._zoom_combo.setCurrentText("100%")
        self._zoom_combo.setFixedWidth(80)
        self._zoom_combo.setStyleSheet("""
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
                width: 16px;
            }
            QComboBox QAbstractItemView {
                background-color: #2d2d2d;
                color: #cccccc;
                selection-background-color: #0078d4;
            }
        """)
        self._zoom_combo.currentTextChanged.connect(self._on_zoom_changed)
        self.addWidget(self._zoom_combo)
        
        zoom_in_btn = QToolButton()
        zoom_in_btn.setText("➕")
        zoom_in_btn.setToolTip("Zoom In (Ctrl++)")
        zoom_in_btn.clicked.connect(self.zoom_in_requested)
        self.addWidget(zoom_in_btn)
        
        fit_btn = QToolButton()
        fit_btn.setText("⊞")
        fit_btn.setToolTip("Fit to View")
        fit_btn.clicked.connect(self.fit_to_view_requested)
        self.addWidget(fit_btn)
        
        actual_btn = QToolButton()
        actual_btn.setText("1:1")
        actual_btn.setToolTip("Actual Size (100%)")
        actual_btn.clicked.connect(self.actual_size_requested)
        self.addWidget(actual_btn)
        # Selection tool chooser (left area)
        sel_label = QLabel("Selection:")
        sel_label.setStyleSheet("color: #888888; padding: 0 8px;")
        self.addWidget(sel_label)

        self._sel_combo = QComboBox()
        self._sel_combo.addItems(["Rect", "Lasso", "Brush", "Pen", "Erase", "Fill"])
        self._sel_combo.setFixedWidth(100)
        self._sel_combo.setStyleSheet("""
            QComboBox {
                background-color: #3c3c3c;
                color: #cccccc;
                border: 1px solid #4a4a4a;
                border-radius: 4px;
                padding: 4px 8px;
            }
        """)
        self._sel_combo.currentTextChanged.connect(lambda t: self.selection_mode_changed.emit(t.lower()))
        self.addWidget(self._sel_combo)

        # Paint mode toggle
        self.addSeparator()
        paint_label = QLabel("Paint:")
        paint_label.setStyleSheet("color: #888888; padding: 0 8px;")
        self.addWidget(paint_label)

        self._paint_toggle = QPushButton("Off")
        self._paint_toggle.setCheckable(True)
        self._paint_toggle.setFixedSize(50, 28)
        self._paint_toggle.setStyleSheet("""
            QPushButton {
                background-color: #3c3c3c;
                color: #cccccc;
                border: 1px solid #4a4a4a;
                border-radius: 4px;
            }
            QPushButton:checked {
                background-color: #0078d4;
                color: white;
            }
        """)
        self._paint_toggle.toggled.connect(self._on_paint_toggled)
        self.addWidget(self._paint_toggle)

        # Paint color picker
        self._color_btn = QPushButton()
        self._color_btn.setFixedSize(40, 28)
        self._paint_color = (0, 0, 0)  # Default black
        self._update_color_button()
        self._color_btn.clicked.connect(self._pick_color)
        self.addWidget(self._color_btn)

        # Spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.addWidget(spacer)
        
        # Canvas size display
        self._size_label = QLabel("800 × 600")
        self._size_label.setStyleSheet("color: #888888; padding: 0 12px;")
        self.addWidget(self._size_label)
    
    def _on_zoom_changed(self, text: str):
        """Handle zoom combo change."""
        try:
            value = int(text.replace("%", ""))
            self.zoom_changed.emit(value)
        except ValueError:
            pass
    
    def set_zoom(self, zoom: float):
        """Set zoom display."""
        percentage = int(zoom * 100)
        self._zoom_combo.setCurrentText(f"{percentage}%")
    
    def set_canvas_size(self, width: int, height: int):
        """Update canvas size display."""
        self._size_label.setText(f"{width} × {height}")
    
    def _on_paint_toggled(self, checked: bool):
        """Handle paint mode toggle."""
        self._paint_toggle.setText("On" if checked else "Off")
        self.paint_mode_toggled.emit(checked)
    
    def _pick_color(self):
        """Open color picker dialog."""
        from PySide6.QtWidgets import QColorDialog
        from PySide6.QtGui import QColor
        
        current = QColor(*self._paint_color)
        color = QColorDialog.getColor(current, None, "Pick Paint Color")
        if color.isValid():
            self._paint_color = (color.red(), color.green(), color.blue())
            self._update_color_button()
            self.paint_color_changed.emit(*self._paint_color)
    
    def _update_color_button(self):
        """Update color button appearance."""
        r, g, b = self._paint_color
        self._color_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgb({r}, {g}, {b});
                border: 2px solid #4a4a4a;
                border-radius: 4px;
            }}
        """)
    
    def set_mode(self, mode: EditorMode):
        """Update mode indicator."""
        self._mode = mode
        if mode == EditorMode.IMAGE:
            self._mode_btn.setText("🖼️ Image Mode")
        else:
            self._mode_btn.setText("🎬 Video Mode")
    
    def set_undo_enabled(self, enabled: bool):
        """Enable/disable undo action."""
        self._undo_action.setEnabled(enabled)
    
    def set_redo_enabled(self, enabled: bool):
        """Enable/disable redo action."""
        self._redo_action.setEnabled(enabled)
