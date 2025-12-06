"""
Goblin Animated Sprite System
Uses individual frame images for Goblin animation
"""
from PySide6.QtWidgets import QGraphicsPixmapItem, QGraphicsRectItem, QGraphicsTextItem
from PySide6.QtGui import QPixmap, QBrush, QPen, QColor, QFont
from PySide6.QtCore import QTimer, Qt
import os
import glob

class GoblinSprite(QGraphicsPixmapItem):
    """Animated Goblin sprite using individual frame files"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Get frames directory
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.frames_directory = os.path.join(base_dir, "assets", "themes", "Goblin")
        
        self.frames = {}  # Dictionary: {state: [frames]}
        self.current_state = "walk_right"
        self.current_frame_index = 0
        
        # Animation settings
        self.animation_speed = 200  # ms per frame (slower, smoother animation)
        self.is_animating = True
        
        # HP bar settings
        self.max_hp = 100
        self.current_hp = 100
        self.hp_bar_width = 100  # Increased significantly
        self.hp_bar_height = 14  # Much taller
        self.level = 1  # Default level
        
        # Animation for HP bar
        self.target_hp_width = self.hp_bar_width
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._animate_hp_bar)
        self.animation_speed_hp = 30  # Faster animation updates (50->30ms)
        
        # Load all frames
        self.load_frames()
        
        # Create HP bar (will be positioned relative to sprite)
        self._create_hp_bar()
        
        # Setup animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_frame)
        
        # Start walking animation
        self.start_animation("walk_right")
    
    def load_frames(self):
        """Load all Goblin frame images from directory"""
        if not os.path.exists(self.frames_directory):
            print(f"❌ Goblin frames directory not found: {self.frames_directory}")
            return
        
        # Load walking right frames (5 frames)
        right_frames = []
        for i in range(1, 6):
            frame_path = os.path.join(self.frames_directory, f"Goblin Andando para a direita - Frame {i}.png")
            if os.path.exists(frame_path):
                pixmap = QPixmap(frame_path)
                if not pixmap.isNull():
                    right_frames.append(pixmap)
                else:
                    print(f"❌ Failed to load: {frame_path}")
            else:
                print(f"⚠️ File not found: {frame_path}")
        
        if right_frames:
            self.frames["walk_right"] = right_frames
            print(f"✅ Loaded {len(right_frames)} frames for walk_right")
        
        # Load walking left frames (5 frames)
        left_frames = []
        for i in range(1, 6):
            # Handle the inconsistent naming (Frame 2 has different spacing)
            if i == 2:
                frame_path = os.path.join(self.frames_directory, f"Goblin Andando para a Esquerda- Frame {i}.png")
            else:
                frame_path = os.path.join(self.frames_directory, f"Goblin Andando para a Esquerda - Frame {i}.png")
            
            if os.path.exists(frame_path):
                pixmap = QPixmap(frame_path)
                if not pixmap.isNull():
                    left_frames.append(pixmap)
                else:
                    print(f"❌ Failed to load: {frame_path}")
            else:
                print(f"⚠️ File not found: {frame_path}")
        
        if left_frames:
            self.frames["walk_left"] = left_frames
            print(f"✅ Loaded {len(left_frames)} frames for walk_left")
        
        # Load death frames (4 frames)
        death_frames = []
        for i in range(1, 5):
            frame_path = os.path.join(self.frames_directory, f"Goblin morrendo - Frame {i}.png")
            if os.path.exists(frame_path):
                pixmap = QPixmap(frame_path)
                if not pixmap.isNull():
                    death_frames.append(pixmap)
                else:
                    print(f"❌ Failed to load: {frame_path}")
            else:
                print(f"⚠️ File not found: {frame_path}")
        
        if death_frames:
            self.frames["death"] = death_frames
            print(f"✅ Loaded {len(death_frames)} frames for death")
        
        print(f"✅ Total Goblin animation states loaded: {len(self.frames)}")
        
        # Set initial frame
        if "walk_right" in self.frames and self.frames["walk_right"]:
            self.setPixmap(self.frames["walk_right"][0])
            # Scale to appropriate size (adjust based on actual frame size)
            self.setScale(0.12)
            print(f"✅ Set initial Goblin frame with scale 0.12")
    
    def start_animation(self, state):
        """Start animation for given state"""
        if state not in self.frames or not self.frames[state]:
            print(f"⚠️ State '{state}' not found or empty")
            return
        
        self.current_state = state
        self.current_frame_index = 0
        
        # Set animation speed based on state
        if state == "death":
            self.timer.start(200)  # Slower death animation
        else:
            self.timer.start(self.animation_speed)
    
    def next_frame(self):
        """Advance to next animation frame"""
        if self.current_state not in self.frames:
            return
        
        current_frames = self.frames[self.current_state]
        if not current_frames:
            return
        
        # Safety check: verify object is still valid
        try:
            # For death animation, play once and stop at last frame
            if self.current_state == "death":
                if self.current_frame_index < len(current_frames) - 1:
                    self.current_frame_index += 1
                    self.setPixmap(current_frames[self.current_frame_index])
                else:
                    # Stay on last frame
                    self.timer.stop()
            else:
                # Cycle through frames for walking
                self.current_frame_index = (self.current_frame_index + 1) % len(current_frames)
                self.setPixmap(current_frames[self.current_frame_index])
        except RuntimeError:
            # Object was deleted, stop the timer
            self.timer.stop()
            return
    
    def walk_right(self):
        """Start walking right animation"""
        self.start_animation("walk_right")
    
    def walk_left(self):
        """Start walking left animation"""
        self.start_animation("walk_left")
    
    def die(self):
        """Play death animation"""
        self.start_animation("death")
    
    def _create_hp_bar(self):
        """Create HP bar graphics above the sprite"""
        # Background bar (dark red)
        self.hp_bar_bg = QGraphicsRectItem(-10, -25, self.hp_bar_width, self.hp_bar_height, self)
        self.hp_bar_bg.setBrush(QBrush(QColor("#2A0000")))  # Very dark red
        self.hp_bar_bg.setPen(QPen(QColor("#000000"), 3))  # Thick black border
        self.hp_bar_bg.setZValue(10)
        
        # Foreground bar (green, represents current HP)
        self.hp_bar_fg = QGraphicsRectItem(-10, -25, self.hp_bar_width, self.hp_bar_height, self)
        self.hp_bar_fg.setBrush(QBrush(QColor("#00FF00")))  # Bright green
        self.hp_bar_fg.setPen(QPen(Qt.PenStyle.NoPen))
        self.hp_bar_fg.setZValue(11)
        
        # Level text (displayed to the right of HP bar)
        self.level_text = QGraphicsTextItem(self)
        self.level_text.setPlainText(f"Lv.{self.level}")
        self.level_text.setDefaultTextColor(QColor("#FFFF00"))  # Yellow
        font = QFont("Arial", 10, QFont.Weight.Bold)
        self.level_text.setFont(font)
        self.level_text.setPos(self.hp_bar_width - 5, -28)  # Position to right of HP bar
        self.level_text.setZValue(12)
    
    def _animate_hp_bar(self):
        """Animate HP bar smoothly transitioning to target width"""
        current_rect = self.hp_bar_fg.rect()
        current_width = current_rect.width()
        
        # Calculate difference
        diff = self.target_hp_width - current_width
        
        # If close enough, snap to target and stop animation
        if abs(diff) < 0.3:
            self.hp_bar_fg.setRect(-10, -25, self.target_hp_width, self.hp_bar_height)
            self.animation_timer.stop()
            return
        
        # Smoothly interpolate (move 15% of the way each frame for visible animation)
        new_width = current_width + (diff * 0.15)
        self.hp_bar_fg.setRect(-10, -25, new_width, self.hp_bar_height)
    
    def update_hp(self, current_hp, max_hp=None):
        """Update HP bar to reflect current health with smooth animation
        
        Args:
            current_hp: Current HP value
            max_hp: Maximum HP value (optional, uses stored max_hp if not provided)
        """
        if max_hp is not None:
            self.max_hp = max_hp
        
        self.current_hp = max(0, min(current_hp, self.max_hp))
        
        # Calculate HP percentage
        hp_percent = self.current_hp / self.max_hp if self.max_hp > 0 else 0
        
        # Calculate target width for animation
        self.target_hp_width = self.hp_bar_width * hp_percent
        
        # Change color based on HP percentage
        if hp_percent > 0.6:
            color = QColor("#00FF00")  # Green
        elif hp_percent > 0.3:
            color = QColor("#FFA500")  # Orange
        else:
            color = QColor("#FF0000")  # Red
        
        self.hp_bar_fg.setBrush(QBrush(color))
        
        # Start smooth animation to target width
        if not self.animation_timer.isActive():
            self.animation_timer.start(self.animation_speed_hp)
    
    def set_level(self, level):
        """Set the Goblin's level and update the display
        
        Args:
            level: The level number to display
        """
        self.level = level
        if hasattr(self, 'level_text'):
            self.level_text.setPlainText(f"Lv.{self.level}")

    def stop_animation(self):
        """Stop animation"""
        self.timer.stop()
    
    def resume_animation(self):
        """Resume animation"""
        if not self.timer.isActive() and self.current_state != "death":
            self.timer.start(self.animation_speed)
