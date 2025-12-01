from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsEllipseItem, QDialog
from PySide6.QtGui import QBrush, QPen, QColor, QPainter, QPixmap, QKeyEvent
from PySide6.QtCore import Qt, QTimer, QRectF, QPointF, QEasingCurve, QPropertyAnimation

import random
from core.game_state import GameState
from core.obstacle_manager import ObstacleType
from core.grid_map import GridMap, TileType

class GridBoardView(QGraphicsView):
    """Grid-based board view with keyboard controls"""
    
    def __init__(self, game_state, parent=None):
        super().__init__(parent)
        self.game_state = game_state
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        
        # Define objectName para estilização QSS
        self.setObjectName("BoardView")
        
        # Create grid map (20x20 with chambers and tunnels)
        self.grid_map = GridMap()  # Uses default 20x20
        self.grid_map.create_from_graph(self.game_state.graph)
        
        # Link grid_map to game_state so logic can access it
        self.game_state.grid_map = self.grid_map
        
        # Create fog of war system
        from core.fog_of_war import FogOfWar
        self.fog_of_war = FogOfWar(self.grid_map.width, self.grid_map.height)
        
        # Initialize player positions in grid
        for player in self.game_state.players:
            grid_pos = self.grid_map.get_position_for_vertex(player.current_vertex_id)
            if grid_pos:
                self.grid_map.set_player_position(player.id, grid_pos[0], grid_pos[1])
                print(f"🎯 {player.name} (ID:{player.id}) inicializado em vertex {player.current_vertex_id} -> grid pos ({grid_pos[0]}, {grid_pos[1]})")
        
        # Player sprites
        self.player_sprites = {}  # player_id -> sprite
        
        # Animation
        self.is_animating = False
        self.current_animation = None
        
        self.main_window = None
        
        # Enable keyboard focus
        self.setFocusPolicy(Qt.StrongFocus)

        # Start update timer to drive game loop (monsters, combat ticks)
        self._last_tick_ms = None
        self.update_timer = QTimer(self)
        self.update_timer.setInterval(120)  # ms ~ 8-9 ticks/s (tune as needed)
        self.update_timer.timeout.connect(self._on_update_tick)
        self.update_timer.start()
        
        # Initialize dynamic layer groups for efficient updates
        from PySide6.QtWidgets import QGraphicsItemGroup
        self._dyn_players = QGraphicsItemGroup()
        self._dyn_monsters = QGraphicsItemGroup()
        self._dyn_fog = QGraphicsItemGroup()
        self.scene.addItem(self._dyn_players)
        self.scene.addItem(self._dyn_monsters)
        self.scene.addItem(self._dyn_fog)
        
        # Set Z-values for proper layering
        self._dyn_players.setZValue(5)   # Players on top
        self._dyn_monsters.setZValue(4)  # Monsters below players
        self._dyn_fog.setZValue(10)      # Fog above everything
        
        # Connect CombatManager callback for damage popups
        if hasattr(self.game_state, 'combat_manager'):
            self.game_state.combat_manager.on_damage_callback = self._on_combat_damage
            self.game_state.combat_manager.on_death_callback = self._on_unit_death
            
        # Connect MonsterSystem callback for movement updates
        if hasattr(self.game_state, 'monster_system'):
            self.game_state.monster_system.on_monster_move = self._on_monster_move
        
        # Desenha apenas uma vez — elementos estáticos
        self._draw_grid()
        self._draw_obstacles()
        self._draw_players()
        self._draw_treasure()
        self._draw_fog()


    def _on_update_tick(self):
        """Update only game logic every tick and refresh lightweight layers."""
        from time import time

        now = time()
        if self._last_tick_ms is None:
            self._last_tick_ms = now
            return

        delta = now - self._last_tick_ms
        self._last_tick_ms = now

        # Update core game logic: monsters, combat, cooldowns
        try:
            self.game_state.update(delta)
        except Exception as e:
            print(f"[ERROR] GameState.update(): {e}")

        # NOTE: NÃO refresh dinâmico a cada tick - muito pesado!
        # Refresh acontece apenas quando necessário (movimento, ações, etc)


    
    def refresh(self):
        """Redraw the entire board"""
        # Stop all sprite timers before clearing
        for sprite in self.player_sprites.values():
            if hasattr(sprite, 'timer'):
                sprite.timer.stop()
        
        # Clear scene (this will delete all items including our groups!)
        self.scene.clear()
        self.player_sprites.clear()
        
        # CRITICAL: Recreate dynamic groups after scene.clear()
        from PySide6.QtWidgets import QGraphicsItemGroup
        self._dyn_players = QGraphicsItemGroup()
        self._dyn_monsters = QGraphicsItemGroup()
        self._dyn_fog = QGraphicsItemGroup()
        self.scene.addItem(self._dyn_players)
        self.scene.addItem(self._dyn_monsters)
        self.scene.addItem(self._dyn_fog)
        
        # Set Z-values for proper layering
        self._dyn_players.setZValue(5)
        self._dyn_monsters.setZValue(4)
        self._dyn_fog.setZValue(10)
        
        # Draw static elements
        self._draw_grid()
        self._draw_obstacles()
        self._draw_treasure()
        
        # Draw dynamic elements into groups
        self._draw_players(into=self._dyn_players)
        self._draw_monsters(into=self._dyn_monsters)
        self._draw_fog(into=self._dyn_fog)
        
        # Set scene rect
        scene_width = self.grid_map.width * self.grid_map.tile_size
        scene_height = self.grid_map.height * self.grid_map.tile_size
        self.scene.setSceneRect(0, 0, scene_width, scene_height)

    
    def _draw_grid(self):
        """Draw the grid tiles with textures"""
        import os
        from PySide6.QtGui import QPixmap, QBrush
        
        tile_size = self.grid_map.tile_size
        
        # Load textures once
        assets_dir = os.path.join(os.path.dirname(__file__), "..", "assets")
        textures = {
            'wall': QPixmap(os.path.join(assets_dir, "wall_texture.png")),
            'path': QPixmap(os.path.join(assets_dir, "path_texture.png")),
            'floor': QPixmap(os.path.join(assets_dir, "dungeon_floor.png")),
            'treasure': QPixmap(os.path.join(assets_dir, "treasure_glow.png"))
        }
        
        # Scale textures to tile size
        for key in textures:
            if not textures[key].isNull():
                textures[key] = textures[key].scaled(tile_size, tile_size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        
        for y in range(self.grid_map.height):
            for x in range(self.grid_map.width):
                tile_type = self.grid_map.get_tile(x, y)
                
                # Calculate pixel position
                px = x * tile_size
                py = y * tile_size
                
                # Create tile rectangle
                tile = QGraphicsRectItem(px, py, tile_size, tile_size)
                
                # Apply texture based on tile type
                if tile_type == TileType.WALL:
                    if not textures['wall'].isNull():
                        tile.setBrush(QBrush(textures['wall']))
                    else:
                        tile.setBrush(QBrush(QColor("#3C3C3C")))
                    tile.setPen(QPen(QColor("#2C2C2C"), 1))
                
                elif tile_type == TileType.CHAMBER:
                    # Chambers are larger rooms (2x2)
                    tile.setBrush(QBrush(QColor("#6B5335")))
                    tile.setPen(QPen(QColor("#5B4325"), 1))
                
                elif tile_type == TileType.TUNNEL:
                    # Tunnels are narrow corridors (1x1)
                    tile.setBrush(QBrush(QColor("#4A4A4A")))
                    tile.setPen(QPen(QColor("#3A3A3A"), 2))
                    
                elif tile_type == TileType.START:
                    if not textures['floor'].isNull():
                        tile.setBrush(QBrush(textures['floor']))
                    else:
                        tile.setBrush(QBrush(QColor("#4CAF50")))
                    tile.setPen(QPen(QColor("#388E3C"), 2))
                    
                elif tile_type == TileType.TREASURE:
                    if not textures['treasure'].isNull():
                        tile.setBrush(QBrush(textures['treasure']))
                    else:
                        tile.setBrush(QBrush(QColor("#FFD700")))
                    tile.setPen(QPen(QColor("#FFA500"), 2))
                    
                else:
                    tile.setBrush(QBrush(QColor("#666666")))
                    tile.setPen(QPen(QColor("#444444"), 1))
                
                tile.setZValue(0)
                self.scene.addItem(tile)

    
    def _draw_obstacles(self):
        """Draw obstacles on the grid"""
        import os
        from PySide6.QtGui import QPixmap
        from PySide6.QtWidgets import QGraphicsPixmapItem
        from core.obstacle_manager import ObstacleType
        
        tile_size = self.grid_map.tile_size
        assets_dir = os.path.join(os.path.dirname(__file__), "..", "assets")
        
        # Load obstacle sprites
        obstacle_sprites = {
            ObstacleType.MONSTER: QPixmap(os.path.join(assets_dir, "monster.png")),
            ObstacleType.DOOR_LOCKED: QPixmap(os.path.join(assets_dir, "door_locked.png")),
            ObstacleType.CHEST: QPixmap(os.path.join(assets_dir, "chest.png")),
        }
        
        # Scale sprites to tile size
        for key in obstacle_sprites:
            if not obstacle_sprites[key].isNull():
                obstacle_sprites[key] = obstacle_sprites[key].scaled(
                    tile_size, tile_size,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
        
        # Draw each obstacle
        for obstacle in self.grid_map.obstacle_manager.get_all_obstacles():
            if not obstacle.is_active:
                continue
            
            x, y = obstacle.position
            px = x * tile_size
            py = y * tile_size
            
            # Get sprite for obstacle type
            sprite_pixmap = obstacle_sprites.get(obstacle.obstacle_type)
            
            if sprite_pixmap and not sprite_pixmap.isNull():
                # Create pixmap item
                item = QGraphicsPixmapItem(sprite_pixmap)
                item.setPos(px, py)
                item.setZValue(3)  # Above tiles, below players
                self.scene.addItem(item)
            else:
                # Fallback: draw colored rectangle for traps and other obstacles
                if obstacle.obstacle_type == ObstacleType.TRAP:
                    trap = QGraphicsRectItem(px + 10, py + 10, tile_size - 20, tile_size - 20)
                    trap.setBrush(QBrush(QColor("#8B0000")))  # Dark red
                    trap.setPen(QPen(QColor("#FF0000"), 2))
                    trap.setZValue(3)
                    self.scene.addItem(trap)
    
    def _draw_players(self, into=None):
        """Draw players on grid
        
        Args:
            into: Optional QGraphicsItemGroup or scene to add items to
        """
        import os
        from .frame_animated_sprite import FrameAnimatedSprite
        from PySide6.QtWidgets import QGraphicsItemGroup
        
        into = into or self.scene  # Default to scene if not specified
        tile_size = self.grid_map.tile_size
        
        for player in self.game_state.players:
            if not player.is_alive:
                continue
                
            grid_pos = self.grid_map.get_player_position(player.id)
            if not grid_pos:
                continue
            
            x, y = grid_pos
            
            # Calculate pixel position (center of tile)
            px = x * tile_size + tile_size // 2
            py = y * tile_size + tile_size // 2
            
            # Load animated sprite
            frames_dir = None
            if player.color == "#FF0000":
                frames_dir = os.path.join(os.path.dirname(__file__), "..", "assets", "themes", "Player_Vermelho")
            elif player.color == "#0000FF":
                frames_dir = os.path.join(os.path.dirname(__file__), "..", "assets", "themes", "Player_Azul")
            
            if frames_dir and os.path.exists(frames_dir):
                sprite = FrameAnimatedSprite(frames_dir)
                sprite_x = px - 20
                sprite_y = py - 25
                sprite.setPos(sprite_x, sprite_y)
                sprite.setZValue(5)
                
                # Add to group or scene
                if isinstance(into, QGraphicsItemGroup):
                    into.addToGroup(sprite)
                else:
                    into.addItem(sprite)
                    
                self.player_sprites[player.id] = sprite
                print(f"🎨 {player.name}: grid({x},{y}) -> pixel({px},{py}) -> sprite_pos({sprite_x},{sprite_y})")
            else:
                # Fallback circle
                circle = QGraphicsEllipseItem(px - 10, py - 10, 20, 20)
                circle.setBrush(QBrush(QColor(player.color)))
                circle.setPen(QPen(QColor("#000000"), 2))
                circle.setZValue(5)
                
                # Add to group or scene
                if isinstance(into, QGraphicsItemGroup):
                    into.addToGroup(circle)
                else:
                    into.addItem(circle)

    
    def _draw_monsters(self, into=None):
        """Draw active monsters from MonsterSystem
        
        Args:
            into: Optional QGraphicsItemGroup or scene to add items to
        """
        import os
        from PySide6.QtWidgets import QGraphicsItemGroup
        from PySide6.QtGui import QPixmap
        
        into = into or self.scene  # Default to scene if not specified
        
        # Check if MonsterSystem exists
        if not hasattr(self.game_state, 'monster_system'):
            return
        
        if not self.game_state.monster_system:
            return
        
        tile_size = self.grid_map.tile_size
        assets_dir = os.path.join(os.path.dirname(__file__), "..", "assets")
        
        # Load monster sprite (generic for now)
        monster_pixmap = QPixmap(os.path.join(assets_dir, "monster.png"))
        if not monster_pixmap.isNull():
            monster_pixmap = monster_pixmap.scaled(
                tile_size, tile_size,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        
        # Draw each active monster
        for vertex_id, monster_state in self.game_state.monster_system.active_monsters.items():
            if not monster_state.monster.is_alive():
                continue
            
            # Get grid position from vertex
            grid_pos = self.grid_map.get_position_for_vertex(vertex_id)
            if not grid_pos:
                continue
            
            x, y = grid_pos
            px = x * tile_size
            py = y * tile_size
            
            # Create monster sprite
            if not monster_pixmap.isNull():
                from PySide6.QtWidgets import QGraphicsPixmapItem
                monster_item = QGraphicsPixmapItem(monster_pixmap)
                monster_item.setPos(px, py)
                monster_item.setZValue(4)
                
                # Add to group or scene
                if isinstance(into, QGraphicsItemGroup):
                    into.addToGroup(monster_item)
                else:
                    into.addItem(monster_item)
            else:
                # Fallback: red rectangle
                monster_rect = QGraphicsRectItem(px + 10, py + 10, tile_size - 20, tile_size - 20)
                monster_rect.setBrush(QBrush(QColor("#8B0000")))
                monster_rect.setPen(QPen(QColor("#FF0000"), 2))
                monster_rect.setZValue(4)
                
                # Add to group or scene
                if isinstance(into, QGraphicsItemGroup):
                    into.addToGroup(monster_rect)
                else:
                    into.addItem(monster_rect)
    
    def _draw_treasure(self):
        """Draw treasure marker"""
        treasure_vertex = self.game_state.treasure_vertex_id
        grid_pos = self.grid_map.get_position_for_vertex(treasure_vertex)
        
        if grid_pos:
            x, y = grid_pos
            tile_size = self.grid_map.tile_size
            px = x * tile_size + tile_size // 2
            py = y * tile_size + tile_size // 2
            
            # Draw treasure icon
            treasure = QGraphicsEllipseItem(px - 8, py - 8, 16, 16)
            treasure.setBrush(QBrush(QColor("#FFD700")))
            treasure.setPen(QPen(QColor("#FFA500"), 2))
            treasure.setZValue(3)
            self.scene.addItem(treasure)
    
    def _draw_fog(self, into=None):
        """Draw fog of war overlay
        
        Args:
            into: Optional QGraphicsItemGroup or scene to add items to
        """
        from PySide6.QtWidgets import QGraphicsItemGroup
        
        into = into or self.scene  # Default to scene if not specified
        tile_size = self.grid_map.tile_size
        
        # Update fog visibility based on current player positions
        player_positions = []
        for player in self.game_state.players:
            pos = self.grid_map.get_player_position(player.id)
            if pos:
                player_positions.append(pos)
        
        # Update visibility with dynamic radius based on location
        self.fog_of_war.update_visibility(
            player_positions,
            lambda x, y: self.grid_map.is_tunnel(x, y)
        )
        
        # Draw fog overlay for each tile
        for y in range(self.grid_map.height):
            for x in range(self.grid_map.width):
                opacity = self.fog_of_war.get_fog_opacity(x, y)
                
                if opacity > 0:  # Only draw if there's fog
                    px = x * tile_size
                    py = y * tile_size
                    
                    fog_tile = QGraphicsRectItem(px, py, tile_size, tile_size)
                    fog_tile.setBrush(QBrush(QColor(0, 0, 0, opacity)))
                    fog_tile.setPen(QPen(Qt.NoPen))
                    fog_tile.setZValue(10)  # Above everything
                    
                    # Add to group or scene
                    if isinstance(into, QGraphicsItemGroup):
                        into.addToGroup(fog_tile)
                    else:
                        into.addItem(fog_tile)

    def _refresh_dynamic_layers(self):
        """Redraw players, monsters and fog only.
        
        Safely removes all child items from dynamic groups and redraws them
        without touching static elements (grid, obstacles, treasure).
        """
        try:
            # Check if groups still exist (might be deleted by scene.clear())
            if not hasattr(self, '_dyn_players') or self._dyn_players is None:
                return
            
            # Remove all children from player group
            for item in list(self._dyn_players.childItems()):
                self._dyn_players.removeFromGroup(item)
                self.scene.removeItem(item)
                # Stop sprite timers if present
                if hasattr(item, 'timer'):
                    item.timer.stop()
            
            # Remove all children from monster group
            for item in list(self._dyn_monsters.childItems()):
                self._dyn_monsters.removeFromGroup(item)
                self.scene.removeItem(item)
            
            # Remove all children from fog group
            for item in list(self._dyn_fog.childItems()):
                self._dyn_fog.removeFromGroup(item)
                self.scene.removeItem(item)
            
            # Clear player sprites tracking (will be rebuilt)
            self.player_sprites.clear()
            
            # Redraw dynamic elements into their respective groups
            self._draw_players(into=self._dyn_players)
            self._draw_monsters(into=self._dyn_monsters)
            self._draw_fog(into=self._dyn_fog)
        except RuntimeError as e:
            # Groups were deleted (e.g., by scene.clear()), skip this refresh
            print(f"[DEBUG] _refresh_dynamic_layers skipped: {e}")
            pass
    
    def show_damage_popup(self, x, y, amount, target_type="player"):
        """Show animated damage popup at grid position
        
        Args:
            x: Grid X coordinate
            y: Grid Y coordinate
            amount: Damage amount to display
            target_type: "player" or "monster" for color coding
        """
        from PySide6.QtWidgets import QGraphicsSimpleTextItem
        from PySide6.QtCore import QTimer
        from PySide6.QtGui import QFont
        
        tile_size = self.grid_map.tile_size
        px = x * tile_size + tile_size // 2
        py = y * tile_size + tile_size // 2
        
        # Create text item
        text = QGraphicsSimpleTextItem(f"-{amount}")
        
        # Set color based on target type
        if target_type == "monster":
            text.setBrush(QBrush(QColor("#FF4444")))  # Red for monster damage
        else:
            text.setBrush(QBrush(QColor("#FFAA00")))  # Orange for player damage
        
        # Make text bold and larger
        font = QFont()
        font.setBold(True)
        font.setPointSize(14)
        text.setFont(font)
        
        text.setPos(px - 15, py - 25)
        text.setZValue(15)  # Above everything
        
        # Add to scene
        self.scene.addItem(text)
        
        # Animate fade out and remove after 600ms
        # Animate fade out and remove after 600ms
        def cleanup():
            try:
                if text.scene():
                    self.scene.removeItem(text)
            except RuntimeError:
                pass # Already deleted
        QTimer.singleShot(600, cleanup)

    def _on_combat_damage(self, player, monster, amount, target_type):
        """Callback from CombatManager when damage occurs"""
        # Determine position based on player's current vertex
        # We need to map vertex to grid coordinates
        try:
            vertex_id = player.current_vertex_id
            grid_pos = self.grid_map.get_position_for_vertex(vertex_id)
            
            if grid_pos:
                x, y = grid_pos
                # Offset slightly for player vs monster
                if target_type == "monster":
                    x += 0.3 # Shift right for monster damage
                    # Trigger shake animation for monster (if we can identify sprite)
                    # For now, just shake the popup slightly
                else:
                    x -= 0.3 # Shift left for player damage
                    # Shake player sprite
                    if player.id in self.player_sprites:
                        self._shake_sprite(self.player_sprites[player.id])
                    
                self.show_damage_popup(x, y, amount, target_type)
        except Exception as e:
            print(f"[ERROR] _on_combat_damage: {e}")

    def _shake_sprite(self, sprite_item):
        """Simple shake animation for sprite"""
        from PySide6.QtCore import QPropertyAnimation, QPointF
        
        # This requires the sprite to be a QObject or have properties we can animate
        # Since our sprites are QGraphicsPixmapItem, we can't easily use QPropertyAnimation directly
        # without a wrapper. For now, let's do a manual jitter.
        orig_pos = sprite_item.pos()
        
        def jitter(count=0):
            if count > 4:
                sprite_item.setPos(orig_pos)
                return
            
            offset_x = random.randint(-5, 5)
            offset_y = random.randint(-5, 5)
            sprite_item.setPos(orig_pos.x() + offset_x, orig_pos.y() + offset_y)
            QTimer.singleShot(50, lambda: jitter(count + 1))
            
        jitter()

    def _on_monster_move(self, ms, old_v, new_v):
        """Callback when a monster moves"""
        # Trigger refresh of dynamic layers to show new position
        # We could optimize to only move the specific sprite, but full refresh is safer for now
        self._refresh_dynamic_layers()
    
    def _on_unit_death(self, unit, unit_type):
        """Callback when a unit dies"""
        print(f"[DEBUG] Unit died: {unit} ({unit_type})")
        
        # Determine position
        x, y = 0, 0
        if unit_type == "player":
            grid_pos = self.grid_map.get_player_position(unit.id)
            if grid_pos: x, y = grid_pos
        else:
            # Monster
            if hasattr(unit, 'grid_pos') and unit.grid_pos:
                x, y = unit.grid_pos
            else:
                # Try to find via active monsters if needed, but grid_pos should be set for static ones
                pass

        # Show skull effect
        tile_size = self.grid_map.tile_size
        px = x * tile_size + tile_size // 2
        py = y * tile_size + tile_size // 2
        
        from PySide6.QtWidgets import QGraphicsSimpleTextItem
        from PySide6.QtGui import QFont
        
        skull = QGraphicsSimpleTextItem("💀")
        font = QFont()
        font.setPointSize(20)
        skull.setFont(font)
        skull.setPos(px - 15, py - 25)
        skull.setZValue(20)
        self.scene.addItem(skull)
        
        # Animate fade out
        def cleanup():
            try:
                if skull.scene():
                    self.scene.removeItem(skull)
            except RuntimeError:
                pass
        QTimer.singleShot(1500, cleanup)
        
        # Refresh board to remove the unit sprite
        self._refresh_dynamic_layers()

    def keyPressEvent(self, event: QKeyEvent):
        """Handle keyboard input for movement - separate controls per player"""
        if self.is_animating:
            return  # Don't allow movement during animation
        
        key = event.key()
        
        # Determine which player is moving based on key pressed
        player_to_move = None
        direction = None
        new_x, new_y = 0, 0

        self.game_state.log(f"🎮 Tecla pressionada: {event.key()}")
        
        # Player Vermelho (Red) - Arrow Keys
        if key == Qt.Key_Up:
            player_to_move = self._get_player_by_color("#FF0000")
            direction = "up"
        elif key == Qt.Key_Down:
            player_to_move = self._get_player_by_color("#FF0000")
            direction = "down"
        elif key == Qt.Key_Left:
            player_to_move = self._get_player_by_color("#FF0000")
            direction = "left"
        elif key == Qt.Key_Right:
            player_to_move = self._get_player_by_color("#FF0000")
            direction = "right"
        
        # Player Azul (Blue) - WASD
        elif key == Qt.Key_W:
            player_to_move = self._get_player_by_color("#0000FF")
            direction = "up"
        elif key == Qt.Key_S:
            player_to_move = self._get_player_by_color("#0000FF")
            direction = "down"
        elif key == Qt.Key_A:
            player_to_move = self._get_player_by_color("#0000FF")
            direction = "left"
        elif key == Qt.Key_D:
            player_to_move = self._get_player_by_color("#0000FF")
            direction = "right"
        else:
            super().keyPressEvent(event)
            return
        
        if not player_to_move:
            return
        
        # Get current position
        grid_pos = self.grid_map.get_player_position(player_to_move.id)
        if not grid_pos:
            return
        
        x, y = grid_pos
        new_x, new_y = x, y
        
        # Calculate new position based on direction
        if direction == "up":
            new_y -= 1
        elif direction == "down":
            new_y += 1
        elif direction == "left":
            new_x -= 1
        elif direction == "right":
            new_x += 1
        
        # Check if there's an obstacle at the new position
        obstacle = self.grid_map.obstacle_manager.get_obstacle((new_x, new_y))
        if obstacle and obstacle.is_active:
            # Check if player can pass through this obstacle
            if not self.grid_map.obstacle_manager.can_pass((new_x, new_y), player_to_move):
                # Show interaction dialog
                self.show_interaction_dialog(obstacle, player_to_move)
                return
        
        # Check if movement is valid (tile type)
        if self.grid_map.can_move_to(new_x, new_y):
            # Check stamina
            stamina_cost = 2  # Cost per tile
            if player_to_move.stamina >= stamina_cost:
                # Update sprite direction
                if player_to_move.id in self.player_sprites:
                    self.player_sprites[player_to_move.id].start_walking(direction)
                
                # Perform movement
                self.move_player_to(player_to_move.id, new_x, new_y, direction)
            else:
                self.game_state.log(f"❌ {player_to_move.name}: Stamina insuficiente! Precisa de {stamina_cost}, tem {player_to_move.stamina}")
                if self.main_window:
                    self.main_window.refresh_all()
        else:
            self.game_state.log(f"❌ {player_to_move.name}: Não pode mover para essa posição!")
    
    def _get_player_by_color(self, color: str):
        """Get player by color"""
        for player in self.game_state.players:
            if player.color == color:
                return player
        return None
    
    def move_player_to(self, player_id: int, new_x: int, new_y: int, direction: str):
        """Move player to new grid position with smooth animation"""
        player = self.game_state._get_player(player_id)
        if not player:
            return
        
        # Get old position for logging
        old_pos = self.grid_map.get_player_position(player_id)
        
        # Update grid position
        self.grid_map.set_player_position(player_id, new_x, new_y)
        
        # Consume stamina
        stamina_cost = 2
        player.consume_stamina(stamina_cost)
        
        # Check if there's a vertex at this position
        vertex_id = self.grid_map.get_vertex_at_position(new_x, new_y)
        if vertex_id is not None:
            # Update game state
            player.current_vertex_id = vertex_id
            self.game_state.enter_vertex(player, vertex_id)
            self.game_state.check_victory()
        
        print(f"🚶 {player.name} moveu de {old_pos} para ({new_x}, {new_y}) [direção: {direction}] - Stamina: -{stamina_cost}")
        self.game_state.log(f"🚶 {player.name} moveu para ({new_x}, {new_y}) - Stamina: -{stamina_cost}")
        
        # Animate movement if sprite exists
        if player_id in self.player_sprites:
            self.animate_movement(player_id, old_pos, (new_x, new_y), direction)
        else:
            # No animation, just refresh
            if self.main_window:
                self.main_window.refresh_all()
            else:
                self.refresh()
    
    def animate_movement(self, player_id: int, old_pos: tuple, new_pos: tuple, direction: str):
        """Animate smooth movement from old position to new position"""
        if old_pos is None:
            # No old position, just refresh
            if self.main_window:
                self.main_window.refresh_all()
            return
        
        sprite = self.player_sprites.get(player_id)
        if not sprite:
            return
        
        # Block new movements during animation
        self.is_animating = True
        
        # Calculate pixel positions
        tile_size = self.grid_map.tile_size
        old_x, old_y = old_pos
        new_x, new_y = new_pos
        
        old_px = old_x * tile_size + tile_size // 2
        old_py = old_y * tile_size + tile_size // 2
        new_px = new_x * tile_size + tile_size // 2
        new_py = new_y * tile_size + tile_size // 2
        
        start_pos = QPointF(old_px - 20, old_py - 25)
        end_pos = QPointF(new_px - 20, new_py - 25)
        
        # Use QVariantAnimation instead of QPropertyAnimation
        # QVariantAnimation doesn't require QObject
        from PySide6.QtCore import QVariantAnimation
        
        animation = QVariantAnimation()
        animation.setDuration(200)  # 200ms for smooth movement
        animation.setStartValue(start_pos)
        animation.setEndValue(end_pos)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Update sprite position on each animation step
        def update_position(value):
            if sprite:
                sprite.setPos(value)
        
        animation.valueChanged.connect(update_position)
        
        # When animation finishes
        def on_animation_finished():
            self.is_animating = False
            # Return sprite to idle state
            if sprite:
                sprite.stop_walking()
            # Refresh UI
            if self.main_window:
                self.main_window.refresh_all()
        
        animation.finished.connect(on_animation_finished)
        
        # Start animation
        animation.start()
        
        # Store animation to prevent garbage collection
        self.current_animation = animation
    
    def show_interaction_dialog(self, obstacle, player):
        """Show interaction dialog for obstacle encounter"""
        from .interaction_dialog import InteractionDialog
        from core.obstacle_manager import ObstacleType
        
        # Create and show dialog
        dialog = InteractionDialog(obstacle, player, self)
        result = dialog.exec()
        
        if result == QDialog.Accepted:
            action = dialog.get_selected_action()
            self.handle_interaction_action(action, obstacle, player)
    
    def handle_interaction_action(self, action, obstacle, player):
        """Handle the selected interaction action"""
        from core.obstacle_manager import ObstacleType
        
        if action == "attack":
            # Start combat with monster
            if obstacle.obstacle_type == ObstacleType.MONSTER:
                monster_name = obstacle.data.get('type', 'monstro')
                # Fix: Obstacle uses .position tuple, not .grid_x/.grid_y
                px, py = obstacle.position
                
                print(f"[DEBUG] Tentando combate em ({px}, {py}) contra {monster_name}")
                
                # Busca o monstro nessa posição
                monster = self.game_state.get_monster_at(px, py)

                if monster:
                    print(f"[DEBUG] Monstro encontrado: {monster}")
                    self.game_state.log(f"⚔️ {player.name} iniciou combate contra {monster_name}!")
                    
                    # Inicia combate tick-based via CombatManager
                    self.game_state.start_combat(player, monster)
                    print(f"[DEBUG] Combate iniciado via CombatManager")
                else:
                    print(f"[ERROR] Nenhum monstro em ({px}, {py})!")
                    self.game_state.log(f"⚠️ Nenhum monstro encontrado em ({px}, {py})")
        
        elif action == "item":
            # Show inventory and use item
            self.game_state.log(f"🎒 {player.name} abriu o inventário")
            # TODO: Show inventory dialog
            # For now, check if player has required item
            if obstacle.obstacle_type == ObstacleType.DOOR_LOCKED:
                # Simulate having key
                self.game_state.log(f"🔑 {player.name} usou uma chave!")
                obstacle.is_active = False
                self.game_state.log(f"✅ Porta destrancada!")
                self.refresh()
        
        elif action == "card":
            # Show cards and use one
            self.game_state.log(f"🎴 {player.name} selecionou uma carta")
            # TODO: Show card selection dialog
        
        elif action == "flee":
            # Player chose to flee/go back
            self.game_state.log(f"🏃 {player.name} decidiu não enfrentar o obstáculo")
        
        # Refresh UI
        if self.main_window:
            self.main_window.refresh_all()

