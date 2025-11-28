"""
Grid-based map system for tile-based movement
Converts graph structure to 2D grid with chambers and tunnels
"""
from enum import Enum
from typing import Dict, Tuple, List, Optional

class TileType(Enum):
    """Types of tiles in the grid"""
    EMPTY = 0
    WALL = 1
    CHAMBER = 2  # Câmara (2x2) - vértice do grafo
    TUNNEL = 3   # Túnel (1x1) - aresta do grafo
    TREASURE = 4
    START = 5

class GridMap:
    """Grid-based map representation with chambers and tunnels"""
    
    def __init__(self, width: int = 20, height: int = 20):
        self.width = width
        self.height = height
        self.tile_size = 50  # pixels per tile
        
        # Initialize grid with walls
        self.tiles: List[List[TileType]] = [
            [TileType.WALL for _ in range(width)] 
            for _ in range(height)
        ]
        
        # Player positions in grid coordinates
        self.player_positions: Dict[int, Tuple[int, int]] = {}
        
        # Mapping from grid position to graph vertex
        self.grid_to_vertex: Dict[Tuple[int, int], int] = {}
        self.vertex_to_grid: Dict[int, Tuple[int, int]] = {}
        
        # Chambers (2x2 each) - vertices of the graph
        self.chambers: Dict[int, Dict] = {}  # {vertex_id: {bounds, center, name}}
        
        # Tunnels (1x1 paths) - edges of the graph
        self.tunnels: List[List[Tuple[int, int]]] = []  # List of paths
        
        # Obstacle manager
        from .obstacle_manager import ObstacleManager
        self.obstacle_manager = ObstacleManager()
    
    def create_from_graph(self, graph):
        """Convert graph structure to chamber-based grid layout"""
        
        # Define chamber positions for 7 vertices (2x2 each)
        # Layout designed to fit in 20x20 grid
        chamber_positions = {
            0: (9, 2),   # Start (top center)
            1: (3, 6),   # Left upper
            2: (2, 11),  # Left lower
            3: (9, 15),  # Bottom center
            4: (15, 6),  # Right upper
            5: (9, 9),   # Center
            6: (9, 18),  # Treasure (bottom)
        }
        
        # Create 2x2 chambers for each vertex
        for vertex_id, (cx, cy) in chamber_positions.items():
            # Chamber is 2x2 centered at (cx, cy)
            x1, y1 = cx, cy
            x2, y2 = cx + 1, cy + 1
            
            self.chambers[vertex_id] = {
                'bounds': (x1, y1, x2, y2),
                'center': (cx, cy),
                'name': graph.vertices[vertex_id].name if vertex_id < len(graph.vertices) else f'Câmara {vertex_id}'
            }
            
            # Fill chamber with CHAMBER tiles
            for y in range(y1, y2 + 1):
                for x in range(x1, x2 + 1):
                    if 0 <= x < self.width and 0 <= y < self.height:
                        self.tiles[y][x] = TileType.CHAMBER
            
            # Map vertex to grid position (center of chamber)
            self.vertex_to_grid[vertex_id] = (cx, cy)
            self.grid_to_vertex[(cx, cy)] = vertex_id
            
            # Mark special tiles
            if vertex_id == 6:  # Treasure
                self.tiles[cy][cx] = TileType.TREASURE
            elif vertex_id == 0:  # Start
                self.tiles[cy][cx] = TileType.START
        
        # Create tunnels (1x1) for each edge in the graph
        for vertex_id in graph.vertices.keys():
            neighbors_list = graph.neighbors(vertex_id)
            for neighbor_id, edge in neighbors_list:
                if vertex_id < neighbor_id:  # Avoid duplicates
                    # Create tunnel between chambers
                    start_pos = chamber_positions[vertex_id]
                    end_pos = chamber_positions[neighbor_id]
                    tunnel_path = self._create_tunnel(start_pos, end_pos)
                    self.tunnels.append(tunnel_path)
                    
                    # Mark tunnel tiles
                    for x, y in tunnel_path:
                        if 0 <= x < self.width and 0 <= y < self.height:
                            if self.tiles[y][x] == TileType.WALL:  # Don't overwrite chambers
                                self.tiles[y][x] = TileType.TUNNEL
        
        print(f"✅ Grid map created: {self.width}x{self.height}")
        print(f"📍 Created {len(self.chambers)} chambers (2x2 each)")
        print(f"🔗 Created {len(self.tunnels)} tunnels")
        
        # Populate chambers with obstacles
        self._populate_obstacles()
    
    def _create_tunnel(self, start: Tuple[int, int], end: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Create 1x1 tunnel path between two chambers using Manhattan pathfinding"""
        x1, y1 = start
        x2, y2 = end
        path = []
        
        # Move horizontally first
        current_x, current_y = x1, y1
        while current_x != x2:
            current_x += 1 if x2 > current_x else -1
            path.append((current_x, current_y))
        
        # Then move vertically
        while current_y != y2:
            current_y += 1 if y2 > current_y else -1
            path.append((current_x, current_y))
        
        return path
    
    def _populate_obstacles(self):
        """Populate chambers with obstacles"""
        # Central Chamber (vertex 5) - Monsters
        if 5 in self.chambers:
            self.obstacle_manager.populate_chamber(
                self.chambers[5]['bounds'],
                "central"
            )
        
        # Treasure Chamber (vertex 6) - Locked door + chest
        if 6 in self.chambers:
            self.obstacle_manager.populate_chamber(
                self.chambers[6]['bounds'],
                "treasure"
            )
        
        print(f"🎯 Populated {len(self.obstacle_manager.get_all_obstacles())} obstacles")
    
    def can_move_to(self, x: int, y: int) -> bool:
        """Check if position is walkable"""
        # Out of bounds
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        
        # Check tile type
        tile = self.tiles[y][x]
        return tile in [TileType.CHAMBER, TileType.TUNNEL, TileType.TREASURE, TileType.START]
    
    def is_tunnel(self, x: int, y: int) -> bool:
        """Check if position is a tunnel"""
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        return self.tiles[y][x] == TileType.TUNNEL
    
    def get_tile(self, x: int, y: int) -> TileType:
        """Get tile type at position"""
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return TileType.WALL
        return self.tiles[y][x]
    
    def set_player_position(self, player_id: int, x: int, y: int):
        """Set player position in grid"""
        self.player_positions[player_id] = (x, y)
    
    def get_player_position(self, player_id: int) -> Optional[Tuple[int, int]]:
        """Get player position in grid"""
        return self.player_positions.get(player_id)
    
    def get_vertex_at_position(self, x: int, y: int) -> Optional[int]:
        """Get graph vertex ID at grid position"""
        return self.grid_to_vertex.get((x, y))
    
    def get_position_for_vertex(self, vertex_id: int) -> Optional[Tuple[int, int]]:
        """Get grid position for graph vertex"""
        return self.vertex_to_grid.get(vertex_id)
