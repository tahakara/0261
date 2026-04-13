"""
Apply Effect Widget - Apply button with progress animation
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QProgressBar, 
                                QLabel, QFrame)
from PySide6.QtCore import Qt, Signal, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor


class ApplyEffectWidget(QWidget):
    """Widget with Apply button and progress animation"""
    
    # Signals
    apply_requested = Signal()
    
    def __init__(self):
        super().__init__()
        self.is_applying = False
        self.setup_ui()
        self.apply_styles()
        
    def setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        
        # Info label
        self.info_label = QLabel("Select an area to apply effects")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setWordWrap(True)
        self.info_label.setObjectName("infoLabel")
        layout.addWidget(self.info_label)
        
        # Apply button
        self.apply_button = QPushButton("Apply Effect")
        self.apply_button.setFixedHeight(40)
        self.apply_button.setObjectName("applyButton")
        self.apply_button.clicked.connect(self.on_apply_clicked)
        self.apply_button.setEnabled(False)
        layout.addWidget(self.apply_button)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setVisible(False)
        self.progress_bar.setObjectName("progressBar")
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setObjectName("statusLabel")
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)
        
        # Timer for animation
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self.update_progress)
        self.progress_value = 0
        
    def on_apply_clicked(self):
        """Handle apply button click"""
        if not self.is_applying:
            self.start_applying()
            self.apply_requested.emit()
    
    def start_applying(self):
        """Start apply animation"""
        self.is_applying = True
        self.apply_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.status_label.setVisible(True)
        self.status_label.setText("Applying effect...")
        
        # Start progress animation
        self.progress_value = 0
        self.progress_bar.setValue(0)
        self.progress_timer.start(30)  # Update every 30ms
    
    def update_progress(self):
        """Update progress bar animation"""
        self.progress_value += 2
        if self.progress_value >= 100:
            self.progress_value = 100
            self.finish_applying(success=True)
        self.progress_bar.setValue(self.progress_value)
    
    def finish_applying(self, success: bool = True, message: str = ""):
        """Finish apply animation"""
        self.progress_timer.stop()
        self.is_applying = False
        
        if success:
            self.progress_bar.setValue(100)
            self.status_label.setText(message or "Effect applied successfully!")
            self.status_label.setStyleSheet("color: #4CAF50;")
        else:
            self.status_label.setText(message or "Failed to apply effect")
            self.status_label.setStyleSheet("color: #f44336;")
        
        # Hide progress after delay
        QTimer.singleShot(2000, self.reset_ui)
    
    def reset_ui(self):
        """Reset UI to initial state"""
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)
        self.status_label.setVisible(False)
        self.status_label.setText("")
        self.apply_button.setEnabled(True)
    
    def set_enabled(self, enabled: bool, info_text: str = ""):
        """Enable/disable apply button with info"""
        self.apply_button.setEnabled(enabled and not self.is_applying)
        if info_text:
            self.info_label.setText(info_text)
    
    def set_selection_status(self, has_selection: bool):
        """Update based on selection status"""
        if has_selection:
            self.info_label.setText("Selection active. Ready to apply.")
            self.apply_button.setEnabled(True)
        else:
            self.info_label.setText("Select an area to apply effects")
            self.apply_button.setEnabled(False)
    
    def apply_styles(self):
        """Apply stylesheet"""
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #e0e0e0;
            }
            
            #infoLabel {
                color: #b0b0b0;
                font-size: 11px;
                padding: 5px;
            }
            
            QPushButton#applyButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 13px;
                font-weight: bold;
            }
            
            QPushButton#applyButton:hover {
                background-color: #1084d8;
            }
            
            QPushButton#applyButton:pressed {
                background-color: #006abc;
            }
            
            QPushButton#applyButton:disabled {
                background-color: #3a3a3a;
                color: #707070;
            }
            
            QProgressBar#progressBar {
                border: 1px solid #3a3a3a;
                border-radius: 3px;
                text-align: center;
                background-color: #1e1e1e;
            }
            
            QProgressBar#progressBar::chunk {
                background-color: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #0078d4, stop: 1 #00a8e8
                );
                border-radius: 2px;
            }
            
            #statusLabel {
                font-size: 11px;
                padding: 3px;
            }
            
            QFrame {
                background-color: #3a3a3a;
            }
        """)
