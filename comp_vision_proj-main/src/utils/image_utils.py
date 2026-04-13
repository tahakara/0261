"""
Image utility functions.
"""

from typing import Tuple, Optional
import numpy as np
import cv2


class ImageUtils:
    """Utility class for common image operations."""
    
    @staticmethod
    def resize(image: np.ndarray, width: int, height: int, 
               keep_aspect: bool = True) -> np.ndarray:
        """
        Resize an image.
        
        Args:
            image: Input image
            width: Target width
            height: Target height
            keep_aspect: If True, maintain aspect ratio (use largest dimension)
            
        Returns:
            Resized image
        """
        h, w = image.shape[:2]
        
        if keep_aspect:
            aspect = w / h
            target_aspect = width / height
            
            if aspect > target_aspect:
                new_w = width
                new_h = int(width / aspect)
            else:
                new_h = height
                new_w = int(height * aspect)
        else:
            new_w, new_h = width, height
        
        return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
    
    @staticmethod
    def crop(image: np.ndarray, x: int, y: int, 
             width: int, height: int) -> np.ndarray:
        """
        Crop a region from the image.
        
        Args:
            image: Input image
            x, y: Top-left corner of the crop region
            width, height: Size of the crop region
            
        Returns:
            Cropped image
        """
        h, w = image.shape[:2]
        
        # Clamp to image bounds
        x1 = max(0, min(x, w))
        y1 = max(0, min(y, h))
        x2 = max(0, min(x + width, w))
        y2 = max(0, min(y + height, h))
        
        return image[y1:y2, x1:x2].copy()
    
    @staticmethod
    def rotate(image: np.ndarray, angle: float, 
               expand: bool = True) -> np.ndarray:
        """
        Rotate the image by the given angle.
        
        Args:
            image: Input image
            angle: Rotation angle in degrees (positive = counter-clockwise)
            expand: If True, expand canvas to fit rotated image
            
        Returns:
            Rotated image
        """
        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        
        # Get rotation matrix
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        
        if expand:
            # Calculate new bounds
            cos = np.abs(M[0, 0])
            sin = np.abs(M[0, 1])
            new_w = int(h * sin + w * cos)
            new_h = int(h * cos + w * sin)
            
            # Adjust rotation matrix
            M[0, 2] += (new_w - w) / 2
            M[1, 2] += (new_h - h) / 2
            
            return cv2.warpAffine(image, M, (new_w, new_h))
        else:
            return cv2.warpAffine(image, M, (w, h))
    
    @staticmethod
    def flip(image: np.ndarray, horizontal: bool = True) -> np.ndarray:
        """
        Flip the image horizontally or vertically.
        
        Args:
            image: Input image
            horizontal: If True, flip horizontally; otherwise vertically
            
        Returns:
            Flipped image
        """
        flip_code = 1 if horizontal else 0
        return cv2.flip(image, flip_code)
    
    @staticmethod
    def convert_color_space(image: np.ndarray, 
                            from_space: str, to_space: str) -> np.ndarray:
        """
        Convert image between color spaces.
        
        Args:
            image: Input image
            from_space: Source color space ('bgr', 'rgb', 'hsv', 'lab', 'gray')
            to_space: Target color space
            
        Returns:
            Converted image
        """
        conversions = {
            ('bgr', 'rgb'): cv2.COLOR_BGR2RGB,
            ('rgb', 'bgr'): cv2.COLOR_RGB2BGR,
            ('bgr', 'hsv'): cv2.COLOR_BGR2HSV,
            ('hsv', 'bgr'): cv2.COLOR_HSV2BGR,
            ('bgr', 'lab'): cv2.COLOR_BGR2LAB,
            ('lab', 'bgr'): cv2.COLOR_LAB2BGR,
            ('bgr', 'gray'): cv2.COLOR_BGR2GRAY,
            ('gray', 'bgr'): cv2.COLOR_GRAY2BGR,
            ('rgb', 'gray'): cv2.COLOR_RGB2GRAY,
            ('gray', 'rgb'): cv2.COLOR_GRAY2RGB,
        }
        
        key = (from_space.lower(), to_space.lower())
        if key in conversions:
            return cv2.cvtColor(image, conversions[key])
        
        return image
    
    @staticmethod
    def add_alpha_channel(image: np.ndarray, 
                          alpha: int = 255) -> np.ndarray:
        """
        Add alpha channel to image if not present.
        
        Args:
            image: Input image (BGR or BGRA)
            alpha: Default alpha value (0-255)
            
        Returns:
            BGRA image
        """
        if len(image.shape) == 2:
            # Grayscale to BGRA
            bgr = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            return cv2.cvtColor(bgr, cv2.COLOR_BGR2BGRA)
        elif image.shape[2] == 3:
            # BGR to BGRA
            bgra = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
            bgra[:, :, 3] = alpha
            return bgra
        
        return image
    
    @staticmethod
    def get_histogram(image: np.ndarray, 
                      channel: int = -1) -> np.ndarray:
        """
        Calculate histogram for an image.
        
        Args:
            image: Input image
            channel: Channel to calculate (-1 for grayscale/average)
            
        Returns:
            Histogram array
        """
        if channel == -1:
            if len(image.shape) == 2:
                return cv2.calcHist([image], [0], None, [256], [0, 256])
            else:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                return cv2.calcHist([gray], [0], None, [256], [0, 256])
        else:
            return cv2.calcHist([image], [channel], None, [256], [0, 256])
    
    @staticmethod
    def auto_levels(image: np.ndarray) -> np.ndarray:
        """
        Automatically adjust levels (histogram stretching).
        
        Args:
            image: Input image
            
        Returns:
            Adjusted image
        """
        if len(image.shape) == 2:
            return cv2.equalizeHist(image)
        else:
            # Process each channel
            channels = cv2.split(image)
            result_channels = []
            
            for i, ch in enumerate(channels):
                if i < 3:  # Don't equalize alpha
                    result_channels.append(cv2.equalizeHist(ch))
                else:
                    result_channels.append(ch)
            
            return cv2.merge(result_channels)
    
    @staticmethod
    def create_checkerboard(width: int, height: int, 
                            square_size: int = 10) -> np.ndarray:
        """
        Create a checkerboard pattern (useful for transparency background).
        
        Args:
            width, height: Image dimensions
            square_size: Size of each square
            
        Returns:
            Checkerboard image (BGR)
        """
        result = np.zeros((height, width, 3), dtype=np.uint8)
        
        light = (200, 200, 200)
        dark = (150, 150, 150)
        
        for y in range(0, height, square_size):
            for x in range(0, width, square_size):
                color = light if ((x // square_size) + (y // square_size)) % 2 == 0 else dark
                x2 = min(x + square_size, width)
                y2 = min(y + square_size, height)
                result[y:y2, x:x2] = color
        
        return result
