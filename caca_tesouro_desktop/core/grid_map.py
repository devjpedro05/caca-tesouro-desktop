"""
Grid-based map system for tile-based movement
Converts graph structure to 2D grid representation
"""
from enum import Enum
from typing import Dict, Tuple, List, Optional

class TileType(Enum):
    """Types of tiles in the grid"""
    EMPTY = 0
    PATH = 1
    WALL = 2
    TREASURE = 3
    MONSTER = 4
    RESOURCE = 5
    START = 6

class GridMap:
    """Grid-based map representation"""
    
    def __init__(self, width: int = 25, height: int = 25):
        self.width = width
        self.height = height
        self.tile_size = 50  # pixels per tile
        
        # Initialize grid with empty tiles
        self.tiles: List[List[TileType]] = [
            [TileType.EMPTY for _ in range(width)] 
            for _ in range(height)
        ]
        
        # Player positions in grid coordinates
        self.player_positions: Dict[int, Tuple[int, int]] = {}
        
        # Mapping from grid position to graph vertex
        self.grid_to_vertex: Dict[Tuple[int, int], int] = {}
        self.vertex_to_grid: Dict[int, Tuple[int, int]] = {}
        
        # Chambers
        self.chambers: List[Dict] = []
        
        # Obstacle manager
        from .obstacle_manager import ObstacleManager
        self.obstacle_manager = ObstacleManager()
    
    def create_from_graph(self, graph):
        """Convert graph structure to chamber-based grid layout"""
        
        # Define 6 chambers with their boundaries
        self.chambers = [
            # Chamber 0: Red Player Start (top-left)
            {'name': 'Start Vermelho', 'bounds': (2, 2, 8, 8), 'center': (5, 5)},
            # Chamber 1: Blue Player Start (bottom-left)
            {'name': 'Start Azul', 'bounds': (2, 16, 8, 22), 'center': (5, 19)},
            # Chamber 2: Central Chamber (middle)
            {'name': 'Câmara Central', 'bounds': (10, 10, 16, 16), 'center': (13, 13)},
            # Chamber 3: Treasure Chamber (right)
            {'name': 'Câmara do Tesouro', 'bounds': (18, 10, 23, 16), 'center': (20, 13)},
            # Chamber 4: Trap Chamber (top-right)
            {'name': 'Câmara de Armadilhas', 'bounds': (18, 2, 23, 8), 'center': (20, 5)},
            # Chamber 5: Resource Chamber (bottom-right)
            {'name': 'Câmara de Recursos', 'bounds': (18, 16, 23, 22), 'center': (20, 19)},
        ]
        
        # Fill chambers with PATH tiles
        for chamber in self.chambers:
            x1, y1, x2, y2 = chamber['bounds']
            for y in range(y1, y2 + 1):
                for x in range(x1, x2 + 1):
                    if 0 <= x < self.width and 0 <= y < self.height:
                        self.tiles[y][x] = TileType.PATH
        
        # Create corridors connecting chambers
        corridors = [
            # Red Start -> Central
            [(8, 5), (9, 5), (10, 5), (10, 6), (10, 7), (10, 8), (10, 9), (10, 10)],
            # Blue Start -> Central
            [(8, 19), (9, 19), (10, 19), (10, 18), (10, 17), (10, 16)],
            # Central -> Treasure
            [(16, 13), (17, 13), (18, 13)],
            # Central -> Trap Chamber
            [(13, 10), (13, 9), (13, 8), (14, 8), (15, 8), (16, 8), (17, 8), (18, 8), (18, 7), (18, 6), (18, 5)],
            # Central -> Resource Chamber
            [(13, 16), (13, 17), (13, 18), (13, 19), (14, 19), (15, 19), (16, 19), (17, 19), (18, 19)],
        ]
        
        for corridor in corridors:
            for x, y in corridor:
                if 0 <= x < self.width and 0 <= y < self.height:
                    self.tiles[y][x] = TileType.PATH
        
        # Map vertices to chamber centers
        vertex_positions = {
            0: (5, 5),    # Red Start
            1: (5, 19),   # Blue Start
            2: (13, 13),  # Central Chamber
            3: (20, 5),   # Trap Chamber
            4: (20, 19),  # Resource Chamber
            5: (20, 13),  # Treasure Chamber (moved from 6)
            6: (20, 13),  # Keep for compatibility
        }
        
        for vertex_id, (x, y) in vertex_positions.items():
            self.vertex_to_grid[vertex_id] = (x, y)
            self.grid_to_vertex[(x, y)] = vertex_id
            
            # Mark special tiles (with bounds checking)
            if 0 <= x < self.width and 0 <= y < self.height:
                if vertex_id == 6 or vertex_id == 5:  # Treasure
                    self.tiles[y][x] = TileType.TREASURE
                elif vertex_id == 0 or vertex_id == 1:  # Starts
                    self.tiles[y][x] = TileType.START
        
        # Fill remaining empty spaces with walls
        for y in range(self.height):
            for x in range(self.width):
                if self.tiles[y][x] == TileType.EMPTY:
                    self.tiles[y][x] = TileType.WALL
        
        print(f"✅ Grid map created: {self.width}x{self.height}")
        print(f"📍 Created {len(self.chambers)} chambers")
        print(f"📍 Mapped {len(vertex_positions)} vertices to grid")
        
        # Populate chambers with obstacles
        self._populate_obstacles()
    
    def _populate_obstacles(self):
        """Populate chambers with obstacles"""
        # Central Chamber - Monsters
        self.obstacle_manager.populate_chamber(
            self.chambers[2]['bounds'],  # Central chamber
            "central"
        )
        
        # Treasure Chamber - Locked door + chest
        self.obstacle_manager.populate_chamber(
            self.chambers[3]['bounds'],  # Treasure chamber
            "treasure"
        )
        
        # Trap Chamber - Traps
        self.obstacle_manager.populate_chamber(
            self.chambers[4]['bounds'],  # Trap chamber
            "trap"
        )
        
        # Resource Chamber - Loot chest
        self.obstacle_manager.populate_chamber(
            self.chambers[5]['bounds'],  # Resource chamber
            "resource"
        )
        
        print(f"🎯 Populated {len(self.obstacle_manager.get_all_obstacles())} obstacles")
    
    def can_move_to(self, x: int, y: int) -> bool:
        """Check if position is walkable"""
        # Out of bounds
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        
        # Check tile type
        tile = self.tiles[y][x]
        return tile in [TileType.PATH, TileType.TREASURE, TileType.START, TileType.RESOURCE]
    
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
