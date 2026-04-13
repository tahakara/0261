"""
Video utility functions.
"""

from typing import Optional, Tuple, Generator, Callable
from pathlib import Path
import numpy as np
import cv2


class VideoUtils:
    """Utility class for common video operations."""
    
    @staticmethod
    def get_video_info(video_path: str) -> dict:
        """
        Get information about a video file.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary with video properties
        """
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            return {}
        
        info = {
            'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'fps': cap.get(cv2.CAP_PROP_FPS),
            'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            'duration': cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS),
            'fourcc': int(cap.get(cv2.CAP_PROP_FOURCC)),
        }
        
        cap.release()
        return info
    
    @staticmethod
    def extract_frame(video_path: str, frame_index: int) -> Optional[np.ndarray]:
        """
        Extract a specific frame from a video.
        
        Args:
            video_path: Path to video file
            frame_index: Index of frame to extract
            
        Returns:
            Frame as numpy array, or None if failed
        """
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            return None
        
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ret, frame = cap.read()
        cap.release()
        
        return frame if ret else None
    
    @staticmethod
    def extract_frames(video_path: str, 
                       start_frame: int = 0,
                       end_frame: Optional[int] = None,
                       step: int = 1) -> Generator[Tuple[int, np.ndarray], None, None]:
        """
        Generator that yields frames from a video.
        
        Args:
            video_path: Path to video file
            start_frame: First frame to extract
            end_frame: Last frame to extract (None = end of video)
            step: Frame step (1 = every frame, 2 = every other, etc.)
            
        Yields:
            Tuples of (frame_index, frame_array)
        """
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            return
        
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if end_frame is None:
            end_frame = total
        
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        
        for i in range(start_frame, min(end_frame, total), step):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            
            if not ret:
                break
                
            yield (i, frame)
        
        cap.release()
    
    @staticmethod
    def create_video_writer(output_path: str, 
                            width: int, height: int,
                            fps: float = 30.0,
                            codec: str = 'mp4v') -> cv2.VideoWriter:
        """
        Create a video writer for saving video.
        
        Args:
            output_path: Output file path
            width, height: Video dimensions
            fps: Frames per second
            codec: Four-character codec code
            
        Returns:
            VideoWriter instance
        """
        fourcc = cv2.VideoWriter_fourcc(*codec)
        return cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    @staticmethod
    def process_video(input_path: str, 
                      output_path: str,
                      process_func: Callable[[np.ndarray, int], np.ndarray],
                      progress_callback: Optional[Callable[[int, int], None]] = None):
        """
        Process a video frame by frame.
        
        Args:
            input_path: Input video path
            output_path: Output video path
            process_func: Function that takes (frame, frame_index) and returns processed frame
            progress_callback: Optional callback(current, total) for progress updates
        """
        cap = cv2.VideoCapture(input_path)
        
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {input_path}")
        
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Determine codec based on output extension
        ext = Path(output_path).suffix.lower()
        codec = 'mp4v' if ext == '.mp4' else 'XVID'
        
        writer = VideoUtils.create_video_writer(output_path, width, height, fps, codec)
        
        frame_index = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Process frame
            processed = process_func(frame, frame_index)
            
            # Ensure correct size
            if processed.shape[:2] != (height, width):
                processed = cv2.resize(processed, (width, height))
            
            # Ensure 3 channels
            if len(processed.shape) == 2:
                processed = cv2.cvtColor(processed, cv2.COLOR_GRAY2BGR)
            elif processed.shape[2] == 4:
                processed = cv2.cvtColor(processed, cv2.COLOR_BGRA2BGR)
            
            writer.write(processed)
            
            frame_index += 1
            
            if progress_callback:
                progress_callback(frame_index, total_frames)
        
        cap.release()
        writer.release()
    
    @staticmethod
    def create_thumbnail(video_path: str, 
                         width: int = 320,
                         frame_index: Optional[int] = None) -> Optional[np.ndarray]:
        """
        Create a thumbnail image from a video.
        
        Args:
            video_path: Path to video file
            width: Thumbnail width (height auto-calculated)
            frame_index: Frame to use (None = middle frame)
            
        Returns:
            Thumbnail image or None
        """
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            return None
        
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if frame_index is None:
            frame_index = total // 2
        
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            return None
        
        # Resize
        h, w = frame.shape[:2]
        ratio = width / w
        new_height = int(h * ratio)
        
        return cv2.resize(frame, (width, new_height))
    
    @staticmethod
    def time_to_frame(time_seconds: float, fps: float) -> int:
        """Convert time in seconds to frame index."""
        return int(time_seconds * fps)
    
    @staticmethod
    def frame_to_time(frame_index: int, fps: float) -> float:
        """Convert frame index to time in seconds."""
        return frame_index / fps
    
    @staticmethod
    def format_time(seconds: float) -> str:
        """Format time in seconds to HH:MM:SS.mmm string."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"
        else:
            return f"{minutes:02d}:{secs:06.3f}"
