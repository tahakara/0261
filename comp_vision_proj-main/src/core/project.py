"""
Project management for image/video editor.
Handles project state, file operations, and undo/redo.
"""

from enum import Enum, auto
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, field
from pathlib import Path
import json
import numpy as np
import cv2
from PySide6.QtCore import QObject, Signal

from .layer import LayerManager, Layer


class EditorMode(Enum):
    """Editor operation mode."""
    IMAGE = auto()
    VIDEO = auto()


@dataclass
class ProjectState:
    """Snapshot of project state for undo/redo."""
    layers_data: List[Dict[str, Any]]
    active_layer_index: int
    canvas_size: tuple


class Project(QObject):
    """
    Represents an editor project.
    Manages layers, canvas, and project-level operations.
    """
    
    # Signals
    project_changed = Signal()
    mode_changed = Signal(EditorMode)
    file_loaded = Signal(str)
    file_saved = Signal(str)
    canvas_size_changed = Signal(int, int)
    
    def __init__(self, mode: EditorMode = EditorMode.IMAGE):
        super().__init__()
        self._mode = mode
        self._layer_manager = LayerManager()
        self._file_path: Optional[Path] = None
        self._is_modified = False
        self._canvas_size = (800, 600)
        
        # Undo/Redo stacks
        self._undo_stack: List[ProjectState] = []
        self._redo_stack: List[ProjectState] = []
        self._max_undo = 50
        
        # Video specific
        self._video_path: Optional[Path] = None
        self._video_capture: Optional[cv2.VideoCapture] = None
        self._current_frame_index = 0
        self._total_frames = 0
        self._fps = 30.0
        
        # Connect layer manager signals
        self._layer_manager.layer_added.connect(self._on_layers_changed)
        self._layer_manager.layer_removed.connect(self._on_layers_changed)
        self._layer_manager.layer_changed.connect(self._on_layers_changed)
    
    @property
    def mode(self) -> EditorMode:
        return self._mode
    
    @property
    def layer_manager(self) -> LayerManager:
        return self._layer_manager
    
    @property
    def file_path(self) -> Optional[Path]:
        return self._file_path
    
    @property
    def is_modified(self) -> bool:
        return self._is_modified
    
    @property
    def canvas_size(self) -> tuple:
        return self._canvas_size
    
    @property
    def canvas_width(self) -> int:
        return self._canvas_size[0]
    
    @property
    def canvas_height(self) -> int:
        return self._canvas_size[1]
    
    # Video properties
    @property
    def is_video_mode(self) -> bool:
        return self._mode == EditorMode.VIDEO
    
    @property
    def current_frame_index(self) -> int:
        return self._current_frame_index
    
    @property
    def total_frames(self) -> int:
        return self._total_frames
    
    @property
    def fps(self) -> float:
        return self._fps
    
    @property
    def duration_seconds(self) -> float:
        if self._fps > 0:
            return self._total_frames / self._fps
        return 0.0
    
    def set_mode(self, mode: EditorMode):
        """Change editor mode."""
        if self._mode != mode:
            self._mode = mode
            self.mode_changed.emit(mode)
    
    def set_canvas_size(self, width: int, height: int):
        """Set canvas dimensions."""
        self._canvas_size = (width, height)
        self._layer_manager.set_canvas_size(width, height)
        self.canvas_size_changed.emit(width, height)
        self._mark_modified()
    
    def new_project(self, width: int = 800, height: int = 600):
        """Create a new empty project."""
        self._layer_manager.clear()
        self.set_canvas_size(width, height)
        self._file_path = None
        self._is_modified = False
        self._undo_stack.clear()
        self._redo_stack.clear()
        
        # Create initial background layer
        self._layer_manager.create_layer("Background", fill_color=(255, 255, 255, 255))
        self.project_changed.emit()
    
    def load_image(self, file_path: str) -> bool:
        """Load an image file into the project."""
        try:
            path = Path(file_path)
            # Read with OpenCV once and avoid extra copies where possible
            image = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
            
            if image is None:
                return False
            
            # Convert to BGRA if necessary (minimize conversions)
            if image.ndim == 2:
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGRA)
            elif image.shape[2] == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
            h, w = image.shape[:2]

            # Determine new canvas size: expand if the new image is larger
            cur_w, cur_h = self._canvas_size
            if self._layer_manager.layer_count == 0:
                # First image in project: set canvas to image size and avoid extra copy
                self.set_canvas_size(w, h)
            else:
                new_w = max(cur_w, w)
                new_h = max(cur_h, h)
                if (new_w, new_h) != (cur_w, cur_h):
                    # Expand project canvas and all existing layers to new canvas size
                    # Use Project.set_canvas_size so both Project and LayerManager stay in sync
                    self.set_canvas_size(new_w, new_h)

            # Prepare layer image sized to canvas. Avoid copying when possible by
            # placing image directly if canvas equals image size.
            canvas_w, canvas_h = self._canvas_size
            if (w, h) == (canvas_w, canvas_h):
                layer_img = image
            else:
                # Create transparent canvas and copy image into it
                canvas_img = np.zeros((canvas_h, canvas_w, 4), dtype=np.uint8)
                # Use slicing assignment (fast) rather than additional copies
                canvas_img[0:h, 0:w] = image
                layer_img = canvas_img

            layer = Layer(name=path.stem, image=layer_img)
            self._layer_manager.add_layer(layer)

            # Do not override project file path when adding images as layers
            self._is_modified = True
            self.file_loaded.emit(str(path))
            self.project_changed.emit()

            return True
        except Exception as e:
            print(f"Error loading image: {e}")
            return False
    
    def load_video(self, file_path: str) -> bool:
        """Load a video file for editing."""
        try:
            path = Path(file_path)
            cap = cv2.VideoCapture(str(path))
            
            if not cap.isOpened():
                return False
            
            self._video_capture = cap
            self._video_path = path
            self._total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self._fps = cap.get(cv2.CAP_PROP_FPS)
            
            w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            self.set_canvas_size(w, h)
            self._layer_manager.clear()
            
            # Load first frame as initial layer
            ret, frame = cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
                layer = Layer(name="Video Frame", image=frame)
                self._layer_manager.add_layer(layer)
            
            self._current_frame_index = 0
            self._file_path = path
            self.file_loaded.emit(str(path))
            self.project_changed.emit()
            
            return True
        except Exception as e:
            print(f"Error loading video: {e}")
            return False
    
    def get_video_frame(self, frame_index: int) -> Optional[np.ndarray]:
        """Get a specific frame from the loaded video."""
        if self._video_capture is None:
            return None
        
        self._video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ret, frame = self._video_capture.read()
        
        if ret:
            self._current_frame_index = frame_index
            return cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
        return None
    
    def save_image(self, file_path: Optional[str] = None) -> bool:
        """Save the flattened image to a file."""
        try:
            path = Path(file_path) if file_path else self._file_path
            if path is None:
                return False
            
            # Flatten all layers
            image = self._layer_manager.flatten()
            if image is None:
                return False
            
            # Convert based on file extension
            ext = path.suffix.lower()
            if ext in ['.jpg', '.jpeg']:
                image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
            
            cv2.imwrite(str(path), image)
            
            self._file_path = path
            self._is_modified = False
            self.file_saved.emit(str(path))
            
            return True
        except Exception as e:
            print(f"Error saving image: {e}")
            return False
    
    def get_composite_image(self) -> Optional[np.ndarray]:
        """Get the flattened composite of all layers."""
        return self._layer_manager.flatten()
    
    # Undo/Redo functionality
    def save_state(self):
        """Save current state for undo."""
        state = self._capture_state()
        self._undo_stack.append(state)
        self._redo_stack.clear()
        
        # Limit undo stack size
        while len(self._undo_stack) > self._max_undo:
            self._undo_stack.pop(0)
    
    def undo(self) -> bool:
        """Undo the last operation."""
        if not self._undo_stack:
            return False
        
        # Save current state to redo stack
        self._redo_stack.append(self._capture_state())
        
        # Restore previous state
        state = self._undo_stack.pop()
        self._restore_state(state)
        
        return True
    
    def redo(self) -> bool:
        """Redo the last undone operation."""
        if not self._redo_stack:
            return False
        
        # Save current state to undo stack
        self._undo_stack.append(self._capture_state())
        
        # Restore redo state
        state = self._redo_stack.pop()
        self._restore_state(state)
        
        return True
    
    def can_undo(self) -> bool:
        return len(self._undo_stack) > 0
    
    def can_redo(self) -> bool:
        return len(self._redo_stack) > 0
    
    def _capture_state(self) -> ProjectState:
        """Capture current project state."""
        layers_data = []
        for layer in self._layer_manager.layers:
            layers_data.append({
                'name': layer.name,
                'image': layer.image.copy() if layer.image is not None else None,
                'visible': layer.visible,
                'opacity': layer.opacity,
                'blend_mode': layer.blend_mode,
                'locked': layer.locked,
                'position': layer.position
            })
        
        return ProjectState(
            layers_data=layers_data,
            active_layer_index=self._layer_manager.active_index,
            canvas_size=self._canvas_size
        )
    
    def _restore_state(self, state: ProjectState):
        """Restore project to a saved state."""
        self._layer_manager.clear()
        self._canvas_size = state.canvas_size
        self._layer_manager.set_canvas_size(*state.canvas_size)
        
        for layer_data in state.layers_data:
            layer = Layer(
                name=layer_data['name'],
                image=layer_data['image'],
                visible=layer_data['visible'],
                opacity=layer_data['opacity'],
                blend_mode=layer_data['blend_mode'],
                locked=layer_data['locked'],
                position=layer_data['position']
            )
            self._layer_manager.add_layer(layer)
        
        self._layer_manager.set_active_layer(state.active_layer_index)
        self.project_changed.emit()
    
    def _on_layers_changed(self, *args):
        """Handle layer changes."""
        self._mark_modified()
    
    def _mark_modified(self):
        """Mark project as modified."""
        self._is_modified = True
        self.project_changed.emit()
    
    def cleanup(self):
        """Clean up resources."""
        if self._video_capture is not None:
            self._video_capture.release()
            self._video_capture = None
