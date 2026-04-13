"""
Overlay Panel - UI for adding and managing video overlays
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                                QLabel, QSlider, QGroupBox, QListWidget, QListWidgetItem,
                                QLineEdit, QSpinBox, QColorDialog, QFileDialog, QCheckBox,
                                QComboBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor
from src.overlay_manager import OverlayType
import cv2


class OverlayPanel(QWidget):
    """Panel for managing video overlays"""
    
    # Signals
    add_text_overlay_requested = Signal(str, int, tuple, int, str)  # text, font_size, color, font_family, name
    add_image_overlay_requested = Signal(str, str)  # image_path, name
    add_video_overlay_requested = Signal(str, str)  # video_path, name
    
    remove_overlay_requested = Signal(int)  # overlay_id
    overlay_selected = Signal(int)  # overlay_id
    overlay_name_changed = Signal(int, str)  # overlay_id, new_name
    
    opacity_changed = Signal(int, float)  # overlay_id, opacity
    keycolor_changed = Signal(int, bool, tuple, int)  # overlay_id, enable, color, tolerance
    
    def __init__(self, overlay_manager):
        super().__init__()
        
        self.overlay_manager = overlay_manager
        self.selected_overlay_id = None
        
        self.setup_ui()
        
        # Connect signals
        self.overlay_manager.overlay_added.connect(self.on_overlay_added)
        self.overlay_manager.overlay_removed.connect(self.on_overlay_removed)
        self.overlay_manager.overlay_updated.connect(self.on_overlay_updated)
        
    def setup_ui(self):
        """Setup the overlay panel UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("Overlay'ler")
        title.setObjectName("panelTitle")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(11)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Add overlay buttons
        add_group = self._create_add_overlay_buttons()
        layout.addWidget(add_group)
        
        # Overlay list
        list_label = QLabel("Overlay Listesi:")
        layout.addWidget(list_label)
        
        self.overlay_list = QListWidget()
        self.overlay_list.setMaximumHeight(150)
        self.overlay_list.itemClicked.connect(self.on_list_item_clicked)
        layout.addWidget(self.overlay_list)
        
        # Remove button
        self.remove_btn = QPushButton("✕ Seçili Overlay'i Sil")
        self.remove_btn.setEnabled(False)
        self.remove_btn.clicked.connect(self.on_remove_overlay)
        layout.addWidget(self.remove_btn)
        
        # Overlay properties
        self.properties_group = self._create_properties_group()
        self.properties_group.setEnabled(False)
        layout.addWidget(self.properties_group)
        
        layout.addStretch()
        
    def _create_add_overlay_buttons(self):
        """Create add overlay buttons group"""
        group = QGroupBox("Overlay Ekle")
        layout = QVBoxLayout(group)
        
        # Text overlay
        text_layout = QHBoxLayout()
        
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Metin girin...")
        text_layout.addWidget(self.text_input)
        
        self.text_name_input = QLineEdit()
        self.text_name_input.setPlaceholderText("İsim (opsiyonel)")
        self.text_name_input.setMaximumWidth(120)
        text_layout.addWidget(self.text_name_input)
        
        layout.addLayout(text_layout)
        
        # Font settings row
        font_layout = QHBoxLayout()
        
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(10, 100)
        self.font_size_spin.setValue(24)
        self.font_size_spin.setPrefix("Boyut: ")
        font_layout.addWidget(self.font_size_spin)
        
        # Font family dropdown
        self.font_family_combo = QComboBox()
        self.font_family_combo.addItem("Simplex", cv2.FONT_HERSHEY_SIMPLEX)
        self.font_family_combo.addItem("Plain", cv2.FONT_HERSHEY_PLAIN)
        self.font_family_combo.addItem("Duplex", cv2.FONT_HERSHEY_DUPLEX)
        self.font_family_combo.addItem("Complex", cv2.FONT_HERSHEY_COMPLEX)
        self.font_family_combo.addItem("Triplex", cv2.FONT_HERSHEY_TRIPLEX)
        self.font_family_combo.addItem("Script Simplex", cv2.FONT_HERSHEY_SCRIPT_SIMPLEX)
        self.font_family_combo.addItem("Script Complex", cv2.FONT_HERSHEY_SCRIPT_COMPLEX)
        font_layout.addWidget(self.font_family_combo)
        
        self.text_color_btn = QPushButton("Renk")
        self.text_color_btn.clicked.connect(self.on_choose_text_color)
        self.text_color = (255, 255, 255)
        font_layout.addWidget(self.text_color_btn)
        
        layout.addLayout(font_layout)
        
        add_text_btn = QPushButton("+ Metin Ekle")
        add_text_btn.clicked.connect(self.on_add_text_overlay)
        layout.addWidget(add_text_btn)
        
        # Image overlay
        add_image_btn = QPushButton("+ Resim Ekle")
        add_image_btn.clicked.connect(self.on_add_image_overlay)
        layout.addWidget(add_image_btn)
        
        # Video overlay
        add_video_btn = QPushButton("+ Video Ekle")
        add_video_btn.clicked.connect(self.on_add_video_overlay)
        layout.addWidget(add_video_btn)
        
        return group
        
    def _create_properties_group(self):
        """Create overlay properties group"""
        group = QGroupBox("Overlay Özellikleri")
        layout = QVBoxLayout(group)
        
        # Name editing
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("İsim:"))
        self.name_edit = QLineEdit()
        self.name_edit.textChanged.connect(self.on_name_edited)
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)
        
        # Opacity
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(QLabel("Opaklık:"))
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.valueChanged.connect(self.on_opacity_changed)
        opacity_layout.addWidget(self.opacity_slider)
        self.opacity_label = QLabel("100%")
        self.opacity_label.setMinimumWidth(40)
        opacity_layout.addWidget(self.opacity_label)
        layout.addLayout(opacity_layout)
        
        # Keycolor (chroma key)
        keycolor_group = QGroupBox("Keycolor (Chroma Key)")
        keycolor_layout = QVBoxLayout(keycolor_group)
        
        self.keycolor_enable = QCheckBox("Keycolor Aktif")
        self.keycolor_enable.stateChanged.connect(self.on_keycolor_changed)
        keycolor_layout.addWidget(self.keycolor_enable)
        
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Renk:"))
        self.keycolor_btn = QPushButton("Yeşil")
        self.keycolor_btn.clicked.connect(self.on_choose_keycolor)
        self.keycolor = (0, 255, 0)  # BGR green
        color_layout.addWidget(self.keycolor_btn)
        keycolor_layout.addLayout(color_layout)
        
        tolerance_layout = QHBoxLayout()
        tolerance_layout.addWidget(QLabel("Tolerans:"))
        self.keycolor_tolerance_slider = QSlider(Qt.Horizontal)
        self.keycolor_tolerance_slider.setRange(0, 100)
        self.keycolor_tolerance_slider.setValue(30)
        self.keycolor_tolerance_slider.valueChanged.connect(self.on_keycolor_changed)
        tolerance_layout.addWidget(self.keycolor_tolerance_slider)
        self.tolerance_label = QLabel("30")
        self.tolerance_label.setMinimumWidth(30)
        tolerance_layout.addWidget(self.tolerance_label)
        keycolor_layout.addLayout(tolerance_layout)
        
        layout.addWidget(keycolor_group)
        
        return group
        
    def on_add_text_overlay(self):
        """Handle add text overlay"""
        text = self.text_input.text().strip()
        if not text:
            return
            
        font_size = self.font_size_spin.value()
        font_family = self.font_family_combo.currentData()
        name = self.text_name_input.text().strip()
        self.add_text_overlay_requested.emit(text, font_size, self.text_color, font_family, name)
        
        self.text_input.clear()
        self.text_name_input.clear()
        
    def on_add_image_overlay(self):
        """Handle add image overlay"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Resim Seç",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if file_path:
            name, ok = self._get_overlay_name("Resim")
            self.add_image_overlay_requested.emit(file_path, name)
            
    def on_add_video_overlay(self):
        """Handle add video overlay"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Video Seç",
            "",
            "Video Files (*.mp4 *.avi *.mov *.mkv)"
        )
        
        if file_path:
            name, ok = self._get_overlay_name("Video")
            self.add_video_overlay_requested.emit(file_path, name)
            
    def _get_overlay_name(self, default_prefix):
        """Get overlay name from user (optional)"""
        from PySide6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "Overlay İsmi", 
                                        f"{default_prefix} overlay için isim (boş bırakabilirsiniz):")
        return name.strip(), ok
            
    def on_choose_text_color(self):
        """Handle choose text color"""
        color = QColorDialog.getColor()
        if color.isValid():
            # Convert QColor to BGR
            self.text_color = (color.blue(), color.green(), color.red())
            self.text_color_btn.setStyleSheet(f"background-color: {color.name()};")
            
    def on_choose_keycolor(self):
        """Handle choose keycolor"""
        color = QColorDialog.getColor(QColor(0, 255, 0))
        if color.isValid():
            # Convert QColor to BGR
            self.keycolor = (color.blue(), color.green(), color.red())
            self.keycolor_btn.setText(color.name())
            self.keycolor_btn.setStyleSheet(f"background-color: {color.name()};")
            self.on_keycolor_changed()
            
    def on_list_item_clicked(self, item):
        """Handle overlay list item click"""
        overlay_id = item.data(Qt.UserRole)
        self.selected_overlay_id = overlay_id
        self.overlay_selected.emit(overlay_id)
        
        # Enable properties
        self.properties_group.setEnabled(True)
        self.remove_btn.setEnabled(True)
        
        # Update properties from overlay
        overlay = self.overlay_manager.get_overlay(overlay_id)
        if overlay:
            self.name_edit.setText(overlay.name)
            self.opacity_slider.setValue(int(overlay.opacity * 100))
            self.keycolor_enable.setChecked(overlay.has_keycolor)
            
    def on_remove_overlay(self):
        """Handle remove overlay"""
        if self.selected_overlay_id is not None:
            self.remove_overlay_requested.emit(self.selected_overlay_id)
            self.selected_overlay_id = None
            self.properties_group.setEnabled(False)
            self.remove_btn.setEnabled(False)
            
    def on_opacity_changed(self, value):
        """Handle opacity slider change"""
        opacity = value / 100.0
        self.opacity_label.setText(f"{value}%")
        
        if self.selected_overlay_id is not None:
            self.opacity_changed.emit(self.selected_overlay_id, opacity)
            
    def on_keycolor_changed(self):
        """Handle keycolor settings change"""
        if self.selected_overlay_id is None:
            return
            
        enable = self.keycolor_enable.isChecked()
        tolerance = self.keycolor_tolerance_slider.value()
        self.tolerance_label.setText(str(tolerance))
        
        self.keycolor_changed.emit(self.selected_overlay_id, enable, self.keycolor, tolerance)
        
    def on_name_edited(self, text):
        """Handle overlay name edit"""
        if self.selected_overlay_id is not None:
            self.overlay_name_changed.emit(self.selected_overlay_id, text)
        
    def on_overlay_added(self, overlay_id):
        """Handle overlay added"""
        overlay = self.overlay_manager.get_overlay(overlay_id)
        if overlay:
            item_text = f"{overlay.name}" if overlay.name else f"{overlay.type.value.upper()} #{overlay_id}"
                
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, overlay_id)
            self.overlay_list.addItem(item)
            
    def on_overlay_removed(self, overlay_id):
        """Handle overlay removed"""
        for i in range(self.overlay_list.count()):
            item = self.overlay_list.item(i)
            if item.data(Qt.UserRole) == overlay_id:
                self.overlay_list.takeItem(i)
                break
                
    def on_overlay_updated(self, overlay_id):
        """Handle overlay updated"""
        # Update list item text with new name
        overlay = self.overlay_manager.get_overlay(overlay_id)
        if overlay:
            for i in range(self.overlay_list.count()):
                item = self.overlay_list.item(i)
                if item.data(Qt.UserRole) == overlay_id:
                    item_text = f"{overlay.name}" if overlay.name else f"{overlay.type.value.upper()} #{overlay_id}"
                    item.setText(item_text)
                    break
