"""
Canvas - High-performance QGraphicsView based workspace for image rendering
"""
import numpy as np
import cv2
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PySide6.QtCore import Qt, Signal, QPointF, QRectF
from PySide6.QtGui import QPixmap, QImage, QPainter, QWheelEvent, QMouseEvent


class ImageCanvas(QGraphicsView):
    """
    High-performance canvas for rendering OpenCV images using QGraphicsView
    Supports zooming, panning, and efficient image updates
    """
    
    # Signals
    mouse_pressed = Signal(int, int)  # x, y in image coordinates
    mouse_moved = Signal(int, int)
    mouse_released = Signal(int, int)
    mouse_double_clicked = Signal(int, int)  # For polygon finalization
    zoom_changed = Signal(float)
    
    def __init__(self):
        super().__init__()
        
        # Setup scene
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        
        # Image item
        self.image_item: QGraphicsPixmapItem = None
        self.current_image: np.ndarray = None
        
        # View settings
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        
        # Zoom settings
        self.zoom_factor = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 10.0
        
        # Background
        self.setBackgroundBrush(Qt.darkGray)
        
        # Mouse tracking
        self.setMouseTracking(True)
        self.is_panning = False
        self.pan_start_pos = QPointF()
        
        # Brush cursor preview
        self.brush_cursor_size = 10
        self.show_brush_cursor = False
        
    def load_image(self, image: np.ndarray):
        """
        Load an OpenCV image (numpy array) onto the canvas
        
        Args:
            image: OpenCV image (BGR or grayscale)
        """
        if image is None or image.size == 0:
            return
            
        self.current_image = image.copy()
        pixmap = self.numpy_to_pixmap(image)
        
        if self.image_item is None:
            self.image_item = QGraphicsPixmapItem(pixmap)
            self.scene.addItem(self.image_item)
        else:
            self.image_item.setPixmap(pixmap)
        
        # Reset view
        self.scene.setSceneRect(QRectF(pixmap.rect()))
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        self.zoom_factor = 1.0
        
    def update_image(self, image: np.ndarray):
        """
        Update the canvas with a new image without resetting the view
        
        Args:
            image: OpenCV image (BGR or grayscale)
        """
        if image is None or image.size == 0:
            return
            
        self.current_image = image.copy()
        pixmap = self.numpy_to_pixmap(image)
        
        if self.image_item is None:
            self.load_image(image)
        else:
            self.image_item.setPixmap(pixmap)
    
    def get_image(self) -> np.ndarray:
        """Get the current image as numpy array"""
        return self.current_image.copy() if self.current_image is not None else None
    
    def numpy_to_pixmap(self, image: np.ndarray) -> QPixmap:
        """
        Convert OpenCV/numpy image to QPixmap efficiently
        
        Args:
            image: OpenCV image (numpy array)
            
        Returns:
            QPixmap for rendering
        """
        if len(image.shape) == 2:
            # Grayscale image
            height, width = image.shape
            bytes_per_line = width
            qt_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
        else:
            # Color image (BGR to RGB conversion)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            height, width, channels = image_rgb.shape
            bytes_per_line = channels * width
            qt_image = QImage(image_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)
        
        return QPixmap.fromImage(qt_image)
    
    def wheelEvent(self, event: QWheelEvent):
        """Handle zoom with mouse wheel"""
        # Get the zoom factor
        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor
        
        # Calculate zoom
        if event.angleDelta().y() > 0:
            zoom_change = zoom_in_factor
        else:
            zoom_change = zoom_out_factor
        
        # Check zoom limits
        new_zoom = self.zoom_factor * zoom_change
        if new_zoom < self.min_zoom or new_zoom > self.max_zoom:
            return
        
        # Apply zoom
        self.scale(zoom_change, zoom_change)
        self.zoom_factor = new_zoom
        self.zoom_changed.emit(self.zoom_factor)
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press"""
        if event.button() == Qt.LeftButton:
            scene_pos = self.mapToScene(event.pos())
            if self.image_item and self.image_item.contains(scene_pos):
                # Convert to image coordinates
                item_pos = self.image_item.mapFromScene(scene_pos)
                self.mouse_pressed.emit(int(item_pos.x()), int(item_pos.y()))
        
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move"""
        scene_pos = self.mapToScene(event.pos())
        if self.image_item and self.image_item.contains(scene_pos):
            # Convert to image coordinates
            item_pos = self.image_item.mapFromScene(scene_pos)
            self.mouse_moved.emit(int(item_pos.x()), int(item_pos.y()))
        
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release"""
        if event.button() == Qt.LeftButton:
            scene_pos = self.mapToScene(event.pos())
            if self.image_item and self.image_item.contains(scene_pos):
                # Convert to image coordinates
                item_pos = self.image_item.mapFromScene(scene_pos)
                self.mouse_released.emit(int(item_pos.x()), int(item_pos.y()))
        
        super().mouseReleaseEvent(event)
    
    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """Handle double-click events"""
        if event.button() == Qt.LeftButton and self.image_item:
            scene_pos = self.mapToScene(event.pos())
            image_pos = self.image_item.mapFromScene(scene_pos)
            x, y = int(image_pos.x()), int(image_pos.y())
            
            # Check bounds
            if self.current_image is not None:
                h, w = self.current_image.shape[:2]
                if 0 <= x < w and 0 <= y < h:
                    self.mouse_double_clicked.emit(x, y)
        
        super().mouseDoubleClickEvent(event)
    
    def reset_view(self):
        """Reset zoom and center the image"""
        if self.image_item:
            self.resetTransform()
            self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
            self.zoom_factor = 1.0
            self.zoom_changed.emit(self.zoom_factor)
    
    def zoom_in(self):
        """Zoom in the view"""
        zoom_change = 1.15
        new_zoom = self.zoom_factor * zoom_change
        if new_zoom <= self.max_zoom:
            self.scale(zoom_change, zoom_change)
            self.zoom_factor = new_zoom
            self.zoom_changed.emit(self.zoom_factor)
    
    def zoom_out(self):
        """Zoom out the view"""
        zoom_change = 1 / 1.15
        new_zoom = self.zoom_factor * zoom_change
        if new_zoom >= self.min_zoom:
            self.scale(zoom_change, zoom_change)
            self.zoom_factor = new_zoom
            self.zoom_changed.emit(self.zoom_factor)
    
    def fit_to_window(self):
        """Fit the image to the window"""
        if self.image_item:
            self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
            # Calculate the actual zoom factor after fitting
            if self.current_image is not None:
                view_rect = self.viewport().rect()
                scene_rect = self.scene.sceneRect()
                x_ratio = view_rect.width() / scene_rect.width()
                y_ratio = view_rect.height() / scene_rect.height()
                self.zoom_factor = min(x_ratio, y_ratio)
                self.zoom_changed.emit(self.zoom_factor)
    
    def set_brush_cursor(self, size: int, show: bool = True):
        """Set brush cursor preview"""
        self.brush_cursor_size = size
        self.show_brush_cursor = show
        
        if show:
            # Create circular cursor
            from PySide6.QtGui import QCursor, QPixmap, QPainter, QPen
            from PySide6.QtCore import QPoint
            
            cursor_size = min(size * 2 + 4, 100)
            pixmap = QPixmap(cursor_size, cursor_size)
            pixmap.fill(Qt.transparent)
            
            painter = QPainter(pixmap)
            painter.setPen(QPen(Qt.white, 2))
            painter.drawEllipse(2, 2, cursor_size - 4, cursor_size - 4)
            painter.setPen(QPen(Qt.black, 1))
            painter.drawEllipse(3, 3, cursor_size - 6, cursor_size - 6)
            painter.end()
            
            cursor = QCursor(pixmap, cursor_size // 2, cursor_size // 2)
            self.setCursor(cursor)
        else:
            self.setCursor(Qt.ArrowCursor)
