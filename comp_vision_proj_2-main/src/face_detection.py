"""
Face Detection System - OpenCV Haar Cascade based face detection with features
"""
import cv2
import numpy as np
from typing import List, Tuple


class FaceDetectionSystem:
    """Face detection with blur, bounding boxes, and numbering"""
    
    def __init__(self):
        # Load Haar Cascade for face detection
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        # Settings
        self.enabled = False
        self.show_boxes = True
        self.show_numbers = True
        self.blur_faces = False
        self.blur_strength = 21  # Must be odd number
        
        # Detection parameters
        self.scale_factor = 1.1
        self.min_neighbors = 5
        self.min_size = (30, 30)
        
        # Last detected faces
        self.last_faces = []
        
    def detect_faces(self, frame):
        """Detect faces in frame"""
        if not self.enabled:
            return frame, []
            
        # Convert to grayscale for detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=self.scale_factor,
            minNeighbors=self.min_neighbors,
            minSize=self.min_size
        )
        
        self.last_faces = faces
        
        # Process frame with detected faces
        result = frame.copy()
        
        for i, (x, y, w, h) in enumerate(faces):
            # Apply blur if enabled
            if self.blur_faces:
                result = self._blur_face(result, x, y, w, h)
            
            # Draw bounding box if enabled
            if self.show_boxes:
                cv2.rectangle(result, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Draw number if enabled
            if self.show_numbers:
                cv2.putText(result, str(i + 1), (x, y - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        
        return result, faces
        
    def _blur_face(self, frame, x, y, w, h):
        """Apply blur to face region"""
        # Extract face region
        face_roi = frame[y:y+h, x:x+w]
        
        # Apply Gaussian blur
        blur_size = min(self.blur_strength, w, h)
        if blur_size % 2 == 0:
            blur_size += 1
            
        blurred_face = cv2.GaussianBlur(face_roi, (blur_size, blur_size), 0)
        
        # Replace face region with blurred version
        frame[y:y+h, x:x+w] = blurred_face
        
        return frame
        
    def set_blur_strength(self, strength):
        """Set blur strength (must be odd, 1-99)"""
        self.blur_strength = max(1, min(99, strength))
        if self.blur_strength % 2 == 0:
            self.blur_strength += 1
            
    def get_face_count(self):
        """Get number of detected faces"""
        return len(self.last_faces)
