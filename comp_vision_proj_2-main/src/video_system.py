"""
Video System - Camera capture, recording, and frame processing
"""
from PySide6.QtCore import QTimer, Signal, QObject
from PySide6.QtGui import QImage
import cv2
import numpy as np
from datetime import datetime
from pathlib import Path
from src.face_detection import FaceDetectionSystem
from src.face_sentiment import FaceSentimentAnalyzer
from src.color_filters import ColorFilter


class VideoSystem(QObject):
    """Manages camera capture, recording, and video processing"""
    
    frame_ready = Signal(np.ndarray)  # Emits processed frame
    recording_status_changed = Signal(bool)  # True when recording starts, False when stops
    recording_duration_updated = Signal(int)  # Emits recording duration in seconds
    
    def __init__(self):
        super().__init__()
        
        # Camera
        self.camera = None
        self.camera_active = False
        self.camera_index = 0
        
        # Recording
        self.is_recording = False
        self.video_writer = None
        self.recording_start_time = None
        self.recording_output_path = None
        self.video_format = "mp4"  # Default format
        
        # Duration timer
        self.duration_timer = QTimer()
        self.duration_timer.timeout.connect(self._update_duration)
        
        # Current frame
        self.current_frame = None
        self.processed_frame = None
        
        # Overlay manager (will be set externally)
        self.overlay_manager = None
        
        # Face detection system
        self.face_detection = FaceDetectionSystem()
        
        # Face sentiment analyzer
        self.face_sentiment = FaceSentimentAnalyzer()
        
        # Color filter
        self.active_filter = None  # None or filter name
        self.filter_intensity = 1.0  # 0.0 to 1.0
        
        # Timer for frame capture
        self.timer = QTimer()
        self.timer.timeout.connect(self.capture_frame)
        self.fps = 25  # Reduced from 30 to 25 for better performance
        
        # Video effects settings
        self.brightness = 0  # -100 to 100
        self.heat_effect = 0  # 0 to 100
        self.denoise_strength = 0  # 0 to 10
        self.noise_strength = 0  # 0 to 100
        
        # RGB channel adjustments
        self.red_adjust = 0  # -100 to 100
        self.green_adjust = 0  # -100 to 100
        self.blue_adjust = 0  # -100 to 100
        
    def start_camera(self):
        """Start camera capture"""
        if self.camera_active:
            return True
            
        self.camera = cv2.VideoCapture(self.camera_index)
        if not self.camera.isOpened():
            return False
            
        self.camera_active = True
        self.timer.start(int(1000 / self.fps))
        return True
        
    def stop_camera(self):
        """Stop camera capture"""
        if not self.camera_active:
            return
            
        self.timer.stop()
        
        if self.is_recording:
            self.stop_recording()
            
        if self.camera:
            self.camera.release()
            self.camera = None
            
        self.camera_active = False
        self.current_frame = None
        self.processed_frame = None
        
    def capture_frame(self):
        """Capture and process a single frame"""
        if not self.camera or not self.camera_active:
            return
            
        ret, frame = self.camera.read()
        if not ret:
            return
            
        self.current_frame = frame.copy()
        
        # Apply effects
        self.processed_frame = self.apply_effects(frame)
        
        # Write to video if recording
        if self.is_recording and self.video_writer:
            self.video_writer.write(self.processed_frame)
            
        # Emit processed frame
        self.frame_ready.emit(self.processed_frame)
        
    def apply_effects(self, frame):
        """Apply all video effects to frame"""
        result = frame.copy()
        faces = []
        
        # Face detection (applied first)
        if self.face_detection.enabled:
            result, faces = self.face_detection.detect_faces(result)
        
        # Face sentiment analysis
        if self.face_sentiment.enabled and faces is not None and len(faces) > 0:
            result, sentiments = self.face_sentiment.analyze_sentiment(result, faces)
        
        # RGB channel adjustments
        if self.red_adjust != 0 or self.green_adjust != 0 or self.blue_adjust != 0:
            result = self._adjust_rgb_channels(result)
            
        # Brightness
        if self.brightness != 0:
            result = self._adjust_brightness(result)
            
        # Heat effect
        if self.heat_effect > 0:
            result = self._apply_heat_effect(result)
            
        # Denoise
        if self.denoise_strength > 0:
            result = self._apply_denoise(result)
            
        # Noise
        if self.noise_strength > 0:
            result = self._apply_noise(result)
            
        # Color filters
        if self.active_filter:
            result = self._apply_color_filter(result)
            
        # Apply overlays - only if overlays exist
        if self.overlay_manager and len(self.overlay_manager.overlays) > 0:
            result = self.overlay_manager.render_overlays(result)
            
        return result
        
    def _adjust_rgb_channels(self, frame):
        """Adjust individual RGB channels"""
        result = frame.astype(np.float32)
        
        # OpenCV uses BGR
        if self.blue_adjust != 0:
            result[:, :, 0] = np.clip(result[:, :, 0] + self.blue_adjust * 2.55, 0, 255)
        if self.green_adjust != 0:
            result[:, :, 1] = np.clip(result[:, :, 1] + self.green_adjust * 2.55, 0, 255)
        if self.red_adjust != 0:
            result[:, :, 2] = np.clip(result[:, :, 2] + self.red_adjust * 2.55, 0, 255)
            
        return result.astype(np.uint8)
        
    def _adjust_brightness(self, frame):
        """Adjust brightness"""
        value = int(self.brightness * 2.55)
        
        if value >= 0:
            return cv2.add(frame, np.array([value, value, value], dtype=np.uint8))
        else:
            return cv2.subtract(frame, np.array([-value, -value, -value], dtype=np.uint8))
            
    def _apply_heat_effect(self, frame):
        """Apply warm/heat color filter"""
        # Increase red and decrease blue for warm effect
        intensity = self.heat_effect / 100.0
        
        result = frame.astype(np.float32)
        result[:, :, 2] = np.clip(result[:, :, 2] * (1 + intensity * 0.3), 0, 255)  # Red
        result[:, :, 0] = np.clip(result[:, :, 0] * (1 - intensity * 0.2), 0, 255)  # Blue
        
        return result.astype(np.uint8)
        
    def _apply_denoise(self, frame):
        """Apply denoising filter"""
        # Use fastNlMeansDenoisingColored for color images
        # Reduce processing for better performance
        h = int(self.denoise_strength * 2)  # Reduced from 3 to 2
        return cv2.fastNlMeansDenoisingColored(frame, None, h, h, 3, 7)  # Reduced template and search window
        
    def _apply_noise(self, frame):
        """Add noise to frame"""
        intensity = self.noise_strength / 100.0
        noise = np.random.normal(0, 25 * intensity, frame.shape).astype(np.float32)
        
        noisy = frame.astype(np.float32) + noise
        return np.clip(noisy, 0, 255).astype(np.uint8)
        
    def start_recording(self, output_path: str, video_format: str = "mp4"):
        """Start recording video"""
        if self.is_recording or not self.camera_active:
            return False
            
        # Get frame dimensions
        if self.current_frame is None:
            return False
            
        height, width = self.current_frame.shape[:2]
        
        # Store format
        self.video_format = video_format
        
        # Adjust output path extension if needed
        path = Path(output_path)
        output_path = str(path.with_suffix(f".{video_format}"))
        
        # Select codec based on format
        codec_map = {
            "mp4": "mp4v",  # or H264 if available
            "avi": "MJPG",
            "mov": "mp4v",
            "mkv": "X264"
        }
        
        codec = codec_map.get(video_format, "mp4v")
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*codec)
        self.video_writer = cv2.VideoWriter(output_path, fourcc, self.fps, (width, height))
        
        if not self.video_writer.isOpened():
            self.video_writer = None
            return False
            
        self.is_recording = True
        self.recording_start_time = datetime.now()
        self.recording_output_path = output_path
        self.recording_status_changed.emit(True)
        
        # Start duration timer (update every second)
        self.duration_timer.start(1000)
        
        return True
        
    def stop_recording(self):
        """Stop recording video"""
        if not self.is_recording:
            return None
            
        self.is_recording = False
        
        # Stop duration timer
        self.duration_timer.stop()
        
        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None
            
        output_path = self.recording_output_path
        self.recording_output_path = None
        self.recording_start_time = None
        
        self.recording_status_changed.emit(False)
        
        return output_path
    
    def _update_duration(self):
        """Update recording duration"""
        if self.is_recording and self.recording_start_time:
            elapsed = (datetime.now() - self.recording_start_time).total_seconds()
            self.recording_duration_updated.emit(int(elapsed))
        
    def take_snapshot(self):
        """Take a snapshot of current frame"""
        if self.processed_frame is not None:
            return self.processed_frame.copy()
        return None
        
    def set_brightness(self, value):
        """Set brightness adjustment (-100 to 100)"""
        self.brightness = np.clip(value, -100, 100)
        
    def set_heat_effect(self, value):
        """Set heat effect intensity (0 to 100)"""
        self.heat_effect = np.clip(value, 0, 100)
        
    def set_denoise_strength(self, value):
        """Set denoise strength (0 to 10)"""
        self.denoise_strength = np.clip(value, 0, 10)
        
    def set_noise_strength(self, value):
        """Set noise strength (0 to 100)"""
        self.noise_strength = np.clip(value, 0, 100)
        
    def set_rgb_adjustments(self, red, green, blue):
        """Set RGB channel adjustments (-100 to 100 each)"""
        self.red_adjust = np.clip(red, -100, 100)
        self.green_adjust = np.clip(green, -100, 100)
        self.blue_adjust = np.clip(blue, -100, 100)
        
    def _apply_color_filter(self, frame):
        """Apply selected color filter"""
        if self.active_filter == "sepia":
            return ColorFilter.sepia(frame, self.filter_intensity)
        elif self.active_filter == "negative":
            return ColorFilter.negative(frame)
        elif self.active_filter == "grayscale":
            return ColorFilter.grayscale(frame)
        elif self.active_filter == "vintage":
            return ColorFilter.vintage(frame, self.filter_intensity)
        elif self.active_filter == "cool":
            return ColorFilter.cool(frame, self.filter_intensity)
        elif self.active_filter == "warm":
            return ColorFilter.warm(frame, self.filter_intensity)
        elif self.active_filter == "high_contrast":
            return ColorFilter.high_contrast(frame, self.filter_intensity)
        elif self.active_filter == "vibrant":
            return ColorFilter.vibrant(frame, self.filter_intensity)
        elif self.active_filter == "black_and_white":
            return ColorFilter.black_and_white(frame)
        return frame
        
    def set_color_filter(self, filter_name, intensity=1.0):
        """Set active color filter"""
        self.active_filter = filter_name
        self.filter_intensity = np.clip(intensity, 0.0, 1.0)
