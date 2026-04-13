"""
Face Sentiment Analysis - Detects emotions from facial expressions
"""
import cv2
import numpy as np


class FaceSentimentAnalyzer:
    """Analyzes facial expressions for sentiment"""
    
    def __init__(self):
        """Initialize sentiment analyzer"""
        self.enabled = False
        self.show_emoji = True
        
    def analyze_sentiment(self, frame, faces):
        """
        Analyze sentiment from detected faces
        
        Args:
            frame: BGR image frame
            faces: List of face rectangles (x, y, w, h)
            
        Returns:
            tuple: (processed_frame, sentiments)
        """
        if not self.enabled or faces is None or len(faces) == 0:
            return frame, []
        
        result_frame = frame.copy()
        sentiments = []
        
        for i, (x, y, w, h) in enumerate(faces):
            # Extract face region
            face_roi = frame[y:y+h, x:x+w]
            
            if face_roi.size == 0:
                continue
            
            # Simple heuristic-based sentiment analysis
            # In real application, you would use a trained model
            sentiment = self._analyze_face_region(face_roi)
            sentiments.append(sentiment)
            
            # Draw emoji on top-left of frame for each face
            if self.show_emoji:
                emoji_y = 30 + i * 40
                self._draw_sentiment_emoji(result_frame, sentiment, 10, emoji_y)
        
        return result_frame, sentiments
    
    def _analyze_face_region(self, face_roi):
        """
        Analyze face region for sentiment using simple heuristics
        
        Args:
            face_roi: Face region (BGR image)
            
        Returns:
            str: Sentiment ('happy', 'sad', 'neutral')
        """
        # Convert to grayscale
        gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
        
        h, w = gray.shape
        
        # Analyze mouth region (bottom third of face)
        mouth_region = gray[int(h*0.66):, :]
        
        # Analyze eye region (top third of face)
        eye_region = gray[:int(h*0.33), :]
        
        # Simple brightness-based heuristic
        # This is a placeholder - real sentiment analysis would use ML models
        mouth_brightness = np.mean(mouth_region)
        eye_brightness = np.mean(eye_region)
        
        # Calculate variance (smile detection heuristic)
        mouth_variance = np.var(mouth_region)
        
        # Balanced decision logic
        # Medium thresholds for realistic detection
        if mouth_variance > 1200 and mouth_brightness > eye_brightness * 1.03:  # Medium threshold for happy
            return 'happy'
        elif mouth_brightness < eye_brightness * 0.88 or mouth_variance < 500:  # Detect sad/angry
            return 'sad'
        else:
            return 'neutral'
    
    def _draw_sentiment_emoji(self, frame, sentiment, x, y):
        """
        Draw sentiment emoji on frame
        
        Args:
            frame: BGR image frame
            sentiment: Sentiment string
            x, y: Position to draw emoji
        """
        emoji_size = 30
        
        if sentiment == 'happy':
            # Happy face emoji
            color = (0, 255, 0)  # Green
            text = "😊"
            label = "Mutlu"
        elif sentiment == 'sad':
            # Sad face emoji
            color = (0, 0, 255)  # Red
            text = "😢"
            label = "Uzgun"
        else:
            # Neutral face emoji
            color = (255, 255, 0)  # Yellow
            text = "😐"
            label = "Notr"
        
        # Draw background rectangle
        cv2.rectangle(frame, (x-5, y-25), (x+120, y+10), (0, 0, 0), -1)
        cv2.rectangle(frame, (x-5, y-25), (x+120, y+10), color, 2)
        
        # Draw label
        cv2.putText(frame, label, (x, y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        # Draw simple face representation (since Unicode emojis may not render)
        face_center_x = x + 100
        face_center_y = y - 10
        face_radius = 12
        
        # Face circle
        cv2.circle(frame, (face_center_x, face_center_y), face_radius, color, 2)
        
        # Eyes
        eye_y = face_center_y - 3
        cv2.circle(frame, (face_center_x - 4, eye_y), 2, color, -1)
        cv2.circle(frame, (face_center_x + 4, eye_y), 2, color, -1)
        
        # Mouth
        mouth_y = face_center_y + 5
        if sentiment == 'happy':
            # Smile
            cv2.ellipse(frame, (face_center_x, mouth_y-2), (6, 4), 0, 0, 180, color, 2)
        elif sentiment == 'sad':
            # Frown
            cv2.ellipse(frame, (face_center_x, mouth_y+2), (6, 4), 0, 180, 360, color, 2)
        else:
            # Neutral line
            cv2.line(frame, (face_center_x-6, mouth_y), (face_center_x+6, mouth_y), color, 2)
