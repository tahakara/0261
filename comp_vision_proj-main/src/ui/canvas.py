"""
Canvas widget for displaying and editing images/video frames.
"""

from typing import Optional, Tuple
import numpy as np
import cv2
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QLabel, 
    QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QPoint, QRect, QSize
from PySide6.QtGui import (
    QImage, QPixmap, QPainter, QPen, QColor, 
    QMouseEvent, QWheelEvent, QKeyEvent
)


class CanvasLabel(QLabel):
    """
    Internal label widget that displays the image and handles interactions.
    """
    
    mouse_pressed = Signal(int, int, int)  # x, y, button
    mouse_moved = Signal(int, int)  # x, y
    mouse_released = Signal(int, int, int)  # x, y, button
    mouse_position = Signal(int, int)  # x, y (for status bar)
    key_pressed = Signal(int)  # key code
    selection_changed = Signal(QRect)  # selection rectangle
    paint_stroke = Signal(int, int, int, int, int, int, int, int, int)  # x, y, r, g, b, radius, softness, transparency, mode (0=brush, 1=pen, 2=erase)
    fill_at_point = Signal(int, int, int, int, int)  # x, y, r, g, b
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setAlignment(Qt.AlignCenter)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self._image: Optional[np.ndarray] = None
        self._zoom = 1.0
        self._offset = QPoint(0, 0)
        
        # Cache for resized pixmap to avoid repeated expensive resizes
        self._cached_pixmap = None
        self._cached_zoom = None
        self._cached_image_ref = None
        # Selection
        self._selection_start: Optional[QPoint] = None
        self._selection_rect: Optional[QRect] = None
        self._is_selecting = False
        # Selection mode: 'rect', 'lasso', 'brush'
        self._selection_mode = 'rect'
        # For non-rect selections we maintain a uint8 mask (0 or 255) matching the image
        self._selection_mask: Optional[np.ndarray] = None
        # Lasso points (in image coords)
        self._lasso_points = []
        # Brush radius (in image pixels)
        self._brush_radius = 20
        # Brush softness (0-100, controls edge feathering)
        self._brush_softness = 0
        # Brush transparency (0-100, controls alpha)
        self._brush_transparency = 0
        # Brush step (spacing between dabs when dragging)
        self._brush_step = 5
        # Last brush position for step calculation
        self._last_brush_pos: Optional[Tuple[int, int]] = None
        # Current mouse position (in widget coords) for brush circle preview
        self._mouse_pos: Optional[QPoint] = None
        
        # Paint mode (when true, painting directly on layer instead of creating selection)
        self._paint_mode = False
        self._paint_color = (0, 0, 0)  # RGB color for painting
        
        # Grid/guides
        self._show_grid = False
        self._show_guides = True
        
        # Set initial cursor
        self._update_cursor()
        
        # Transform overlay (in image coordinates)
        self._transform_rect: Optional[QRect] = None
        
        self.setStyleSheet("background-color: #2a2a2a;")

        # Processing overlay (hidden by default)
        self._processing_overlay = QLabel(self)
        self._processing_overlay.setAlignment(Qt.AlignCenter)
        self._processing_overlay.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 0, 0, 140);
                color: white;
                font-weight: bold;
                border: 1px solid rgba(255,255,255,20);
                border-radius: 6px;
            }
        """)
        self._processing_overlay.hide()
    
    def set_image(self, image: np.ndarray):
        """Set the image to display."""
        self._image = image
        # Invalidate cache and update display
        self._cached_pixmap = None
        self._cached_image_ref = image
        # reset selection mask when image changes
        self._selection_mask = None
        self._lasso_points = []
        self._update_display()
    
    def get_image(self) -> Optional[np.ndarray]:
        """Get the current image."""
        return self._image
    
    def set_zoom(self, zoom: float):
        """Set zoom level (1.0 = 100%)."""
        self._zoom = max(0.1, min(10.0, zoom))
        # Invalidate cached resized pixmap when zoom changes
        self._cached_pixmap = None
        self._cached_zoom = None
        self._update_display()
    
    def get_zoom(self) -> float:
        """Get current zoom level."""
        return self._zoom
    
    def zoom_in(self):
        """Increase zoom by 25%."""
        self.set_zoom(self._zoom * 1.25)
    
    def zoom_out(self):
        """Decrease zoom by 25%."""
        self.set_zoom(self._zoom / 1.25)
    
    def fit_to_view(self):
        """Fit image to widget size."""
        if self._image is None:
            return
        
        h, w = self._image.shape[:2]
        parent = self.parent()
        if parent:
            pw, ph = parent.width() - 40, parent.height() - 40
            zoom_w = pw / w
            zoom_h = ph / h
            self._zoom = min(zoom_w, zoom_h, 1.0)
            self._update_display()
    
    def actual_size(self):
        """Set zoom to 100%."""
        self.set_zoom(1.0)
    
    @property
    def selection(self) -> Optional[QRect]:
        """Get current selection rectangle in image coordinates."""
        return self._selection_rect

    def get_selection_mask(self) -> Optional[np.ndarray]:
        """Return a boolean mask for the current selection (image coords).

        Returns an ndarray of shape (h, w) dtype=bool where True indicates
        selected pixels. If selection is rectangular or empty, returns None
        (use selection QRect in that case).
        """
        if self._selection_mask is not None:
            return self._selection_mask.astype(bool)
        return None

    def set_selection_mode(self, mode: str):
        """Set selection tool mode: 'rect', 'lasso', 'brush', 'pen', 'erase', or 'fill'."""
        valid_modes = ('rect', 'lasso', 'brush', 'pen', 'erase', 'fill')
        if mode not in valid_modes:
            return
        self._selection_mode = mode
        # reset temporary lasso points when switching
        if mode != 'lasso':
            self._lasso_points = []
        # Update cursor icon
        self._update_cursor()
        self._update_display()
    
    def _update_cursor(self):
        """Update cursor based on selection mode."""
        if self._selection_mode == 'rect':
            self.setCursor(Qt.CrossCursor)
        elif self._selection_mode == 'lasso':
            # Use pointing hand for lasso
            self.setCursor(Qt.PointingHandCursor)
        elif self._selection_mode == 'brush':
            # Use blank cursor for brush (we'll draw custom circle)
            self.setCursor(Qt.BlankCursor)

    def set_brush_radius(self, radius: int):
        """Set brush radius in image pixels."""
        self._brush_radius = max(1, int(radius))
        if self._selection_mode == 'brush':
            self._update_display()
    
    def set_brush_softness(self, softness: int):
        """Set brush softness (0-100)."""
        self._brush_softness = max(0, min(100, softness))
    
    def set_brush_transparency(self, transparency: int):
        """Set brush transparency (0-100)."""
        self._brush_transparency = max(0, min(100, transparency))
    
    def set_brush_step(self, step: int):
        """Set brush step spacing."""
        self._brush_step = max(1, step)
    
    def set_paint_mode(self, enabled: bool):
        """Enable or disable paint mode."""
        self._paint_mode = enabled
        if enabled:
            # Clear selection when entering paint mode
            self.clear_selection()
    
    def set_paint_color(self, r: int, g: int, b: int):
        """Set the paint color."""
        self._paint_color = (r, g, b)
    
    def _paint_brush_stroke(self, x: int, y: int):
        """Paint a single brush stroke at the given position with softness and transparency."""
        if self._selection_mask is None or self._image is None:
            return
        
        h, w = self._image.shape[:2]
        
        # Calculate alpha based on transparency (0 = opaque, 100 = fully transparent)
        alpha = int(255 * (1.0 - self._brush_transparency / 100.0))
        
        if self._brush_softness == 0:
            # Hard edge brush
            cv2.circle(self._selection_mask, (x, y), self._brush_radius, alpha, -1)
        else:
            # Soft edge brush using Gaussian blur
            # Create a temporary layer for the soft brush
            temp_mask = np.zeros((h, w), dtype='uint8')
            cv2.circle(temp_mask, (x, y), self._brush_radius, 255, -1)
            
            # Apply Gaussian blur based on softness
            kernel_size = max(3, int(self._brush_radius * self._brush_softness / 100.0))
            if kernel_size % 2 == 0:
                kernel_size += 1
            temp_mask = cv2.GaussianBlur(temp_mask, (kernel_size, kernel_size), 0)
            
            # Scale by alpha and combine with existing mask (max operation for accumulation)
            temp_mask = (temp_mask.astype(np.float32) * alpha / 255.0).astype(np.uint8)
            self._selection_mask = np.maximum(self._selection_mask, temp_mask)
    
    def clear_selection(self):
        """Clear the current selection."""
        self._selection_rect = None
        self._selection_mask = None
        self._lasso_points = []
        self._update_display()
        self.selection_changed.emit(QRect())
    
    def _update_display(self):
        """Update the displayed pixmap."""
        if self._image is None:
            self.setPixmap(QPixmap())
            return
        
        # Convert numpy array to QImage
        image = self._image
        h, w = image.shape[:2]
        
        # Use cached pixmap when image object and zoom haven't changed
        if (self._cached_pixmap is not None and
                self._cached_zoom == self._zoom and
                self._cached_image_ref is self._image):
            pixmap = self._cached_pixmap
        else:
            # Apply zoom and create new pixmap
            new_w = int(w * self._zoom)
            new_h = int(h * self._zoom)

            if new_w > 0 and new_h > 0:
                resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
            else:
                resized = image

            # Convert to QImage
            if len(resized.shape) == 2:
                qimg = QImage(resized.data, resized.shape[1], resized.shape[0], 
                             resized.strides[0], QImage.Format_Grayscale8)
            elif resized.shape[2] == 3:
                rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
                qimg = QImage(rgb.data, rgb.shape[1], rgb.shape[0], 
                             rgb.strides[0], QImage.Format_RGB888)
            else:
                rgba = cv2.cvtColor(resized, cv2.COLOR_BGRA2RGBA)
                qimg = QImage(rgba.data, rgba.shape[1], rgba.shape[0], 
                             rgba.strides[0], QImage.Format_RGBA8888)

            pixmap = QPixmap.fromImage(qimg)
            # Cache for subsequent repaints (selection/overlay drawing)
            self._cached_pixmap = pixmap
            self._cached_zoom = self._zoom
            self._cached_image_ref = self._image
        
        # Draw overlays (selection, transform) on a copy to avoid mutating the cached pixmap
        if self._cached_pixmap is not None and self._cached_zoom == self._zoom and self._cached_image_ref is self._image:
            display_pixmap = self._cached_pixmap.copy()
        else:
            display_pixmap = pixmap

        # Draw selection overlay if exists (rect or mask) - but NOT in paint mode for pen/erase/fill
        painter = None
        # Skip selection drawing if in paint mode with paint-only tools
        skip_selection = self._paint_mode and self._selection_mode in ['pen', 'erase', 'fill', 'brush', 'lasso']
        
        if not skip_selection and self._selection_mask is not None and self._selection_mask.any():
            # Draw mask contours filled with translucent color
            try:
                # Ensure mask is uint8 with values 0 or 255
                mask_img = self._selection_mask.copy()
                if mask_img.dtype == bool:
                    mask_img = mask_img.astype('uint8') * 255
                contours, _ = cv2.findContours(mask_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                if contours:
                    painter = QPainter(display_pixmap)
                    painter.setPen(QPen(QColor(0, 120, 215), 2, Qt.SolidLine))
                    painter.setBrush(QColor(0, 120, 215, 60))
                    from PySide6.QtGui import QPolygon
                    for cnt in contours:
                        # cnt is Nx1x2 array of points in image coords; scale by zoom
                        pts = [QPoint(int(pt[0][0] * self._zoom), int(pt[0][1] * self._zoom)) for pt in cnt]
                        if pts and len(pts) >= 3:
                            polygon = QPolygon(pts)
                            painter.drawPolygon(polygon)
            except Exception as e:
                pass
        elif not skip_selection and self._selection_rect and not self._selection_rect.isEmpty():
            painter = QPainter(display_pixmap)
            painter.setPen(QPen(QColor(0, 120, 215), 1, Qt.DashLine))
            painter.setBrush(QColor(0, 120, 215, 30))

            # Scale selection rect to current zoom
            scaled_rect = QRect(
                int(self._selection_rect.x() * self._zoom),
                int(self._selection_rect.y() * self._zoom),
                int(self._selection_rect.width() * self._zoom),
                int(self._selection_rect.height() * self._zoom)
            )
            painter.drawRect(scaled_rect)

        if painter is not None:
            painter.end()

        # Draw transform rect and handles if set
        if self._transform_rect and not self._transform_rect.isEmpty():
            painter = QPainter(display_pixmap)
            pen = QPen(QColor(255, 165, 0), 2)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)

            scaled = QRect(
                int(self._transform_rect.x() * self._zoom),
                int(self._transform_rect.y() * self._zoom),
                int(self._transform_rect.width() * self._zoom),
                int(self._transform_rect.height() * self._zoom)
            )
            painter.drawRect(scaled)

            # Draw handles as small filled circles at corners and midpoints
            handle_color = QColor(255, 165, 0)
            handle_radius = max(4, int(6 * self._zoom))
            points = [
                scaled.topLeft(), scaled.topRight(), scaled.bottomLeft(), scaled.bottomRight(),
                QPoint(scaled.center().x(), scaled.top()), QPoint(scaled.center().x(), scaled.bottom()),
                QPoint(scaled.left(), scaled.center().y()), QPoint(scaled.right(), scaled.center().y())
            ]
            painter.setBrush(handle_color)
            for pt in points:
                painter.drawEllipse(pt, handle_radius, handle_radius)
            painter.end()

        # Draw brush circle preview if in brush/pen/erase mode and mouse is over canvas
        if self._selection_mode in ['brush', 'pen', 'erase'] and self._mouse_pos is not None:
            painter = QPainter(display_pixmap)
            painter.setPen(QPen(QColor(255, 255, 255), 2, Qt.SolidLine))
            painter.setBrush(Qt.NoBrush)
            # Draw circle at mouse position with brush radius scaled to zoom
            radius_scaled = int(self._brush_radius * self._zoom)
            painter.drawEllipse(self._mouse_pos, radius_scaled, radius_scaled)
            painter.end()

        self.setPixmap(display_pixmap)
        self.setFixedSize(display_pixmap.size())

        # Position processing overlay to cover the pixmap
        if self._processing_overlay is not None:
            self._processing_overlay.setFixedSize(display_pixmap.size())
            self._processing_overlay.move(0, 0)
            self._processing_overlay.raise_()

    def show_processing_overlay(self, text: str = "Processing..."):
        """Show a semi-transparent overlay with text on the canvas."""
        if self._processing_overlay is None:
            return
        self._processing_overlay.setText(text)
        self._processing_overlay.show()

    def hide_processing_overlay(self):
        """Hide the processing overlay."""
        if self._processing_overlay is None:
            return
        self._processing_overlay.hide()
    
    def _widget_to_image_coords(self, pos: QPoint) -> Tuple[int, int]:
        """Convert widget coordinates to image coordinates."""
        if self._image is None:
            return (0, 0)
        
        x = int(pos.x() / self._zoom)
        y = int(pos.y() / self._zoom)
        
        h, w = self._image.shape[:2]
        x = max(0, min(x, w - 1))
        y = max(0, min(y, h - 1))
        
        return (x, y)

    def set_transform_rect(self, rect: Optional[QRect]):
        """Set the transform rectangle in image coordinates to display handles."""
        self._transform_rect = rect
        self._update_display()
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press."""
        x, y = self._widget_to_image_coords(event.position().toPoint())
        # Emit integer button value to ensure proper conversion to C++ types
        # Use the enum's numeric value which is safe to emit across the binding
        try:
            btn_val = event.button().value
        except Exception:
            btn_val = int(event.button()) if hasattr(event.button(), '__int__') else 0
        self.mouse_pressed.emit(x, y, int(btn_val))
        
        # Start selection depending on mode
        if event.button() == Qt.LeftButton and event.modifiers() == Qt.NoModifier:
            # Pen, erase, and fill ONLY work in paint mode
            if self._selection_mode in ['pen', 'erase', 'fill']:
                if not self._paint_mode:
                    # Do nothing if paint mode is off for these tools
                    super().mousePressEvent(event)
                    return
                # Paint directly on layer - NO selection tracking
                if self._selection_mode in ['pen', 'erase']:
                    mode_indicator = 1 if self._selection_mode == 'pen' else 2
                    # Pen uses 1 pixel radius for pixel-perfect drawing
                    pen_radius = 1 if self._selection_mode == 'pen' else self._brush_radius
                    pen_step = 1 if self._selection_mode == 'pen' else self._brush_step
                    self.paint_stroke.emit(x, y, *self._paint_color, pen_radius, 0, self._brush_transparency, mode_indicator)
                    self._last_brush_pos = (x, y)
                    self._is_selecting = True  # Track for drag painting
                elif self._selection_mode == 'fill':
                    # Emit fill signal - no dragging needed
                    self.fill_at_point.emit(x, y, *self._paint_color)
                # Early return - don't process as selection
                super().mousePressEvent(event)
                return
            # Check if in paint mode for brush/lasso
            elif self._paint_mode and self._selection_mode in ['brush', 'lasso']:
                # Paint directly on layer - track for dragging but no selection rect
                if self._selection_mode == 'brush':
                    mode_indicator = 0
                    self.paint_stroke.emit(x, y, *self._paint_color, self._brush_radius, self._brush_softness, self._brush_transparency, mode_indicator)
                    self._last_brush_pos = (x, y)
                    self._is_selecting = True  # Track for drag painting
                elif self._selection_mode == 'lasso':
                    self._lasso_points = [(x, y)]
                    self._is_selecting = True  # Track for drag painting
                # Early return - don't process as selection
                super().mousePressEvent(event)
                return
            else:
                # Selection mode for rect, lasso, brush
                self._is_selecting = True
                self._selection_start = event.position().toPoint()
                if self._selection_mode == 'rect':
                    self._selection_rect = None
                elif self._selection_mode == 'lasso':
                    # start freehand path with first point
                    self._lasso_points = [(x, y)]
                    self._selection_mask = None
                elif self._selection_mode == 'brush':
                    # ensure mask exists
                    if self._image is not None:
                        h, w = self._image.shape[:2]
                        if self._selection_mask is None or self._selection_mask.shape != (h, w):
                            self._selection_mask = np.zeros((h, w), dtype='uint8')
                        self._paint_brush_stroke(x, y)
                        self._last_brush_pos = (x, y)
                        # update bounding rect
                        ys, xs = np.where(self._selection_mask > 0)
                        if ys.size:
                            self._selection_rect = QRect(int(xs.min()), int(ys.min()), int(xs.max()-xs.min()+1), int(ys.max()-ys.min()+1))
                        else:
                            self._selection_rect = None
                        self._update_display()
                        ys, xs = np.where(self._selection_mask > 0)
                        if ys.size:
                            self._selection_rect = QRect(int(xs.min()), int(ys.min()), int(xs.max()-xs.min()+1), int(ys.max()-ys.min()+1))
                        else:
                            self._selection_rect = None
                        self._update_display()
        
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move."""
        x, y = self._widget_to_image_coords(event.position().toPoint())
        self.mouse_moved.emit(x, y)
        self.mouse_position.emit(x, y)
        
        # Update mouse position for brush circle preview
        self._mouse_pos = event.position().toPoint()
        if self._selection_mode in ['brush', 'pen', 'erase'] and not self._is_selecting:
            self._update_display()
        
        # Update selection depending on mode
        if self._is_selecting:
            current = event.position().toPoint()
            # Pen and erase only work in paint mode
            if self._selection_mode in ['pen', 'erase'] and self._paint_mode:
                # Paint mode: emit paint strokes with step control
                x_cur, y_cur = self._widget_to_image_coords(current)
                mode_indicator = 1 if self._selection_mode == 'pen' else 2
                # Pen uses 1 pixel radius and step for pixel-perfect drawing
                pen_radius = 1 if self._selection_mode == 'pen' else self._brush_radius
                pen_step = 1 if self._selection_mode == 'pen' else self._brush_step
                if self._last_brush_pos is not None:
                    last_x, last_y = self._last_brush_pos
                    dist = np.sqrt((x_cur - last_x)**2 + (y_cur - last_y)**2)
                    if dist >= pen_step:
                        # Interpolate points
                        steps = int(dist / pen_step)
                        for i in range(steps + 1):
                            t = i / max(steps, 1)
                            interp_x = int(last_x + t * (x_cur - last_x))
                            interp_y = int(last_y + t * (y_cur - last_y))
                            self.paint_stroke.emit(interp_x, interp_y, *self._paint_color, pen_radius, 0, self._brush_transparency, mode_indicator)
                        self._last_brush_pos = (x_cur, y_cur)
                else:
                    self.paint_stroke.emit(x_cur, y_cur, *self._paint_color, pen_radius, 0, self._brush_transparency, mode_indicator)
                    self._last_brush_pos = (x_cur, y_cur)
                super().mouseMoveEvent(event)
                return
            elif self._paint_mode and self._selection_mode == 'brush':
                # Paint mode: emit paint strokes with step control
                x_cur, y_cur = self._widget_to_image_coords(current)
                mode_indicator = 0
                if self._last_brush_pos is not None:
                    last_x, last_y = self._last_brush_pos
                    dist = np.sqrt((x_cur - last_x)**2 + (y_cur - last_y)**2)
                    if dist >= self._brush_step:
                        # Interpolate points
                        steps = int(dist / self._brush_step)
                        for i in range(steps + 1):
                            t = i / max(steps, 1)
                            interp_x = int(last_x + t * (x_cur - last_x))
                            interp_y = int(last_y + t * (y_cur - last_y))
                            self.paint_stroke.emit(interp_x, interp_y, *self._paint_color, self._brush_radius, self._brush_softness, self._brush_transparency, mode_indicator)
                        self._last_brush_pos = (x_cur, y_cur)
                else:
                    self.paint_stroke.emit(x_cur, y_cur, *self._paint_color, self._brush_radius, self._brush_softness, self._brush_transparency, mode_indicator)
                    self._last_brush_pos = (x_cur, y_cur)
                super().mouseMoveEvent(event)
                return
            elif self._paint_mode and self._selection_mode == 'lasso':
                # Paint mode lasso: accumulate points for freehand painting
                x_cur, y_cur = self._widget_to_image_coords(current)
                last = self._lasso_points[-1] if self._lasso_points else (None, None)
                if last[0] is None or (abs(x_cur-last[0]) + abs(y_cur-last[1]) > 2):
                    self._lasso_points.append((x_cur, y_cur))
                    # Emit paint for line segment
                    if len(self._lasso_points) >= 2:
                        mode_indicator = 0  # Lasso uses brush mode
                        self.paint_stroke.emit(x_cur, y_cur, *self._paint_color, self._brush_radius, self._brush_softness, self._brush_transparency, mode_indicator)
                super().mouseMoveEvent(event)
                return
            elif self._selection_mode == 'rect':
                # Calculate selection in image coordinates
                start_x, start_y = self._widget_to_image_coords(self._selection_start)
                end_x, end_y = self._widget_to_image_coords(current)
                self._selection_rect = QRect(
                    min(start_x, end_x),
                    min(start_y, end_y),
                    abs(end_x - start_x),
                    abs(end_y - start_y)
                )
                self._update_display()
            elif self._selection_mode == 'lasso':
                x_cur, y_cur = self._widget_to_image_coords(current)
                # append point if moved enough
                last = self._lasso_points[-1] if self._lasso_points else (None, None)
                if last[0] is None or (abs(x_cur-last[0]) + abs(y_cur-last[1]) > 2):
                    self._lasso_points.append((x_cur, y_cur))
                # build mask from lasso points
                if self._image is not None and len(self._lasso_points) >= 3:
                    h, w = self._image.shape[:2]
                    mask = np.zeros((h, w), dtype='uint8')
                    pts = np.array(self._lasso_points, dtype=np.int32).reshape((-1,1,2))
                    cv2.fillPoly(mask, [pts], 255)
                    self._selection_mask = mask
                    ys, xs = np.where(self._selection_mask > 0)
                    if ys.size:
                        self._selection_rect = QRect(int(xs.min()), int(ys.min()), int(xs.max()-xs.min()+1), int(ys.max()-ys.min()+1))
                    else:
                        self._selection_rect = None
                    self._update_display()
            elif self._selection_mode in ['brush', 'pen', 'erase']:
                x_cur, y_cur = self._widget_to_image_coords(current)
                if self._image is not None:
                    h, w = self._image.shape[:2]
                    if self._selection_mask is None or self._selection_mask.shape != (h, w):
                        self._selection_mask = np.zeros((h, w), dtype='uint8')
                    
                    # Use step to control spacing between brush dabs
                    if self._last_brush_pos is not None:
                        last_x, last_y = self._last_brush_pos
                        dist = np.sqrt((x_cur - last_x)**2 + (y_cur - last_y)**2)
                        if dist >= self._brush_step:
                            # Interpolate points between last and current position
                            steps = int(dist / self._brush_step)
                            for i in range(steps + 1):
                                t = i / max(steps, 1)
                                interp_x = int(last_x + t * (x_cur - last_x))
                                interp_y = int(last_y + t * (y_cur - last_y))
                                self._paint_brush_stroke(interp_x, interp_y)
                            self._last_brush_pos = (x_cur, y_cur)
                    else:
                        self._paint_brush_stroke(x_cur, y_cur)
                        self._last_brush_pos = (x_cur, y_cur)
                    
                    ys, xs = np.where(self._selection_mask > 0)
                    if ys.size:
                        self._selection_rect = QRect(int(xs.min()), int(ys.min()), int(xs.max()-xs.min()+1), int(ys.max()-ys.min()+1))
                    else:
                        self._selection_rect = None
                    self._update_display()
        
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release."""
        x, y = self._widget_to_image_coords(event.position().toPoint())
        # Emit integer button value to ensure proper conversion to C++ types
        try:
            btn_val = event.button().value
        except Exception:
            btn_val = int(event.button()) if hasattr(event.button(), '__int__') else 0
        self.mouse_released.emit(x, y, int(btn_val))
        
        if self._is_selecting:
            self._is_selecting = False
            # Reset last brush position
            self._last_brush_pos = None
            # finalize lasso into mask if needed
            if self._selection_mode == 'lasso' and self._lasso_points and self._image is not None:
                if len(self._lasso_points) >= 3:
                    h, w = self._image.shape[:2]
                    mask = np.zeros((h, w), dtype='uint8')
                    pts = np.array(self._lasso_points, dtype=np.int32).reshape((-1,1,2))
                    cv2.fillPoly(mask, [pts], 255)
                    self._selection_mask = mask
                    ys, xs = np.where(self._selection_mask > 0)
                    if ys.size:
                        self._selection_rect = QRect(int(xs.min()), int(ys.min()), int(xs.max()-xs.min()+1), int(ys.max()-ys.min()+1))
                self._lasso_points = []

            if self._selection_rect and not self._selection_rect.isEmpty():
                self.selection_changed.emit(self._selection_rect)
        
        super().mouseReleaseEvent(event)
    
    def wheelEvent(self, event: QWheelEvent):
        """Handle mouse wheel for zooming."""
        if event.modifiers() == Qt.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
        else:
            super().wheelEvent(event)
    
    def leaveEvent(self, event):
        """Handle mouse leaving widget."""
        self._mouse_pos = None
        if self._selection_mode == 'brush':
            self._update_display()
        super().leaveEvent(event)
    
    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press."""
        self.key_pressed.emit(event.key())
        
        if event.key() == Qt.Key_Escape:
            self.clear_selection()
        elif event.key() == Qt.Key_Plus and event.modifiers() == Qt.ControlModifier:
            self.zoom_in()
        elif event.key() == Qt.Key_Minus and event.modifiers() == Qt.ControlModifier:
            self.zoom_out()
        elif event.key() == Qt.Key_0 and event.modifiers() == Qt.ControlModifier:
            self.actual_size()
        
        super().keyPressEvent(event)


class CanvasWidget(QScrollArea):
    """
    Main canvas widget with scrolling support.
    Contains the CanvasLabel for actual image display.
    """
    
    # Forward signals from canvas label
    mouse_pressed = Signal(int, int, int)
    mouse_moved = Signal(int, int)
    mouse_released = Signal(int, int, int)
    mouse_position = Signal(int, int)
    key_pressed = Signal(int)
    selection_changed = Signal(QRect)
    zoom_changed = Signal(float)
    paint_stroke = Signal(int, int, int, int, int, int, int, int, int)
    fill_at_point = Signal(int, int, int, int, int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWidgetResizable(False)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QScrollArea {
                background-color: #1a1a1a;
                border: none;
            }
            QScrollBar:vertical, QScrollBar:horizontal {
                background-color: #2a2a2a;
                width: 12px;
                height: 12px;
            }
            QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
                background-color: #4a4a4a;
                border-radius: 5px;
                min-height: 20px;
                min-width: 20px;
            }
            QScrollBar::handle:hover {
                background-color: #5a5a5a;
            }
        """)
        
        # Create canvas label
        self._canvas = CanvasLabel()
        self.setWidget(self._canvas)
        
        # Connect signals
        self._canvas.mouse_pressed.connect(self.mouse_pressed)
        self._canvas.mouse_moved.connect(self.mouse_moved)
        self._canvas.mouse_released.connect(self.mouse_released)
        self._canvas.mouse_position.connect(self.mouse_position)
        self._canvas.key_pressed.connect(self.key_pressed)
        self._canvas.selection_changed.connect(self.selection_changed)
        self._canvas.paint_stroke.connect(self.paint_stroke)
        self._canvas.fill_at_point.connect(self.fill_at_point)
    
    @property
    def canvas(self) -> CanvasLabel:
        """Access the internal canvas label."""
        return self._canvas
    
    def set_image(self, image: np.ndarray):
        """Set the image to display."""
        self._canvas.set_image(image)
    
    def get_image(self) -> Optional[np.ndarray]:
        """Get the current image."""
        return self._canvas.get_image()
    
    def set_zoom(self, zoom: float):
        """Set zoom level."""
        self._canvas.set_zoom(zoom)
        self.zoom_changed.emit(zoom)
    
    def get_zoom(self) -> float:
        """Get current zoom level."""
        return self._canvas.get_zoom()
    
    def zoom_in(self):
        """Zoom in."""
        self._canvas.zoom_in()
        self.zoom_changed.emit(self._canvas.get_zoom())
    
    def zoom_out(self):
        """Zoom out."""
        self._canvas.zoom_out()
        self.zoom_changed.emit(self._canvas.get_zoom())
    
    def fit_to_view(self):
        """Fit image to view."""
        self._canvas.fit_to_view()
        self.zoom_changed.emit(self._canvas.get_zoom())
    
    def actual_size(self):
        """Set to 100% zoom."""
        self._canvas.actual_size()
        self.zoom_changed.emit(self._canvas.get_zoom())
    
    @property
    def selection(self) -> Optional[QRect]:
        """Get current selection."""
        return self._canvas.selection
    
    def clear_selection(self):
        """Clear selection."""
        self._canvas.clear_selection()
