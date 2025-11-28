"""
Fog of War system for dungeon exploration
Manages tile visibility and lighting effects
"""
from typing import Set, Tuple
import math

class FogOfWar:
    """Manages fog of war and lighting in the dungeon"""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        
        # Track which tiles have been explored (permanently revealed)
        self.explored: Set[Tuple[int, int]] = set()
        
        # Track currently visible tiles (around players)
        self.visible: Set[Tuple[int, int]] = set()
    
    def reveal(self, x: int, y: int, radius: int = 2):
        """Reveal tiles around a position with given radius"""
        revealed_tiles = set()
        
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                # Calculate distance (circular radius)
                distance = math.sqrt(dx * dx + dy * dy)
                
                if distance <= radius:
                    tile_x = x + dx
                    tile_y = y + dy
                    
                    # Check bounds
                    if 0 <= tile_x < self.width and 0 <= tile_y < self.height:
                        tile_pos = (tile_x, tile_y)
                        self.explored.add(tile_pos)
                        revealed_tiles.add(tile_pos)
        
        return revealed_tiles
    
    def update_visibility(self, player_positions: list, is_in_tunnel_func):
        """Update currently visible tiles based on player positions"""
        self.visible.clear()
        
        for x, y in player_positions:
            # Check if player is in tunnel
            in_tunnel = is_in_tunnel_func(x, y)
            
            # Smaller radius in tunnels, larger in chambers
            radius = 1 if in_tunnel else 3
            
            # Reveal and make visible
            revealed = self.reveal(x, y, radius)
            self.visible.update(revealed)
    
    def is_explored(self, x: int, y: int) -> bool:
        """Check if tile has been explored"""
        return (x, y) in self.explored
    
    def is_visible(self, x: int, y: int) -> bool:
        """Check if tile is currently visible"""
        return (x, y) in self.visible
    
    def get_fog_opacity(self, x: int, y: int) -> int:
        """Get fog opacity for a tile (0-255)"""
        if self.is_visible(x, y):
            return 0  # Fully visible
        elif self.is_explored(x, y):
            return 100  # Dimly lit (explored but not currently visible)
        else:
            return 220  # Dark (unexplored)
