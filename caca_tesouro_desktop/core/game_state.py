"""
Complete Game State Management
Integrates all game systems: graph, players, cards, obstacles, combat, events, resources
"""
import random
from enum import Enum
from typing import List, Optional, Dict, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from .grid_map import GridMap

from .graph import Graph, BiomeType, HazardType, EdgeType
from .player import Player, BuffType, Buff
from .cards import Card, CardType, CardRarity
from .obstacles import Monster, MonsterType, Obstacle, TreasureChestObstacle
from .algorithms import bfs, dijkstra, a_star
from .combat import CombatSystem, CombatResult
from .events import EventManager, EventType
from .resources import ResourceManager, ResourceType
from .systems.monster_system import MonsterSystem
from .systems.combat_system import CombatManager

class GameMode(Enum):
    """Game modes"""
    EXPLORATION = "exploration"
    COMBAT = "combat"
    VICTORY = "victory"
    DEFEAT = "defeat"

class GameState:
    """
    Main game state manager - integrates all game systems
    """
    def __init__(self):
        # Core components
        self.graph = Graph()
        self.players: List[Player] = []
        self.current_player_index = 0
        
        # Cards
        self.deck: List[Card] = []
        self.discard_pile: List[Card] = []
        self._next_card_id = 0
        
        # Game objectives
        self.treasure_vertex_id: Optional[int] = None
        # Game objectives
        self.treasure_vertex_id: Optional[int] = None
        self.boss_monster: Optional[Monster] = None
        self.monsters: List[Monster] = [] # Legacy list fallback
        
        # Game state
        self.turn_number = 0
        self.game_mode = GameMode.EXPLORATION
        self.game_over = False
        self.winner: Optional[Player] = None
        
        # Event system
        self.event_manager = EventManager()
        self.events_enabled = True
        
        # Logs
        self.logs: List[str] = []
        self.max_log_size = 100
        
        # Settings
        self.auto_combat = True
        self.random_events_per_turn = True
        self.monster_spawn_chance = 0.15
        self.resource_spawn_chance = 0.2

        #Systems
        self.monster_system = MonsterSystem(self)
        self.combat_manager = CombatManager(self)
        
        # Grid map (dynamically added by views or DualGameManager)
        self.grid_map: Optional['GridMap'] = None  # Will be set to GridMap instance
        
        # Main window reference (for UI updates)
        self.main_window = None

    
    @property
    def current_player(self) -> Optional[Player]:
        """Get current player"""
        if not self.players:
            return None
        return self.players[self.current_player_index]
    
    def log(self, message: str):
        """Add message to game log"""
        self.logs.append(message)
        print(f"[LOG] {message}")
        
        # Keep log size manageable
        if len(self.logs) > self.max_log_size:
            self.logs = self.logs[-self.max_log_size:]
    
    # ============================================
    # GAME INITIALIZATION
    # ============================================
    
    @staticmethod
    def new_default_game() -> 'GameState':
        """Create a new game with default settings"""
        gs = GameState()
        
        # Create graph
        gs.graph = Graph.sample_graph()
        
        # Setup players with SEPARATE starting positions
        p1 = Player(0, "Explorador Vermelho", "#FF0000", 0)  # Starts in vertex 0 (Red chamber)
        p2 = Player(1, "Explorador Azul", "#0000FF", 1)      # Starts in vertex 1 (Blue chamber)
        gs.players = [p1, p2]
        
        # Setup treasure (now in vertex 5/6)
        gs.treasure_vertex_id = 6
        
        # Create deck
        gs._create_deck()
        
        # Deal initial cards
        for player in gs.players:
            for _ in range(3):
                gs.draw_card(player.id)
        
        # Distribuir itens iniciais igualmente para ambos os jogadores
        from .resources import ResourceType
        initial_items = [
            ("Poção de Cura", "health_potion", 2),
            ("Escudo Nível 1", "shield_lv1", 1),
            ("Poção de Stamina", "stamina_potion", 2)
        ]
        for player in gs.players:
            for item_name, item_id, quantity in initial_items:
                for _ in range(quantity):
                    player.add_item({"name": item_name, "id": item_id, "type": "consumable"})
            gs.log(f"🎒 {player.name} recebeu itens iniciais: 2x Poção de Cura, 1x Escudo Nível 1, 2x Poção de Stamina")
        
        # Spawn initial resources (NO random monsters to avoid conflicts)
        gs.spawn_resources()
        
        # FORCE spawn exactly 4 monsters (NO random spawns)
        # v0="Entrada" at (9,2) (Player Vermelho), v1="Caverna Azul" at (3,6) (Player Azul)
        # Spawn in v2="Salão dos Ecos", v3="Túnel Escuro", v4="Ponte de Pedra", v5="Lago Subterrâneo" (centro)
        gs.graph.vertices[2].has_monster = True
        gs.graph.vertices[2].monster_type = "goblin"
        
        gs.graph.vertices[3].has_monster = True
        gs.graph.vertices[3].monster_type = "orc"  # Orc level 3 no Túnel Escuro
        
        gs.graph.vertices[4].has_monster = True
        gs.graph.vertices[4].monster_type = "goblin"
        
        gs.graph.vertices[5].has_monster = True
        gs.graph.vertices[5].monster_type = "goblin"
        
        # Ensure MonsterSystem has loaded monsters from graph
        if hasattr(gs, 'monster_system') and gs.monster_system:
            gs.monster_system.spawn_from_graph()
        
        gs.log("🎮 Jogo iniciado!")
        gs.log(f"🏆 O tesouro está em: {gs.graph.vertices[gs.treasure_vertex_id].name}")
        
        return gs
    
    def _create_deck(self):
        """Create the card deck"""
        # Card distribution
        card_counts = {
            CardType.CORDA: 8,
            CardType.ECO: 6,
            CardType.DESABAMENTO: 5,
            CardType.EXPLOSIVO: 4,
            CardType.CURA: 6,
            CardType.TELEPORTE: 3,
            CardType.ESCUDO: 5,
            CardType.VISAO: 2,
            CardType.REFORCO: 4,
            CardType.ARMADILHA: 3
        }
        
        for card_type, count in card_counts.items():
            for _ in range(count):
                value = 0
                if card_type == CardType.CORDA:
                    value = random.randint(1, 3)
                elif card_type == CardType.CURA:
                    value = random.randint(1, 3)
                
                card = Card(self._next_card_id, card_type, value)
                self._next_card_id += 1
                self.deck.append(card)
        
        random.shuffle(self.deck)
        self.log(f"📚 Baralho criado com {len(self.deck)} cartas")
    
    # ============================================
    # TURN MANAGEMENT
    # ============================================
    
    # ============================================
    # REAL-TIME UPDATE
    # ============================================

    def update(self, delta_time: float):
        """Global real-time update"""
        # 1. Update systems
        if self.monster_system:
            try:
                self.monster_system.update(delta_time)
            except Exception as e:
                self.log(f"[ERROR] MonsterSystem: {e}")

        if self.combat_manager:
            try:
                self.combat_manager.update(delta_time)
            except Exception as e:
                self.log(f"[ERROR] CombatManager: {e}")
        
        # 2. Update players (Resource Regen & Buffs)
        # Use a localized time accumulator for less frequent updates if needed, 
        # but for smooth bar animation, updating every tick is fine.
        for player in self.players:
            player.update(delta_time)

        # 3. Check Game Over
        self.check_game_over()

    # Legacy turn method removed/deprecated
    def execute_turn(self):
        """Deprecated: Real-time game logic handled in update()"""
        pass
    
    def end_turn(self):
         """Deprecated: Real-time game logic handled in update()"""
         pass

    def start_combat(self, player, monster):
        """
        Inicia um combate entre um jogador e um monstro via CombatManager.
        """
        if not self.combat_manager:
            print("[ERROR] CombatManager não inicializado!")
            return

        print(f"[COMBAT] {player.name} iniciou combate contra {monster.monster_type.value.title()}!")
        self.log(f"⚔️ (TickCombat) Iniciando combate: {player.name} vs {monster.monster_type.value.title()}")
        self.combat_manager.start_combat(player, monster)

    def get_monster_at(self, gx, gy):
        """
        Retorna o monstro que está na posição de grid (gx, gy).
        Procura tanto em MonsterSystem quanto na lista legada.
        """
        # Primeiro tenta MonsterSystem (novo)
        if hasattr(self, 'monster_system') and self.monster_system:
            # Procura o vertex que corresponde a essa grid position
            vertex_id = self.grid_map.get_vertex_at_position(gx, gy) if hasattr(self, 'grid_map') else None
            
            if vertex_id and vertex_id in self.monster_system.active_monsters:
                ms = self.monster_system.active_monsters[vertex_id]
                return ms.monster
        
        # Fallback 1: Check ObstacleManager (static obstacles that are monsters)
        if hasattr(self, 'grid_map') and hasattr(self.grid_map, 'obstacle_manager'):
            obstacle = self.grid_map.obstacle_manager.get_obstacle((gx, gy))
            if obstacle and obstacle.obstacle_type.value == "monster":
                # Create a temporary monster wrapper if needed
                # Ideally we should sync this with MonsterSystem, but for now just return a Monster object
                from .obstacles import Monster, MonsterType
                m_type_str = obstacle.data.get('type', 'goblin')
                try:
                    m_type = MonsterType(m_type_str)
                except:
                    m_type = MonsterType.GOBLIN
                
                # Check if we already have a live monster for this obstacle in monsters list
                for m in self.monsters:
                    if getattr(m, 'grid_pos', None) == (gx, gy):
                        return m
                
                # Create new temp monster
                new_monster = Monster(m_type, level=obstacle.data.get('level', 1))
                new_monster.grid_pos = (gx, gy)
                self.monsters.append(new_monster)
                return new_monster

        # Fallback 2: legacy list of monsters
        for monster in self.monsters:
            if hasattr(monster, "grid_pos") and monster.grid_pos == (gx, gy):
                return monster
        
        return None

    






    
    # ============================================
    # PLAYER ACTIONS
    # ============================================
    
    def roll_dice(self, sides: int = 20) -> int:
        """Roll dice"""
        value = random.randint(1, sides)
        self.log(f"🎲 {self.current_player.name} rolou: {value}")
        return value
    
    def move_player(self, player_id: int, edge_id: int) -> bool:
        """
        Move player along an edge
        Returns True if successful
        """
        player = self._get_player(player_id)
        edge = self.graph.edges.get(edge_id)
        
        if not player or not edge:
            return False
        
        # Check if player can act
        if not player.can_act():
            self.log(f"❌ {player.name} não pode agir (atordoado ou morto)!")
            return False
        
        # Check if edge is blocked
        if edge.blocked:
            self.log(f"❌ Movimento falhou: Túnel bloqueado!")
            return False
        
        # Check if edge connects to current vertex
        if player.current_vertex_id not in (edge.v1_id, edge.v2_id):
            self.log(f"❌ Movimento inválido: Túnel não conecta à posição atual")
            return False
        
        # ⭐ CHECK STAMINA (Real-time check)
        cost = edge.weight
        stamina_cost = cost * 2
        if player.stamina < stamina_cost:
            # Silent fail for smoothness or small log
            # self.log(f"❌ {player.name}: Stamina insuficiente!")
            return False
        
        # Check for obstacles on edge
        for obstacle in edge.obstacles:
            can_pass, reason = obstacle.can_pass(player)
            if not can_pass:
                self.log(f"🚫 {reason}")
                return False
        
        # Calculate new position
        new_vertex_id = edge.v2_id if edge.v1_id == player.current_vertex_id else edge.v1_id
        old_vertex = self.graph.vertices[player.current_vertex_id]
        new_vertex = self.graph.vertices[new_vertex_id]
        
        # Check for tunnel collapse
        if edge.attempt_collapse():
            self.log(f"💥 DESABAMENTO! O túnel colapsou enquanto você passava!")
            damage = random.randint(15, 30)
            actual_damage = player.take_damage(damage)
            self.log(f"💔 Você sofreu {actual_damage} de dano!")
            return False
        
        # Consume stamina BEFORE moving (so we know we have enough)
        player.consume_stamina(stamina_cost)
        
        # Move player
        player.current_vertex_id = new_vertex_id
        player.total_cost += cost
        player.distance_traveled += cost
        
        # self.log(f"🚶 {player.name} moveu de {old_vertex.name} para {new_vertex.name} (Custo: {cost}, Stamina: -{stamina_cost})")
        
        # Enter new vertex
        self.enter_vertex(player, new_vertex_id)
        
        # Check victory
        self.check_victory()
        
        return True
    
    def enter_vertex(self, player: Player, vertex_id: int):
        """Handle entering a new vertex"""
        vertex = self.graph.vertices[vertex_id]
        
        self.log(f"📍 Entrando em: {vertex.name} ({vertex.biome.value})")
        
        # Mark as explored
        if not vertex.explored:
            vertex.explored = True
            self.log(f"🗺️ Nova área explorada!")
            
            # Exploration reward
            rewards = ResourceManager.generate_exploration_reward()
            for resource, amount in rewards.items():
                player.add_item(resource, amount)
                if resource == "gold":
                    player.add_gold(amount)
                    self.log(f"💰 Encontrou {amount} ouro!")
                else:
                    self.log(f"📦 Encontrou {amount}x {resource}!")
        
        # Handle hazards
        for hazard in vertex.hazards:
            self._apply_hazard(player, hazard)
        
        # Handle obstacles
        for obstacle in vertex.obstacles:
            success, message = obstacle.interact(player, self)
            if message:
                self.log(message)
        
        # Handle monster encounter via MonsterSystem
        if vertex.has_monster and vertex.monster_type:
            # Let MonsterSystem decide (ambush, engagement, etc.)
            try:
                self.monster_system.handle_player_enter_vertex(player, vertex)
            except Exception as e:
                # Fallback to immediate combat if something fails
                self.log(f"[ERROR] monster_system.handle_player_enter_vertex: {e}")
                self.trigger_combat(player, vertex)

        
        # Handle treasure chest
        if vertex.has_treasure_chest:
            self._handle_treasure_chest(player, vertex)
    
    def _apply_hazard(self, player: Player, hazard: HazardType):
        """Apply environmental hazard effects"""
        if hazard == HazardType.TOXIC_GAS:
            damage = random.randint(5, 15)
            actual_damage = player.take_damage(damage)
            self.log(f"☠️ Gás tóxico! Perdeu {actual_damage} HP")
        
        elif hazard == HazardType.EXTREME_HEAT:
            if not player.has_item("heat_resistance_potion"):
                damage = random.randint(10, 20)
                actual_damage = player.take_damage(damage)
                self.log(f"🔥 Calor extremo! Perdeu {actual_damage} HP")
        
        elif hazard == HazardType.EXTREME_COLD:
            stamina_loss = random.randint(10, 20)
            player.consume_stamina(stamina_loss)
            self.log(f"❄️ Frio extremo! Perdeu {stamina_loss} stamina")
        
        elif hazard == HazardType.DARKNESS:
            if not player.has_item("torch"):
                self.log(f"🌑 Escuridão total! Você tropeça...")
                if random.random() < 0.3:
                    damage = random.randint(5, 10)
                    player.take_damage(damage)
                    self.log(f"💔 Você se machucou no escuro!")
    
    def _handle_treasure_chest(self, player: Player, vertex):
        """Handle treasure chest interaction"""
        # This would be called when player interacts with chest
        # For now, auto-open
        pass
    
    # ============================================
    # COMBAT SYSTEM
    # ============================================
    
    def trigger_combat(self, player: Player, vertex) -> CombatResult:
        """Trigger combat with monster at vertex"""
        # If MonsterSystem has active monster, use it
        # ==========================================================
        # 🔥 ANTI-DUPLICATE COMBAT GUARD
        # ==========================================================
        # Se já existe um combate envolvendo este player, NÃO iniciar outro
        for inst in self.combat_manager.active_instances:
            if inst.player.id == player.id and not inst.ended:
                self.log(f"[DEBUG] Ignorando trigger_combat duplicado para {player.name}")
                return inst.get_result()
        
        active_ms = None
        try:
            active_ms = self.monster_system.active_monsters.get(vertex.id)
        except Exception:
            active_ms = None

        if active_ms:
            monster = active_ms.monster
        else:
            # fallback: create a Monster from vertex.monster_type
            try:
                monster = Monster(MonsterType[vertex.monster_type.upper()], player.level)
            except Exception:
                monster = Monster(MonsterType.GOBLIN, player.level)

        self.log(f"\n⚔️ COMBATE: {player.name} vs {monster}")

        # If auto_combat is True, use tick-based CombatManager for simultaneous hits
        if self.auto_combat:
            inst = self.combat_manager.start_combat(player, monster)
            # For auto immediate execution, run a fast loop until finished (only if UI is not handling ticks)
            # But prefer letting UI call update(delta). Here, run a short blocking fallback to completion for headless runs.
            # Run small simulated ticks until finished to return a CombatResult immediately
            if hasattr(self, 'run_combat_blocking') and self.run_combat_blocking:
                # Blocking mode (for non-UI tests)
                while not inst.ended:
                    inst.tick(0.2)
                return inst.get_result()
            else:
                # Non-blocking: return an initial CombatResult (UI will display as combat progresses)
                res = inst.get_result()
                # If res empty, create minimal CombatResult
                return res
        else:
            # Fallback to legacy blocking combat
            result = CombatSystem.execute_combat(player, monster, self.auto_combat)
            # Log combat
            for msg in result.combat_log:
                self.log(msg)
            # Clear monster if defeated
            if result.player_won:
                vertex.has_monster = False
                vertex.monster_type = None
            if result.player_died:
                self.game_over = True
                self.game_mode = GameMode.DEFEAT
                self.log(f"\n💀 GAME OVER - {player.name} foi derrotado!")
            return result

    
    # ============================================
    # CARD SYSTEM
    # ============================================
    
    def draw_card(self, player_id: int) -> bool:
        """Draw a card from deck"""
        player = self._get_player(player_id)
        if not player:
            return False
        
        # Check hand size
        if len(player.hand_cards) >= player.max_hand_size:
            self.log(f"❌ Mão cheia! (Máximo: {player.max_hand_size})")
            return False
        
        # Check deck
        if not self.deck:
            self.log("📚 Baralho vazio! Embaralhando descarte...")
            if not self.discard_pile:
                self.log("❌ Sem cartas disponíveis!")
                return False
            self.deck = self.discard_pile
            self.discard_pile = []
            random.shuffle(self.deck)
        
        # Draw card
        card = self.deck.pop()
        player.hand_cards.append(card)
        self.log(f"🃏 {player.name} comprou: {card.type.value} (Nível {card.level})")
        return True
    
    def play_card(self, player_id: int, card_id: int, 
                  target_edge_id: Optional[int] = None,
                  target_vertex_id: Optional[int] = None) -> bool:
        """Play a card"""
        player = self._get_player(player_id)
        if not player:
            return False
        
        # Find card in hand
        card = next((c for c in player.hand_cards if c.id == card_id), None)
        if not card:
            self.log(f"❌ Carta não encontrada na mão!")
            return False
        
        # Apply card
        success, message = card.apply(player, self, target_edge_id, target_vertex_id)
        
        self.log(message)
        
        if success:
            # Remove from hand and add to discard
            player.hand_cards.remove(card)
            self.discard_pile.append(card)
            return True
        
        return False
    
    # ============================================
    # MONSTER & RESOURCE SPAWNING
    # ============================================
    
    def spawn_monsters(self):
        """Spawn monsters in unexplored vertices"""
        # Ensure MonsterSystem recognizes them
        try:
            self.monster_system.spawn_from_graph()
        except Exception:
            pass
        spawned = self.graph.spawn_random_monsters(
            self.monster_spawn_chance,
            [mt.value for mt in MonsterType]
        )
        if spawned:
            self.log(f"👹 {len(spawned)} monstros apareceram nas cavernas!")

    
    def spawn_resources(self):
        """Spawn resources in unexplored vertices"""
        spawned = self.graph.add_random_resources(self.resource_spawn_chance)
        if spawned:
            self.log(f"💎 Recursos apareceram em {len(spawned)} locais!")
    
    # ============================================
    # VICTORY/DEFEAT CONDITIONS
    # ============================================
    
    def check_victory(self) -> Optional[Player]:
        """Check if any player won"""
        if self.game_over:
            return self.winner

        winners = []
        for player in self.players:
            if player.current_vertex_id == self.treasure_vertex_id:
                winners.append(player)
        
        if winners:
             # ...
            # Resolve tie by lowest cost
            winner = min(winners, key=lambda p: p.total_cost)
            self.winner = winner
            self.game_over = True
            self.game_mode = GameMode.VICTORY
            self.log(f"\n🏆 VITÓRIA! {winner.name} encontrou o tesouro!")
            self.log(f"   Custo total: {winner.total_cost}")
            self.log(f"   Monstros derrotados: {winner.monsters_killed}")
            self.log(f"   Tesouros encontrados: {winner.treasures_found}")
            return winner
        
        return None
    
    def check_game_over(self):
        """Check for game over conditions"""
        if self.game_over:
            return

        # Check if all players are dead
        alive_players = [p for p in self.players if p.is_alive]
        if not alive_players:
            self.game_over = True
            self.game_mode = GameMode.DEFEAT
            self.log(f"\n💀 GAME OVER - Todos os jogadores foram derrotados!")
            return
        
        # Check victory
        self.check_victory()
    
    # ============================================
    # UTILITY METHODS
    # ============================================
    
    def _get_player(self, player_id: int) -> Optional[Player]:
        """Get player by ID"""
        return next((p for p in self.players if p.id == player_id), None)
    
    def get_game_summary(self) -> Dict:
        """Get complete game state summary"""
        return {
            "turn": self.turn_number,
            "mode": self.game_mode.value,
            "game_over": self.game_over,
            "current_player": self.current_player.name if self.current_player else None,
            "players": [p.get_status_summary() for p in self.players],
            "treasure_location": self.graph.vertices[self.treasure_vertex_id].name if self.treasure_vertex_id else None,
            "winner": self.winner.name if self.winner else None
        }
    
    def save_game_state(self) -> Dict:
        """Serialize game state (for saving)"""
        # This would serialize the entire game state to a dictionary
        # Implementation depends on save/load requirements
        pass
    
    @staticmethod
    def load_game_state(data: Dict) -> 'GameState':
        """Deserialize game state (for loading)"""
        # This would restore game state from a dictionary
        # Implementation depends on save/load requirements
        pass
