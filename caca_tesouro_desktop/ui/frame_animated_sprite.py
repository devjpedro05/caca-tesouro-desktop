"""
Frame-Based Animated Sprite System
Uses individual frame images for character animation
"""
from PySide6.QtWidgets import QGraphicsPixmapItem
from PySide6.QtGui import QPixmap
from PySide6.QtCore import QTimer
import os
import glob

class FrameAnimatedSprite(QGraphicsPixmapItem):
    """Animated sprite using individual frame files"""
    
    def __init__(self, frames_directory, parent=None):
        super().__init__(parent)
        
        self.frames_directory = frames_directory
        self.frames = {}  # Dictionary: {state: [pixmap1, pixmap2, ...]}
        self.current_state = "idle_down"
        self.current_frame_index = 0
        
        # Animation settings
        self.animation_speed = 100  # ms per frame (snappy)
        self.is_animating = True
        
        # Load all frames
        self.load_frames()
        
        # Setup animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_frame)
        
        # Start idle animation
        self.start_animation("idle_down")
    
    def load_frames(self):
        """Load all frame images from directory"""
        if not os.path.exists(self.frames_directory):
            print(f"❌ Frames directory not found: {self.frames_directory}")
            return
        
        # Map file patterns to animation states
        frame_patterns = {
            "idle_down": "*Parado*frente*.png",
            "idle_up": "*Parado*Costas*.png",
            "idle_right": "*Parado*Direito*.png",
            "idle_left": "*Parado*Esquerdo*.png",
            "walk_down": "*Andando*frente*.png",
            "walk_up": "*Andando*Costas*.png",
            "walk_right": "*Andando*Direito*.png",
            "walk_left": "*Andando*Esquerdo*.png",
        }
        
        for state, pattern in frame_patterns.items():
            # Find matching files
            search_path = os.path.join(self.frames_directory, pattern)
            matching_files = glob.glob(search_path)
            
            # Sort files to ensure correct frame order (e.g. 1.png, 2.png)
            matching_files.sort()
            
            if matching_files:
                self.frames[state] = []
                for frame_path in matching_files:
                    pixmap = QPixmap(frame_path)
                    if not pixmap.isNull():
                        self.frames[state].append(pixmap)
                    else:
                        print(f"❌ Failed to load {state}: {frame_path}")
            else:
                pass
        
        # Set initial frame
        if "idle_down" in self.frames and self.frames["idle_down"]:
            self.setPixmap(self.frames["idle_down"][0])
            self.setScale(0.08)
    
    def start_animation(self, state):
        """Start animation for given state"""
        # Fallback if state has no frames
        if state not in self.frames or not self.frames[state]:
            # Try basic fallback
            if "idle_down" in self.frames and self.frames["idle_down"]:
                state = "idle_down"
            else:
                return

        self.current_state = state
        self.current_frame_index = 0
        
        # Set first frame immediately
        self.setPixmap(self.frames[state][0])
        
        # Start timer
        self.timer.start(self.animation_speed)
    
    def next_frame(self):
        """Advance to next animation frame"""
        frame_list = self.frames.get(self.current_state)
        if not frame_list:
            return
        
        # Safety check: verify object is valid
        try:
            # Cycle through frames
            self.current_frame_index = (self.current_frame_index + 1) % len(frame_list)
            self.setPixmap(frame_list[self.current_frame_index])
        except RuntimeError:
            self.timer.stop()
            return

    def set_direction(self, direction):
        """Change animation direction (up, down, left, right)"""
        if f"idle_{direction}" != self.current_state:
            self.start_animation(f"idle_{direction}")
    
    def start_walking(self, direction):
        """Start walking animation in given direction"""
        target_state = f"walk_{direction}"
        if target_state != self.current_state:
            self.start_animation(target_state)
    
    def stop_walking(self):
        """Stop walking and return to idle"""
        # Determine current direction from state string
        parts = self.current_state.split("_")
        direction = parts[1] if len(parts) > 1 else "down"
        
        target_state = f"idle_{direction}"
        if target_state != self.current_state:
            self.start_animation(target_state)
    
    def stop_animation(self):
        """Stop animation"""
        self.timer.stop()
    
    def resume_animation(self):
        """Resume animation"""
        if not self.timer.isActive():
            self.timer.start(self.animation_speed)
