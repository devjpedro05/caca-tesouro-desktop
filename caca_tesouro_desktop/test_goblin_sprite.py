"""
Test Goblin Sprite Loading
"""
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene
from ui.goblin_sprite import GoblinSprite

def test_goblin_sprite():
    """Test loading and displaying Goblin sprite"""
    app = QApplication(sys.argv)
    
    # Create scene and view
    scene = QGraphicsScene()
    view = QGraphicsView(scene)
    view.setWindowTitle("Test Goblin Sprite")
    view.resize(400, 400)
    
    # Create Goblin sprite
    goblin = GoblinSprite()
    goblin.setPos(100, 100)
    scene.addItem(goblin)
    
    # Show view
    view.show()
    
    print("✅ Goblin sprite test window created")
    print("   Walking right animation should be playing")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    test_goblin_sprite()
