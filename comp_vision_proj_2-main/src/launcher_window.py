"""
Launcher Window - Welcome screen for mode selection
"""
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                                QPushButton, QLabel, QFrame)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon


class LauncherWindow(QMainWindow):
    """
    Welcome screen that allows users to select between Image Editor and Video Editor modes
    """
    
    # Signals
    mode_selected = Signal(str)  # Emits "image" or "video"
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vision Editor - Welcome")
        self.setFixedSize(800, 500)
        self.setup_ui()
        self.apply_styles()
        
    def setup_ui(self):
        """Setup the launcher UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(30)
        
        # Title section
        title_label = QLabel("Görsel Düzenleyici")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(36)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setObjectName("titleLabel")
        
        subtitle_label = QLabel("Profesyonel Resim & Video İşleme Yazılımı")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_font = QFont()
        subtitle_font.setPointSize(12)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setObjectName("subtitleLabel")
        
        main_layout.addWidget(title_label)
        main_layout.addWidget(subtitle_label)
        main_layout.addSpacing(20)
        
        # Mode selection section
        mode_label = QLabel("Düzenleyici Modu Seçin:")
        mode_label.setAlignment(Qt.AlignCenter)
        mode_font = QFont()
        mode_font.setPointSize(14)
        mode_label.setFont(mode_font)
        main_layout.addWidget(mode_label)
        
        # Button container
        button_layout = QHBoxLayout()
        button_layout.setSpacing(30)
        
        # Image Editor Button
        self.image_editor_btn = self._create_mode_button(
            "Resim Düzenleyici",
            "Güçlü araçlar ve efektlerle\nfotoğraf düzenleyin",
            "◈"
        )
        self.image_editor_btn.clicked.connect(lambda: self.on_mode_selected("image"))
        
        # Video Editor Button
        self.video_editor_btn = self._create_mode_button(
            "Video Düzenleyici",
            "Hassas kontrol ve yaratıcılıkla\nvideo düzenleyin",
            "▶"
        )
        self.video_editor_btn.clicked.connect(lambda: self.on_mode_selected("video"))
        
        button_layout.addWidget(self.image_editor_btn)
        button_layout.addWidget(self.video_editor_btn)
        
        main_layout.addLayout(button_layout)
        main_layout.addStretch()
        
        # Footer
        footer_label = QLabel("Version 1.0.0 | Plugin-Based Architecture")
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setObjectName("footerLabel")
        main_layout.addWidget(footer_label)
        
    def _create_mode_button(self, title: str, description: str, icon: str) -> QPushButton:
        """Create a styled mode selection button"""
        button = QPushButton()
        button.setFixedSize(300, 150)
        button.setCursor(Qt.PointingHandCursor)
        
        # Button layout
        layout = QVBoxLayout(button)
        layout.setAlignment(Qt.AlignCenter)
        
        # Icon label
        icon_label = QLabel(icon)
        icon_font = QFont()
        icon_font.setPointSize(48)
        icon_label.setFont(icon_font)
        icon_label.setAlignment(Qt.AlignCenter)
        
        # Title label
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        
        # Description label
        desc_label = QLabel(description)
        desc_font = QFont()
        desc_font.setPointSize(10)
        desc_label.setFont(desc_font)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        
        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        
        button.setObjectName("modeButton")
        return button
        
    def on_mode_selected(self, mode: str):
        """Handle mode selection"""
        self.mode_selected.emit(mode)
        
    def apply_styles(self):
        """Apply stylesheet to the launcher"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            
            #titleLabel {
                color: #ffffff;
            }
            
            #subtitleLabel {
                color: #b0b0b0;
            }
            
            #footerLabel {
                color: #707070;
                font-size: 10px;
            }
            
            QPushButton#modeButton {
                background-color: #3a3a3a;
                border: 2px solid #505050;
                border-radius: 10px;
                color: #ffffff;
            }
            
            QPushButton#modeButton:hover {
                background-color: #4a4a4a;
                border: 2px solid #0078d4;
            }
            
            QPushButton#modeButton:pressed {
                background-color: #303030;
            }
            
            QLabel {
                color: #e0e0e0;
            }
        """)
