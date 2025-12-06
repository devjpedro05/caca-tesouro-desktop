"""Debug visual positions of monsters and players"""
from core.game_state import GameState
from core.grid_map import GridMap

# Create game
gs = GameState.new_default_game()

# Create grid map
grid_map = GridMap()
grid_map.create_from_graph(gs.graph)

print("\n=== CHAMBER GRID POSITIONS ===")
for vertex_id, chamber_info in grid_map.chambers.items():
    vertex = gs.graph.vertices[vertex_id]
    center = chamber_info['center']
    print(f"v{vertex_id}: {vertex.name}")
    print(f"  Grid center: {center}")
    print(f"  Pixel position: ({center[0] * grid_map.tile_size}, {center[1] * grid_map.tile_size})")
    if vertex.has_monster:
        print(f"  ⚔️ HAS MONSTER: {vertex.monster_type}")

print("\n=== PLAYER POSITIONS ===")
for p in gs.players:
    vertex_id = p.current_vertex_id
    vertex = gs.graph.vertices[vertex_id]
    center = grid_map.chambers[vertex_id]['center']
    print(f"{p.name}:")
    print(f"  Vertex: v{vertex_id} ({vertex.name})")
    print(f"  Grid center: {center}")
    print(f"  Pixel position: ({center[0] * grid_map.tile_size}, {center[1] * grid_map.tile_size})")

print("\n=== MONSTERS ===")
for vertex_id, monster_state in gs.monster_system.active_monsters.items():
    vertex = gs.graph.vertices[vertex_id]
    center = grid_map.chambers[vertex_id]['center']
    print(f"{monster_state.monster.monster_type.value} at v{vertex_id} ({vertex.name}):")
    print(f"  Grid center: {center}")
    print(f"  Pixel position: ({center[0] * grid_map.tile_size}, {center[1] * grid_map.tile_size})")
