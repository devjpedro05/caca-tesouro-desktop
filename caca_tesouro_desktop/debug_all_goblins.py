"""Debug ALL Goblin positions in the game"""
import sys
from PySide6.QtWidgets import QApplication
from core.game_state import GameState
from ui.grid_board_view import GridBoardView

# Create app
app = QApplication(sys.argv)

# Create game
gs = GameState.new_default_game()

# Create board view
board = GridBoardView(gs)

print("\n" + "="*60)
print("DEBUGGING ALL GOBLIN POSITIONS")
print("="*60)

print("\n=== VERTEX DATA ===")
for v in gs.graph.vertices.values():
    chamber = board.grid_map.chambers.get(v.id)
    if chamber:
        print(f"v{v.id}: {v.name:20} grid:{chamber['center']} pixel:({chamber['center'][0]*50},{chamber['center'][1]*50}) monster:{v.has_monster}")

print("\n=== PLAYER POSITIONS ===")
for p in gs.players:
    v_id = p.current_vertex_id
    chamber = board.grid_map.chambers[v_id]
    print(f"{p.name:20} v{v_id} grid:{chamber['center']} pixel:({chamber['center'][0]*50},{chamber['center'][1]*50})")

print("\n=== ACTIVE MONSTERS (MonsterSystem) ===")
for vertex_id, monster_state in gs.monster_system.active_monsters.items():
    chamber = board.grid_map.chambers[vertex_id]
    print(f"v{vertex_id}: {monster_state.monster.monster_type.value:15} grid:{chamber['center']} pixel:({chamber['center'][0]*50},{chamber['center'][1]*50})")

print("\n=== MONSTER SPRITES (Visual) ===")
if hasattr(board, 'monster_sprites'):
    for vertex_id, sprite in board.monster_sprites.items():
        chamber = board.grid_map.chambers[vertex_id]
        pos = sprite.pos()
        print(f"v{vertex_id}: Sprite at ({pos.x():.0f},{pos.y():.0f}) [chamber center grid:{chamber['center']}]")
else:
    print("No monster_sprites dict found!")

print("\n=== SCENE ITEMS (All GoblinSprite objects) ===")
from ui.goblin_sprite import GoblinSprite
goblin_count = 0
for item in board.scene.items():
    if isinstance(item, GoblinSprite):
        goblin_count += 1
        pos = item.pos()
        print(f"GoblinSprite #{goblin_count} at pixel ({pos.x():.0f},{pos.y():.0f})")

print(f"\nTotal GoblinSprite objects in scene: {goblin_count}")
print("="*60)

app.quit()
