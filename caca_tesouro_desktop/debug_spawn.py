"""Debug script to check monster spawn positions"""
from core.game_state import GameState

# Create game
gs = GameState.new_default_game()

print("\n=== GRAPH STRUCTURE ===")
for v in gs.graph.vertices.values():
    print(f"v{v.id}: {v.name} at ({v.x}, {v.y})")
    if v.has_monster:
        print(f"  -> HAS MONSTER: {v.monster_type}")

print("\n=== PLAYER POSITIONS ===")
for p in gs.players:
    print(f"{p.name}: vertex {p.current_vertex_id} ({gs.graph.vertices[p.current_vertex_id].name})")

print("\n=== ACTIVE MONSTERS ===")
for vertex_id, monster_state in gs.monster_system.active_monsters.items():
    vertex = gs.graph.vertices[vertex_id]
    print(f"Monster at v{vertex_id}: {vertex.name} - {monster_state.monster.monster_type.value}")
