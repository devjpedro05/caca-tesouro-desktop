from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsEllipseItem, QDialog
from PySide6.QtGui import QBrush, QPen, QColor, QPainter, QPixmap, QKeyEvent
from PySide6.QtCore import Qt, QTimer, QRectF, QPointF, QEasingCurve, QPropertyAnimation

import random
from core.game_state import GameState
from core.obstacle_manager import ObstacleType
from core.grid_map import GridMap, TileType

class GridBoardView(QGraphicsView):
    """Grid-based board view with keyboard controls"""
    
    def __init__(self, game_state, parent=None, player_index=None):
        super().__init__(parent)
        self.game_state = game_state
        self.player_index = player_index  # None = both players, 0 = player 1, 1 = player 2
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Define objectName para estilização QSS
        self.setObjectName("BoardView")
        
        # Create or reuse grid map (20x20 with chambers and tunnels)
        # In split-screen mode, share the same grid_map across views
        if hasattr(game_state, 'grid_map') and game_state.grid_map is not None:
            self.grid_map = game_state.grid_map
        else:
            self.grid_map = GridMap()  # Uses default 20x20
            self.grid_map.create_from_graph(self.game_state.graph)
            # Link grid_map to game_state so logic can access it
            self.game_state.grid_map = self.grid_map
        
        # Create fog of war system (individual per view for split-screen)
        from core.fog_of_war import FogOfWar
        self.fog_of_war = FogOfWar(self.grid_map.width, self.grid_map.height)
        
        # Initialize player positions in grid (only if not already done)
        for player in self.game_state.players:
            grid_pos = self.grid_map.get_position_for_vertex(player.current_vertex_id)
            if grid_pos and self.grid_map.get_player_position(player.id) is None:
                self.grid_map.set_player_position(player.id, grid_pos[0], grid_pos[1])
                print(f"🎯 {player.name} (ID:{player.id}) inicializado em vertex {player.current_vertex_id} -> grid pos ({grid_pos[0]}, {grid_pos[1]})")
        
        # Player sprites
        self.player_sprites = {}  # player_id -> sprite
        
        # Monster sprites
        self.monster_sprites = {}  # vertex_id -> sprite
        self.monster_patrol_data = {}  # vertex_id -> {offset_x, offset_y, direction, speed}
        
        # Animation
        self.is_animating = False
        self.current_animation = None
        
        # Track if board has been initially drawn
        self._board_initialized = False
        self.victory_animation_played = False
        
        self.main_window = None
        
        # Key state tracking for continuous movement
        self.pressed_keys = set()  # Track currently pressed keys
        self.movement_cooldown = 0.0  # Cooldown between movements (seconds)
        self.movement_delay = 0.25  # Delay between movements (250ms - balanced speed)
        
        # Don't grab focus - let MainWindow handle keyboard events
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

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
        self._scene.addItem(self._dyn_players)
        self._scene.addItem(self._dyn_monsters)
        self._scene.addItem(self._dyn_fog)
        
        # Set Z-values for proper layering
        self._dyn_players.setZValue(5)   # Players on top
        self._dyn_monsters.setZValue(4)  # Monsters below players
        self._dyn_fog.setZValue(10)      # Fog above everything
        
        # Connect CombatManager callbacks - usar lista ao invés de sobrescrever
        if hasattr(self.game_state, 'combat_manager'):
            # Inicializar listas de callbacks se não existirem
            if not hasattr(self.game_state.combat_manager, '_damage_callbacks'):
                self.game_state.combat_manager._damage_callbacks = []
            if not hasattr(self.game_state.combat_manager, '_death_callbacks'):
                self.game_state.combat_manager._death_callbacks = []
            
            # Adicionar callbacks desta view
            if self._on_combat_damage not in self.game_state.combat_manager._damage_callbacks:
                self.game_state.combat_manager._damage_callbacks.append(self._on_combat_damage)
            if self._on_unit_death not in self.game_state.combat_manager._death_callbacks:
                self.game_state.combat_manager._death_callbacks.append(self._on_unit_death)
            
            # Criar wrapper que chama todos os callbacks
            def call_all_damage(*args, **kwargs):
                for cb in self.game_state.combat_manager._damage_callbacks:
                    cb(*args, **kwargs)
            
            def call_all_death(*args, **kwargs):
                for cb in self.game_state.combat_manager._death_callbacks:
                    cb(*args, **kwargs)
            
            self.game_state.combat_manager.on_damage_callback = call_all_damage
            self.game_state.combat_manager.on_death_callback = call_all_death
            
        # Connect MonsterSystem callback for movement updates
        if hasattr(self.game_state, 'monster_system'):
            self.game_state.monster_system.on_monster_move = self._on_monster_move
        
        # Desenha apenas uma vez — elementos estáticos
        self._draw_grid()
        self._draw_spawn_chambers()  # Draw dungeon floor texture in player spawn chambers
        self._draw_obstacles()
        self._draw_players()
        self._draw_monsters()  # Draw animated Goblin sprites
        self._draw_treasure()
        self._draw_fog()


    def center_on_current_player(self):
        """Center the view on the current player's position"""
        current_player = self.game_state.current_player
        if not current_player:
            return
        
        # Get player sprite
        sprite = self.player_sprites.get(current_player.id)
        if sprite:
            # Center view on player
            self.centerOn(sprite)

    def _on_update_tick(self):
        """Update only game logic every tick and refresh lightweight layers."""
        from time import time

        now = time()
        if self._last_tick_ms is None:
            self._last_tick_ms = now
            return

        delta = now - self._last_tick_ms
        self._last_tick_ms = now

        # Update movement cooldown
        if self.movement_cooldown > 0:
            self.movement_cooldown -= delta
        
        # Process continuous movement if cooldown expired
        if self.movement_cooldown <= 0 and self.pressed_keys:
            self._process_continuous_movement()
            self.movement_cooldown = self.movement_delay

        # Update Goblin patrol positions
        self._update_goblin_patrol(delta)

        # Check for victory animation
        if self.game_state.game_mode.name == "VICTORY" and not self.victory_animation_played:
            self.play_victory_animation()

        # Update core game logic: monsters, combat, cooldowns
        try:
            self.game_state.update(delta)
            # Advance animations
            self._scene.advance()
        except Exception as e:
            print(f"[ERROR] GameState.update(): {e}")

        # NOTE: NÃO refresh dinâmico a cada tick - muito pesado!
        # Refresh acontece apenas quando necessário (movimento, ações, etc)
    
    def _update_goblin_patrol(self, delta):
        """Update Goblin patrol positions within their chambers"""
        tile_size = self.grid_map.tile_size
        
        for vertex_id, patrol in list(self.monster_patrol_data.items()):
            # Check if monster still exists and is alive
            if vertex_id not in self.monster_sprites:
                continue
            
            if hasattr(self.game_state, 'monster_system'):
                monster_state = self.game_state.monster_system.active_monsters.get(vertex_id)
                if not monster_state or not monster_state.monster.is_alive():
                    continue
            
            # Update horizontal patrol position
            patrol['offset_x'] += patrol['direction'] * patrol['speed'] * delta
            
            # Reverse direction when reaching patrol bounds
            if abs(patrol['offset_x']) > patrol['patrol_range']:
                patrol['direction'] *= -1
                patrol['offset_x'] = patrol['patrol_range'] * patrol['direction']
                
                # Update sprite direction
                sprite = self.monster_sprites.get(vertex_id)
                if sprite:
                    if patrol['direction'] > 0:
                        sprite.walk_right()
                    else:
                        sprite.walk_left()
            
            # Update sprite position
            sprite = self.monster_sprites.get(vertex_id)
            if sprite:
                chamber_info = self.grid_map.chambers.get(vertex_id)
                if chamber_info:
                    center_x, center_y = chamber_info['center']
                    px = (center_x + patrol['offset_x']) * tile_size + tile_size // 2
                    py = (center_y + patrol['offset_y']) * tile_size + tile_size // 2
                    
                    sprite_x = px - 30
                    sprite_y = py - 30
                    sprite.setPos(sprite_x, sprite_y)


    
    def refresh(self):
        """Redraw or update the board"""
        # If board hasn't been initialized yet, do full draw
        if not self._board_initialized:
            self._full_refresh()
            self._board_initialized = True
        else:
            # Just update dynamic elements (players, monsters, fog)
            self._update_dynamic_elements()
    
    def _full_refresh(self):
        """Full board redraw (only called initially or when structure changes)"""
        # Stop all sprite timers before clearing
        for sprite in self.player_sprites.values():
            if hasattr(sprite, 'timer'):
                sprite.timer.stop()
        
        for sprite in self.monster_sprites.values():
            if hasattr(sprite, 'timer'):
                sprite.timer.stop()
        
        # Clear scene (this will delete all items including our groups!)
        self._scene.clear()
        self.player_sprites.clear()
        self.monster_sprites.clear()  # Must clear because scene.clear() deleted the sprites
        
        # CRITICAL: Recreate dynamic groups after scene.clear()
        from PySide6.QtWidgets import QGraphicsItemGroup
        self._dyn_players = QGraphicsItemGroup()
        self._dyn_monsters = QGraphicsItemGroup()
        self._dyn_fog = QGraphicsItemGroup()
        self._scene.addItem(self._dyn_players)
        self._scene.addItem(self._dyn_monsters)
        self._scene.addItem(self._dyn_fog)
        
        # Set Z-values for proper layering
        self._dyn_players.setZValue(5)
        self._dyn_monsters.setZValue(4)
        self._dyn_fog.setZValue(10)
        
        # Draw static elements
        self._draw_grid()
        self._draw_spawn_chambers()  # Draw dungeon floor in spawn chambers
        self._draw_obstacles()
        self._draw_treasure()
        
        # Draw dynamic elements into groups
        self._draw_players(into=self._dyn_players)
        self._draw_monsters(into=self._dyn_monsters)
        self._draw_fog(into=self._dyn_fog)
        
        # Set scene rect
        scene_width = self.grid_map.width * self.grid_map.tile_size
        scene_height = self.grid_map.height * self.grid_map.tile_size
        self._scene.setSceneRect(0, 0, scene_width, scene_height)
    
    def _update_dynamic_elements(self):
        """Update only dynamic elements without recreating everything"""
        # Update fog of war always (even during animation)
        self._update_fog()
        
        # Don't update sprite positions during animation to avoid interrupting smooth movement
        if self.is_animating:
            return
            
        # Update player positions and HP
        for player in self.game_state.players:
            if player.id in self.player_sprites:
                sprite = self.player_sprites[player.id]
                # Use get_player_position (actual grid position) instead of get_position_for_vertex
                # because player might be between vertices
                grid_pos = self.grid_map.get_player_position(player.id)
                if grid_pos:
                    gx, gy = grid_pos
                    tile_size = self.grid_map.tile_size
                    px = gx * tile_size + tile_size // 2
                    py = gy * tile_size + tile_size // 2
                    sprite_x = px - 20
                    sprite_y = py - 25
                    
                    # Only update position if it changed significantly
                    current_pos = sprite.pos()
                    if abs(current_pos.x() - sprite_x) > 1 or abs(current_pos.y() - sprite_y) > 1:
                        sprite.setPos(sprite_x, sprite_y)
        
        # Update monster HP (positions should be stable unless they die)
        if hasattr(self.game_state, 'monster_system') and self.game_state.monster_system:
            for vertex_id, monster_state in self.game_state.monster_system.active_monsters.items():
                if vertex_id in self.monster_sprites:
                    goblin_sprite = self.monster_sprites[vertex_id]
                    if hasattr(monster_state.monster, 'hp') and hasattr(monster_state.monster, 'max_hp'):
                        goblin_sprite.update_hp(monster_state.monster.hp, monster_state.monster.max_hp)
    
    def _update_fog(self):
        """Update fog of war without recreating everything"""
        if not hasattr(self, '_dyn_fog'):
            return
            
        # Clear existing fog items
        for item in self._dyn_fog.childItems():
            self._dyn_fog.removeFromGroup(item)
            if item.scene():
                self._scene.removeItem(item)
        
        # Redraw fog (filtered by player_index if set)
        self._draw_fog(into=self._dyn_fog)

    
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
                textures[key] = textures[key].scaled(tile_size, tile_size, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
        
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
                self._scene.addItem(tile)

    def _draw_spawn_chambers(self):
        """Draw special textures covering chambers:
        - dungeon_floor.png for player spawn chambers (v0, v1)
        - path_texture.png for other chambers (v2, v3, v4, v5)
        """
        import os
        from PySide6.QtGui import QPixmap
        from PySide6.QtWidgets import QGraphicsPixmapItem
        
        tile_size = self.grid_map.tile_size
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Load textures
        floor_path = os.path.join(base_dir, "assets", "dungeon_floor.png")
        path_path = os.path.join(base_dir, "assets", "path_texture.png")
        
        floor_pixmap = QPixmap(floor_path) if os.path.exists(floor_path) else QPixmap()
        path_pixmap = QPixmap(path_path) if os.path.exists(path_path) else QPixmap()
        
        # Define which texture to use for each chamber
        # v0, v1 = player spawns (dungeon_floor)
        # v2, v3, v4, v5 = other chambers (path_texture)
        # v6 = treasure chamber (already has treasure_glow)
        chamber_textures = {
            0: floor_pixmap,  # Player Vermelho spawn
            1: floor_pixmap,  # Player Azul spawn
            2: path_pixmap,   # Salão dos Ecos
            3: path_pixmap,   # Túnel Escuro
            4: path_pixmap,   # Ponte de Pedra
            5: path_pixmap,   # Lago Subterrâneo
            # v6 (treasure) already handled by _draw_treasure()
        }
        
        for vertex_id, texture_pixmap in chamber_textures.items():
            if texture_pixmap.isNull():
                continue
                
            chamber_info = self.grid_map.chambers.get(vertex_id)
            if not chamber_info:
                continue
            
            # Get chamber bounds (x1, y1, x2, y2)
            x1, y1, x2, y2 = chamber_info['bounds']
            
            # Chamber is 2x2 tiles
            chamber_pixel_size = tile_size * 2
            px = x1 * tile_size
            py = y1 * tile_size
            
            # Scale texture to fit entire chamber (2x2 tiles)
            scaled_pixmap = texture_pixmap.scaled(
                chamber_pixel_size,
                chamber_pixel_size,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            
            texture_item = QGraphicsPixmapItem(scaled_pixmap)
            texture_item.setPos(px, py)
            texture_item.setZValue(0.5)  # Above regular floor tiles but below everything else
            self._scene.addItem(texture_item)
    
    def _draw_obstacles(self):
        """Draw obstacles on the grid (excluding monsters - they have animated sprites)"""
        import os
        from PySide6.QtGui import QPixmap
        from PySide6.QtWidgets import QGraphicsPixmapItem
        from core.obstacle_manager import ObstacleType
        
        tile_size = self.grid_map.tile_size
        assets_dir = os.path.join(os.path.dirname(__file__), "..", "assets")
        
        # Load obstacle sprites (excluding MONSTER - handled by _draw_monsters)
        obstacle_sprites = {
            ObstacleType.DOOR_LOCKED: QPixmap(os.path.join(assets_dir, "door_locked.png")),
            ObstacleType.CHEST: QPixmap(os.path.join(assets_dir, "chest.png")),
        }
        
        # Scale sprites to tile size
        for key in obstacle_sprites:
            if not obstacle_sprites[key].isNull():
                obstacle_sprites[key] = obstacle_sprites[key].scaled(
                    tile_size, tile_size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
        
        # Draw each obstacle
        for obstacle in self.grid_map.obstacle_manager.get_all_obstacles():
            if not obstacle.is_active:
                continue
            
            # SKIP MONSTERS - they are drawn as animated sprites by _draw_monsters()
            if obstacle.obstacle_type == ObstacleType.MONSTER:
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
                self._scene.addItem(item)
            else:
                # Fallback: draw colored rectangle for traps and other obstacles
                if obstacle.obstacle_type == ObstacleType.TRAP:
                    trap = QGraphicsRectItem(px + 10, py + 10, tile_size - 20, tile_size - 20)
                    trap.setBrush(QBrush(QColor("#8B0000")))  # Dark red
                    trap.setPen(QPen(QColor("#FF0000"), 2))
                    trap.setZValue(3)
                    self._scene.addItem(trap)
    
    def _draw_players(self, into=None):
        """Draw players on grid
        
        Args:
            into: Optional QGraphicsItemGroup or scene to add items to
        """
        import os
        from .frame_animated_sprite import FrameAnimatedSprite
        from PySide6.QtWidgets import QGraphicsItemGroup
        
        into = into or self._scene  # Default to scene if not specified
        tile_size = self.grid_map.tile_size
        
        for player in self.game_state.players:
            if not player.is_alive:
                continue
            
            # In split-screen mode, only draw this view's player
            # Each GameState has only 1 player, so check player.id instead of index
            if self.player_index is not None:
                # player_index 0 = Player ID 0, player_index 1 = Player ID 1
                if player.id != self.player_index:
                    continue  # Skip other players
                
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
        """Draw active monsters from MonsterSystem with animated Goblin sprites
        
        Args:
            into: Optional QGraphicsItemGroup or scene to add items to
        """
        import os
        import random
        from PySide6.QtWidgets import QGraphicsItemGroup
        from .goblin_sprite import GoblinSprite
        
        into = into or self._scene  # Default to scene if not specified
        
        # Check if MonsterSystem exists
        if not hasattr(self.game_state, 'monster_system'):
            return
        
        if not self.game_state.monster_system:
            return
        
        tile_size = self.grid_map.tile_size
        
        
        # Draw each active monster
        for vertex_id, monster_state in self.game_state.monster_system.active_monsters.items():
            if not monster_state.monster.is_alive():
                # Remove dead monster sprite
                if vertex_id in self.monster_sprites:
                    sprite = self.monster_sprites[vertex_id]
                    if sprite.scene():
                        sprite.scene().removeItem(sprite)
                    del self.monster_sprites[vertex_id]
                continue
            
            # Get chamber bounds for this vertex
            chamber_info = self.grid_map.chambers.get(vertex_id)
            if not chamber_info:
                continue
            
            # Get chamber center
            center_x, center_y = chamber_info['center']
            
            # NO PATROL - Monsters stay at exact center of chamber
            # Calculate pixel position (no offset, perfectly centered)
            px = center_x * tile_size + tile_size // 2
            py = center_y * tile_size + tile_size // 2
            
            # Determine walking direction based on vertex ID (just for animation variety)
            walk_direction = 1 if vertex_id % 2 == 0 else -1  # 1 = right, -1 = left
            
            # Reuse existing sprite or create new one
            if vertex_id in self.monster_sprites:
                goblin_sprite = self.monster_sprites[vertex_id]
                # Sprite already exists and is in scene, just update position
            else:
                # Create animated Goblin sprite (only once!)
                goblin_sprite = GoblinSprite()
                goblin_sprite.setZValue(4)
                
                # Set the level from monster
                if hasattr(monster_state.monster, 'level'):
                    goblin_sprite.set_level(monster_state.monster.level)
                
                # Add to group or scene
                if isinstance(into, QGraphicsItemGroup):
                    into.addToGroup(goblin_sprite)
                else:
                    into.addItem(goblin_sprite)
                
                # Store reference for updates
                self.monster_sprites[vertex_id] = goblin_sprite
            
            # Update position (centered in chamber)
            sprite_x = px - 30  # Offset to center sprite
            sprite_y = py - 30
            goblin_sprite.setPos(sprite_x, sprite_y)
            
            # Update HP bar with monster's current health
            if hasattr(monster_state.monster, 'hp') and hasattr(monster_state.monster, 'max_hp'):
                goblin_sprite.update_hp(monster_state.monster.hp, monster_state.monster.max_hp)
            
            # Set walking direction based on vertex ID (just for animation variety)
            if walk_direction > 0:
                goblin_sprite.walk_right()
            else:
                goblin_sprite.walk_left()
        
        # Fallback for any remaining logic
        if False:
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
        """Draw treasure marker with glow effect covering entire chamber"""
        treasure_vertex = self.game_state.treasure_vertex_id
        
        # Get chamber info for the treasure vertex
        chamber_info = self.grid_map.chambers.get(treasure_vertex)
        
        if chamber_info:
            tile_size = self.grid_map.tile_size
            
            # Get chamber bounds (x1, y1, x2, y2)
            x1, y1, x2, y2 = chamber_info['bounds']
            
            # Chamber is 2x2 tiles
            chamber_pixel_size = tile_size * 2
            px = x1 * tile_size
            py = y1 * tile_size
            
            # Load and draw treasure glow image covering entire chamber
            import os
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            glow_path = os.path.join(base_dir, "assets", "treasure_glow.png")
            
            if os.path.exists(glow_path):
                from PySide6.QtGui import QPixmap
                from PySide6.QtWidgets import QGraphicsPixmapItem
                
                glow_pixmap = QPixmap(glow_path)
                if not glow_pixmap.isNull():
                    # Scale image to fit entire chamber (2x2 tiles)
                    scaled_pixmap = glow_pixmap.scaled(
                        chamber_pixel_size, 
                        chamber_pixel_size,
                        Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    
                    glow_item = QGraphicsPixmapItem(scaled_pixmap)
                    glow_item.setPos(px, py)
                    glow_item.setZValue(2.5)  # Below monsters/players but above floor
                    self._scene.addItem(glow_item)
            
            # Draw small golden treasure icon at center
            center_x, center_y = chamber_info['center']
            center_px = center_x * tile_size + tile_size // 2
            center_py = center_y * tile_size + tile_size // 2
            
            treasure = QGraphicsEllipseItem(center_px - 8, center_py - 8, 16, 16)
            treasure.setBrush(QBrush(QColor("#FFD700")))
            treasure.setPen(QPen(QColor("#FFA500"), 2))
            treasure.setZValue(3)
            self._scene.addItem(treasure)
    
    def _draw_fog(self, into=None):
        """Draw fog of war overlay
        
        Args:
            into: Optional QGraphicsItemGroup or scene to add items to
        """
        from PySide6.QtWidgets import QGraphicsItemGroup
        
        into = into or self._scene  # Default to scene if not specified
        tile_size = self.grid_map.tile_size
        
        # Update fog visibility based on current player positions
        # If player_index is set, only show fog for that specific player
        player_positions = []
        if self.player_index is not None:
            # Single player view - show only this player's perspective
            # In dual mode, each GameState has only 1 player at index 0
            if len(self.game_state.players) > 0:
                player = self.game_state.players[0]  # Always use index 0 in dual mode
                pos = self.grid_map.get_player_position(player.id)
                if pos:
                    player_positions.append(pos)
        else:
            # Both players view (legacy mode)
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
                    fog_tile.setPen(QPen(Qt.PenStyle.NoPen))
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
                self._scene.removeItem(item)
                # Stop sprite timers if present
                if hasattr(item, 'timer'):
                    item.timer.stop()  # type: ignore[attr-defined]
            
            # Remove all children from monster group (but keep monster sprites alive)
            monster_sprites_to_keep = set(self.monster_sprites.values())
            for item in list(self._dyn_monsters.childItems()):
                if item not in monster_sprites_to_keep:
                    self._dyn_monsters.removeFromGroup(item)
                    self._scene.removeItem(item)
                else:
                    # Just remove from group, don't delete
                    self._dyn_monsters.removeFromGroup(item)
            
            # Remove all children from fog group
            for item in list(self._dyn_fog.childItems()):
                self._dyn_fog.removeFromGroup(item)
                self._scene.removeItem(item)
            
            # Clear player sprites tracking (will be rebuilt)
            self.player_sprites.clear()
            
            # DON'T clear monster sprites - they persist and get reused
            # self.monster_sprites.clear()  # REMOVED
            
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
        self._scene.addItem(text)
        
        # Animate fade out and remove after 600ms
        # Animate fade out and remove after 600ms
        def cleanup():
            try:
                if text.scene():
                    self._scene.removeItem(text)
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
                    # Update monster HP bar
                    if hasattr(self.game_state, 'monster_system'):
                        monster_state = self.game_state.monster_system.active_monsters.get(vertex_id)
                        if monster_state and vertex_id in self.monster_sprites:
                            goblin_sprite = self.monster_sprites[vertex_id]
                            goblin_sprite.update_hp(monster_state.monster.hp, monster_state.monster.max_hp)
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
                try:
                    sprite_item.setPos(orig_pos)
                except RuntimeError:
                    pass  # Sprite was deleted
                return
            
            try:
                offset_x = random.randint(-5, 5)
                offset_y = random.randint(-5, 5)
                sprite_item.setPos(orig_pos.x() + offset_x, orig_pos.y() + offset_y)
                QTimer.singleShot(50, lambda: jitter(count + 1))
            except RuntimeError:
                pass  # Sprite was deleted
            
        jitter()

    def _on_monster_move(self, ms, old_v, new_v):
        """Callback when a monster moves - updates Goblin animation direction"""
        # Get grid positions
        old_pos = self.grid_map.get_position_for_vertex(old_v)
        new_pos = self.grid_map.get_position_for_vertex(new_v)
        
        if old_pos and new_pos:
            # Determine movement direction
            dx = new_pos[0] - old_pos[0]
            
            # Update sprite animation direction if it exists
            if old_v in self.monster_sprites:
                goblin_sprite = self.monster_sprites[old_v]
                
                # Change animation based on horizontal movement
                if dx > 0:  # Moving right
                    goblin_sprite.walk_right()
                elif dx < 0:  # Moving left
                    goblin_sprite.walk_left()
        
        # Trigger refresh of dynamic layers to show new position
        self._refresh_dynamic_layers()
    
    def _on_unit_death(self, unit, unit_type):
        """Callback when a unit dies"""
        # Evitar processamento duplicado - marcar unidade como processada
        if hasattr(unit, '_death_processed'):
            return
        unit._death_processed = True
        
        print(f"[DEBUG] Unit died: {unit} ({unit_type})")
        
        # Determine position
        x, y = 0, 0
        vertex_id = None
        
        if unit_type == "player":
            grid_pos = self.grid_map.get_player_position(unit.id)
            if grid_pos: x, y = grid_pos
        else:
            # Monster - find the MonsterState that contains this monster
            if hasattr(self.game_state, 'monster_system'):
                for v_id, monster_state in self.game_state.monster_system.active_monsters.items():
                    if monster_state.monster == unit:
                        vertex_id = v_id
                        
                        # Play death animation on the Goblin sprite (apenas na primeira view)
                        if vertex_id in self.monster_sprites:
                            goblin_sprite = self.monster_sprites[vertex_id]
                            
                            # Verificar se a animação já foi iniciada
                            if not hasattr(goblin_sprite, '_death_anim_started'):
                                goblin_sprite._death_anim_started = True
                                goblin_sprite.die()
                                
                                # Remove sprite after death animation completes
                                def remove_goblin():
                                    try:
                                        if goblin_sprite.scene():
                                            self._scene.removeItem(goblin_sprite)
                                        if vertex_id in self.monster_sprites:
                                            del self.monster_sprites[vertex_id]
                                    except RuntimeError:
                                        pass
                                
                                # Death animation is 4 frames * 200ms = 800ms
                                QTimer.singleShot(900, remove_goblin)
                        
                        grid_pos = self.grid_map.get_position_for_vertex(vertex_id)
                        if grid_pos: x, y = grid_pos
                        break
            
            # Fallback if not found in monster system
            if vertex_id is None and hasattr(unit, 'grid_pos') and unit.grid_pos:
                x, y = unit.grid_pos

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
        self._scene.addItem(skull)
        
        # Animate fade out
        def cleanup():
            try:
                if skull.scene():
                    self._scene.removeItem(skull)
            except RuntimeError:
                pass
        QTimer.singleShot(1500, cleanup)
        
        # Refresh board to remove the unit sprite (only if not monster with death animation)
        if unit_type != "monster":
            self._refresh_dynamic_layers()

    def keyPressEvent(self, event: QKeyEvent):
        """Handle keyboard input for movement - separate controls per player"""
        key = event.key()
        
        # Add key to pressed_keys set for continuous movement
        # Movement is processed by _process_continuous_movement() every 150ms
        valid_keys = {
            Qt.Key.Key_Up, Qt.Key.Key_Down, Qt.Key.Key_Left, Qt.Key.Key_Right,  # Player Vermelho
            Qt.Key.Key_W, Qt.Key.Key_S, Qt.Key.Key_A, Qt.Key.Key_D  # Player Azul
        }
        
        if key in valid_keys:
            self.pressed_keys.add(key)
        else:
            super().keyPressEvent(event)
    
    def keyReleaseEvent(self, event: QKeyEvent):
        """Handle key release to stop continuous movement"""
        key = event.key()
        self.pressed_keys.discard(key)  # Remove key from pressed set
        super().keyReleaseEvent(event)
    
    def _process_continuous_movement(self):
        """Process continuous movement for all currently pressed keys"""
        for key in list(self.pressed_keys):  # Use list() to avoid modification during iteration
            # Determine player and direction based on key
            player_to_move = None
            direction = None
            
            # Player Vermelho (Red) - Arrow Keys
            if key == Qt.Key.Key_Up:
                player_to_move = self._get_player_by_color("#FF0000")
                direction = "up"
            elif key == Qt.Key.Key_Down:
                player_to_move = self._get_player_by_color("#FF0000")
                direction = "down"
            elif key == Qt.Key.Key_Left:
                player_to_move = self._get_player_by_color("#FF0000")
                direction = "left"
            elif key == Qt.Key.Key_Right:
                player_to_move = self._get_player_by_color("#FF0000")
                direction = "right"
            # Player Azul (Blue) - WASD
            elif key == Qt.Key.Key_W:
                player_to_move = self._get_player_by_color("#0000FF")
                direction = "up"
            elif key == Qt.Key.Key_S:
                player_to_move = self._get_player_by_color("#0000FF")
                direction = "down"
            elif key == Qt.Key.Key_A:
                player_to_move = self._get_player_by_color("#0000FF")
                direction = "left"
            elif key == Qt.Key.Key_D:
                player_to_move = self._get_player_by_color("#0000FF")
                direction = "right"
            else:
                continue  # Skip unknown keys
            
            if not player_to_move:
                continue
            
            # In split-screen mode, only respond if this view controls this player
            if self.player_index is not None:
                if player_to_move not in self.game_state.players:
                    continue  # This view doesn't control this player
            
            # Get current position
            grid_pos = self.grid_map.get_player_position(player_to_move.id)
            if not grid_pos:
                continue
            
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
                if not self.grid_map.obstacle_manager.can_pass((new_x, new_y), player_to_move):
                    continue  # Can't move through obstacle
            
            # Check if movement is valid and player has stamina
            if self.grid_map.can_move_to(new_x, new_y):
                stamina_cost = 3
                if player_to_move.stamina >= stamina_cost:
                    # Perform movement (without animation for continuous movement)
                    self._move_player_instant(player_to_move.id, new_x, new_y, direction)
    
    def _get_player_by_color(self, color: str):
        """Get player by color"""
        for player in self.game_state.players:
            if player.color == color:
                return player
        return None
    
    def _move_player_instant(self, player_id: int, new_x: int, new_y: int, direction: str):
        """Move player instantly without animation (for continuous movement)"""
        player = self.game_state._get_player(player_id)
        if not player:
            return
        
        # Get old position
        old_pos = self.grid_map.get_player_position(player_id)
        
        # Update grid position
        self.grid_map.set_player_position(player_id, new_x, new_y)
        
        # Consume stamina
        stamina_cost = 3
        player.consume_stamina(stamina_cost)
        
        # Update sprite position instantly (no animation) and show walking sprite
        if player_id in self.player_sprites:
            sprite = self.player_sprites[player_id]
            
            # Start walking animation
            sprite.start_walking(direction)
            
            # Update position
            tile_size = self.grid_map.tile_size
            px = new_x * tile_size + tile_size // 2
            py = new_y * tile_size + tile_size // 2
            sprite_x = px - 20
            sprite_y = py - 25
            sprite.setPos(sprite_x, sprite_y)
            
            # Keep walking animation active longer to be visible during continuous movement
            # Return to idle just before next movement cycle (250ms - 50ms buffer = 200ms)
            QTimer.singleShot(200, lambda: sprite.stop_walking() if sprite else None)
        
        # Check if there's a vertex at this position
        vertex_id = self.grid_map.get_vertex_at_position(new_x, new_y)
        if vertex_id is not None:
            player.current_vertex_id = vertex_id
            
            # Check for monster (but don't show dialog during continuous movement)
            if hasattr(self.game_state, 'monster_system'):
                monster_state = self.game_state.monster_system.active_monsters.get(vertex_id)
                if monster_state and monster_state.monster.is_alive():
                    # Stop continuous movement when encountering monster
                    self.pressed_keys.clear()
                    self.show_monster_interaction_dialog(monster_state, player)
                    return
            
            self.game_state.enter_vertex(player, vertex_id)
            self.game_state.check_victory()
        
        # Don't refresh dynamic layers here - it recreates sprites and breaks animation!
        # Just update fog of war directly
        self._update_fog()
    
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
        stamina_cost = 3
        player.consume_stamina(stamina_cost)
        
        # Check if there's a vertex at this position
        vertex_id = self.grid_map.get_vertex_at_position(new_x, new_y)
        if vertex_id is not None:
            # Update game state
            player.current_vertex_id = vertex_id
            
            # Check if there's a monster at this vertex
            if hasattr(self.game_state, 'monster_system'):
                monster_state = self.game_state.monster_system.active_monsters.get(vertex_id)
                if monster_state and monster_state.monster.is_alive():
                    # Player encountered a monster - show interaction dialog
                    self.show_monster_interaction_dialog(monster_state, player)
                    return  # Don't continue with normal vertex entry
            
            self.game_state.enter_vertex(player, vertex_id)
            self.game_state.check_victory()
        
        # print(f"🚶 {player.name} moveu de {old_pos} para ({new_x}, {new_y}) [direção: {direction}] - Stamina: -{stamina_cost}")
        # self.game_state.log(f"🚶 {player.name} moveu para ({new_x}, {new_y}) - Stamina: -{stamina_cost}")
        
        # Center camera on player after movement
        self.center_on_current_player()
        
        # Animate movement if sprite exists
        if player_id in self.player_sprites and old_pos is not None:
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
        animation.setDuration(100)  # 100ms for very fast, responsive movement
        animation.setStartValue(start_pos)
        animation.setEndValue(end_pos)
        animation.setEasingCurve(QEasingCurve.Type.InOutQuad)  # Smooth easing for better feel
        
        # Update sprite position on each animation step
        def update_position(value):
            if sprite:
                try:
                    sprite.setPos(value)
                except RuntimeError:
                    pass  # Sprite was deleted
        
        animation.valueChanged.connect(update_position)
        
        # When animation finishes
        def on_animation_finished():
            # Return sprite to idle state
            if sprite:
                try:
                    sprite.stop_walking()
                except RuntimeError:
                    pass  # Sprite was deleted
            
            # Refresh UI to update fog
            # Note: Commenting this out to allow simultaneous player movement
            # Each view will refresh independently
            # if self.main_window:
            #     self.main_window.refresh_all()
            
            # Refresh only this view's fog
            self._refresh_dynamic_layers()
            
            # Add a very short delay before allowing next movement
            QTimer.singleShot(20, lambda: setattr(self, 'is_animating', False))
        
        animation.finished.connect(on_animation_finished)
        
        # Start animation
        animation.start()
        
        # Store animation to prevent garbage collection
        self.current_animation = animation
    
    def show_interaction_dialog(self, obstacle, player):
        """Show interaction dialog for obstacle encounter"""
        from .interaction_dialog import InteractionDialog
        from core.obstacle_manager import ObstacleType
        
        # Pause game loop while dialog is open
        if self.main_window and hasattr(self.main_window, 'game_timer'):
            self.main_window.game_timer.stop()
        
        # Create and show dialog
        dialog = InteractionDialog(obstacle, player, self)
        result = dialog.exec()
        
        # Resume game loop
        if self.main_window and hasattr(self.main_window, 'game_timer'):
            self.main_window.game_timer.start()
        
        if result == QDialog.DialogCode.Accepted:
            action = dialog.get_selected_action()
            self.handle_interaction_action(action, obstacle, player)
    
    def show_monster_interaction_dialog(self, monster_state, player):
        """Show interaction dialog when player encounters a monster"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGridLayout, QProgressBar
        from PySide6.QtCore import Qt, QTimer
        from PySide6.QtGui import QFont
        
        # Pause game loop while dialog is open
        if self.main_window and hasattr(self.main_window, 'game_timer'):
            self.main_window.game_timer.stop()
        
        dialog = QDialog(self)
        dialog.setWindowTitle("⚔️ Encontro com Monstro!")
        dialog.setModal(True)
        dialog.setMinimumWidth(500)
        dialog.setMinimumHeight(400)
        
        # Set dialog stylesheet for light text on dark background
        dialog.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
            }
            QLabel {
                color: #ffffff;
                background-color: transparent;
            }
            QPushButton {
                background-color: #4a4a4a;
                color: #ffffff;
                border: 2px solid #666666;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
                border-color: #888888;
            }
            QPushButton:pressed {
                background-color: #3a3a3a;
            }
            QProgressBar {
                border: 2px solid #666666;
                border-radius: 5px;
                text-align: center;
                background-color: #1a1a1a;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Title
        monster = monster_state.monster
        title_label = QLabel(f"👹 {monster.monster_type.value.title()} Lv{monster.level} bloqueando o caminho!")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Monster stats with HP bar
        stats_layout = QGridLayout()
        stats_layout.addWidget(QLabel("❤️ HP:"), 0, 0)
        monster_hp_label = QLabel(f"{monster.hp}/{monster.max_hp}")
        stats_layout.addWidget(monster_hp_label, 0, 1)
        
        # Monster HP progress bar
        monster_hp_bar = QProgressBar()
        monster_hp_bar.setMaximum(monster.max_hp)
        monster_hp_bar.setValue(monster.hp)
        monster_hp_bar.setTextVisible(True)
        monster_hp_bar.setFormat(f"%v / {monster.max_hp} HP")
        stats_layout.addWidget(monster_hp_bar, 0, 2)
        
        stats_layout.addWidget(QLabel("⚔️ Ataque:"), 1, 0)
        stats_layout.addWidget(QLabel(str(monster.attack)), 1, 1)
        stats_layout.addWidget(QLabel("🛡️ Defesa:"), 2, 0)
        stats_layout.addWidget(QLabel(str(monster.defense)), 2, 1)
        stats_layout.addWidget(QLabel("⚡ Velocidade:"), 3, 0)
        stats_layout.addWidget(QLabel(str(monster.speed)), 3, 1)
        layout.addLayout(stats_layout)
        
        layout.addSpacing(20)
        
        # Player stats with HP bar
        player_label = QLabel(f"📊 {player.name}")
        player_font = QFont()
        player_font.setPointSize(12)
        player_font.setBold(True)
        player_label.setFont(player_font)
        layout.addWidget(player_label)
        
        player_stats_layout = QGridLayout()
        player_stats_layout.addWidget(QLabel("❤️ HP:"), 0, 0)
        player_hp_label = QLabel(f"{player.hp}/{player.max_hp}")
        player_stats_layout.addWidget(player_hp_label, 0, 1)
        
        # Player HP progress bar
        player_hp_bar = QProgressBar()
        player_hp_bar.setMaximum(player.max_hp)
        player_hp_bar.setValue(player.hp)
        player_hp_bar.setTextVisible(True)
        player_hp_bar.setFormat(f"%v / {player.max_hp} HP")
        player_stats_layout.addWidget(player_hp_bar, 0, 2)
        
        player_stats_layout.addWidget(QLabel("⚔️ Ataque:"), 1, 0)
        player_attack_label = QLabel(str(player.attack))
        player_stats_layout.addWidget(player_attack_label, 1, 1)
        player_stats_layout.addWidget(QLabel("🛡️ Defesa:"), 2, 0)
        player_defense_label = QLabel(str(player.defense))
        player_stats_layout.addWidget(player_defense_label, 2, 1)
        player_stats_layout.addWidget(QLabel("💧 Stamina:"), 3, 0)
        player_stamina_label = QLabel(f"{int(player.stamina)}/{player.max_stamina}")
        player_stats_layout.addWidget(player_stamina_label, 3, 1)
        layout.addLayout(player_stats_layout)
        
        layout.addSpacing(20)
        
        # Action buttons
        actions_label = QLabel("O que você deseja fazer?")
        actions_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(actions_label)
        
        buttons_layout = QVBoxLayout()
        
        # Combat button
        combat_btn = QPushButton("⚔️ Iniciar Combate")
        combat_btn.setMinimumHeight(40)
        buttons_layout.addWidget(combat_btn)
        
        # Inventory button
        inventory_btn = QPushButton("🎒 Ver Inventário")
        inventory_btn.setMinimumHeight(40)
        inventory_btn.clicked.connect(lambda: self._handle_monster_action("inventory", dialog, monster_state, player))
        buttons_layout.addWidget(inventory_btn)
        
        # Cards button
        cards_btn = QPushButton(f"🎴 Usar Carta ({len(player.hand_cards)} cartas)")
        cards_btn.setMinimumHeight(40)
        cards_btn.clicked.connect(lambda: self._handle_monster_action("cards", dialog, monster_state, player))
        buttons_layout.addWidget(cards_btn)
        
        # Flee button
        flee_btn = QPushButton("🏃 Tentar Fugir")
        flee_btn.setMinimumHeight(40)
        flee_btn.clicked.connect(lambda: self._handle_monster_action("flee", dialog, monster_state, player))
        buttons_layout.addWidget(flee_btn)
        
        layout.addLayout(buttons_layout)
        dialog.setLayout(layout)
        
        # Combat update timer (runs during combat)
        combat_timer = QTimer(dialog)
        combat_timer.setInterval(120)  # Same as game loop tick rate
        
        def update_combat():
            """Update combat state and HP displays"""
            if hasattr(self.game_state, 'combat_manager'):
                # Update combat system
                self.game_state.combat_manager.update(0.12)
                
                # Update HP labels and bars
                player_hp_label.setText(f"{player.hp}/{player.max_hp}")
                player_hp_bar.setValue(player.hp)
                player_hp_bar.setFormat(f"{player.hp} / {player.max_hp} HP")
                
                monster_hp_label.setText(f"{monster.hp}/{monster.max_hp}")
                monster_hp_bar.setValue(monster.hp)
                monster_hp_bar.setFormat(f"{monster.hp} / {monster.max_hp} HP")
                
                player_stamina_label.setText(f"{int(player.stamina)}/{player.max_stamina}")
                
                # Check end conditions
                if not player.is_alive or not monster.is_alive():
                    combat_timer.stop()
                    
                    # Show result message
                    if not player.is_alive:
                        actions_label.setText("💀 Você foi derrotado!")
                    elif not monster.is_alive():
                        actions_label.setText(f"🏆 Vitória! +{monster.get_reward_gold() if hasattr(monster, 'get_reward_gold') else 0} Gold")
                    
                    # Close dialog after 2 seconds
                    QTimer.singleShot(2000, dialog.accept)
        
        def start_combat():
            """Initialize combat and start update timer"""
            # Start combat via combat manager
            if hasattr(self.game_state, 'combat_manager'):
                self.game_state.combat_manager.start_combat(player, monster)
                self.game_state.log(f"⚔️ {player.name} iniciou combate contra {monster.monster_type.value.title()}!")
                
                # Disable action buttons during combat
                combat_btn.setEnabled(False)
                inventory_btn.setEnabled(False)
                cards_btn.setEnabled(False)
                flee_btn.setEnabled(False)
                
                # Update label
                actions_label.setText("⚔️ Combate em andamento...")
                
                # Start combat update timer
                combat_timer.start()
        
        combat_timer.timeout.connect(update_combat)
        combat_btn.clicked.connect(start_combat)
        
        dialog.exec()
        
        # Clean up timer
        combat_timer.stop()
        
        # After dialog closes, check if monster died and remove it
        if not monster.is_alive():
            # Remove monster from monster system
            if hasattr(self.game_state, 'monster_system'):
                vertex_id = player.current_vertex_id  # Monster is at same position as player
                if vertex_id in self.game_state.monster_system.active_monsters:
                    del self.game_state.monster_system.active_monsters[vertex_id]
                    self.game_state.log(f"🗑️ {monster.monster_type.value.title()} removido do mapa")
                
                # Remove monster sprite from view
                if vertex_id in self.monster_sprites:
                    sprite = self.monster_sprites[vertex_id]
                    if sprite.scene():
                        self._scene.removeItem(sprite)
                    del self.monster_sprites[vertex_id]
            
            # Refresh to update view
            self._update_fog()
        
        # Resume game loop after dialog closes
        if self.main_window and hasattr(self.main_window, 'game_timer'):
            self.main_window.game_timer.start()
    
    def _handle_monster_action(self, action, dialog, monster_state, player):
        """Handle monster interaction action"""
        if action == "combat":
            # Start combat
            self.game_state.log(f"⚔️ {player.name} iniciou combate contra {monster_state.monster.monster_type.value.title()}!")
            dialog.accept()
            
            # Start combat via CombatManager
            self.game_state.start_combat(player, monster_state.monster)
            
            # Refresh UI
            if self.main_window:
                self.main_window.refresh_all()
        
        elif action == "inventory":
            # Show inventory
            self.game_state.log(f"🎒 {player.name} abriu o inventário")
            from .inventory_dialog import InventoryDialog
            inv_dialog = InventoryDialog(player, self.game_state, self)
            inv_dialog.exec()
            
            # Update stats in combat dialog after closing inventory
            if hasattr(dialog, 'update_stats'):
                dialog.update_stats()
            
            if self.main_window:
                self.main_window.refresh_all()
        
        elif action == "cards":
            # Show cards
            self.game_state.log(f"🎴 {player.name} está analisando suas cartas...")
            from .cards_dialog import CardsDialog
            cards_dialog = CardsDialog(player, self.game_state, self)
            cards_dialog.exec()
            
            # Update stats in combat dialog after closing cards
            if hasattr(dialog, 'update_stats'):
                dialog.update_stats()
            
            if self.main_window:
                self.main_window.refresh_all()
        
        elif action == "flee":
            # "Tentar fugir" que deve apenas fechar a aba de opções, permitindo a continuidade do jogo.
            self.game_state.log(f"🏃 {player.name} decidiu ignorar o monstro por enquanto.")
            dialog.reject() # Close the dialog
            
            if self.main_window:
                self.main_window.refresh_all()
    
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

    def play_victory_animation(self):
        """Play victory animation: golden light burst from treasure chest"""
        self.victory_animation_played = True
        
        vertex_id = self.game_state.treasure_vertex_id
        if vertex_id is None:
            return
            
        chamber_info = self.grid_map.chambers.get(vertex_id)
        if not chamber_info:
            return
            
        center_x, center_y = chamber_info['center']
        tile_size = self.grid_map.tile_size
        px = center_x * tile_size + tile_size // 2
        py = center_y * tile_size + tile_size // 2
        
        # Create light burst item
        from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsSimpleTextItem
        from PySide6.QtGui import QRadialGradient, QBrush, QColor, QFont
        from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QPointF, QVariantAnimation
        from PySide6.QtCore import Qt
        
        # Large yellow circle with gradient
        radius = 10
        light = QGraphicsEllipseItem(-radius, -radius, radius*2, radius*2)
        light.setPos(px, py)
        light.setZValue(20) # Topmost
        
        gradient = QRadialGradient(0, 0, radius)
        gradient.setColorAt(0, QColor(255, 255, 200, 255)) # White-yellow center
        gradient.setColorAt(0.5, QColor(255, 215, 0, 200)) # Gold middle
        gradient.setColorAt(1, QColor(255, 140, 0, 0))     # Transparent orange edge
        light.setBrush(QBrush(gradient))
        light.setPen(Qt.PenStyle.NoPen)
        
        self._scene.addItem(light)
        
        # 1. Expand Animation
        expand = QVariantAnimation(self)
        expand.setDuration(2000)
        expand.setStartValue(1.0)
        expand.setEndValue(30.0) # Expand 30x
        expand.setEasingCurve(QEasingCurve.Type.OutExpo)
        
        def update_scale(s):
            light.setTransform(light.transform().fromScale(s, s))
            
        expand.valueChanged.connect(update_scale)
        expand.start()
        
        # 2. Add text
        text = QGraphicsSimpleTextItem("TESOURO ENCONTRADO!")
        font = QFont("Arial", 24, QFont.Weight.Bold)
        text.setFont(font)
        text.setBrush(QBrush(QColor("white")))
        
        # Center text (approx width calculation)
        text_width = text.boundingRect().width()
        text.setPos(px - text_width/2, py - 50)
        text.setZValue(21)
        self._scene.addItem(text)
        
        # Keep references
        self.victory_anim = expand 




