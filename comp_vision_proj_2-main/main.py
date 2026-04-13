"""
Main Application Entry Point
"""
import sys
from PySide6.QtWidgets import QApplication
from src.launcher_window import LauncherWindow
from src.editor_window import EditorWindow


class VisionEditorApp:
    """Main application controller"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.launcher = None
        self.editor = None
        
    def run(self):
        """Run the application"""
        # Show launcher window
        self.launcher = LauncherWindow()
        self.launcher.mode_selected.connect(self.on_mode_selected)
        self.launcher.show()
        
        return self.app.exec()
    
    def on_mode_selected(self, mode: str):
        """Handle mode selection from launcher"""
        # Hide launcher
        self.launcher.hide()
        
        # Show editor window
        self.editor = EditorWindow(mode=mode)
        self.editor.show()


def main():
    """Main entry point"""
    app = VisionEditorApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
