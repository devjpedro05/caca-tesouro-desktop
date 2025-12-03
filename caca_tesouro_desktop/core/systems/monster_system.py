# core/systems/monster_system.py
import math
import random
from typing import Dict, Optional, Tuple, List

from ..obstacles import Monster, MonsterType
from ..graph import Graph, Vertex
from ..combat import CombatSystem
from ..player import Player

class MonsterState:
    """Runtime state for an active monster"""
    def __init__(self, monster: Monster, vertex_id: int, patrol_points: List[int] = None):
        self.monster = monster
        self.vertex_id = vertex_id
        self.patrol_points = patrol_points or []
        self.patrol_index = 0
        self.patrol_forward = True
        self.state = "idle"        # idle | patrol | chase | engaging
        self.aggro_target: Optional[int] = None  # player id
        self.time_since_last_move = 0.0
        self.chase_timer = 0.0
        # movement cooldown in seconds (inversely proportional to speed)
        self.move_cooldown = max(0.4, 1.5 - (monster.speed * 0.05))
        # For vision cone / distance
        self.vision_range = 3  # graph steps (configurable)
        self.vision_angle = 360  # full for simplicity; could be limited
        # Combat engagement lock to prevent duplicate triggers
        self.engaging = False
        self.engaging_since = 0.0

    def __repr__(self):
        return f"<MonsterState {self.monster} @v{self.vertex_id} state={self.state}>"

class MonsterSystem:
    """Manage active monsters: patrol, detect, chase and trigger combat"""
    def __init__(self, game_state):
        self.gs = game_state
        self.graph: Graph = game_state.graph
        # active_monsters: vertex_id -> MonsterState
        self.active_monsters: Dict[int, MonsterState] = {}
        self.on_monster_move = None # Callback(monster_state, old_vertex, new_vertex)

    def spawn_from_graph(self):
        """Convert graph flags into active_monsters (idempotent)"""
        for v_id, vertex in self.graph.vertices.items():
            if vertex.has_monster and v_id not in self.active_monsters:
                # Create Monster instance from vertex.monster_type
                mtype_str = vertex.monster_type
                try:
                    # Accept both 'goblin' and 'Goblin'
                    mtype = MonsterType[mtype_str.upper()] if isinstance(mtype_str, str) else MonsterType(mtype_str)
                except Exception:
                    # fallback
                    mtype = MonsterType.GOBLIN
                monster = Monster(mtype, level=1)
                # Optionally assign simple 2-point patrol around vertex (neighbors)
                neighbors = [n for n, e in self.graph.neighbors(v_id)]
                patrol_points = [v_id] + (neighbors[:1] if neighbors else [])
                ms = MonsterState(monster, v_id, patrol_points=patrol_points)
                ms.state = "patrol" if len(ms.patrol_points) > 1 else "idle"
                self.active_monsters[v_id] = ms
                # ensure vertex is treated as having an active monster
                vertex.has_monster = True
        # remove stale monsters for vertices that lost flag
        stale = [v for v in self.active_monsters if not self.graph.vertices[v].has_monster]
        for v in stale:
            del self.active_monsters[v]

    def update(self, delta: float):
        """Lightweight monster update loop (fast & safe)."""
        self.spawn_from_graph()

        for v_id, ms in list(self.active_monsters.items()):
            ms.time_since_last_move += delta

            # Remove dead monsters
            if not ms.monster.is_alive():
                self._on_monster_death(ms)
                continue
            
            # Debug active monsters occasionally
            # if random.random() < 0.01:
            #    print(f"[DEBUG] Monster {ms.monster} at v{ms.vertex_id} state={ms.state}")

            # --- CHASE MODE ---
            if ms.state == "chase" and ms.aggro_target is not None:
                player = self.gs._get_player(ms.aggro_target)

                if not player or not player.is_alive:
                    ms.state = "patrol" if len(ms.patrol_points) > 1 else "idle"
                    ms.aggro_target = None
                    continue

                # Only pathfind if cooldown completed
                if ms.time_since_last_move >= ms.move_cooldown:
                    ms.time_since_last_move = 0.0

                    # Lightweight chase: walk to neighbor closer to player
                    next_v = self._pick_best_neighbor(ms.vertex_id, player.current_vertex_id)

                    if next_v is not None and next_v != ms.vertex_id:
                        self._move_monster(ms, next_v)

                    # Reached player
                    if ms.vertex_id == player.current_vertex_id:
                        # Only trigger combat once per engagement
                        if ms.state != "engaging" and not ms.engaging:
                            ms.state = "engaging"
                            ms.engaging = True
                            ms.engaging_since = 0.0
                            self.gs.log(f"⚠️ {ms.monster.monster_type.value.title()} iniciou combate com {player.name}!")
                            self.gs.trigger_combat(player, self.graph.vertices[ms.vertex_id])

                continue

            # --- PATROL / IDLE ---
            detected = self._detect_player_in_range(ms)
            if detected:
                ms.aggro_target = detected.id
                ms.state = "chase"
                self.gs.log(f"👀 {ms.monster.monster_type.value.title()} detectou {detected.name}!")
                continue

            # Patrol only if >1 point
            if ms.state == "patrol" and len(ms.patrol_points) > 1:
                if ms.time_since_last_move >= ms.move_cooldown:
                    ms.time_since_last_move = 0.0
                    next_v = self._next_patrol_point(ms)
                    self._move_monster(ms, next_v)

    def _move_monster(self, ms: MonsterState, new_vertex_id: int):
        """Safely move monster between vertices."""
        # Remove old marker
        old = ms.vertex_id
        self.graph.vertices[old].has_monster = False
        self.graph.vertices[old].monster_type = None

        # Update state
        ms.vertex_id = new_vertex_id

        # Set new marker
        self.graph.vertices[new_vertex_id].has_monster = True
        self.graph.vertices[new_vertex_id].monster_type = ms.monster.monster_type.value
        
        # Notify UI
        if self.on_monster_move:
            self.on_monster_move(ms, old, new_vertex_id)

    def _pick_best_neighbor(self, from_v: int, target_v: int) -> Optional[int]:
        """Instead of full Dijkstra, pick neighbor closer to target."""
        best_next = None
        best_dist = 9999

        # Precompute distances via a single Dijkstra (rare)
        try:
            from ..algorithms import dijkstra
            dist, _ = dijkstra(self.graph, from_v, target_v)
            
            for nb, _ in self.graph.neighbors(from_v):
                d = dist.get(nb, 9999)
                if d < best_dist:
                    best_dist = d
                    best_next = nb
        except Exception as e:
            # Fallback: Use simple heuristic based on graph structure
            # Pick neighbor that appears to reduce distance (simple approximation)
            print(f"[DEBUG] Dijkstra failed for v{from_v}->v{target_v}, using heuristic fallback: {e}")
            
            # Simple heuristic: pick any valid neighbor (patrol-like behavior when pathfinding fails)
            neighbors = [n for n, _ in self.graph.neighbors(from_v)]
            if neighbors:
                # Prefer neighbors that haven't been visited recently (would need tracking)
                # For now, just pick the first valid neighbor
                best_next = neighbors[0]

        return best_next

    def _next_patrol_point(self, ms: MonsterState) -> int:
        if ms.patrol_forward:
            ms.patrol_index += 1
            if ms.patrol_index >= len(ms.patrol_points):
                ms.patrol_index = len(ms.patrol_points) - 2
                ms.patrol_forward = False
        else:
            ms.patrol_index -= 1
            if ms.patrol_index < 0:
                ms.patrol_index = 1
                ms.patrol_forward = True

        return ms.patrol_points[ms.patrol_index]


    def _detect_player_in_range(self, ms: MonsterState) -> Optional[Player]:
        """Return a player object if inside vision range (graph distance)"""
        for player in self.gs.players:
            if not player.is_alive:
                continue
            try:
                from ..algorithms import dijkstra
                distances, _ = dijkstra(self.graph, ms.vertex_id, player.current_vertex_id)
                if distances.get(player.current_vertex_id, float('inf')) <= ms.vision_range:
                    return player
            except Exception:
                continue
        return None

    def _on_monster_death(self, ms: MonsterState):
        """Handle monster death cleanup"""
        v = ms.vertex_id
        
        # Reset engaging state
        ms.engaging = False
        ms.state = "idle"
        
        if v in self.active_monsters:
            del self.active_monsters[v]
        # ensure graph flags cleared
        if v in self.graph.vertices:
            self.graph.vertices[v].has_monster = False
            self.graph.vertices[v].monster_type = None
        # spawn loot via game_state
        # NOTE: GameState.trigger_combat already handles removing vertex monster and spawning loot

    def handle_player_enter_vertex(self, player: Player, vertex: Vertex):
        """Called when player enters a vertex - if monster present, decide engagement/ambush"""
        if vertex.has_monster:
            # find monster state if present
            ms = self.active_monsters.get(vertex.id)
            if ms:
                # If monster is alive and not already engaging, trigger combat
                if ms.monster.is_alive() and ms.state != "engaging":
                    ms.state = "engaging"
                    self.gs.log(f"⚔️ Encontro! {player.name} encontrou {ms.monster.monster_type.value.title()} em {vertex.name}")
                    # Trigger combat via GameState
                    self.gs.trigger_combat(player, vertex)
            else:
                # fallback: create temp monster and fight
                monster = Monster(MonsterType.GOBLIN, player.level)
                vertex.has_monster = False
                vertex.monster_type = None
                self.gs.log(f"⚔️ Encontro improvisado! {player.name} encontrou {monster.monster_type.value.title()}")
                self.gs.trigger_combat(player, vertex)
