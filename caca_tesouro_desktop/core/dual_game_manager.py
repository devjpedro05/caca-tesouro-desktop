"""
Dual Game Manager - Manages separate game states for each player
"""
from typing import Optional, Tuple, TYPE_CHECKING
from .game_state import GameState, GameMode
from .player import Player
from .graph import Graph

if TYPE_CHECKING:
    from .grid_map import GridMap

class DualGameManager:
    """
    Manages two independent game states - one for each player
    Handles victory conditions and game synchronization
    """
    
    def __init__(self):
        # Create two independent game states
        self.game_state_p1: Optional[GameState] = None
        self.game_state_p2: Optional[GameState] = None
        
        # Shared graph structure (same map layout for both players)
        self.shared_graph: Optional[Graph] = None
        
        # Victory tracking
        self.winner: Optional[Player] = None
        self.game_over = False
        
        # Victory conditions
        self.victory_points_target = 100  # Points needed to win
        self.treasure_hunt_mode = True  # If True, finding treasure wins instantly
        
    def initialize_dual_games(self, graph: Graph, player1_name: str = "Explorador Azul", 
                             player2_name: str = "Explorador Vermelho"):
        """
        Initialize two separate game states with the same graph structure
        """
        from .grid_map import GridMap
        from .obstacle_manager import ObstacleManager
        
        self.shared_graph = graph
        
        # ===== PLAYER 1 GAME STATE =====
        self.game_state_p1 = GameState()
        self.game_state_p1.graph = graph
        
        # Create grid map for P1 and generate dungeon
        self.game_state_p1.grid_map = GridMap(20, 20)
        self.game_state_p1.grid_map.obstacle_manager = ObstacleManager()
        self.game_state_p1.grid_map.obstacle_manager.grid_map = self.game_state_p1.grid_map
        self.game_state_p1.grid_map.create_from_graph(graph)  # Generate dungeon from graph
        
        # Create player 1
        player1 = Player(0, player1_name, "#0000FF", 0)  # Blue
        player1.current_vertex_id = 0
        self.game_state_p1.players = [player1]
        self.game_state_p1.current_player_index = 0
        
        # ===== PLAYER 2 GAME STATE =====
        self.game_state_p2 = GameState()
        self.game_state_p2.graph = graph
        
        # Create grid map for P2 (independent from P1)
        self.game_state_p2.grid_map = GridMap(20, 20)
        self.game_state_p2.grid_map.obstacle_manager = ObstacleManager()
        self.game_state_p2.grid_map.obstacle_manager.grid_map = self.game_state_p2.grid_map
        self.game_state_p2.grid_map.create_from_graph(graph)  # Generate dungeon from graph
        
        # Create player 2
        player2 = Player(1, player2_name, "#FF0000", 0)  # Red
        player2.current_vertex_id = 0
        self.game_state_p2.players = [player2]
        self.game_state_p2.current_player_index = 0
        
        # Set treasure location (same for both)
        if graph.vertices:
            treasure_vertex = max(range(len(graph.vertices)), 
                                key=lambda i: len(graph.vertices[i].name))
            self.game_state_p1.treasure_vertex_id = treasure_vertex
            self.game_state_p2.treasure_vertex_id = treasure_vertex
        
        # Initialize grid positions for both players
        self._initialize_grid_positions(self.game_state_p1)
        self._initialize_grid_positions(self.game_state_p2)
        
        # Spawn initial monsters for both (independent spawns)
        self._spawn_initial_monsters(self.game_state_p1)
        self._spawn_initial_monsters(self.game_state_p2)
        
        print(f"[DUAL_GAME] ✅ Game initialized - {player1.name} vs {player2.name}")
        print(f"[DUAL_GAME] Treasure at vertex {self.game_state_p1.treasure_vertex_id}")
    
    def _initialize_grid_positions(self, game_state: GameState):
        """Initialize grid positions for graph vertices and players"""
        # Map vertex IDs to grid positions
        vertex_to_grid = {
            0: (9, 2),   # Entrada
            1: (3, 6),   # Caverna Azul
            2: (3, 14),  # Salão dos Ecos
            3: (9, 10),  # Túnel Escuro
            4: (9, 18),  # Ponte de Pedra
            5: (15, 6),  # Lago Subterrâneo
            6: (15, 14), # Câmara do Tesouro
        }
        
        # Assign grid positions to vertices
        for vertex_id, (row, col) in vertex_to_grid.items():
            if vertex_id in game_state.graph.vertices:
                vertex = game_state.graph.vertices[vertex_id]
                vertex.grid_pos = (row, col)
        
        # Add player to grid_map at starting position
        if game_state.players and game_state.grid_map:
            player = game_state.players[0]
            start_vertex_id = player.current_vertex_id
            if start_vertex_id in vertex_to_grid:
                start_pos = vertex_to_grid[start_vertex_id]
                game_state.grid_map.set_player_position(player.id, start_pos[0], start_pos[1])
                print(f"[DUAL_GAME] {player.name} placed at grid position {start_pos}")
    
    def _spawn_initial_monsters(self, game_state: GameState):
        """Mark vertices as having monsters - GridBoardView will render them"""
        # Define monster spawn locations (vertex_id, level)
        monster_spawns = [
            (2, 1),    # Salão dos Ecos - Level 1
            (3, 2),    # Túnel Escuro - Level 2  
            (4, 1),    # Ponte de Pedra - Level 1
            (5, 3),    # Lago Subterrâneo - Level 3
        ]
        
        for vertex_id, level in monster_spawns:
            if vertex_id in game_state.graph.vertices:
                vertex = game_state.graph.vertices[vertex_id]
                # Mark vertex as having monster - this is enough for rendering
                vertex.has_monster = True
                vertex.monster_type = "goblin"
                vertex.monster_level = level
        
        print(f"[DUAL_GAME] Marked {len(monster_spawns)} vertices with monsters for {game_state.players[0].name if game_state.players else 'player'}")
    
    def get_player1(self) -> Optional[Player]:
        """Get Player 1"""
        if self.game_state_p1 and self.game_state_p1.players:
            return self.game_state_p1.players[0]
        return None
    
    def get_player2(self) -> Optional[Player]:
        """Get Player 2"""
        if self.game_state_p2 and self.game_state_p2.players:
            return self.game_state_p2.players[0]
        return None
    
    def check_victory_conditions(self) -> Optional[Player]:
        """
        Check if any player has won
        Returns the winning player or None
        """
        if self.game_over:
            return self.winner
        
        p1 = self.get_player1()
        p2 = self.get_player2()
        
        if not p1 or not p2:
            return None
        
        # Check if player 1 won
        if p1 and self.game_state_p1 and self._check_player_victory(p1, self.game_state_p1):
            self.winner = p1
            self.game_over = True
            self.game_state_p1.game_mode = GameMode.VICTORY
            if self.game_state_p2:
                self.game_state_p2.game_mode = GameMode.DEFEAT
            return p1
        
        # Check if player 2 won
        if p2 and self.game_state_p2 and self._check_player_victory(p2, self.game_state_p2):
            self.winner = p2
            self.game_over = True
            if self.game_state_p1:
                self.game_state_p1.game_mode = GameMode.DEFEAT
            self.game_state_p2.game_mode = GameMode.VICTORY
            return p2
        
        return None
    
    def _check_player_victory(self, player: Player, game_state: GameState) -> bool:
        """
        Check if a specific player has won
        Victory conditions:
        1. Treasure Hunt Mode: Reach treasure vertex
        2. Points Mode: Accumulate enough victory points
        3. Hybrid: Either condition wins
        """
        # Treasure hunt victory
        if self.treasure_hunt_mode:
            if player.current_vertex_id == game_state.treasure_vertex_id:
                return True
        
        # Points victory
        victory_points = self._calculate_victory_points(player)
        if victory_points >= self.victory_points_target:
            return True
        
        return False
    
    def _calculate_victory_points(self, player: Player) -> int:
        """
        Calculate victory points for a player
        Points from:
        - Gold collected (1 gold = 1 point)
        - Monsters defeated (based on level)
        - Experience gained
        - Items collected
        """
        points = 0
        
        # Gold
        points += player.gold
        
        # Experience (10 XP = 1 point)
        points += player.experience // 10
        
        # Level bonus
        points += (player.level - 1) * 10
        
        # Items (5 points per item)
        points += len(player.inventory) * 5
        
        return points
    
    def get_scores(self) -> Tuple[int, int]:
        """Get current scores for both players"""
        p1 = self.get_player1()
        p2 = self.get_player2()
        
        score_p1 = self._calculate_victory_points(p1) if p1 else 0
        score_p2 = self._calculate_victory_points(p2) if p2 else 0
        
        return score_p1, score_p2
    
    def update(self, delta_time: float):
        """
        Update both game states
        Called each frame
        """
        if self.game_over:
            return
        
        # Update both game states independently
        if self.game_state_p1:
            self.game_state_p1.combat_manager.update(delta_time)
        
        if self.game_state_p2:
            self.game_state_p2.combat_manager.update(delta_time)
        
        # Check victory conditions
        winner = self.check_victory_conditions()
        if winner:
            print(f"[DUAL_GAME] 🏆 {winner.name} VENCEU O JOGO! 🏆")
