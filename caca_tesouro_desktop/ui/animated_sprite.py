"""
Animated Sprite System for Character Animation
Handles sprite sheet loading, frame extraction, and animation
"""
from PySide6.QtWidgets import QGraphicsPixmapItem
from PySide6.QtGui import QPixmap, QPainter
from PySide6.QtCore import QTimer, QRectF, Qt
import os

class AnimatedSprite(QGraphicsPixmapItem):
    """Animated sprite that cycles through frames"""
    
    def __init__(self, sprite_sheet_path, frame_width=64, frame_height=64, parent=None):
        super().__init__(parent)
        
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.current_frame = 0
        self.frames = []
        
        # Animation settings
        self.animation_speed = 200  # ms per frame
        self.is_animating = True
        
        # Load sprite sheet and extract frames
        self.load_sprite_sheet(sprite_sheet_path)
        
        # Setup animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_frame)
        
        # Start idle animation
        self.start_idle_animation()
    
    def load_sprite_sheet(self, path):
        """Load sprite sheet and extract individual frames"""
        if not os.path.exists(path):
            print(f"❌ Sprite sheet not found: {path}")
            return
        
        sprite_sheet = QPixmap(path)
        if sprite_sheet.isNull():
            print(f"❌ Failed to load sprite sheet: {path}")
            return
        
        print(f"✅ Loaded sprite sheet: {sprite_sheet.width()}x{sprite_sheet.height()}")
        
        # Calculate actual frame size from sprite sheet
        # The sprite sheet has 4 columns x 4 rows (each row has 4 different poses)
        cols = 4  # Changed from 2 to 4
        rows = 4
        actual_frame_width = sprite_sheet.width() // cols
        actual_frame_height = sprite_sheet.height() // rows
        
        print(f"📐 Calculated frame size: {actual_frame_width}x{actual_frame_height}")
        print(f"📐 Grid: {cols} cols x {rows} rows")
        
        # Extract each frame
        for row in range(rows):
            for col in range(cols):
                x = col * actual_frame_width
                y = row * actual_frame_height
                
                # Extract frame
                frame = sprite_sheet.copy(x, y, actual_frame_width, actual_frame_height)
                self.frames.append(frame)
        
        print(f"✅ Extracted {len(self.frames)} frames")
        
        # Debug: print first frame size
        if self.frames:
            print(f"📏 Frame 0 size: {self.frames[0].width()}x{self.frames[0].height()}")
        
        # Set initial frame
        if self.frames:
            self.setPixmap(self.frames[0])
            # Scale down significantly (343x256 is too large)
            # Scale to ~50 pixels wide: 50/343 ≈ 0.15
            self.setScale(0.15)
            print(f"✅ Set initial frame and scale (0.15x)")
    
    def start_idle_animation(self):
        """Start idle breathing animation (frames 0-1)"""
        # Row 0, columns 0-1: front-facing poses
        self.animation_frames = [0, 1]
        self.current_frame_index = 0
        self.timer.start(self.animation_speed * 3)  # Slower for idle (600ms)
    
    def start_walk_animation(self, direction="down"):
        """Start walking animation"""
        # Map directions to frame ranges (4x4 grid = 16 frames total)
        # Row 0 (frames 0-3): Front views
        # Row 1 (frames 4-7): Right views  
        # Row 2 (frames 8-11): Left views
        # Row 3 (frames 12-15): Back views
        direction_frames = {
            "down": [0, 1],      # Row 0, cols 0-1: Front
            "right": [4, 5],     # Row 1, cols 0-1: Right
            "left": [8, 9],      # Row 2, cols 0-1: Left  
            "up": [12, 13]       # Row 3, cols 0-1: Back
        }
        
        self.animation_frames = direction_frames.get(direction, [0, 1])
        self.current_frame_index = 0
        self.timer.start(self.animation_speed)
    
    def next_frame(self):
        """Advance to next animation frame"""
        if not self.frames or not self.animation_frames:
            return
        
        self.current_frame_index = (self.current_frame_index + 1) % len(self.animation_frames)
        frame_number = self.animation_frames[self.current_frame_index]
        
        if frame_number < len(self.frames):
            # Set the pixmap to the specific frame
            self.setPixmap(self.frames[frame_number])
            # Debug: verify we're showing the right frame
            # print(f"🎬 Showing frame {frame_number}")
    
    def stop_animation(self):
        """Stop animation"""
        self.timer.stop()
    
    def resume_animation(self):
        """Resume animation"""
        if not self.timer.isActive():
            self.timer.start(self.animation_speed)
