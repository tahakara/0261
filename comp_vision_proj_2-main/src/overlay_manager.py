"""
Video Overlay System - Text, image, and video overlays with transformations
"""
from PySide6.QtCore import QObject, QRectF, QPointF, Signal
from PySide6.QtGui import QColor, QFont
import cv2
import numpy as np
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Tuple


class OverlayType(Enum):
    """Types of overlays"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"


@dataclass
class OverlayData:
    """Data structure for an overlay"""
    id: int
    type: OverlayType
    position: Tuple[int, int]  # (x, y) top-left corner
    size: Tuple[int, int]  # (width, height)
    name: str = ""  # User-defined name
    opacity: float = 1.0  # 0.0 to 1.0
    
    # Text overlay specific
    text: str = ""
    font_size: int = 24
    font_family: int = cv2.FONT_HERSHEY_SIMPLEX  # OpenCV font
    text_color: Tuple[int, int, int] = (255, 255, 255)  # BGR
    
    # Image/Video overlay specific
    content: Optional[np.ndarray] = None  # Image data or current video frame
    original_content: Optional[np.ndarray] = None  # Original for resizing
    
    # Video overlay specific
    video_path: str = ""
    video_capture: Optional[cv2.VideoCapture] = None
    current_frame_index: int = 0
    
    # Key color (chroma key)
    has_keycolor: bool = False
    keycolor: Tuple[int, int, int] = (0, 255, 0)  # BGR - default green
    keycolor_tolerance: int = 30  # 0-255


class OverlayManager(QObject):
    """Manages video overlays"""
    
    overlay_added = Signal(int)  # overlay_id
    overlay_removed = Signal(int)  # overlay_id
    overlay_updated = Signal(int)  # overlay_id
    
    def __init__(self):
        super().__init__()
        
        self.overlays = {}  # id -> OverlayData
        self.next_id = 1
        self.selected_overlay_id = None
        self.show_selection_frame = True  # Show selection frame for selected overlay
        
    def select_overlay(self, overlay_id):
        """Select an overlay"""
        if overlay_id in self.overlays:
            self.selected_overlay_id = overlay_id
            self.overlay_updated.emit(overlay_id)
            return True
        return False
    
    def deselect_overlay(self):
        """Deselect current overlay"""
        if self.selected_overlay_id:
            old_id = self.selected_overlay_id
            self.selected_overlay_id = None
            self.overlay_updated.emit(old_id)
    
    def get_selected_overlay(self):
        """Get currently selected overlay"""
        if self.selected_overlay_id:
            return self.overlays.get(self.selected_overlay_id)
        return None
    
    def is_point_in_overlay(self, overlay_id, point):
        """Check if point is inside overlay bounds"""
        overlay = self.overlays.get(overlay_id)
        if not overlay:
            return False
        
        x, y = point
        ox, oy = overlay.position
        ow, oh = overlay.size
        
        return ox <= x <= ox + ow and oy <= y <= oy + oh
    
    def get_resize_handle(self, overlay_id, point):
        """Check if point is on a resize handle"""
        overlay = self.overlays.get(overlay_id)
        if not overlay:
            return None
        
        x, y = point
        ox, oy = overlay.position
        ow, oh = overlay.size
        
        handle_size = 10
        
        # Check corners (priority)
        handles = {
            'top_left': (ox, oy),
            'top_right': (ox + ow, oy),
            'bottom_left': (ox, oy + oh),
            'bottom_right': (ox + ow, oy + oh)
        }
        
        for handle_name, (hx, hy) in handles.items():
            if abs(x - hx) <= handle_size and abs(y - hy) <= handle_size:
                return handle_name
        
        return None
        
    def add_text_overlay(self, text, position, font_size=24, color=(255, 255, 255), font_family=cv2.FONT_HERSHEY_SIMPLEX, name=""):
        """Add a text overlay"""
        # Estimate text size
        font_scale = font_size / 30.0
        thickness = max(1, int(font_size / 15))
        
        (text_width, text_height), _ = cv2.getTextSize(text, font_family, font_scale, thickness)
        
        # Generate default name if not provided
        if not name:
            name = f"Text {self.next_id}"
        
        overlay = OverlayData(
            id=self.next_id,
            type=OverlayType.TEXT,
            name=name,
            position=position,
            size=(text_width + 20, text_height + 20),
            text=text,
            font_size=font_size,
            font_family=font_family,
            text_color=color
        )
        
        self.overlays[self.next_id] = overlay
        overlay_id = self.next_id
        self.next_id += 1
        
        self.overlay_added.emit(overlay_id)
        return overlay_id
        
    def add_image_overlay(self, image_path, position, size=None, name=""):
        """Add an image overlay"""
        # Load image with alpha channel
        image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        if image is None:
            return None
            
        # Convert to BGRA if needed
        if len(image.shape) == 2:  # Grayscale
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGRA)
        elif image.shape[2] == 3:  # BGR
            image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
            
        # Resize if size is specified
        if size:
            image = cv2.resize(image, size)
        
        # Generate default name if not provided
        if not name:
            name = f"Image {self.next_id}"
        
        overlay = OverlayData(
            id=self.next_id,
            type=OverlayType.IMAGE,
            name=name,
            position=position,
            size=(image.shape[1], image.shape[0]),
            content=image.copy(),
            original_content=image.copy()
        )
        
        self.overlays[self.next_id] = overlay
        overlay_id = self.next_id
        self.next_id += 1
        
        self.overlay_added.emit(overlay_id)
        return overlay_id
        
    def add_video_overlay(self, video_path, position, size=None, name=""):
        """Add a video overlay"""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return None
            
        # Read first frame
        ret, frame = cap.read()
        if not ret:
            cap.release()
            return None
            
        # Convert to BGRA
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
        
        # Resize if size is specified
        if size:
            frame = cv2.resize(frame, size)
            
        # Reset to beginning
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        
        # Generate default name if not provided
        if not name:
            name = f"Video {self.next_id}"
        
        overlay = OverlayData(
            id=self.next_id,
            type=OverlayType.VIDEO,
            name=name,
            position=position,
            size=(frame.shape[1], frame.shape[0]),
            content=frame.copy(),
            original_content=frame.copy(),
            video_path=video_path,
            video_capture=cap
        )
        
        self.overlays[self.next_id] = overlay
        overlay_id = self.next_id
        self.next_id += 1
        
        self.overlay_added.emit(overlay_id)
        return overlay_id
        
    def remove_overlay(self, overlay_id):
        """Remove an overlay"""
        if overlay_id in self.overlays:
            overlay = self.overlays[overlay_id]
            
            # Release video capture if it's a video overlay
            if overlay.type == OverlayType.VIDEO and overlay.video_capture:
                overlay.video_capture.release()
                
            del self.overlays[overlay_id]
            self.overlay_removed.emit(overlay_id)
            
            if self.selected_overlay_id == overlay_id:
                self.selected_overlay_id = None
                
    def update_overlay_position(self, overlay_id, position):
        """Update overlay position"""
        if overlay_id in self.overlays:
            self.overlays[overlay_id].position = position
            self.overlay_updated.emit(overlay_id)
            
    def update_overlay_size(self, overlay_id, size):
        """Update overlay size"""
        if overlay_id not in self.overlays:
            return
            
        overlay = self.overlays[overlay_id]
        overlay.size = size
        
        # Resize content for image/video overlays
        if overlay.type in [OverlayType.IMAGE, OverlayType.VIDEO]:
            if overlay.original_content is not None:
                overlay.content = cv2.resize(overlay.original_content, size)
                
        self.overlay_updated.emit(overlay_id)
        
    def update_overlay_opacity(self, overlay_id, opacity):
        """Update overlay opacity (0.0 to 1.0)"""
        if overlay_id in self.overlays:
            self.overlays[overlay_id].opacity = np.clip(opacity, 0.0, 1.0)
            self.overlay_updated.emit(overlay_id)
            
    def update_overlay_name(self, overlay_id, name):
        """Update overlay name"""
        if overlay_id in self.overlays:
            self.overlays[overlay_id].name = name
            self.overlay_updated.emit(overlay_id)
            
    def set_overlay_keycolor(self, overlay_id, enable, color=(0, 255, 0), tolerance=30):
        """Set keycolor (chroma key) for overlay"""
        if overlay_id in self.overlays:
            overlay = self.overlays[overlay_id]
            overlay.has_keycolor = enable
            overlay.keycolor = color
            overlay.keycolor_tolerance = tolerance
            self.overlay_updated.emit(overlay_id)
            
    def update_video_frame(self, overlay_id):
        """Update video overlay to next frame"""
        if overlay_id not in self.overlays:
            return
            
        overlay = self.overlays[overlay_id]
        if overlay.type != OverlayType.VIDEO or not overlay.video_capture:
            return
            
        ret, frame = overlay.video_capture.read()
        if not ret:
            # Loop video
            overlay.video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = overlay.video_capture.read()
            
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
            frame = cv2.resize(frame, overlay.size)
            overlay.content = frame
            overlay.original_content = frame.copy()
            
    def render_overlays(self, base_frame):
        """Render all overlays on base frame"""
        result = base_frame.copy()
        
        # Convert to BGRA if needed
        if len(result.shape) == 2:
            result = cv2.cvtColor(result, cv2.COLOR_GRAY2BGRA)
        elif result.shape[2] == 3:
            result = cv2.cvtColor(result, cv2.COLOR_BGR2BGRA)
            
        # Render each overlay in order
        for overlay_id in sorted(self.overlays.keys()):
            overlay = self.overlays[overlay_id]
            
            # Update video frames
            if overlay.type == OverlayType.VIDEO:
                self.update_video_frame(overlay_id)
                
            result = self._render_single_overlay(result, overlay)
            
            # Draw selection frame if this overlay is selected
            if overlay_id == self.selected_overlay_id and self.show_selection_frame:
                result = self._draw_selection_frame(result, overlay)
            
        return result
        
    def _render_single_overlay(self, base_frame, overlay: OverlayData):
        """Render a single overlay on base frame"""
        x, y = overlay.position
        w, h = overlay.size
        
        # Check bounds
        if x < 0 or y < 0 or x + w > base_frame.shape[1] or y + h > base_frame.shape[0]:
            return base_frame
            
        if overlay.type == OverlayType.TEXT:
            # Render text
            font_scale = overlay.font_size / 30.0
            thickness = max(1, int(overlay.font_size / 15))
            
            # Apply opacity to text color
            color = tuple(int(c * overlay.opacity) for c in overlay.text_color)
            
            cv2.putText(base_frame, overlay.text, (x + 10, y + h - 10),
                       overlay.font_family, font_scale, color, thickness, cv2.LINE_AA)
                       
        elif overlay.type in [OverlayType.IMAGE, OverlayType.VIDEO]:
            if overlay.content is None:
                return base_frame
                
            overlay_img = overlay.content.copy()
            
            # Apply keycolor if enabled
            if overlay.has_keycolor:
                overlay_img = self._apply_keycolor(overlay_img, overlay.keycolor, 
                                                   overlay.keycolor_tolerance)
                                                   
            # Apply opacity to alpha channel
            if overlay_img.shape[2] == 4:
                overlay_img[:, :, 3] = (overlay_img[:, :, 3] * overlay.opacity).astype(np.uint8)
                
            # Blend overlay onto base frame
            base_frame = self._blend_overlay(base_frame, overlay_img, (x, y))
            
        return base_frame
        
    def _apply_keycolor(self, image, keycolor, tolerance):
        """Apply chroma key to image"""
        # Convert to float for processing
        img_float = image.astype(np.float32)
        
        # Create mask based on color similarity
        lower = np.array([max(0, c - tolerance) for c in keycolor], dtype=np.float32)
        upper = np.array([min(255, c + tolerance) for c in keycolor], dtype=np.float32)
        
        # Check if pixel is within keycolor range
        mask = cv2.inRange(image[:, :, :3], lower.astype(np.uint8), upper.astype(np.uint8))
        
        # Set alpha to 0 for keycolor pixels
        if image.shape[2] == 4:
            image[:, :, 3][mask > 0] = 0
        else:
            # Convert to BGRA
            image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
            image[:, :, 3][mask > 0] = 0
            
        return image
        
    def _blend_overlay(self, base, overlay, position):
        """Blend overlay onto base image at position"""
        x, y = position
        h, w = overlay.shape[:2]
        
        if overlay.shape[2] == 4:  # Has alpha channel
            alpha = overlay[:, :, 3:4] / 255.0
            
            # Blend
            roi = base[y:y+h, x:x+w]
            blended = overlay[:, :, :3] * alpha + roi[:, :, :3] * (1 - alpha)
            base[y:y+h, x:x+w, :3] = blended.astype(np.uint8)
        else:
            # No alpha, just copy
            base[y:y+h, x:x+w, :3] = overlay[:, :, :3]
            
        return base
        
    def get_overlay_at_position(self, pos):
        """Get overlay ID at position (for selection)"""
        x, y = pos
        
        # Check overlays in reverse order (top to bottom)
        for overlay_id in reversed(sorted(self.overlays.keys())):
            overlay = self.overlays[overlay_id]
            ox, oy = overlay.position
            w, h = overlay.size
            
            if ox <= x <= ox + w and oy <= y <= oy + h:
                return overlay_id
                
        return None
        
    def get_overlay(self, overlay_id):
        """Get overlay data"""
        return self.overlays.get(overlay_id)
    
    def select_overlay(self, overlay_id):
        """Select an overlay"""
        if overlay_id in self.overlays:
            self.selected_overlay_id = overlay_id
            self.overlay_updated.emit(overlay_id)
            return True
        return False
    
    def deselect_overlay(self):
        """Deselect current overlay"""
        if self.selected_overlay_id:
            old_id = self.selected_overlay_id
            self.selected_overlay_id = None
            self.overlay_updated.emit(old_id)
    
    def get_selected_overlay(self):
        """Get currently selected overlay"""
        if self.selected_overlay_id:
            return self.overlays.get(self.selected_overlay_id)
        return None
    
    def is_point_in_overlay(self, overlay_id, point):
        """Check if point is inside overlay bounds"""
        overlay = self.overlays.get(overlay_id)
        if not overlay:
            return False
        
        x, y = point
        ox, oy = overlay.position
        ow, oh = overlay.size
        
        return ox <= x <= ox + ow and oy <= y <= oy + oh
    
    def get_resize_handle(self, overlay_id, point):
        """Check if point is on a resize handle"""
        overlay = self.overlays.get(overlay_id)
        if not overlay:
            return None
        
        x, y = point
        ox, oy = overlay.position
        ow, oh = overlay.size
        
        handle_size = 10
        
        # Check corners (priority)
        handles = {
            'top_left': (ox, oy),
            'top_right': (ox + ow, oy),
            'bottom_left': (ox, oy + oh),
            'bottom_right': (ox + ow, oy + oh)
        }
        
        for handle_name, (hx, hy) in handles.items():
            if abs(x - hx) <= handle_size and abs(y - hy) <= handle_size:
                return handle_name
        
        return None
    
    def _draw_selection_frame(self, frame, overlay):
        """Draw selection frame and resize handles"""
        x, y = overlay.position
        w, h = overlay.size
        
        # Draw selection rectangle
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
        
        # Draw resize handles at corners
        handle_size = 8
        handle_color = (0, 255, 255)
        handle_thickness = -1  # Filled
        
        handles = [
            (x, y),  # Top-left
            (x + w, y),  # Top-right
            (x, y + h),  # Bottom-left
            (x + w, y + h)  # Bottom-right
        ]
        
        for hx, hy in handles:
            cv2.rectangle(frame, 
                         (hx - handle_size//2, hy - handle_size//2),
                         (hx + handle_size//2, hy + handle_size//2),
                         handle_color, handle_thickness)
        
        return frame
        
    def get_all_overlays(self):
        """Get all overlays"""
        return list(self.overlays.values())
