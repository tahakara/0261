"""
Selection Manager - Handles selection areas and operations
"""
import numpy as np
import cv2
from enum import Enum
from typing import Optional, Tuple, List
from dataclasses import dataclass


class SelectionMode(Enum):
    """Selection operation modes"""
    NEW = "New Selection"
    ADD = "Add to Selection"
    SUBTRACT = "Remove from Selection"
    INTERSECT = "Intersect with Selection"


class SelectionShape(Enum):
    """Selection shape types"""
    RECTANGLE = "Rectangle"
    ELLIPSE = "Ellipse"
    POLYGON = "Polygon"
    LASSO = "Lasso"


@dataclass
class SelectionRegion:
    """Represents a selection region"""
    mask: np.ndarray  # Binary mask (0 or 255)
    bounds: Tuple[int, int, int, int]  # x, y, width, height
    feather: int = 0  # Feather/softness amount
    
    def get_feathered_mask(self) -> np.ndarray:
        """Get mask with feathering applied"""
        if self.feather == 0:
            return self.mask
        
        # Apply Gaussian blur for feathering
        kernel_size = self.feather * 2 + 1
        feathered = cv2.GaussianBlur(self.mask, (kernel_size, kernel_size), 0)
        return feathered


class SelectionManager:
    """Manages selection operations and masks"""
    
    def __init__(self, image_size: Tuple[int, int]):
        """
        Initialize selection manager
        
        Args:
            image_size: (width, height) of the image
        """
        self.image_size = image_size
        self.selection_mask: Optional[np.ndarray] = None
        self.has_selection = False
        self.mode = SelectionMode.NEW
        self.clipboard_image: Optional[np.ndarray] = None  # For copy/paste
        
    def create_selection(self, mask: np.ndarray, mode: SelectionMode = SelectionMode.NEW):
        """
        Create or modify selection based on mode
        
        Args:
            mask: Binary mask (0 or 255)
            mode: Selection operation mode
        """
        if mode == SelectionMode.NEW:
            self.selection_mask = mask.copy()
            self.has_selection = np.any(mask > 0)
            
        elif mode == SelectionMode.ADD:
            if self.selection_mask is None:
                self.selection_mask = mask.copy()
            else:
                self.selection_mask = cv2.bitwise_or(self.selection_mask, mask)
            self.has_selection = True
            
        elif mode == SelectionMode.SUBTRACT:
            if self.selection_mask is not None:
                self.selection_mask = cv2.bitwise_and(
                    self.selection_mask, 
                    cv2.bitwise_not(mask)
                )
                self.has_selection = np.any(self.selection_mask > 0)
            
        elif mode == SelectionMode.INTERSECT:
            if self.selection_mask is not None:
                self.selection_mask = cv2.bitwise_and(self.selection_mask, mask)
                self.has_selection = np.any(self.selection_mask > 0)
            else:
                self.selection_mask = mask.copy()
                self.has_selection = True
    
    def create_rectangle_selection(self, x1: int, y1: int, x2: int, y2: int, 
                                   feather: int = 0, mode: SelectionMode = SelectionMode.NEW):
        """Create rectangular selection"""
        h, w = self.image_size[1], self.image_size[0]
        mask = np.zeros((h, w), dtype=np.uint8)
        
        # Draw filled rectangle
        cv2.rectangle(mask, (x1, y1), (x2, y2), 255, -1)
        
        # Apply feather
        if feather > 0:
            kernel_size = feather * 2 + 1
            mask = cv2.GaussianBlur(mask, (kernel_size, kernel_size), 0)
        
        self.create_selection(mask, mode)
    
    def create_ellipse_selection(self, center_x: int, center_y: int, 
                                 radius_x: int, radius_y: int,
                                 feather: int = 0, mode: SelectionMode = SelectionMode.NEW):
        """Create elliptical selection"""
        h, w = self.image_size[1], self.image_size[0]
        mask = np.zeros((h, w), dtype=np.uint8)
        
        # Draw filled ellipse
        cv2.ellipse(mask, (center_x, center_y), (radius_x, radius_y), 0, 0, 360, 255, -1)
        
        # Apply feather
        if feather > 0:
            kernel_size = feather * 2 + 1
            mask = cv2.GaussianBlur(mask, (kernel_size, kernel_size), 0)
        
        self.create_selection(mask, mode)
    
    def create_polygon_selection(self, points: List[Tuple[int, int]], 
                                feather: int = 0, mode: SelectionMode = SelectionMode.NEW):
        """Create polygon selection"""
        h, w = self.image_size[1], self.image_size[0]
        mask = np.zeros((h, w), dtype=np.uint8)
        
        # Convert points to numpy array
        pts = np.array(points, dtype=np.int32)
        cv2.fillPoly(mask, [pts], 255)
        
        # Apply feather
        if feather > 0:
            kernel_size = feather * 2 + 1
            mask = cv2.GaussianBlur(mask, (kernel_size, kernel_size), 0)
        
        self.create_selection(mask, mode)
    
    def create_lasso_selection(self, points: List[Tuple[int, int]], 
                              feather: int = 0, mode: SelectionMode = SelectionMode.NEW):
        """Create freehand lasso selection"""
        # Same as polygon but with continuous points
        self.create_polygon_selection(points, feather, mode)
    
    def clear_selection(self):
        """Clear the current selection"""
        self.selection_mask = None
        self.has_selection = False
    
    def invert_selection(self):
        """Invert the current selection"""
        if self.selection_mask is not None:
            self.selection_mask = cv2.bitwise_not(self.selection_mask)
    
    def select_all(self):
        """Select entire image"""
        h, w = self.image_size[1], self.image_size[0]
        self.selection_mask = np.ones((h, w), dtype=np.uint8) * 255
        self.has_selection = True
    
    def get_selection_mask(self) -> Optional[np.ndarray]:
        """Get the current selection mask"""
        return self.selection_mask.copy() if self.selection_mask is not None else None
    
    def get_selection_bounds(self) -> Optional[Tuple[int, int, int, int]]:
        """Get bounding box of selection (x, y, width, height)"""
        if self.selection_mask is None:
            return None
        
        # Find non-zero pixels
        coords = cv2.findNonZero(self.selection_mask)
        if coords is None:
            return None
        
        x, y, w, h = cv2.boundingRect(coords)
        return (x, y, w, h)
    

    
    def apply_to_image(self, image: np.ndarray, processed: np.ndarray) -> np.ndarray:
        """Apply processed image only to selected area"""
        if not self.has_selection or self.selection_mask is None:
            return processed
        
        result = image.copy()
        
        # Resize mask if needed to match image shape
        mask = self.selection_mask
        if mask.shape[0] != image.shape[0] or mask.shape[1] != image.shape[1]:
            mask = cv2.resize(mask, (image.shape[1], image.shape[0]), interpolation=cv2.INTER_NEAREST)
        
        # Resize processed if needed
        if processed.shape[:2] != image.shape[:2]:
            processed = cv2.resize(processed, (image.shape[1], image.shape[0]))
        
        # Ensure mask is same size as image
        if len(image.shape) == 3:
            mask_3d = cv2.merge([mask, mask, mask])
        else:
            mask_3d = mask
        
        # Normalize mask to 0-1 range
        mask_normalized = mask_3d.astype(float) / 255.0
        
        # Blend: result = image * (1 - mask) + processed * mask
        result = (image * (1 - mask_normalized) + processed * mask_normalized).astype(np.uint8)
        
        return result
    
    def feather_selection(self, amount: int):
        """Apply feathering to current selection"""
        if self.selection_mask is not None and amount > 0:
            kernel_size = amount * 2 + 1
            self.selection_mask = cv2.GaussianBlur(
                self.selection_mask, 
                (kernel_size, kernel_size), 
                0
            )
    
    def expand_selection(self, pixels: int):
        """Expand selection by specified pixels"""
        if self.selection_mask is not None:
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (pixels*2+1, pixels*2+1))
            self.selection_mask = cv2.dilate(self.selection_mask, kernel)
    
    def contract_selection(self, pixels: int):
        """Contract selection by specified pixels"""
        if self.selection_mask is not None:
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (pixels*2+1, pixels*2+1))
            self.selection_mask = cv2.erode(self.selection_mask, kernel)
    
    def get_selection_bounds(self) -> Optional[Tuple[int, int, int, int]]:
        """Get bounding box of current selection (x, y, width, height)"""
        if not self.has_selection or self.selection_mask is None:
            return None
        
        coords = cv2.findNonZero(self.selection_mask)
        if coords is None:
            return None
        
        x, y, w, h = cv2.boundingRect(coords)
        return (x, y, w, h)
    
    def copy_selection(self, image: np.ndarray) -> bool:
        """Copy selected area to clipboard"""
        if not self.has_selection or self.selection_mask is None:
            return False
        
        # Resize mask if needed
        mask = self.selection_mask
        if mask.shape[0] != image.shape[0] or mask.shape[1] != image.shape[1]:
            mask = cv2.resize(mask, (image.shape[1], image.shape[0]), interpolation=cv2.INTER_NEAREST)
        
        bounds = self.get_selection_bounds()
        if not bounds:
            return False
        
        x, y, w, h = bounds
        
        # Make sure bounds are within image
        x = max(0, min(x, image.shape[1] - 1))
        y = max(0, min(y, image.shape[0] - 1))
        w = min(w, image.shape[1] - x)
        h = min(h, image.shape[0] - y)
        
        if w <= 0 or h <= 0:
            return False
        
        selected_region = image[y:y+h, x:x+w].copy()
        mask_region = mask[y:y+h, x:x+w]
        
        if len(selected_region.shape) == 2:
            selected_region = cv2.cvtColor(selected_region, cv2.COLOR_GRAY2BGR)
        
        alpha = mask_region.astype(np.uint8)
        self.clipboard_image = cv2.cvtColor(selected_region, cv2.COLOR_BGR2BGRA)
        self.clipboard_image[:, :, 3] = alpha
        
        return True
    
    def paste_selection(self, image: np.ndarray, x: int = 0, y: int = 0) -> Optional[np.ndarray]:
        """Paste clipboard image at specified position"""
        if self.clipboard_image is None:
            return None
        
        result = image.copy()
        h, w = self.clipboard_image.shape[:2]
        img_h, img_w = image.shape[:2]
        
        if x < 0 or y < 0 or x + w > img_w or y + h > img_h:
            return None
        
        clipboard_rgb = self.clipboard_image[:, :, :3]
        clipboard_alpha = self.clipboard_image[:, :, 3] / 255.0
        
        roi = result[y:y+h, x:x+w]
        for c in range(3):
            roi[:, :, c] = (clipboard_alpha * clipboard_rgb[:, :, c] + 
                           (1 - clipboard_alpha) * roi[:, :, c])
        
        return result
    
    def delete_selection(self, image: np.ndarray, fill_color: Tuple[int, int, int] = (255, 255, 255)) -> Optional[np.ndarray]:
        """Delete (fill with color) selected area"""
        if not self.has_selection or self.selection_mask is None:
            return None
        
        result = image.copy()
        
        # Resize mask if needed
        mask = self.selection_mask
        if mask.shape[0] != image.shape[0] or mask.shape[1] != image.shape[1]:
            mask = cv2.resize(mask, (image.shape[1], image.shape[0]), interpolation=cv2.INTER_NEAREST)
        
        if len(image.shape) == 2:
            result[mask > 0] = fill_color[0]
        else:
            for c in range(min(3, image.shape[2])):
                result[:, :, c][mask > 0] = fill_color[c]
        
        return result
    
    def get_selection_overlay(self, image_shape: Tuple[int, int]) -> Optional[np.ndarray]:
        """Get visual overlay for selection (marching ants effect)"""
        if not self.has_selection or self.selection_mask is None:
            return None
        
        # Create overlay with target image shape
        overlay = np.zeros((image_shape[0], image_shape[1], 4), dtype=np.uint8)
        
        # Resize mask if needed to match image shape
        mask = self.selection_mask
        if mask.shape[0] != image_shape[0] or mask.shape[1] != image_shape[1]:
            mask = cv2.resize(mask, (image_shape[1], image_shape[0]), interpolation=cv2.INTER_NEAREST)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Draw selection border in bright magenta (more visible)
        for contour in contours:
            cv2.drawContours(overlay, [contour], -1, (255, 0, 255, 255), 3)  # Magenta, 3px thick
        
        # Add semi-transparent magenta tint inside selection
        overlay[:, :, 3][mask > 0] = 50  # More visible transparency
        overlay[:, :, 0][mask > 0] = 255  # Blue
        overlay[:, :, 1][mask > 0] = 0    # Green
        overlay[:, :, 2][mask > 0] = 255  # Red = Magenta
        
        return overlay
    
    def crop_to_selection(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Crop image to selection bounds"""
        if not self.has_selection or self.selection_mask is None:
            return None
        
        # Resize mask if needed
        mask = self.selection_mask
        if mask.shape[0] != image.shape[0] or mask.shape[1] != image.shape[1]:
            mask = cv2.resize(mask, (image.shape[1], image.shape[0]), interpolation=cv2.INTER_NEAREST)
        
        # Find bounds from resized mask
        coords = cv2.findNonZero(mask)
        if coords is None:
            return None
        
        x, y, w, h = cv2.boundingRect(coords)
        cropped = image[y:y+h, x:x+w].copy()
        
        return cropped
    
    def cutout_mask(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Create cutout mask - keep selection, make rest white"""
        if not self.has_selection or self.selection_mask is None:
            return None
        
        result = np.ones_like(image) * 255
        
        # Resize mask if needed
        mask = self.selection_mask
        if mask.shape[0] != image.shape[0] or mask.shape[1] != image.shape[1]:
            mask = cv2.resize(mask, (image.shape[1], image.shape[0]), interpolation=cv2.INTER_NEAREST)
        
        # Copy selected area to result
        if len(image.shape) == 2:
            result[mask > 0] = image[mask > 0]
        else:
            for c in range(image.shape[2]):
                result[:, :, c][mask > 0] = image[:, :, c][mask > 0]
        
        return result
