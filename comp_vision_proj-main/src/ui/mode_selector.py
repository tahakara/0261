"""
Mode selector dialog - shown at startup to choose Image or Video editor mode.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QFrame, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor, QPixmap, QPainter, QLinearGradient

from ..core.project import EditorMode


class ModeButton(QPushButton):
    """Custom styled button for mode selection."""
    
    def __init__(self, title: str, description: str, icon_text: str, parent=None):
        super().__init__(parent)
        self.setFixedSize(220, 180)
        self.setCursor(Qt.PointingHandCursor)
        
        self._title = title
        self._description = description
        self._icon_text = icon_text
        self._hovered = False
        
        self.setStyleSheet("""
            ModeButton {
                background-color: #2d2d2d;
                border: 2px solid #404040;
                border-radius: 12px;
                padding: 15px;
            }
            ModeButton:hover {
                background-color: #3d3d3d;
                border-color: #0078d4;
            }
            ModeButton:pressed {
                background-color: #1d1d1d;
            }
        """)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
        
        self._setup_layout()
    
    def _setup_layout(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Icon
        icon_label = QLabel(self._icon_text)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFont(QFont("Segoe UI", 36))
        icon_label.setStyleSheet("color: #0078d4;")
        layout.addWidget(icon_label)
        
        # Title
        title_label = QLabel(self._title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title_label.setStyleSheet("color: #ffffff;")
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(self._description)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setFont(QFont("Segoe UI", 9))
        desc_label.setStyleSheet("color: #888888;")
        layout.addWidget(desc_label)


class ModeSelectorDialog(QDialog):
    """
    Startup dialog to select between Image and Video editor modes.
    """
    
    mode_selected = Signal(EditorMode)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Editor Mode")
        self.setFixedSize(520, 320)
        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self._selected_mode: EditorMode = None
        self._setup_ui()
    
    def _setup_ui(self):
        # Main container with background
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border-radius: 16px;
                border: 1px solid #333333;
            }
        """)
        
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(20)
        container_layout.setContentsMargins(30, 25, 30, 25)
        
        # Title
        title = QLabel("Welcome to Image/Video Editor")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #ffffff; background: transparent;")
        container_layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Choose your editing mode to get started")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(QFont("Segoe UI", 10))
        subtitle.setStyleSheet("color: #888888; background: transparent;")
        container_layout.addWidget(subtitle)
        
        container_layout.addSpacing(10)
        
        # Mode buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)
        
        # Image Editor button
        self.image_btn = ModeButton(
            "Image Editor",
            "Edit photos and create graphics with layers and effects",
            "🖼️"
        )
        self.image_btn.clicked.connect(lambda: self._select_mode(EditorMode.IMAGE))
        buttons_layout.addWidget(self.image_btn)
        
        # Video Editor button
        self.video_btn = ModeButton(
            "Video Editor",
            "Edit videos with timeline, effects and transitions",
            "🎬"
        )
        self.video_btn.clicked.connect(lambda: self._select_mode(EditorMode.VIDEO))
        buttons_layout.addWidget(self.video_btn)
        
        container_layout.addLayout(buttons_layout)
        
        # Close button
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        
        close_btn = QPushButton("Cancel")
        close_btn.setFixedSize(80, 32)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #888888;
                border: 1px solid #404040;
                border-radius: 6px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #333333;
                color: #ffffff;
            }
        """)
        close_btn.clicked.connect(self.reject)
        close_layout.addWidget(close_btn)
        
        container_layout.addLayout(close_layout)
        
        main_layout.addWidget(container)
    
    def _select_mode(self, mode: EditorMode):
        """Handle mode selection."""
        self._selected_mode = mode
        self.mode_selected.emit(mode)
        self.accept()
    
    @property
    def selected_mode(self) -> EditorMode:
        return self._selected_mode
    
    def mousePressEvent(self, event):
        """Allow dragging the dialog."""
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """Handle dialog dragging."""
        if event.buttons() == Qt.LeftButton and hasattr(self, '_drag_pos'):
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
