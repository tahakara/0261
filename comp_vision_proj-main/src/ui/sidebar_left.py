"""
Left sidebar - Contains modules/tools list organized by category.
"""

from typing import Dict, List, Optional, Callable
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QFrame,
    QPushButton, QLabel, QHBoxLayout, QToolButton,
    QSizePolicy, QSpacerItem
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QIcon

from ..core.module_base import ModuleBase, ModuleCategory


class ModuleButton(QPushButton):
    """Button representing a module in the sidebar."""
    
    def __init__(self, module: ModuleBase, parent=None):
        super().__init__(parent)
        self._module = module
        
        self.setText(module.name)
        self.setToolTip(module.description)
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(36)
        
        if module.icon:
            self.setIcon(module.icon)
            self.setIconSize(QSize(20, 20))
        
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #cccccc;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                text-align: left;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
            }
            QPushButton:checked {
                background-color: #0078d4;
                color: white;
            }
            QPushButton:checked:hover {
                background-color: #1084d8;
            }
        """)
    
    @property
    def module(self) -> ModuleBase:
        return self._module


class CategorySection(QFrame):
    """Collapsible section for a module category."""
    
    module_clicked = Signal(ModuleBase)
    
    def __init__(self, category: ModuleCategory, parent=None):
        super().__init__(parent)
        self._category = category
        self._is_expanded = True
        self._buttons: List[ModuleButton] = []
        
        self._setup_ui()
    
    def _setup_ui(self):
        self.setStyleSheet("""
            CategorySection {
                background-color: transparent;
                border: none;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        # Header
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(8, 8, 8, 4)
        header_layout.setSpacing(6)
        
        self._expand_btn = QToolButton()
        self._expand_btn.setArrowType(Qt.DownArrow)
        self._expand_btn.setFixedSize(16, 16)
        self._expand_btn.setStyleSheet("""
            QToolButton {
                background: transparent;
                border: none;
            }
        """)
        self._expand_btn.clicked.connect(self._toggle_expand)
        header_layout.addWidget(self._expand_btn)
        
        category_names = {
            ModuleCategory.TOOL: "Tools",
            ModuleCategory.ADJUSTMENT: "Adjustments",
            ModuleCategory.FILTER: "Filters",
            ModuleCategory.EFFECT: "Effects",
            ModuleCategory.TRANSFORM: "Transform",
            ModuleCategory.COLOR: "Color",
            ModuleCategory.VIDEO: "Video",
            ModuleCategory.OTHER: "Other"
        }
        
        title = QLabel(category_names.get(self._category, "Other"))
        title.setFont(QFont("Segoe UI", 10, QFont.Bold))
        title.setStyleSheet("color: #888888;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        layout.addWidget(header)
        
        # Content area for modules
        self._content = QWidget()
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setContentsMargins(8, 0, 8, 8)
        self._content_layout.setSpacing(2)
        layout.addWidget(self._content)
    
    def add_module(self, module: ModuleBase):
        """Add a module button to this category."""
        btn = ModuleButton(module)
        btn.clicked.connect(lambda: self.module_clicked.emit(module))
        self._buttons.append(btn)
        self._content_layout.addWidget(btn)
    
    def _toggle_expand(self):
        """Toggle section expansion."""
        self._is_expanded = not self._is_expanded
        self._content.setVisible(self._is_expanded)
        self._expand_btn.setArrowType(
            Qt.DownArrow if self._is_expanded else Qt.RightArrow
        )
    
    def deselect_all(self):
        """Deselect all module buttons."""
        for btn in self._buttons:
            btn.setChecked(False)
    
    def select_module(self, module: ModuleBase):
        """Select a specific module."""
        for btn in self._buttons:
            btn.setChecked(btn.module == module)


class LeftSidebar(QScrollArea):
    """
    Left sidebar containing all modules organized by category.
    """
    
    module_selected = Signal(ModuleBase)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setMinimumWidth(200)
        self.setMaximumWidth(280)
        
        self.setStyleSheet("""
            QScrollArea {
                background-color: #252526;
                border: none;
                border-right: 1px solid #3c3c3c;
            }
            QScrollBar:vertical {
                background-color: #252526;
                width: 8px;
            }
            QScrollBar::handle:vertical {
                background-color: #4a4a4a;
                border-radius: 4px;
                min-height: 20px;
            }
        """)
        
        # Main content
        content = QWidget()
        self._layout = QVBoxLayout(content)
        self._layout.setContentsMargins(0, 8, 0, 8)
        self._layout.setSpacing(4)
        self.setWidget(content)
        
        # Category sections
        self._sections: Dict[ModuleCategory, CategorySection] = {}
        self._current_module: Optional[ModuleBase] = None
        
        # Add title
        title = QLabel("Modules")
        title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        title.setStyleSheet("color: #ffffff; padding: 8px 12px;")
        self._layout.addWidget(title)
        
        # Spacer at bottom
        self._layout.addStretch()
    
    def add_module(self, module: ModuleBase):
        """Add a module to the sidebar."""
        category = module.category
        
        # Create section if doesn't exist
        if category not in self._sections:
            section = CategorySection(category)
            section.module_clicked.connect(self._on_module_clicked)
            self._sections[category] = section
            
            # Insert before spacer
            self._layout.insertWidget(self._layout.count() - 1, section)
        
        self._sections[category].add_module(module)
    
    def _on_module_clicked(self, module: ModuleBase):
        """Handle module selection."""
        # Deselect all in other sections
        for section in self._sections.values():
            section.deselect_all()
        
        # Select in the correct section
        if module.category in self._sections:
            self._sections[module.category].select_module(module)
        
        self._current_module = module
        self.module_selected.emit(module)
    
    @property
    def current_module(self) -> Optional[ModuleBase]:
        """Get currently selected module."""
        return self._current_module
    
    def clear_modules(self):
        """Remove all modules."""
        for section in self._sections.values():
            section.deleteLater()
        self._sections.clear()
        self._current_module = None
