"""
Script para verificar o estado visual do jogo após inicialização.
"""
from core.game_state import GameState
from ui.grid_board_view import GridBoardView
from PySide6.QtWidgets import QApplication, QGraphicsScene
import sys

# Create Qt application
app = QApplication(sys.argv)

# Create game state
print("=== CREATING GAME STATE ===")
gs = GameState.new_default_game()

# Create scene and view
scene = QGraphicsScene()
view = GridBoardView(gs, scene)

# Force initial draw
print("\n=== FORCING INITIAL DRAW ===")
view.refresh()

print("\n=== MONSTER DATA ===")
for vid, ms in gs.monster_system.active_monsters.items():
    print(f"v{vid}: {ms.monster.monster_type.value}")

print("\n=== MONSTER SPRITES IN DICT ===")
for vid, sprite in view.monster_sprites.items():
    print(f"v{vid}: sprite at pos({sprite.pos().x():.0f},{sprite.pos().y():.0f})")

print("\n=== ALL GOBLIN SPRITES IN SCENE ===")
from ui.goblin_sprite import GoblinSprite
all_items = scene.items()
goblin_count = 0
for item in all_items:
    if isinstance(item, GoblinSprite):
        goblin_count += 1
        print(f"GoblinSprite #{goblin_count} at pos({item.pos().x():.0f},{item.pos().y():.0f})")

print(f"\nTotal GoblinSprite in scene: {goblin_count}")

# Check if sprites are in the group instead
print("\n=== SPRITES IN _dyn_monsters GROUP ===")
if hasattr(view, '_dyn_monsters'):
    group_items = view._dyn_monsters.childItems()
    print(f"Items in group: {len(group_items)}")
    for i, item in enumerate(group_items):
        print(f"  Item {i}: {type(item).__name__} at pos({item.pos().x():.0f},{item.pos().y():.0f})")
else:
    print("NO _dyn_monsters group found!")

# Don't run the event loop, just exit
sys.exit(0)
