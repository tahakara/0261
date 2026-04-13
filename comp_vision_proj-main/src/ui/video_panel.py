from typing import Optional, List, Tuple
import os
import time
import subprocess
import shutil
import cv2
import numpy as np

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtCore import QEvent, QPoint
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QSlider, QCheckBox, QFileDialog, QFrame, QSpinBox, QLineEdit,
    QInputDialog, QColorDialog, QFontDialog
)
from PySide6.QtGui import QImage, QPixmap, QPainter, QFont, QColor, QFontMetrics


class VideoPanel(QFrame):
    """Live video panel with camera, recording, filters, overlays, and face blur."""

    error_signal = Signal(str)
    overlays_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setStyleSheet(
            """
            VideoPanel { background-color: #1e1e1e; border: none; }
            QLabel#videoLabel { background-color: #000000; border: 1px solid #3c3c3c; }
            QPushButton { background-color: #3c3c3c; color: #cccccc; border: none; border-radius: 4px; padding: 6px; }
            QPushButton:hover { background-color: #4a4a4a; }
            QSlider::groove:horizontal { background: #3c3c3c; height: 6px; border-radius: 3px; }
            QSlider::handle:horizontal { background: #0078d4; width: 14px; height: 14px; margin: -4px 0; border-radius: 7px; }
            QSlider::sub-page:horizontal { background: #0078d4; border-radius: 3px; }
            QComboBox { background-color: #3c3c3c; color: #cccccc; border: 1px solid #4a4a4a; border-radius: 4px; padding: 4px 8px; }
            QCheckBox { color: #cccccc; }
            QLabel { color: #cccccc; }
            """
        )

        self._cap: Optional[cv2.VideoCapture] = None
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_frame)
        self._writer: Optional[cv2.VideoWriter] = None
        self._recording = False
        self._record_path: Optional[str] = None
        self._frame_size: Optional[Tuple[int, int]] = None
        self._frame_count = 0
        self._faces_enabled = False
        self._blur_faces = False
        self._face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self._face_id_counter = 0
        self._last_faces: List[Tuple[int, int, int, int, int]] = []  # (x,y,w,h,id)

        # Processing parameters
        self._flip_h = False
        self._flip_v = False
        self._brightness = 0  # [-100, 100]
        self._contrast = 0    # [-100, 100]
        self._saturation = 0  # [-100, 100]
        self._blur_amount = 0 # [0, 50]
        self._denoise_strength = 0 # [0, 100]
        self._color_temp = 0  # [-100 cool, +100 warm]
        self._filter = 'None'

        # UI
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(8)

        # Video area
        self._video_label = QLabel()
        self._video_label.setObjectName('videoLabel')
        self._video_label.setMinimumHeight(360)
        from PySide6.QtWidgets import QSizePolicy as QSP
        self._video_label.setSizePolicy(QSP.Expanding, QSP.Expanding)
        self._video_label.setAlignment(Qt.AlignCenter)
        root.addWidget(self._video_label, stretch=1)
        # Recording overlay indicator on the video area
        self._rec_label = QLabel('REC', self._video_label)
        self._rec_label.setStyleSheet(
            "background-color: rgba(0,0,0,120); color: #ff3b3b;"
            "padding: 2px 6px; border-radius: 4px; font-weight: bold;"
        )
        try:
            self._rec_label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        except Exception:
            pass
        self._rec_label.hide()

        # Controls container (scrollable for small screens)
        from PySide6.QtWidgets import QScrollArea
        self._controls_scroll = QScrollArea()
        self._controls_scroll.setWidgetResizable(True)
        self._controls_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._controls_container = QWidget()
        self._controls_layout = QVBoxLayout(self._controls_container)
        self._controls_layout.setContentsMargins(0, 0, 0, 0)
        self._controls_layout.setSpacing(8)
        self._controls_scroll.setWidget(self._controls_container)
        root.addWidget(self._controls_scroll, stretch=0)

        # For responsive label widths
        self._responsive_labels: list[QLabel] = []

        # Controls row 1: camera & recording
        row1 = QHBoxLayout()
        self._btn_start_cam = QPushButton('Start Camera')
        self._btn_stop_cam = QPushButton('Stop Camera')
        self._btn_start_rec = QPushButton('Start Recording')
        self._btn_stop_rec = QPushButton('Stop Recording')
        self._btn_snapshot = QPushButton('Snapshot')
        # Recording elapsed time label (shown during recording)
        self._lbl_rec_elapsed = QLabel('00:00')
        try:
            self._lbl_rec_elapsed.setStyleSheet('color: #ff3b3b; font-weight: bold;')
        except Exception:
            pass
        self._lbl_rec_elapsed.hide()
        # Codec selection
        lbl_codec = QLabel('Codec:')
        self._responsive_labels.append(lbl_codec)
        self._codec_combo = QComboBox()
        self._codec_combo.addItems([
            'MP4 (mp4v)',
            'XVID (avi)',
            'MJPEG (avi)',
            'FFmpeg H.264 (mp4)',
            'FFmpeg H.265 (mp4)'
        ])
        # Camera index selector
        lbl_cam = QLabel('Camera:')
        self._responsive_labels.append(lbl_cam)
        self._camera_combo = QComboBox()
        self._camera_combo.addItems(['Auto', '0', '1', '2', '3', '4', '5'])
        row1.addWidget(lbl_cam)
        row1.addWidget(self._camera_combo)
        row1.addWidget(self._btn_start_cam)
        row1.addWidget(self._btn_stop_cam)
        row1.addStretch()
        row1.addWidget(self._btn_start_rec)
        row1.addWidget(self._lbl_rec_elapsed)
        row1.addWidget(self._btn_stop_rec)
        row1.addWidget(self._btn_snapshot)
        row1.addStretch()
        row1.addWidget(lbl_codec)
        row1.addWidget(self._codec_combo)
        # Target FPS control
        lbl_fps = QLabel('FPS:')
        self._responsive_labels.append(lbl_fps)
        self._fps_spin = QSpinBox()
        self._fps_spin.setRange(5, 60)
        self._fps_spin.setValue(30)
        row1.addWidget(lbl_fps)
        row1.addWidget(self._fps_spin)
        self._controls_layout.addLayout(row1)

        # Controls row 2: face detection & flip
        row2 = QHBoxLayout()
        self._chk_faces = QCheckBox('Detect Faces')
        self._chk_blur_faces = QCheckBox('Blur Faces')
        self._chk_face_emoji = QCheckBox('Emoji on Face')
        self._btn_face_emoji_pick = QPushButton('Pick Emoji Image')
        self._chk_flip_h = QCheckBox('Flip Horizontal')
        self._chk_flip_v = QCheckBox('Flip Vertical')
        row2.addWidget(self._chk_faces)
        row2.addWidget(self._chk_blur_faces)
        row2.addWidget(self._chk_face_emoji)
        row2.addWidget(self._btn_face_emoji_pick)
        row2.addStretch()
        row2.addWidget(self._chk_flip_h)
        row2.addWidget(self._chk_flip_v)
        self._controls_layout.addLayout(row2)
        # Hint note under face emoji controls
        try:
            self._lbl_face_emoji_hint = QLabel("Emoji'nin yüzlerde görünmesi için 'Detect Faces' etkin olmalı, Blur Face etkin olmamalıdır olmalıdır.")
            self._lbl_face_emoji_hint.setStyleSheet('color: #aaaaaa; font-size: 11px;')
            self._lbl_face_emoji_hint.hide()
            # also provide a tooltip on the pick button
            self._btn_face_emoji_pick.setToolTip("Yüzlere emoji yerleştirmek için 'Detect Faces' aktif olmalı.")
            self._controls_layout.addWidget(self._lbl_face_emoji_hint)
        except Exception:
            pass

        # Controls row 3: filter & color temperature
        row3 = QHBoxLayout()
        lbl_filter = QLabel('Filter:')
        self._responsive_labels.append(lbl_filter)
        row3.addWidget(lbl_filter)
        self._filter_combo = QComboBox()
        self._filter_combo.addItems([
            'None', 'Grayscale', 'Red', 'Green', 'Blue',
            'Red+Green', 'Red+Blue', 'Green+Blue'
        ])
        row3.addWidget(self._filter_combo)
        row3.addStretch()
        lbl_temp = QLabel('Color Temp')
        self._responsive_labels.append(lbl_temp)
        row3.addWidget(lbl_temp)
        self._temp_slider = QSlider(Qt.Horizontal)
        self._temp_slider.setRange(-100, 100)
        self._temp_slider.setValue(0)
        row3.addWidget(self._temp_slider)
        self._controls_layout.addLayout(row3)

        # Controls grid: adjustments (limited to ~50% width)
        self._adjustments_container = QWidget()
        adj_grid = QVBoxLayout(self._adjustments_container)
        def add_slider(label_text: str, rng: Tuple[int,int], initial: int) -> QSlider:
            h = QHBoxLayout()
            lbl = QLabel(label_text)
            lbl.setFixedWidth(90)
            self._responsive_labels.append(lbl)
            h.addWidget(lbl)
            sl = QSlider(Qt.Horizontal)
            sl.setRange(rng[0], rng[1])
            sl.setValue(initial)
            h.addWidget(sl)
            adj_grid.addLayout(h)
            return sl

        # Limit Brightness/Contrast to ±50
        self._brightness_slider = add_slider('Brightness', (-50, 50), 0)
        self._contrast_slider   = add_slider('Contrast',   (-50, 50), 0)
        self._saturation_slider = add_slider('Saturation', (-100, 100), 0)
        self._noise_slider      = add_slider('Noise',       (0, 100), 0)
        self._blur_slider       = add_slider('Blur',       (0, 50), 0)
        # Blur type selection
        h_blurtype = QHBoxLayout()
        lbl_bt = QLabel('Blur Type')
        lbl_bt.setFixedWidth(90)
        self._responsive_labels.append(lbl_bt)
        h_blurtype.addWidget(lbl_bt)
        self._blur_type_combo = QComboBox()
        self._blur_type_combo.addItems(['Gaussian', 'Box', 'Median'])
        h_blurtype.addWidget(self._blur_type_combo)
        adj_grid.addLayout(h_blurtype)
        self._denoise_slider    = add_slider('Denoise',    (0, 100), 0)
        wrap_adj = QHBoxLayout()
        wrap_adj.addWidget(self._adjustments_container)
        wrap_adj.addStretch()
        self._controls_layout.addLayout(wrap_adj)

        # Overlay controls
        # Overlay controls (wrap in container to limit width)
        self._overlay_controls_container = QWidget()
        overlay_box = QVBoxLayout(self._overlay_controls_container)
        lbl_overlay = QLabel('Overlay Image (Layer over video)')
        self._responsive_labels.append(lbl_overlay)
        overlay_box.addWidget(lbl_overlay)
        ol_row1 = QHBoxLayout()
        self._btn_overlay_add = QPushButton('Add Overlay')
        self._btn_overlay_clear = QPushButton('Clear Overlay')
        self._chk_overlay_lock = QCheckBox('Lock Overlay')
        ol_row1.addWidget(self._btn_overlay_add)
        ol_row1.addWidget(self._btn_overlay_clear)
        ol_row1.addStretch()
        ol_row1.addWidget(self._chk_overlay_lock)
        overlay_box.addLayout(ol_row1)

        # Text overlay controls
        lbl_text_overlay = QLabel('Text Overlay')
        self._responsive_labels.append(lbl_text_overlay)
        overlay_box.addWidget(lbl_text_overlay)
        text_row1 = QHBoxLayout()
        self._text_overlay_input = QLineEdit()
        self._text_overlay_input.setPlaceholderText('Enter text to overlay...')
        self._btn_text_add = QPushButton('Add Text')
        text_row1.addWidget(self._text_overlay_input)
        text_row1.addWidget(self._btn_text_add)
        overlay_box.addLayout(text_row1)

        text_row2 = QHBoxLayout()
        lbl_text_color = QLabel('Text Color')
        self._responsive_labels.append(lbl_text_color)
        self._btn_text_color = QPushButton('Select Color')
        self._btn_text_color.setStyleSheet('background-color: #ffffff; color: #000000;')
        text_row2.addWidget(lbl_text_color)
        text_row2.addWidget(self._btn_text_color)
        lbl_text_size = QLabel('Size')
        self._responsive_labels.append(lbl_text_size)
        self._text_size_spin = QSpinBox()
        self._text_size_spin.setRange(10, 200)
        self._text_size_spin.setValue(64)
        text_row2.addWidget(lbl_text_size)
        text_row2.addWidget(self._text_size_spin)
        text_row2.addStretch()
        overlay_box.addLayout(text_row2)

        text_row3 = QHBoxLayout()
        lbl_text_font = QLabel('Font')
        self._responsive_labels.append(lbl_text_font)
        self._text_font_combo = QComboBox()
        self._text_font_combo.addItems([
            'Segoe UI', 'Arial', 'Times New Roman', 'Courier New',
            'Verdana', 'Georgia', 'Comic Sans MS', 'Trebuchet MS'
        ])
        self._text_font_combo.setCurrentText('Segoe UI')
        text_row3.addWidget(lbl_text_font)
        text_row3.addWidget(self._text_font_combo)
        text_row3.addStretch()
        overlay_box.addLayout(text_row3)

        def add_spin(label_text: str, rng: Tuple[int,int], initial: int, step: int = 1) -> QSpinBox:
            h = QHBoxLayout()
            lbl = QLabel(label_text)
            lbl.setFixedWidth(90)
            self._responsive_labels.append(lbl)
            h.addWidget(lbl)
            sp = QSpinBox()
            sp.setRange(rng[0], rng[1])
            sp.setSingleStep(step)
            sp.setValue(initial)
            h.addWidget(sp)
            overlay_box.addLayout(h)
            return sp

        self._overlay_pos_x = add_spin('Pos X', (-2000, 2000), 100, 5)
        self._overlay_pos_y = add_spin('Pos Y', (-2000, 2000), 100, 5)
        self._overlay_scale_spin = add_spin('Scale x100', (10, 500), 100, 5)  # 100 = 1.0
        self._overlay_rot_spin = add_spin('Rotation', (-180, 180), 0, 5)
        self._overlay_crop_l = add_spin('Crop Left', (0, 2000), 0, 5)
        self._overlay_crop_t = add_spin('Crop Top', (0, 2000), 0, 5)
        self._overlay_crop_r = add_spin('Crop Right', (0, 2000), 0, 5)
        self._overlay_crop_b = add_spin('Crop Bottom', (0, 2000), 0, 5)

        wrap_overlay = QHBoxLayout()
        wrap_overlay.addWidget(self._overlay_controls_container)
        wrap_overlay.addStretch()
        self._controls_layout.addLayout(wrap_overlay)

        # Wire events
        self._btn_start_cam.clicked.connect(self.start_camera)
        self._btn_stop_cam.clicked.connect(self.stop_camera)
        self._btn_start_rec.clicked.connect(self.start_recording)
        self._btn_stop_rec.clicked.connect(self.stop_recording)
        self._btn_snapshot.clicked.connect(self.snapshot)
        self._chk_faces.toggled.connect(self._on_faces_toggle)
        self._chk_blur_faces.toggled.connect(self._on_blur_faces_toggle)
        self._chk_flip_h.toggled.connect(lambda v: setattr(self, '_flip_h', v))
        self._chk_flip_v.toggled.connect(lambda v: setattr(self, '_flip_v', v))
        self._filter_combo.currentTextChanged.connect(lambda t: setattr(self, '_filter', t))
        self._temp_slider.valueChanged.connect(lambda v: setattr(self, '_color_temp', v))
        self._brightness_slider.valueChanged.connect(lambda v: setattr(self, '_brightness', v))
        self._contrast_slider.valueChanged.connect(lambda v: setattr(self, '_contrast', v))
        self._saturation_slider.valueChanged.connect(lambda v: setattr(self, '_saturation', v))
        self._blur_slider.valueChanged.connect(lambda v: setattr(self, '_blur_amount', v))
        self._denoise_slider.valueChanged.connect(lambda v: setattr(self, '_denoise_strength', v))
        self._noise_slider.valueChanged.connect(lambda v: setattr(self, '_noise_amount', v))
        self._blur_type_combo.currentTextChanged.connect(lambda t: setattr(self, '_blur_type', t))
        self._fps_spin.valueChanged.connect(self._on_fps_changed)

        # Overlay wiring
        self._btn_overlay_add.clicked.connect(self._on_overlay_add)
        self._btn_overlay_clear.clicked.connect(self._on_overlay_clear)
        self._chk_overlay_lock.toggled.connect(lambda v: setattr(self, '_overlay_locked', v))
        self._overlay_pos_x.valueChanged.connect(self._on_overlay_params_changed)
        self._overlay_pos_y.valueChanged.connect(self._on_overlay_params_changed)
        self._overlay_scale_spin.valueChanged.connect(self._on_overlay_params_changed)
        self._overlay_rot_spin.valueChanged.connect(self._on_overlay_params_changed)
        self._overlay_crop_l.valueChanged.connect(self._on_overlay_params_changed)
        self._overlay_crop_t.valueChanged.connect(self._on_overlay_params_changed)
        self._overlay_crop_r.valueChanged.connect(self._on_overlay_params_changed)
        self._overlay_crop_b.valueChanged.connect(self._on_overlay_params_changed)
        # Text overlay wiring
        self._btn_text_add.clicked.connect(self._on_text_overlay_add)
        self._btn_text_color.clicked.connect(self._on_text_color_changed)
        self._text_size_spin.valueChanged.connect(self._on_text_size_changed)
        self._text_font_combo.currentTextChanged.connect(self._on_text_font_changed)
        # Emoji wiring
        self._chk_face_emoji.toggled.connect(lambda v: setattr(self, '_face_emoji_enabled', v))
        self._btn_face_emoji_pick.clicked.connect(self._on_face_emoji_pick)

        # Overlay state (multiple overlays)
        self._overlays: list = []
        self._active_overlay: int = -1
        self._overlay_locked: bool = False

        # Text overlay state
        self._text_color: Tuple[int, int, int] = (255, 255, 255)  # RGB white
        self._text_size: int = 64
        self._text_font: str = 'Segoe UI'

        # Recording via ffmpeg
        self._ffmpeg_proc: Optional[subprocess.Popen] = None

        # Disable wheel on overlay controls
        self._no_wheel_widgets: List[QWidget] = []
        for sp in (self._overlay_pos_x, self._overlay_pos_y, self._overlay_scale_spin,
                   self._overlay_rot_spin, self._overlay_crop_l, self._overlay_crop_t,
                   self._overlay_crop_r, self._overlay_crop_b):
            try:
                sp.installEventFilter(self)
                self._no_wheel_widgets.append(sp)
            except Exception:
                pass

        # Initial responsive setup
        self._update_responsive_layout()

        # Mouse interaction state
        self._display_scale: float = 1.0
        self._display_offset: Tuple[int, int] = (0, 0)
        self._interaction_mode: str = 'none'  # 'move'|'scale'|'rotate'|'none'
        self._drag_start_pos: Optional[QPoint] = None
        self._drag_start_params: dict = {}
        self._last_overlay_bbox_disp: Optional[Tuple[int,int,int,int]] = None

        # Receive mouse on video label
        self._video_label.setMouseTracking(True)
        self._video_label.installEventFilter(self)

        # Defaults
        self._noise_amount = 0
        self._blur_type = 'Gaussian'
        self._target_fps = 30
        # Text overlay defaults
        self._default_font_family = 'Segoe UI'
        self._default_font_size = 64
        # Drawing defaults
        self._draw_enabled = False
        self._draw_tool = 'pen'  # pen|brush|rect|ellipse|line
        self._draw_color = (0, 255, 0)
        self._draw_fill = True
        self._draw_thickness = 3
        self._draw_layer: Optional[np.ndarray] = None
        self._draw_start: Optional[QPoint] = None
        self._draw_last_point: Optional[QPoint] = None
        # Face emoji
        self._face_emoji_enabled = False
        self._face_emoji_img: Optional[np.ndarray] = None
        self._record_start_ts: Optional[float] = None

    # Camera control
    def start_camera(self, index: int = 0):
        try:
            # Ensure previous state is clean
            try:
                self._timer.stop()
            except Exception:
                pass
            if self._cap is not None:
                try:
                    self._cap.release()
                except Exception:
                    pass
                self._cap = None

            # Resolve selected camera index
            try:
                sel = self._camera_combo.currentText()
                if sel and sel.lower() != 'auto':
                    index = int(sel)
            except Exception:
                pass

            # Try indices without specifying backend to avoid overload issues
            opened = False
            tried: List[int] = []
            def try_open(idx: int) -> bool:
                nonlocal opened, index
                tried.append(idx)
                try:
                    cap = cv2.VideoCapture(idx)
                except Exception:
                    cap = None
                if cap is not None and cap.isOpened():
                    # Set common properties (best-effort)
                    try:
                        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                        cap.set(cv2.CAP_PROP_FPS, 30)
                    except Exception:
                        pass
                    # Sanity: read one frame
                    ok, _test = cap.read()
                    if ok:
                        self._cap = cap
                        opened = True
                        index = idx
                        return True
                    # If read fails, release and continue
                    try:
                        cap.release()
                    except Exception:
                        pass
                return False

            # First attempt: requested index
            try_open(index)
            # Fallback: scan indices 0..10 if not opened
            if not opened:
                for idx in range(0, 11):
                    if try_open(idx):
                        break

            if not opened:
                self.error_signal.emit(f"Camera could not be opened. Tried indices -> {', '.join(str(i) for i in tried)}")
                self._cap = None
                return

            w = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            if not w or not h:
                w, h = 1280, 720
            self._frame_size = (w, h)
            self._frame_count = 0
            interval = max(10, int(1000 / max(5, min(self._target_fps, 60))))
            self._timer.start(interval)
        except Exception as e:
            self.error_signal.emit(str(e))

    def stop_camera(self):
        try:
            self._timer.stop()
        except Exception:
            pass
        if self._cap is not None:
            try:
                self._cap.release()
            except Exception:
                pass
            self._cap = None
        # Reset frame size/count
        self._frame_size = None
        self._frame_count = 0

    def _on_fps_changed(self, value: int):
        try:
            self._target_fps = int(value)
            if self._timer.isActive():
                interval = max(10, int(1000 / max(5, min(self._target_fps, 60))))
                self._timer.start(interval)
        except Exception:
            pass

    # Recording
    def start_recording(self):
        if self._cap is None or self._frame_size is None:
            self.error_signal.emit('Start camera before recording')
            return
        ts = time.strftime('%Y%m%d_%H%M%S')
        default_dir = os.path.join(os.path.expanduser('~'), 'Videos')
        os.makedirs(default_dir, exist_ok=True)
        codec_text = self._codec_combo.currentText()
        use_ffmpeg = codec_text.startswith('FFmpeg')
        ext = 'mp4' if 'mp4' in codec_text.lower() else ('avi' if 'avi' in codec_text.lower() else 'mp4')
        out_path = os.path.join(default_dir, f'record_{ts}.{ext}')
        if use_ffmpeg:
            codec_lib = 'libx264' if 'H.264' in codec_text else 'libx265'
            try:
                self._record_path = out_path
                self._start_ffmpeg_recording(out_path, self._frame_size[0], self._frame_size[1], 30, codec_lib)
                self._recording = True
                self._rec_label.show()
                # UI: mark recording state
                try:
                    self._record_start_ts = time.monotonic()
                    self._lbl_rec_elapsed.show()
                    self._btn_start_rec.setStyleSheet(
                        'QPushButton { background-color: #3c3c3c; color: #cccccc; border: 2px solid #ff3b3b; border-radius: 4px; padding: 6px; }'
                        'QPushButton:hover { background-color: #4a4a4a; border-color: #ff6b6b; }'
                    )
                except Exception:
                    pass
                return
            except Exception as e:
                self.error_signal.emit(f'FFmpeg start failed, falling back: {e}')
        # Fallback to OpenCV writer
        if 'XVID' in codec_text:
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
        elif 'MJPEG' in codec_text:
            fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        else:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self._writer = cv2.VideoWriter(out_path, fourcc, 30.0, self._frame_size)
        if hasattr(self._writer, 'isOpened') and not self._writer.isOpened():
            self.error_signal.emit('OpenCV writer failed to open output file')
            try:
                self._writer.release()
            except Exception:
                pass
            self._writer = None
            self._recording = False
            self._record_path = None
        else:
            self._recording = True
            self._record_path = out_path
            self._rec_label.show()
            # UI: mark recording state
            try:
                self._record_start_ts = time.monotonic()
                self._lbl_rec_elapsed.show()
                self._btn_start_rec.setStyleSheet(
                    'QPushButton { background-color: #3c3c3c; color: #cccccc; border: 2px solid #ff3b3b; border-radius: 4px; padding: 6px; }'
                    'QPushButton:hover { background-color: #4a4a4a; border-color: #ff6b6b; }'
                )
            except Exception:
                pass

    def stop_recording(self):
        self._recording = False
        if self._writer is not None:
            self._writer.release()
            self._writer = None
        if self._ffmpeg_proc is not None:
            try:
                self._ffmpeg_proc.stdin.flush()
                self._ffmpeg_proc.stdin.close()
                self._ffmpeg_proc.wait(timeout=5)
            except Exception:
                pass
            self._ffmpeg_proc = None
        try:
            self._rec_label.hide()
        except Exception:
            pass
        # Reset UI for recording state
        try:
            self._record_start_ts = None
            self._lbl_rec_elapsed.hide()
            self._lbl_rec_elapsed.setText('00:00')
            self._btn_start_rec.setStyleSheet('')
        except Exception:
            pass
        # Prompt for destination folder and move recorded file if exists
        try:
            if self._record_path and os.path.isfile(self._record_path):
                default_dir = os.path.dirname(self._record_path)
                target_dir = QFileDialog.getExistingDirectory(self, 'Select Save Folder', default_dir)
                if target_dir:
                    src = self._record_path
                    dest = os.path.join(target_dir, os.path.basename(src))
                    if os.path.abspath(src) != os.path.abspath(dest):
                        try:
                            shutil.move(src, dest)
                            self._record_path = dest
                        except Exception as e:
                            self.error_signal.emit(f'Failed to move file: {e}')
        except Exception:
            pass

    def snapshot(self):
        pix = self._video_label.pixmap()
        if not pix:
            return
        ts = time.strftime('%Y%m%d_%H%M%S')
        default_dir = os.path.join(os.path.expanduser('~'), 'Pictures')
        os.makedirs(default_dir, exist_ok=True)
        default_name = f'snapshot_{ts}.png'
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            'Save Snapshot',
            os.path.join(default_dir, default_name),
            'PNG (*.png);;JPEG (*.jpg);;BMP (*.bmp);;All Files (*)'
        )
        if file_path:
            pix.save(file_path)

    def _on_faces_toggle(self, enabled: bool):
        self._faces_enabled = enabled
        if not enabled:
            self._last_faces.clear()
            # Reset emoji
            self._face_emoji_enabled = False

    def _on_blur_faces_toggle(self, enabled: bool):
        self._blur_faces = enabled

    def _on_face_emoji_pick(self):
        try:
            fname, _ = QFileDialog.getOpenFileName(self, 'Pick Emoji Image', '', 'Images (*.png *.jpg *.jpeg *.bmp *.webp)')
            if not fname:
                return
            img = cv2.imread(fname, cv2.IMREAD_UNCHANGED)
            if img is None:
                self.error_signal.emit('Failed to load emoji image')
                return
            # Ensure BGRA
            if img.ndim == 2:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGRA)
            elif img.shape[2] == 3:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
            self._face_emoji_img = img
            self._face_emoji_enabled = True
            # Show reminder note below controls
            try:
                self._lbl_face_emoji_hint.show()
            except Exception:
                pass
        except Exception as e:
            self.error_signal.emit(str(e))

    # Frame update
    def _update_frame(self):
        if self._cap is None:
            return
        ok, frame = self._cap.read()
        if not ok:
            return

        # Process pipeline
        frame = self._apply_processing(frame)

        # Write to recorder
        if self._recording:
            if self._writer is not None:
                self._writer.write(frame)
            elif self._ffmpeg_proc is not None and self._ffmpeg_proc.stdin:
                try:
                    self._ffmpeg_proc.stdin.write(frame.tobytes())
                except Exception:
                    pass

        # Convert to QImage/QPixmap for display
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w = rgb.shape[:2]
        from PySide6.QtGui import QImage, QPixmap
        qimg = QImage(rgb.data, w, h, w * 3, QImage.Format_RGB888)
        # Compute scaling info for hit testing
        label_sz = self._video_label.size()
        scale = min(label_sz.width() / float(w), label_sz.height() / float(h)) if w and h else 1.0
        disp_w = int(w * scale)
        disp_h = int(h * scale)
        off_x = (label_sz.width() - disp_w) // 2
        off_y = (label_sz.height() - disp_h) // 2
        self._display_scale = scale
        self._display_offset = (off_x, off_y)
        self._video_label.setPixmap(QPixmap.fromImage(qimg).scaled(label_sz, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        # Position REC overlay if visible
        try:
            self._rec_label.adjustSize()
            self._rec_label.move(off_x + 8, off_y + 8)
            self._rec_label.raise_()
        except Exception:
            pass
        # Update elapsed time label if recording
        try:
            if self._recording and self._record_start_ts is not None:
                elapsed = int(time.monotonic() - self._record_start_ts)
                mm = elapsed // 60
                ss = elapsed % 60
                self._lbl_rec_elapsed.setText(f"{mm:02d}:{ss:02d}")
        except Exception:
            pass
        # Update elapsed time label if recording
        try:
            if self._recording and self._record_start_ts is not None:
                elapsed = int(time.monotonic() - self._record_start_ts)
                mm = elapsed // 60
                ss = elapsed % 60
                self._lbl_rec_elapsed.setText(f"{mm:02d}:{ss:02d}")
        except Exception:
            pass

    # Processing chain
    def _apply_processing(self, frame_bgr: np.ndarray) -> np.ndarray:
        img = frame_bgr.copy()

        # Flip
        if self._flip_h:
            img = cv2.flip(img, 1)
        if self._flip_v:
            img = cv2.flip(img, 0)

        # Brightness/Contrast using alpha/beta
        alpha = 1.0 + (self._contrast / 100.0)  # scale
        beta = self._brightness  # shift
        img = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)

        # Saturation
        if self._saturation != 0:
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
            s = hsv[:, :, 1]
            s = np.clip(s + (self._saturation * 255.0 / 100.0), 0, 255)
            hsv[:, :, 1] = s
            img = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

        # Intentional noise addition
        if getattr(self, '_noise_amount', 0) > 0:
            sigma = float(self._noise_amount)
            noise = np.random.normal(0.0, sigma, img.shape).astype(np.float32)
            img = np.clip(img.astype(np.float32) + noise, 0, 255).astype(np.uint8)

        # Global blur (types)
        if self._blur_amount > 0:
            k = max(1, self._blur_amount)
            if self._blur_type == 'Median':
                if k % 2 == 0:
                    k += 1
                img = cv2.medianBlur(img, k)
            elif self._blur_type == 'Box':
                img = cv2.blur(img, (k, k))
            else:  # Gaussian
                if k % 2 == 0:
                    k += 1
                img = cv2.GaussianBlur(img, (k, k), 0)

        # Denoise (bilateral filter)
        if self._denoise_strength > 0:
            d = 9
            sigma = self._denoise_strength
            img = cv2.bilateralFilter(img, d, sigma, sigma)

        # Color temperature: warm/cool by shifting channels
        if self._color_temp != 0:
            t = self._color_temp / 100.0
            # warm: increase R, decrease B; cool opposite
            b, g, r = cv2.split(img)
            if t > 0:
                offset = int(np.clip(40 * t, 0, 100))
                r = cv2.add(r, np.full_like(r, offset, dtype=r.dtype))
                b = cv2.subtract(b, np.full_like(b, offset, dtype=b.dtype))
            else:
                offset = int(np.clip(40 * -t, 0, 100))
                b = cv2.add(b, np.full_like(b, offset, dtype=b.dtype))
                r = cv2.subtract(r, np.full_like(r, offset, dtype=r.dtype))
            img = cv2.merge([b, g, r])

        # Filters
        img = self._apply_filter(img, self._filter)

        # Face detection and overlay
        if self._faces_enabled:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = self._face_cascade.detectMultiScale(gray, 1.2, 5, minSize=(40, 40))
            annotated = img.copy()
            new_faces = []
            fid = 0
            for (x, y, w, h) in faces:
                fid += 1
                new_faces.append((x, y, w, h, fid))
                # Blur ROI if enabled
                if self._blur_faces:
                    roi = annotated[y:y+h, x:x+w]
                    if roi.size > 0:
                        k = max(9, (w // 10) | 1)  # ensure odd
                        roi_blur = cv2.GaussianBlur(roi, (k, k), 0)
                        annotated[y:y+h, x:x+w] = roi_blur
                elif self._face_emoji_enabled and self._face_emoji_img is not None:
                    try:
                        # Resize emoji to face box and composite
                        em = self._face_emoji_img
                        eh, ew = em.shape[:2]
                        if ew > 0 and eh > 0:
                            em_res = cv2.resize(em, (w, h), interpolation=cv2.INTER_LINEAR)
                            annotated = self._composite_overlay(annotated, em_res, x, y)
                    except Exception:
                        pass
                # Draw rectangle and id label
                cv2.rectangle(annotated, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(annotated, f"ID {fid}", (x+4, y+16), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
            self._last_faces = new_faces
            img = annotated

        # Drawing layer compositing (above video, below overlays)
        if self._draw_layer is not None:
            try:
                img = self._composite_overlay(img, self._draw_layer, 0, 0)
            except Exception:
                pass

        # Overlay compositing (after other effects)
        if self._overlays:
            try:
                for idx, ov in enumerate(self._overlays):
                    if not ov.get('visible', True):
                        continue
                    
                    if ov.get('type') == 'text':
                        # Render text overlay
                        img = self._render_text_overlay(img, ov)
                        # Store bbox for active text overlay
                        if idx == self._active_overlay:
                            text_bbox = self._compute_text_bbox(ov)
                            if text_bbox:
                                self._last_overlay_bbox_disp = text_bbox
                    else:
                        # Render image overlay
                        overlay = self._compute_overlay_transformed_for(ov)
                        pos_x = int(ov.get('pos_x', 0))
                        pos_y = int(ov.get('pos_y', 0))
                        img = self._composite_overlay(img, overlay, pos_x, pos_y)
                        if idx == self._active_overlay:
                            oh, ow = overlay.shape[:2]
                            self._last_overlay_bbox_disp = (
                                int(self._display_offset[0] + pos_x * self._display_scale),
                                int(self._display_offset[1] + pos_y * self._display_scale),
                                int(ow * self._display_scale),
                                int(oh * self._display_scale)
                            )
                            try:
                                self._draw_overlay_handles(img, pos_x, pos_y, ow, oh)
                            except Exception:
                                pass
            except Exception:
                pass

        return img

    def _apply_filter(self, img: np.ndarray, name: str) -> np.ndarray:
        if name == 'None':
            return img
        if name == 'Grayscale':
            g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            return cv2.cvtColor(g, cv2.COLOR_GRAY2BGR)
        b, g, r = cv2.split(img)
        if name == 'Red':
            return cv2.merge([np.zeros_like(b), np.zeros_like(g), r])
        if name == 'Green':
            return cv2.merge([np.zeros_like(b), g, np.zeros_like(r)])
        if name == 'Blue':
            return cv2.merge([b, np.zeros_like(g), np.zeros_like(r)])
        if name == 'Red+Green':
            return cv2.merge([np.zeros_like(b), g, r])
        if name == 'Red+Blue':
            return cv2.merge([b, np.zeros_like(g), r])
        if name == 'Green+Blue':
            return cv2.merge([b, g, np.zeros_like(r)])
        return img

    # Lifecycle hooks for MainWindow
    def activate(self):
        # Called when mode switched to video
        pass

    def deactivate(self):
        # Called when leaving video mode
        self.stop_recording()
        self.stop_camera()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_responsive_layout()

    def _update_responsive_layout(self):
        w = self.width()
        compact = w < 900
        label_width = 70 if compact else 90
        spacing = 4 if compact else 8
        self._controls_layout.setSpacing(spacing)
        for lbl in self._responsive_labels:
            try:
                lbl.setFixedWidth(label_width)
            except Exception:
                pass
        # Video area height tuning
        self._video_label.setMinimumHeight(240 if compact else 360)
        # Limit overlay controls width to ~50% of panel
        try:
            max_w = max(240, int(w * 0.5))
            self._overlay_controls_container.setMaximumWidth(max_w)
            self._adjustments_container.setMaximumWidth(max_w)
        except Exception:
            pass
        # Limit adjustments width to ~50% of panel
        try:
            max_w = max(240, int(w * 0.5))
            self._adjustments_container.setMaximumWidth(max_w)
        except Exception:
            pass

    # Overlay helpers
    def _on_overlay_add(self):
        try:
            fname, _ = QFileDialog.getOpenFileName(self, 'Select Overlay Image', '', 'Images (*.png *.jpg *.jpeg *.bmp *.webp)')
            if not fname:
                return
            img = cv2.imread(fname, cv2.IMREAD_UNCHANGED)
            if img is None:
                self.error_signal.emit('Failed to load overlay image')
                return
            # Ensure BGRA
            if img.ndim == 2:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGRA)
            elif img.shape[2] == 3:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
            elif img.shape[2] == 4:
                pass
            else:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
            name = os.path.basename(fname)
            ov = {
                'type': 'image',
                'name': name,
                'image': img,
                'pos_x': self._overlay_pos_x.value(),
                'pos_y': self._overlay_pos_y.value(),
                'scale': self._overlay_scale_spin.value(),
                'rot': self._overlay_rot_spin.value(),
                'crop_l': self._overlay_crop_l.value(),
                'crop_t': self._overlay_crop_t.value(),
                'crop_r': self._overlay_crop_r.value(),
                'crop_b': self._overlay_crop_b.value(),
                'visible': True,
            }
            self._overlays.append(ov)
            self._active_overlay = len(self._overlays) - 1
            self.overlays_changed.emit()
        except Exception as e:
            self.error_signal.emit(str(e))

    def _on_overlay_clear(self):
        if 0 <= self._active_overlay < len(self._overlays):
            del self._overlays[self._active_overlay]
            self._active_overlay = min(self._active_overlay, len(self._overlays)-1)
            self.overlays_changed.emit()

    def _on_text_overlay_add(self):
        """Add a text overlay to the video."""
        text = self._text_overlay_input.text().strip()
        if not text:
            self.error_signal.emit('Please enter some text first')
            return
        
        try:
            # Create text overlay entry
            ov = {
                'type': 'text',
                'name': f'Text: {text[:20]}...' if len(text) > 20 else f'Text: {text}',
                'text': text,
                'color': self._text_color,  # RGB tuple
                'size': self._text_size,
                'font_family': self._text_font,
                'pos_x': 100,
                'pos_y': 100,
                'visible': True,
            }
            self._overlays.append(ov)
            self._active_overlay = len(self._overlays) - 1
            self._text_overlay_input.clear()  # Clear input after adding
            self.overlays_changed.emit()
        except Exception as e:
            self.error_signal.emit(f'Failed to add text overlay: {e}')

    def _on_text_color_changed(self):
        """Open color picker to change text color."""
        try:
            color_dialog = QColorDialog(self)
            # Convert from RGB to QColor
            r, g, b = self._text_color
            color_dialog.setCurrentColor(QColor(r, g, b))
            
            if color_dialog.exec() == QColorDialog.Accepted:
                qcolor = color_dialog.selectedColor()
                self._text_color = (qcolor.red(), qcolor.green(), qcolor.blue())
                # Update button color preview
                self._btn_text_color.setStyleSheet(
                    f'background-color: rgb({self._text_color[0]}, {self._text_color[1]}, {self._text_color[2]}); '
                    f'color: {"#000000" if sum(self._text_color) > 382 else "#ffffff"};'
                )
        except Exception as e:
            self.error_signal.emit(f'Color selection failed: {e}')

    def _on_text_size_changed(self):
        """Handle text size change."""
        try:
            self._text_size = self._text_size_spin.value()
        except Exception as e:
            self.error_signal.emit(f'Text size update failed: {e}')

    def _on_text_font_changed(self):
        """Handle text font change."""
        try:
            self._text_font = self._text_font_combo.currentText()
            # Update active text overlay's font if selected
            ov = self._current_overlay()
            if ov and ov.get('type') == 'text':
                ov['font_family'] = self._text_font
        except Exception as e:
            self.error_signal.emit(f'Text font update failed: {e}')

    def _compute_text_bbox(self, text_overlay: dict) -> Optional[Tuple[int, int, int, int]]:
        """Compute bounding box for text overlay in display coordinates."""
        try:
            text = text_overlay.get('text', '')
            if not text:
                return None
            
            font_size = text_overlay.get('size', 64)
            font_family = text_overlay.get('font_family', 'Segoe UI')
            pos_x = int(text_overlay.get('pos_x', 100))
            pos_y = int(text_overlay.get('pos_y', 100))
            
            # Map font family to OpenCV font
            font_map = {
                'Segoe UI': cv2.FONT_HERSHEY_SIMPLEX,
                'Arial': cv2.FONT_HERSHEY_SIMPLEX,
                'Times New Roman': cv2.FONT_HERSHEY_TRIPLEX,
                'Courier New': cv2.FONT_HERSHEY_COMPLEX,
                'Verdana': cv2.FONT_HERSHEY_SIMPLEX,
                'Georgia': cv2.FONT_HERSHEY_TRIPLEX,
                'Comic Sans MS': cv2.FONT_HERSHEY_PLAIN,
                'Trebuchet MS': cv2.FONT_HERSHEY_SIMPLEX,
            }
            
            font_face = font_map.get(font_family, cv2.FONT_HERSHEY_SIMPLEX)
            font_scale = max(0.5, font_size / 64.0)
            thickness = max(1, int(font_size / 32))
            
            # Get text size
            (text_w, text_h), baseline = cv2.getTextSize(text, font_face, font_scale, thickness)
            
            # Convert to display coordinates
            disp_x = int(self._display_offset[0] + pos_x * self._display_scale)
            disp_y = int(self._display_offset[1] + pos_y * self._display_scale)
            disp_w = int(text_w * self._display_scale)
            disp_h = int((text_h + baseline) * self._display_scale)
            
            return (disp_x, disp_y, disp_w, disp_h)
        except Exception:
            return None

    def _render_text_overlay(self, img: np.ndarray, text_overlay: dict) -> np.ndarray:
        """Render text overlay on the image."""
        try:
            text = text_overlay.get('text', '')
            if not text:
                return img
            
            color_rgb = text_overlay.get('color', (255, 255, 255))
            # Convert RGB to BGR for OpenCV
            color_bgr = (color_rgb[2], color_rgb[1], color_rgb[0])
            
            font_size = text_overlay.get('size', 64)
            font_family = text_overlay.get('font_family', 'Segoe UI')
            pos_x = int(text_overlay.get('pos_x', 100))
            pos_y = int(text_overlay.get('pos_y', 100))
            
            # Map font family to OpenCV font
            font_map = {
                'Segoe UI': cv2.FONT_HERSHEY_SIMPLEX,
                'Arial': cv2.FONT_HERSHEY_SIMPLEX,
                'Times New Roman': cv2.FONT_HERSHEY_TRIPLEX,
                'Courier New': cv2.FONT_HERSHEY_COMPLEX,
                'Verdana': cv2.FONT_HERSHEY_SIMPLEX,
                'Georgia': cv2.FONT_HERSHEY_TRIPLEX,
                'Comic Sans MS': cv2.FONT_HERSHEY_PLAIN,
                'Trebuchet MS': cv2.FONT_HERSHEY_SIMPLEX,
            }
            
            font_face = font_map.get(font_family, cv2.FONT_HERSHEY_SIMPLEX)
            font_scale = max(0.5, font_size / 64.0)  # Scale relative to default size
            thickness = max(1, int(font_size / 32))
            
            # Put text on image
            cv2.putText(img, text, (pos_x, pos_y), font_face, font_scale, color_bgr, thickness, cv2.LINE_AA)
            
            return img
        except Exception as e:
            print(f"Error rendering text overlay: {e}")
            return img

    def _on_overlay_params_changed(self, *args):
        ov = self._current_overlay()
        if ov is None:
            return
        if ov.get('type') == 'text':
            # Text overlays only have position
            ov['pos_x'] = self._overlay_pos_x.value()
            ov['pos_y'] = self._overlay_pos_y.value()
        else:
            # Image overlays have all parameters
            if self._overlay_locked:
                return
            ov['pos_x'] = self._overlay_pos_x.value()
            ov['pos_y'] = self._overlay_pos_y.value()
            ov['scale'] = self._overlay_scale_spin.value()
            ov['rot'] = self._overlay_rot_spin.value()
            ov['crop_l'] = self._overlay_crop_l.value()
            ov['crop_t'] = self._overlay_crop_t.value()
            ov['crop_r'] = self._overlay_crop_r.value()
            ov['crop_b'] = self._overlay_crop_b.value()

    def _compute_overlay_transformed_for(self, ov: dict) -> Optional[np.ndarray]:
        # Skip for text overlays (they are rendered directly)
        if ov.get('type') == 'text':
            return None
            
        # Resolve source image
        src = ov.get('image')
        if src is None:
            return None
        img = src.copy()
        h, w = img.shape[:2]
        # Crop margins
        l = max(0, min(int(ov['crop_l']), w-1))
        t = max(0, min(int(ov['crop_t']), h-1))
        r = max(0, min(int(ov['crop_r']), w-1))
        b = max(0, min(int(ov['crop_b']), h-1))
        x0 = l
        y0 = t
        x1 = max(x0+1, w - r)
        y1 = max(y0+1, h - b)
        img = img[y0:y1, x0:x1]
        if img.size == 0:
            return ov.get('image')

        # Scale
        scale = max(0.1, int(ov['scale']) / 100.0)
        new_w = max(1, int(img.shape[1] * scale))
        new_h = max(1, int(img.shape[0] * scale))
        img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

        # Rotate around center
        angle = float(ov['rot'])
        (h2, w2) = img.shape[:2]
        center = (w2 // 2, h2 // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        # compute new bounds
        cos = abs(M[0, 0])
        sin = abs(M[0, 1])
        nW = int((h2 * sin) + (w2 * cos))
        nH = int((h2 * cos) + (w2 * sin))
        M[0, 2] += (nW / 2) - center[0]
        M[1, 2] += (nH / 2) - center[1]
        img = cv2.warpAffine(img, M, (nW, nH), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_TRANSPARENT)
        return img

    def _composite_overlay(self, base_bgr: np.ndarray, overlay_bgra: np.ndarray, pos_x: int, pos_y: int) -> np.ndarray:
        out = base_bgr.copy()
        oh, ow = overlay_bgra.shape[:2]
        bh, bw = out.shape[:2]
        # target rect
        x0 = int(pos_x)
        y0 = int(pos_y)
        x1 = x0 + ow
        y1 = y0 + oh
        # Clip to base bounds
        if x1 <= 0 or y1 <= 0 or x0 >= bw or y0 >= bh:
            return out
        cx0 = max(0, x0)
        cy0 = max(0, y0)
        cx1 = min(bw, x1)
        cy1 = min(bh, y1)
        ox0 = cx0 - x0
        oy0 = cy0 - y0
        ox1 = ox0 + (cx1 - cx0)
        oy1 = oy0 + (cy1 - cy0)

        roi = out[cy0:cy1, cx0:cx1]
        ov = overlay_bgra[oy0:oy1, ox0:ox1]
        if ov.shape[2] == 4:
            alpha = ov[:, :, 3].astype(np.float32) / 255.0
            ov_bgr = ov[:, :, :3].astype(np.float32)
        else:
            alpha = np.ones((ov.shape[0], ov.shape[1]), dtype=np.float32)
            ov_bgr = ov.astype(np.float32)
        roi_f = roi.astype(np.float32)
        for c in range(3):
            roi_f[:, :, c] = roi_f[:, :, c] * (1.0 - alpha) + ov_bgr[:, :, c] * alpha
        out[cy0:cy1, cx0:cx1] = np.clip(roi_f, 0, 255).astype(np.uint8)
        return out

    def _draw_overlay_handles(self, img: np.ndarray, pos_x: int, pos_y: int, ow: int, oh: int):
        # Draw small squares at corners in image coordinates
        color = (255, 0, 0)  # BGR red
        size = 8
        pts = [(pos_x, pos_y), (pos_x+ow, pos_y), (pos_x, pos_y+oh), (pos_x+ow, pos_y+oh)]
        for (x, y) in pts:
            x0 = max(0, x - size)
            y0 = max(0, y - size)
            x1 = min(img.shape[1]-1, x + size)
            y1 = min(img.shape[0]-1, y + size)
            cv2.rectangle(img, (x0, y0), (x1, y1), color, 2)

        # Event filter for mouse interactions
    def eventFilter(self, obj, event):
        # Prevent wheel from changing overlay spinboxes while scrolling
        try:
            from PySide6.QtCore import QEvent as _QEvent
            if event.type() == _QEvent.Wheel and obj in getattr(self, '_no_wheel_widgets', []):
                return True
        except Exception:
            pass
        # Overlay interactions on video label
        if obj is self._video_label and len(self._overlays) > 0:
            if event.type() == QEvent.MouseButtonPress:
                return self._on_mouse_press(event)
            if event.type() == QEvent.MouseMove:
                return self._on_mouse_move(event)
            if event.type() == QEvent.MouseButtonRelease:
                return self._on_mouse_release(event)
        return super().eventFilter(obj, event)

    def _start_ffmpeg_recording(self, out_path: str, width: int, height: int, fps: int, codec: str):
        cmd = [
            'ffmpeg', '-y',
            '-f', 'rawvideo',
            '-pix_fmt', 'bgr24',
            '-s', f'{width}x{height}',
            '-r', str(fps),
            '-i', '-',
            '-c:v', codec,
            '-preset', 'veryfast',
            '-crf', '23',
            out_path
        ]
        self._ffmpeg_proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    def _hit_test(self, px: int, py: int) -> str:
        # Use display-space bbox
        if not self._last_overlay_bbox_disp:
            return 'none'
        x, y, w, h = self._last_overlay_bbox_disp
        
        # Check if it's a text overlay (no scale/rotate for text)
        ov = self._current_overlay()
        is_text = ov and ov.get('type') == 'text'
        
        # Handle areas (corners) - only for image overlays
        if not is_text:
            hs = 12  # pixels in display space
            corners = [
                (x, y), (x+w, y), (x, y+h), (x+w, y+h)
            ]
            for cx, cy in corners:
                if abs(px - cx) <= hs and abs(py - cy) <= hs:
                    return 'scale'
            # Rotation handle: above top center
            rx, ry = x + w//2, y - 24
            if abs(px - rx) <= hs and abs(py - ry) <= hs:
                return 'rotate'
        
        # Inside bbox -> move (for both text and image)
        if x <= px <= x+w and y <= py <= y+h:
            return 'move'
        return 'none'

    # Drawing handlers removed - no longer supported

    def _find_overlay_at_pos(self, px: int, py: int) -> int:
        """Find which overlay is at the given display position."""
        # Convert display coordinates to image coordinates
        if self._display_scale > 0:
            img_x = int((px - self._display_offset[0]) / self._display_scale)
            img_y = int((py - self._display_offset[1]) / self._display_scale)
        else:
            return -1
        
        # Check overlays in reverse order (top to bottom)
        for idx in range(len(self._overlays) - 1, -1, -1):
            ov = self._overlays[idx]
            if not ov.get('visible', True):
                continue
            
            if ov.get('type') == 'text':
                # For text, check if click is near the text position
                pos_x = int(ov.get('pos_x', 0))
                pos_y = int(ov.get('pos_y', 0))
                text = ov.get('text', '')
                
                # Simple check: is click within reasonable distance from text start?
                # Get text dimensions
                font_size = ov.get('size', 64)
                text_height = int(font_size * 1.5)  # Rough estimate
                text_width = len(text) * int(font_size * 0.6)  # Rough estimate
                
                if (pos_x <= img_x <= pos_x + text_width and 
                    pos_y - text_height <= img_y <= pos_y):
                    return idx
            else:
                # For image overlays, check bounding box
                pos_x = int(ov.get('pos_x', 0))
                pos_y = int(ov.get('pos_y', 0))
                # Rough check - image size not known here
                # Just check if near position
                if abs(img_x - pos_x) < 150 and abs(img_y - pos_y) < 150:
                    return idx
        
        return -1

    def _on_mouse_press(self, ev) -> bool:
        if self._overlay_locked:
            return False
        
        self._drag_start_pos = ev.position().toPoint()
        
        # First, find which overlay is at this position
        clicked_idx = self._find_overlay_at_pos(self._drag_start_pos.x(), self._drag_start_pos.y())
        
        if clicked_idx >= 0:
            # Set as active overlay
            self.set_active_overlay(clicked_idx)
        
        # Now check hit test with active overlay
        mode = self._hit_test(self._drag_start_pos.x(), self._drag_start_pos.y())
        if mode == 'none':
            return False
        self._interaction_mode = mode
        ov = self._current_overlay()
        if ov is None:
            return False
        # Snapshot starting params
        self._drag_start_params = {
            'pos_x': int(ov['pos_x']),
            'pos_y': int(ov['pos_y']),
        }
        # Only add scale/rot params for image overlays
        if ov.get('type') != 'text':
            self._drag_start_params.update({
                'scale': int(ov.get('scale', 100)),
                'rot': int(ov.get('rot', 0))
            })
        return True

    def _on_mouse_move(self, ev) -> bool:
        if self._interaction_mode == 'none' or self._drag_start_pos is None:
            return False
        
        ov = self._current_overlay()
        if ov is None:
            return False
            
        cur = ev.position().toPoint()
        dx = cur.x() - self._drag_start_pos.x()
        dy = cur.y() - self._drag_start_pos.y()
        
        # Convert display delta to image-space delta
        if self._interaction_mode == 'move':
            new_x = int(self._drag_start_params['pos_x'] + dx / self._display_scale)
            new_y = int(self._drag_start_params['pos_y'] + dy / self._display_scale)
            # Update both overlay data and spinner
            ov['pos_x'] = new_x
            ov['pos_y'] = new_y
            self._overlay_pos_x.blockSignals(True)
            self._overlay_pos_y.blockSignals(True)
            self._overlay_pos_x.setValue(new_x)
            self._overlay_pos_y.setValue(new_y)
            self._overlay_pos_x.blockSignals(False)
            self._overlay_pos_y.blockSignals(False)
        elif self._interaction_mode == 'scale':
            # Only for image overlays
            if 'scale' in self._drag_start_params:
                # Uniform scale based on horizontal drag amount
                delta = dx  # pixels in display
                new_scale = int(max(10, min(500, self._drag_start_params['scale'] + delta / 2)))
                ov['scale'] = new_scale
                self._overlay_scale_spin.blockSignals(True)
                self._overlay_scale_spin.setValue(new_scale)
                self._overlay_scale_spin.blockSignals(False)
        elif self._interaction_mode == 'rotate':
            # Only for image overlays
            if 'rot' in self._drag_start_params and self._last_overlay_bbox_disp:
                # Angle change based on mouse move around center in display space
                bx, by, bw, bh = self._last_overlay_bbox_disp
                cx = bx + bw/2
                cy = by + bh/2
                import math
                a0 = math.degrees(math.atan2(self._drag_start_pos.y() - cy, self._drag_start_pos.x() - cx))
                a1 = math.degrees(math.atan2(cur.y() - cy, cur.x() - cx))
                da = a1 - a0
                new_rot = int(self._drag_start_params['rot'] + da)
                ov['rot'] = new_rot
                self._overlay_rot_spin.blockSignals(True)
                self._overlay_rot_spin.setValue(new_rot)
                self._overlay_rot_spin.blockSignals(False)
        return True

    def _on_mouse_release(self, ev) -> bool:
        self._interaction_mode = 'none'
        self._drag_start_pos = None
        self._drag_start_params = {}
        return True

    # Overlay management API for RightSidebar
    def get_overlays(self) -> list:
        return [
            {'name': ov.get('name', f'Overlay {i+1}'), 'visible': ov.get('visible', True)}
            for i, ov in enumerate(self._overlays)
        ]

    def set_active_overlay(self, index: int):
        if 0 <= index < len(self._overlays):
            self._active_overlay = index
            ov = self._overlays[index]
            self._overlay_pos_x.setValue(int(ov['pos_x']))
            self._overlay_pos_y.setValue(int(ov['pos_y']))
            
            # Only load image overlay parameters if it's an image overlay
            if ov.get('type') != 'text':
                self._overlay_scale_spin.setValue(int(ov.get('scale', 100)))
                self._overlay_rot_spin.setValue(int(ov.get('rot', 0)))
                self._overlay_crop_l.setValue(int(ov.get('crop_l', 0)))
                self._overlay_crop_t.setValue(int(ov.get('crop_t', 0)))
                self._overlay_crop_r.setValue(int(ov.get('crop_r', 0)))
                self._overlay_crop_b.setValue(int(ov.get('crop_b', 0)))
            else:
                # For text overlays, update the text color, size, and font
                if 'color' in ov:
                    self._text_color = ov['color']
                    r, g, b = self._text_color
                    self._btn_text_color.setStyleSheet(
                        f'background-color: rgb({r}, {g}, {b}); '
                        f'color: {"#000000" if sum(self._text_color) > 382 else "#ffffff"};'
                    )
                if 'size' in ov:
                    self._text_size_spin.setValue(int(ov['size']))
                    self._text_size = ov['size']
                if 'font_family' in ov:
                    font_family = ov['font_family']
                    self._text_font = font_family
                    idx = self._text_font_combo.findText(font_family)
                    if idx >= 0:
                        self._text_font_combo.setCurrentIndex(idx)

    def set_overlay_visibility(self, index: int, visible: bool):
        if 0 <= index < len(self._overlays):
            self._overlays[index]['visible'] = visible
            self.overlays_changed.emit()

    def remove_overlay(self, index: int):
        if 0 <= index < len(self._overlays):
            del self._overlays[index]
            if self._active_overlay >= len(self._overlays):
                self._active_overlay = len(self._overlays) - 1
            self.overlays_changed.emit()

    def move_overlay_up(self, index: int):
        if 0 < index < len(self._overlays):
            self._overlays[index-1], self._overlays[index] = self._overlays[index], self._overlays[index-1]
            self._active_overlay = index-1 if self._active_overlay == index else self._active_overlay
            self.overlays_changed.emit()

    def move_overlay_down(self, index: int):
        if 0 <= index < len(self._overlays)-1:
            self._overlays[index+1], self._overlays[index] = self._overlays[index], self._overlays[index+1]
            self._active_overlay = index+1 if self._active_overlay == index else self._active_overlay
            self.overlays_changed.emit()

    def rename_overlay(self, index: int, new_name: str):
        if 0 <= index < len(self._overlays):
            self._overlays[index]['name'] = new_name
            self.overlays_changed.emit()

    # Text overlay functions removed - no longer supported

    def _current_overlay(self) -> Optional[dict]:
        if 0 <= self._active_overlay < len(self._overlays):
            return self._overlays[self._active_overlay]
        return None
