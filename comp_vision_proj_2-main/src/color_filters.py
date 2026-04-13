"""
Color Filters - Various artistic color filters for video
"""
import cv2
import numpy as np


class ColorFilter:
    """Color filter effects"""
    
    @staticmethod
    def sepia(frame, intensity=1.0):
        """Apply sepia tone effect"""
        # Sepia transformation matrix
        kernel = np.array([[0.272, 0.534, 0.131],
                          [0.349, 0.686, 0.168],
                          [0.393, 0.769, 0.189]])
        
        sepia_img = cv2.transform(frame, kernel)
        sepia_img = np.clip(sepia_img, 0, 255).astype(np.uint8)
        
        # Blend with original based on intensity
        return cv2.addWeighted(frame, 1 - intensity, sepia_img, intensity, 0)
        
    @staticmethod
    def negative(frame):
        """Apply negative (invert colors) effect"""
        return cv2.bitwise_not(frame)
        
    @staticmethod
    def grayscale(frame):
        """Convert to grayscale"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        
    @staticmethod
    def vintage(frame, intensity=1.0):
        """Apply vintage effect"""
        # Reduce saturation
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 1] = hsv[:, :, 1] * 0.5  # Reduce saturation
        hsv = np.clip(hsv, 0, 255).astype(np.uint8)
        vintage_img = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        
        # Add slight sepia tint
        vintage_img = ColorFilter.sepia(vintage_img, 0.3)
        
        # Blend with original
        return cv2.addWeighted(frame, 1 - intensity, vintage_img, intensity, 0)
        
    @staticmethod
    def cool(frame, intensity=1.0):
        """Apply cool (blue) tone"""
        cool_img = frame.copy().astype(np.float32)
        cool_img[:, :, 0] = np.clip(cool_img[:, :, 0] * 1.2, 0, 255)  # More blue
        cool_img[:, :, 2] = np.clip(cool_img[:, :, 2] * 0.8, 0, 255)  # Less red
        cool_img = cool_img.astype(np.uint8)
        
        return cv2.addWeighted(frame, 1 - intensity, cool_img, intensity, 0)
        
    @staticmethod
    def warm(frame, intensity=1.0):
        """Apply warm (orange/red) tone"""
        warm_img = frame.copy().astype(np.float32)
        warm_img[:, :, 2] = np.clip(warm_img[:, :, 2] * 1.2, 0, 255)  # More red
        warm_img[:, :, 0] = np.clip(warm_img[:, :, 0] * 0.8, 0, 255)  # Less blue
        warm_img = warm_img.astype(np.uint8)
        
        return cv2.addWeighted(frame, 1 - intensity, warm_img, intensity, 0)
        
    @staticmethod
    def high_contrast(frame, intensity=1.0):
        """Apply high contrast effect"""
        # Convert to LAB color space
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB).astype(np.float32)
        
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l = clahe.apply(l.astype(np.uint8)).astype(np.float32)
        
        lab = cv2.merge([l, a, b])
        contrast_img = cv2.cvtColor(lab.astype(np.uint8), cv2.COLOR_LAB2BGR)
        
        return cv2.addWeighted(frame, 1 - intensity, contrast_img, intensity, 0)
        
    @staticmethod
    def vibrant(frame, intensity=1.0):
        """Increase color vibrance"""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.5, 0, 255)  # Increase saturation
        hsv = hsv.astype(np.uint8)
        vibrant_img = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        
        return cv2.addWeighted(frame, 1 - intensity, vibrant_img, intensity, 0)
        
    @staticmethod
    def black_and_white(frame, threshold=127):
        """Convert to black and white (binary)"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, bw = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
        return cv2.cvtColor(bw, cv2.COLOR_GRAY2BGR)
