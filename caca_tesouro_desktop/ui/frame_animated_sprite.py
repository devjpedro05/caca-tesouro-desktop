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
        self.frames = {}  # Dictionary: {state: [frame1, frame2, ...]}
        self.current_state = "idle_down"
        self.current_frame_index = 0
        
        # Animation settings
        self.animation_speed = 150  # ms per frame (faster for smoother walking)
        self.idle_speed = 500  # ms per frame for idle (slower breathing)
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
            
            if matching_files:
                # Load the frame
                frame_path = matching_files[0]  # Take first match
                pixmap = QPixmap(frame_path)
                
                if not pixmap.isNull():
                    self.frames[state] = pixmap
                    # print(f"✅ Loaded {state}: {os.path.basename(frame_path)}")
                else:
                    print(f"❌ Failed to load {state}: {frame_path}")
            else:
                # print(f"⚠️ No frame found for {state} (pattern: {pattern})")
                pass
        
        # print(f"✅ Total frames loaded: {len(self.frames)}")
        
        # Set initial frame
        if "idle_down" in self.frames:
            self.setPixmap(self.frames["idle_down"])
            # Scale to appropriate size
            self.setScale(0.08)  # Adjust based on actual frame size
            # print(f"✅ Set initial frame (idle_down) with scale 0.08")
    
    def start_animation(self, state):
        """Start animation for given state"""
        if state not in self.frames:
            # print(f"⚠️ State '{state}' not found, using idle_down")
            state = "idle_down"
        
        self.current_state = state
        self.current_frame_index = 0
        
        # For idle animations, alternate between idle and walk frames
        if state.startswith("idle"):
            direction = state.split("_")[1]  # Extract direction (down, up, left, right)
            self.animation_frames = [f"idle_{direction}", f"walk_{direction}"]
            self.timer.start(self.idle_speed)  # Slower for breathing effect
        else:
            # Walking animation
            self.animation_frames = [state]
            self.timer.start(self.animation_speed)  # Faster for walking
    
    def next_frame(self):
        """Advance to next animation frame"""
        if not self.animation_frames:
            return
        
        # Safety check: verify object is still valid
        try:
            # Cycle through frames
            self.current_frame_index = (self.current_frame_index + 1) % len(self.animation_frames)
            frame_state = self.animation_frames[self.current_frame_index]
            
            if frame_state in self.frames:
                self.setPixmap(self.frames[frame_state])
        except RuntimeError:
            # Object was deleted, stop the timer
            self.timer.stop()
            return

    
    def set_direction(self, direction):
        """Change animation direction (up, down, left, right)"""
        self.start_animation(f"idle_{direction}")
    
    def start_walking(self, direction):
        """Start walking animation in given direction"""
        self.start_animation(f"walk_{direction}")
    
    def stop_walking(self):
        """Stop walking and return to idle"""
        # Extract current direction from current state
        if "_" in self.current_state:
            direction = self.current_state.split("_")[1]
            self.start_animation(f"idle_{direction}")
        else:
            self.start_animation("idle_down")
    
    def stop_animation(self):
        """Stop animation"""
        self.timer.stop()
    
    def resume_animation(self):
        """Resume animation"""
        if not self.timer.isActive():
            self.timer.start(self.animation_speed)
