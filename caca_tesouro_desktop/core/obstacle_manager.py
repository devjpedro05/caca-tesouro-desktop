"""
Obstacle management system for interactive game elements
Handles monsters, doors, chests, traps, and other obstacles
"""
from enum import Enum
from typing import Dict, Tuple, Optional, List
from dataclasses import dataclass

class ObstacleType(Enum):
    """Types of obstacles in the game"""
    MONSTER = "monster"
    DOOR_LOCKED = "door_locked"
    CHEST = "chest"
    TRAP = "trap"
    WALL_DESTRUCTIBLE = "wall_destructible"
    PIT = "pit"

@dataclass
class Obstacle:
    """Represents an obstacle on the map"""
    obstacle_type: ObstacleType
    position: Tuple[int, int]  # (x, y) grid coordinates
    is_active: bool = True
    required_item: Optional[str] = None  # Item needed to pass/interact
    data: Dict = None  # Additional data (monster stats, chest loot, etc.)
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}

class ObstacleManager:
    """Manages all obstacles on the map"""
    
    def __init__(self):
        self.obstacles: Dict[Tuple[int, int], Obstacle] = {}
    
    def add_obstacle(self, obstacle: Obstacle):
        """Add an obstacle to the map"""
        self.obstacles[obstacle.position] = obstacle
    
    def remove_obstacle(self, position: Tuple[int, int]):
        """Remove an obstacle from the map"""
        if position in self.obstacles:
            del self.obstacles[position]
    
    def get_obstacle(self, position: Tuple[int, int]) -> Optional[Obstacle]:
        """Get obstacle at position"""
        return self.obstacles.get(position)
    
    def has_obstacle(self, position: Tuple[int, int]) -> bool:
        """Check if there's an obstacle at position"""
        obstacle = self.obstacles.get(position)
        return obstacle is not None and obstacle.is_active
    
    def can_pass(self, position: Tuple[int, int], player) -> bool:
        """Check if player can pass through this position"""
        obstacle = self.get_obstacle(position)
        if not obstacle or not obstacle.is_active:
            return True
        
        # Check if player has required item
        if obstacle.required_item:
            # TODO: Check player inventory
            return False
        
        # Monsters block passage until defeated
        if obstacle.obstacle_type == ObstacleType.MONSTER:
            return False
        
        # Locked doors block passage
        if obstacle.obstacle_type == ObstacleType.DOOR_LOCKED:
            return False
        
        # Destructible walls block passage
        if obstacle.obstacle_type == ObstacleType.WALL_DESTRUCTIBLE:
            return False
        
        # Pits block passage without rope/teleport
        if obstacle.obstacle_type == ObstacleType.PIT:
            return False
        
        # Chests and traps don't block movement
        return True
    
    def populate_chamber(self, chamber_bounds: Tuple[int, int, int, int], chamber_type: str):
        """Populate a chamber with appropriate obstacles"""
        x1, y1, x2, y2 = chamber_bounds
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        
        if chamber_type == "central":
            # Add monsters to central chamber
            self.add_obstacle(Obstacle(
                ObstacleType.MONSTER,
                (center_x - 1, center_y),
                data={"level": 2, "type": "orc"}
            ))
            self.add_obstacle(Obstacle(
                ObstacleType.MONSTER,
                (center_x + 1, center_y),
                data={"level": 2, "type": "goblin"}
            ))
        
        elif chamber_type == "treasure":
            # Add locked door before treasure
            self.add_obstacle(Obstacle(
                ObstacleType.DOOR_LOCKED,
                (x1, center_y),
                required_item="golden_key"
            ))
            # Add treasure chest
            self.add_obstacle(Obstacle(
                ObstacleType.CHEST,
                (center_x, center_y),
                data={"loot": ["gold:100", "gem:5"]}
            ))
        
        elif chamber_type == "trap":
            # Add traps
            for i in range(3):
                self.add_obstacle(Obstacle(
                    ObstacleType.TRAP,
                    (center_x - 1 + i, center_y - 1),
                    data={"damage": 10}
                ))
        
        elif chamber_type == "resource":
            # Add resource chests
            self.add_obstacle(Obstacle(
                ObstacleType.CHEST,
                (center_x, center_y),
                data={"loot": ["potion:3", "key:1"]}
            ))
    
    def get_all_obstacles(self) -> List[Obstacle]:
        """Get list of all obstacles"""
        return list(self.obstacles.values())
    
    def get_obstacles_by_type(self, obstacle_type: ObstacleType) -> List[Obstacle]:
        """Get all obstacles of a specific type"""
        return [obs for obs in self.obstacles.values() if obs.obstacle_type == obstacle_type]
