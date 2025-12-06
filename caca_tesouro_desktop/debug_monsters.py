"""
Debug script to check if monsters are being spawned
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.game_state import GameState

gs = GameState.new_default_game()

print("=== GRAPH VERTICES ===")
for v_id, vertex in gs.graph.vertices.items():
    print(f"  Vertex {v_id}: {vertex.name}, has_monster={vertex.has_monster}, monster_type={vertex.monster_type}")

print("\n=== MONSTER SYSTEM ===")
if hasattr(gs, 'monster_system') and gs.monster_system:
    print(f"  MonsterSystem exists: {gs.monster_system}")
    print(f"  Active monsters: {list(gs.monster_system.active_monsters.keys())}")
    
    for v_id, monster_state in gs.monster_system.active_monsters.items():
        print(f"  - Vertex {v_id}: {monster_state}")
else:
    print("  NO MONSTER SYSTEM!")

print("\n=== GRID MAP CHAMBERS ===")
# We need to create the grid map to check chambers
from core.grid_map import GridMap
grid_map = GridMap()
grid_map.create_from_graph(gs.graph)

for v_id, chamber in grid_map.chambers.items():
    print(f"  Vertex {v_id}: center={chamber['center']}, bounds={chamber['bounds']}")
