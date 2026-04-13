"""
Image/Video Editor Application
Main entry point.
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from src.ui.main_window import MainWindow


def main():
    """Main entry point for the application."""
    
    # High DPI support
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    
    # Set application info
    app.setApplicationName("Image/Video Editor")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Editor")
    
    # Set default font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Set global stylesheet for dark theme
    app.setStyleSheet("""
        QWidget {
            font-family: "Segoe UI", sans-serif;
        }
        QToolTip {
            background-color: #2d2d2d;
            color: #cccccc;
            border: 1px solid #3c3c3c;
            padding: 4px;
            border-radius: 4px;
        }
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
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
