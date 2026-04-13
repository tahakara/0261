"""
Video Control Panel - Camera, recording, and effect controls for video editor
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                                QLabel, QSlider, QGroupBox, QFileDialog, QMessageBox,
                                QCheckBox, QComboBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from pathlib import Path


class VideoControlPanel(QWidget):
    """Control panel for video editor with camera, recording, and effect controls"""
    
    # Signals
    camera_toggle_requested = Signal(bool)  # True to start, False to stop
    recording_toggle_requested = Signal()
    snapshot_requested = Signal()
    
    # Effect signals
    brightness_changed = Signal(int)
    heat_changed = Signal(int)
    denoise_changed = Signal(int)
    noise_changed = Signal(int)
    rgb_changed = Signal(int, int, int)  # red, green, blue
    
    # Face detection signals
    face_detection_toggled = Signal(bool)
    face_blur_toggled = Signal(bool)
    face_boxes_toggled = Signal(bool)
    face_numbers_toggled = Signal(bool)
    face_blur_strength_changed = Signal(int)
    face_sentiment_toggled = Signal(bool)
    face_sentiment_emoji_toggled = Signal(bool)
    
    # Color filter signal
    color_filter_changed = Signal(str, float)  # filter_name, intensity
    
    def __init__(self):
        super().__init__()
        
        self.camera_active = False
        self.is_recording = False
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the control panel UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("Video Kontrolleri")
        title.setObjectName("panelTitle")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(11)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Camera controls
        camera_group = self._create_camera_controls()
        layout.addWidget(camera_group)
        
        # Recording controls
        recording_group = self._create_recording_controls()
        layout.addWidget(recording_group)
        
        # Effect controls
        effect_group = self._create_effect_controls()
        layout.addWidget(effect_group)
        
        # RGB controls
        rgb_group = self._create_rgb_controls()
        layout.addWidget(rgb_group)
        
        # Face detection controls
        face_group = self._create_face_detection_controls()
        layout.addWidget(face_group)
        
        # Color filter controls
        filter_group = self._create_color_filter_controls()
        layout.addWidget(filter_group)
        
        layout.addStretch()
        
    def _create_camera_controls(self):
        """Create camera control group"""
        group = QGroupBox("Kamera")
        layout = QVBoxLayout(group)
        
        # Camera toggle button
        self.camera_btn = QPushButton("▶ Kamerayı Aç")
        self.camera_btn.setCheckable(True)
        self.camera_btn.clicked.connect(self.on_camera_toggle)
        layout.addWidget(self.camera_btn)
        
        return group
        
    def _create_recording_controls(self):
        """Create recording control group"""
        group = QGroupBox("Kayıt")
        layout = QVBoxLayout(group)
        
        # Format selection
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Format:"))
        self.format_combo = QComboBox()
        self.format_combo.addItem("MP4 (H.264)", "mp4")
        self.format_combo.addItem("AVI (MJPEG)", "avi")
        self.format_combo.addItem("MOV (H.264)", "mov")
        self.format_combo.addItem("MKV (H.264)", "mkv")
        format_layout.addWidget(self.format_combo)
        layout.addLayout(format_layout)
        
        # Recording button
        self.record_btn = QPushButton("● Kaydı Başlat")
        self.record_btn.setEnabled(False)
        self.record_btn.clicked.connect(self.on_record_toggle)
        layout.addWidget(self.record_btn)
        
        # Recording duration label
        self.duration_label = QLabel("Süre: 00:00")
        self.duration_label.setVisible(False)
        self.duration_label.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(self.duration_label)
        
        # Snapshot button
        self.snapshot_btn = QPushButton("□ Snapshot Al")
        self.snapshot_btn.setEnabled(False)
        self.snapshot_btn.clicked.connect(self.on_snapshot)
        layout.addWidget(self.snapshot_btn)
        
        return group
        
    def _create_effect_controls(self):
        """Create effect control group"""
        group = QGroupBox("Efektler")
        layout = QVBoxLayout(group)
        
        # Brightness
        brightness_layout = QHBoxLayout()
        brightness_layout.addWidget(QLabel("Parlaklık:"))
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(-100, 100)
        self.brightness_slider.setValue(0)
        self.brightness_slider.valueChanged.connect(self.on_brightness_changed)
        brightness_layout.addWidget(self.brightness_slider)
        self.brightness_label = QLabel("0")
        self.brightness_label.setMinimumWidth(30)
        brightness_layout.addWidget(self.brightness_label)
        layout.addLayout(brightness_layout)
        
        # Heat effect
        heat_layout = QHBoxLayout()
        heat_layout.addWidget(QLabel("Isı Efekti:"))
        self.heat_slider = QSlider(Qt.Horizontal)
        self.heat_slider.setRange(0, 100)
        self.heat_slider.setValue(0)
        self.heat_slider.valueChanged.connect(self.on_heat_changed)
        heat_layout.addWidget(self.heat_slider)
        self.heat_label = QLabel("0")
        self.heat_label.setMinimumWidth(30)
        heat_layout.addWidget(self.heat_label)
        layout.addLayout(heat_layout)
        
        # Denoise
        denoise_layout = QHBoxLayout()
        denoise_layout.addWidget(QLabel("Gürültü Azaltma:"))
        self.denoise_slider = QSlider(Qt.Horizontal)
        self.denoise_slider.setRange(0, 10)
        self.denoise_slider.setValue(0)
        self.denoise_slider.valueChanged.connect(self.on_denoise_changed)
        denoise_layout.addWidget(self.denoise_slider)
        self.denoise_label = QLabel("0")
        self.denoise_label.setMinimumWidth(30)
        denoise_layout.addWidget(self.denoise_label)
        layout.addLayout(denoise_layout)
        
        # Noise
        noise_layout = QHBoxLayout()
        noise_layout.addWidget(QLabel("Gürültü Ekleme:"))
        self.noise_slider = QSlider(Qt.Horizontal)
        self.noise_slider.setRange(0, 100)
        self.noise_slider.setValue(0)
        self.noise_slider.valueChanged.connect(self.on_noise_changed)
        noise_layout.addWidget(self.noise_slider)
        self.noise_label = QLabel("0")
        self.noise_label.setMinimumWidth(30)
        noise_layout.addWidget(self.noise_label)
        layout.addLayout(noise_layout)
        
        return group
        
    def _create_rgb_controls(self):
        """Create RGB channel control group"""
        group = QGroupBox("RGB Kanalları")
        layout = QVBoxLayout(group)
        
        # Red channel
        red_layout = QHBoxLayout()
        red_layout.addWidget(QLabel("Kırmızı:"))
        self.red_slider = QSlider(Qt.Horizontal)
        self.red_slider.setRange(-100, 100)
        self.red_slider.setValue(0)
        self.red_slider.valueChanged.connect(self.on_rgb_changed)
        red_layout.addWidget(self.red_slider)
        self.red_label = QLabel("0")
        self.red_label.setMinimumWidth(30)
        red_layout.addWidget(self.red_label)
        layout.addLayout(red_layout)
        
        # Green channel
        green_layout = QHBoxLayout()
        green_layout.addWidget(QLabel("Yeşil:"))
        self.green_slider = QSlider(Qt.Horizontal)
        self.green_slider.setRange(-100, 100)
        self.green_slider.setValue(0)
        self.green_slider.valueChanged.connect(self.on_rgb_changed)
        green_layout.addWidget(self.green_slider)
        self.green_label = QLabel("0")
        self.green_label.setMinimumWidth(30)
        green_layout.addWidget(self.green_label)
        layout.addLayout(green_layout)
        
        # Blue channel
        blue_layout = QHBoxLayout()
        blue_layout.addWidget(QLabel("Mavi:"))
        self.blue_slider = QSlider(Qt.Horizontal)
        self.blue_slider.setRange(-100, 100)
        self.blue_slider.setValue(0)
        self.blue_slider.valueChanged.connect(self.on_rgb_changed)
        blue_layout.addWidget(self.blue_slider)
        self.blue_label = QLabel("0")
        self.blue_label.setMinimumWidth(30)
        blue_layout.addWidget(self.blue_label)
        layout.addLayout(blue_layout)
        
        return group
        
    def on_camera_toggle(self, checked):
        """Handle camera toggle button"""
        self.camera_active = checked
        
        if checked:
            self.camera_btn.setText("■ Kamerayı Kapat")
            self.record_btn.setEnabled(True)
            self.snapshot_btn.setEnabled(True)
        else:
            self.camera_btn.setText("▶ Kamerayı Aç")
            self.record_btn.setEnabled(False)
            self.snapshot_btn.setEnabled(False)
            
            # Stop recording if active
            if self.is_recording:
                self.on_record_toggle()
                
        self.camera_toggle_requested.emit(checked)
        
    def on_record_toggle(self):
        """Handle record toggle button"""
        self.is_recording = not self.is_recording
        
        if self.is_recording:
            self.record_btn.setText("■ Kaydı Durdur")
            self.camera_btn.setEnabled(False)
            self.snapshot_btn.setEnabled(False)
            self.format_combo.setEnabled(False)
            self.duration_label.setVisible(True)
        else:
            self.record_btn.setText("● Kaydı Başlat")
            self.camera_btn.setEnabled(True)
            self.snapshot_btn.setEnabled(True)
            self.format_combo.setEnabled(True)
            self.duration_label.setVisible(False)
            
        self.recording_toggle_requested.emit()
        
    def update_recording_duration(self, seconds):
        """Update recording duration display"""
        minutes = seconds // 60
        secs = seconds % 60
        self.duration_label.setText(f"Süre: {minutes:02d}:{secs:02d}")
        
    def get_selected_format(self):
        """Get selected video format"""
        return self.format_combo.currentData()
        
    def on_snapshot(self):
        """Handle snapshot button"""
        self.snapshot_requested.emit()
        
    def on_brightness_changed(self, value):
        """Handle brightness slider"""
        self.brightness_label.setText(str(value))
        self.brightness_changed.emit(value)
        
    def on_heat_changed(self, value):
        """Handle heat effect slider"""
        self.heat_label.setText(str(value))
        self.heat_changed.emit(value)
        
    def on_denoise_changed(self, value):
        """Handle denoise slider"""
        self.denoise_label.setText(str(value))
        self.denoise_changed.emit(value)
        
    def on_noise_changed(self, value):
        """Handle noise slider"""
        self.noise_label.setText(str(value))
        self.noise_changed.emit(value)
        
    def on_rgb_changed(self):
        """Handle RGB sliders"""
        red = self.red_slider.value()
        green = self.green_slider.value()
        blue = self.blue_slider.value()
        
        self.red_label.setText(str(red))
        self.green_label.setText(str(green))
        self.blue_label.setText(str(blue))
        
        self.rgb_changed.emit(red, green, blue)
        
    def set_recording_status(self, is_recording):
        """Update recording status from external source"""
        if self.is_recording != is_recording:
            self.on_record_toggle()
            
    def _create_face_detection_controls(self):
        """Create face detection control group"""
        group = QGroupBox("Yüz Tanıma")
        layout = QVBoxLayout(group)
        
        # Enable face detection
        self.face_detect_check = QCheckBox("Yüz Tanıma Aktif")
        self.face_detect_check.stateChanged.connect(
            lambda: self.face_detection_toggled.emit(self.face_detect_check.isChecked()))
        layout.addWidget(self.face_detect_check)
        
        # Show bounding boxes
        self.face_boxes_check = QCheckBox("Çerçeve Göster")
        self.face_boxes_check.setChecked(True)
        self.face_boxes_check.stateChanged.connect(
            lambda: self.face_boxes_toggled.emit(self.face_boxes_check.isChecked()))
        layout.addWidget(self.face_boxes_check)
        
        # Show numbers
        self.face_numbers_check = QCheckBox("Numaralandır")
        self.face_numbers_check.setChecked(True)
        self.face_numbers_check.stateChanged.connect(
            lambda: self.face_numbers_toggled.emit(self.face_numbers_check.isChecked()))
        layout.addWidget(self.face_numbers_check)
        
        # Blur faces
        self.face_blur_check = QCheckBox("Yüzleri Bulanıklaştır")
        self.face_blur_check.stateChanged.connect(
            lambda: self.face_blur_toggled.emit(self.face_blur_check.isChecked()))
        layout.addWidget(self.face_blur_check)
        
        # Blur strength
        blur_layout = QHBoxLayout()
        blur_layout.addWidget(QLabel("Blur Gücü:"))
        self.face_blur_slider = QSlider(Qt.Horizontal)
        self.face_blur_slider.setRange(1, 49)
        self.face_blur_slider.setValue(21)
        self.face_blur_slider.setSingleStep(2)
        self.face_blur_slider.valueChanged.connect(self.on_face_blur_changed)
        blur_layout.addWidget(self.face_blur_slider)
        self.face_blur_label = QLabel("21")
        self.face_blur_label.setMinimumWidth(30)
        blur_layout.addWidget(self.face_blur_label)
        layout.addLayout(blur_layout)
                # Sentiment analysis
        self.sentiment_check = QCheckBox("Duygu Analizi")
        self.sentiment_check.stateChanged.connect(
            lambda: self.face_sentiment_toggled.emit(self.sentiment_check.isChecked()))
        layout.addWidget(self.sentiment_check)
        
        # Show sentiment emoji
        self.sentiment_emoji_check = QCheckBox("Duygu Emoji G\u00f6ster")
        self.sentiment_emoji_check.setChecked(True)
        self.sentiment_emoji_check.stateChanged.connect(
            lambda: self.face_sentiment_emoji_toggled.emit(self.sentiment_emoji_check.isChecked()))
        layout.addWidget(self.sentiment_emoji_check)
        
        return group
        
    def _create_color_filter_controls(self):
        """Create color filter control group"""
        group = QGroupBox("Renk Filtreleri")
        layout = QVBoxLayout(group)
        
        # Filter selection
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filtre:"))
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItem("Yok", None)
        self.filter_combo.addItem("Sepia", "sepia")
        self.filter_combo.addItem("Siyah-Beyaz", "grayscale")
        self.filter_combo.addItem("Negatif", "negative")
        self.filter_combo.addItem("Vintage", "vintage")
        self.filter_combo.addItem("Soğuk Ton", "cool")
        self.filter_combo.addItem("Sıcak Ton", "warm")
        self.filter_combo.addItem("Yüksek Kontrast", "high_contrast")
        self.filter_combo.addItem("Canlı", "vibrant")
        self.filter_combo.addItem("İkili (B&W)", "black_and_white")
        self.filter_combo.currentIndexChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(self.filter_combo)
        layout.addLayout(filter_layout)
        
        # Filter intensity
        intensity_layout = QHBoxLayout()
        intensity_layout.addWidget(QLabel("Yoğunluk:"))
        self.filter_intensity_slider = QSlider(Qt.Horizontal)
        self.filter_intensity_slider.setRange(0, 100)
        self.filter_intensity_slider.setValue(100)
        self.filter_intensity_slider.valueChanged.connect(self.on_filter_changed)
        intensity_layout.addWidget(self.filter_intensity_slider)
        self.filter_intensity_label = QLabel("100%")
        self.filter_intensity_label.setMinimumWidth(40)
        intensity_layout.addWidget(self.filter_intensity_label)
        layout.addLayout(intensity_layout)
        
        return group
        
    def on_face_blur_changed(self, value):
        """Handle face blur strength slider"""
        # Ensure odd number
        if value % 2 == 0:
            value += 1
            self.face_blur_slider.setValue(value)
        self.face_blur_label.setText(str(value))
        self.face_blur_strength_changed.emit(value)
        
    def on_filter_changed(self):
        """Handle filter selection or intensity change"""
        filter_name = self.filter_combo.currentData()
        intensity = self.filter_intensity_slider.value() / 100.0
        self.filter_intensity_label.setText(f"{int(intensity * 100)}%")
        self.color_filter_changed.emit(filter_name if filter_name else "", intensity)
