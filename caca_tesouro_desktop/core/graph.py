"""
Enhanced Graph System for Treasure Hunt Game
Includes vertices with biomes/hazards, edges with types/states, and dynamic modifications
"""
import random
from enum import Enum
from typing import List, Dict, Optional, Tuple

class BiomeType(Enum):
    """Types of biomes/environments in the cave system"""
    CAVE = "cave"
    UNDERGROUND_LAKE = "underground_lake"
    CRYSTAL_CAVERN = "crystal_cavern"
    LAVA_CHAMBER = "lava_chamber"
    ICE_TUNNEL = "ice_tunnel"
    MUSHROOM_GROVE = "mushroom_grove"
    ANCIENT_RUINS = "ancient_ruins"

class HazardType(Enum):
    """Environmental hazards in vertices"""
    NONE = "none"
    TOXIC_GAS = "toxic_gas"
    UNSTABLE_FLOOR = "unstable_floor"
    DARKNESS = "darkness"
    EXTREME_HEAT = "extreme_heat"
    EXTREME_COLD = "extreme_cold"
    RADIATION = "radiation"

class EdgeType(Enum):
    """Types of tunnels/passages"""
    NORMAL_TUNNEL = "normal_tunnel"
    UNSTABLE_TUNNEL = "unstable_tunnel"
    SECRET_PASSAGE = "secret_passage"
    COLLAPSED_TUNNEL = "collapsed_tunnel"
    REINFORCED_TUNNEL = "reinforced_tunnel"
    NARROW_PASSAGE = "narrow_passage"
    UNDERWATER_PASSAGE = "underwater_passage"

class Vertex:
    """
    Represents a location/room in the cave system
    """
    def __init__(self, id: int, name: str, x: float, y: float, 
                 biome: BiomeType = BiomeType.CAVE,
                 hazards: List[HazardType] = None):
        self.id = id
        self.name = name
        self.x = x
        self.y = y
        self.biome = biome
        self.hazards = hazards if hazards else []
        
        # Dynamic properties
        self.explored = False
        self.has_treasure_chest = False
        self.has_monster = False
        self.monster_type: Optional[str] = None
        self.resources = {}  # resource_type -> amount
        self.obstacles = []  # List of obstacle objects
        
        # Grid position (set by grid_map or DualGameManager)
        self.grid_pos: Optional[Tuple[int, int]] = None
        
        # Monster level (for dual game manager)
        self.monster_level: int = 1  # Default level
    def add_hazard(self, hazard: HazardType):
        """Add a hazard to this vertex"""
        if hazard not in self.hazards:
            self.hazards.append(hazard)
    
    def remove_hazard(self, hazard: HazardType):
        """Remove a hazard from this vertex"""
        if hazard in self.hazards:
            self.hazards.remove(hazard)
    
    def add_resource(self, resource_type: str, amount: int):
        """Add resources to this vertex"""
        self.resources[resource_type] = self.resources.get(resource_type, 0) + amount
    
    def take_resource(self, resource_type: str, amount: int) -> int:
        """Take resources from this vertex, returns amount actually taken"""
        available = self.resources.get(resource_type, 0)
        taken = min(available, amount)
        self.resources[resource_type] = available - taken
        if self.resources[resource_type] <= 0:
            self.resources.pop(resource_type, None)
        return taken
    
    def __repr__(self):
        return f"Vertex({self.id}, {self.name}, {self.biome.value})"

class Edge:
    """
    Represents a tunnel/passage between two vertices
    """
    def __init__(self, id: int, v1_id: int, v2_id: int, 
                 weight: int = 1, 
                 edge_type: EdgeType = EdgeType.NORMAL_TUNNEL,
                 blocked: bool = False):
        self.id = id
        self.v1_id = v1_id
        self.v2_id = v2_id
        self.weight = weight
        self.edge_type = edge_type
        self.blocked = blocked
        
        # Dynamic states
        self.stability = 100  # 0-100, affects collapse chance
        self.reinforced = False
        self.has_fissures = False
        self.collapse_chance = 0.0  # Probability of collapse when traversed
        self.discovered = False  # For secret passages
        self.obstacles = []  # List of obstacle objects on this edge
        
        # Stamina cost system - strategic tunnels
        self.stamina_cost = 3  # Default stamina cost to traverse
        self.monster_level_hint = 0  # 0 = no monster, 1-5 = monster level
        
        # Calculate initial collapse chance based on type
        self._update_collapse_chance()
    
    def _update_collapse_chance(self):
        """Update collapse chance based on stability and type"""
        base_chance = 0.0
        
        if self.edge_type == EdgeType.UNSTABLE_TUNNEL:
            base_chance = 0.15
        elif self.edge_type == EdgeType.COLLAPSED_TUNNEL:
            base_chance = 1.0  # Already collapsed
        elif self.edge_type == EdgeType.REINFORCED_TUNNEL:
            base_chance = 0.01
        
        # Modify by stability
        stability_factor = (100 - self.stability) / 100.0
        self.collapse_chance = min(1.0, base_chance + stability_factor * 0.3)
        
        if self.has_fissures:
            self.collapse_chance += 0.1
        
        if self.reinforced:
            self.collapse_chance *= 0.3
    
    def damage_stability(self, amount: int):
        """Reduce stability (e.g., from explosions, earthquakes)"""
        self.stability = max(0, self.stability - amount)
        self._update_collapse_chance()
    
    def reinforce(self):
        """Reinforce this tunnel to reduce collapse chance"""
        self.reinforced = True
        self.stability = min(100, self.stability + 30)
        self._update_collapse_chance()
    
    def add_fissures(self):
        """Add fissures/cracks to the tunnel"""
        self.has_fissures = True
        self._update_collapse_chance()
    
    def attempt_collapse(self) -> bool:
        """Check if tunnel collapses, returns True if collapsed"""
        if random.random() < self.collapse_chance:
            self.blocked = True
            self.edge_type = EdgeType.COLLAPSED_TUNNEL
            return True
        return False
    
    def __repr__(self):
        status = "BLOCKED" if self.blocked else f"w={self.weight}"
        return f"Edge({self.id}, {self.v1_id}-{self.v2_id}, {self.edge_type.value}, {status})"

class Graph:
    """
    Represents the cave system as a graph with dynamic modifications
    """
    def __init__(self):
        self.vertices: Dict[int, Vertex] = {}
        self.edges: Dict[int, Edge] = {}
        self.adj: Dict[int, List[int]] = {}  # vertex_id -> list of edge_ids
        self._next_v_id = 0
        self._next_e_id = 0
    
    def add_vertex(self, name: str, x: float, y: float, 
                   biome: BiomeType = BiomeType.CAVE,
                   hazards: List[HazardType] = None) -> Vertex:
        """Add a new vertex to the graph"""
        v_id = self._next_v_id
        self._next_v_id += 1
        v = Vertex(v_id, name, x, y, biome, hazards)
        self.vertices[v_id] = v
        self.adj[v_id] = []
        return v
    
    def add_edge(self, v1_id: int, v2_id: int, weight: int = 1,
                 edge_type: EdgeType = EdgeType.NORMAL_TUNNEL) -> Optional[Edge]:
        """Add a new edge between two vertices"""
        if v1_id not in self.vertices or v2_id not in self.vertices:
            return None
        
        e_id = self._next_e_id
        self._next_e_id += 1
        e = Edge(e_id, v1_id, v2_id, weight, edge_type)
        self.edges[e_id] = e
        self.adj[v1_id].append(e_id)
        self.adj[v2_id].append(e_id)
        return e
    
    def remove_edge(self, edge_id: int) -> bool:
        """Permanently remove an edge from the graph"""
        if edge_id not in self.edges:
            return False
        
        edge = self.edges[edge_id]
        self.adj[edge.v1_id].remove(edge_id)
        self.adj[edge.v2_id].remove(edge_id)
        del self.edges[edge_id]
        return True
    
    def block_edge(self, edge_id: int):
        """Block an edge (can be unblocked later)"""
        if edge_id in self.edges:
            self.edges[edge_id].blocked = True
    
    def unblock_edge(self, edge_id: int):
        """Unblock a previously blocked edge"""
        if edge_id in self.edges:
            self.edges[edge_id].blocked = False
    
    def neighbors(self, vertex_id: int, include_blocked: bool = False) -> List[Tuple[int, Edge]]:
        """
        Returns a list of (neighbor_vertex_id, edge) tuples
        By default, excludes blocked edges
        """
        result = []
        if vertex_id not in self.adj:
            return result
        
        for e_id in self.adj[vertex_id]:
            edge = self.edges[e_id]
            if not include_blocked and edge.blocked:
                continue
            
            other_id = edge.v2_id if edge.v1_id == vertex_id else edge.v1_id
            result.append((other_id, edge))
        return result
    
    def get_edge(self, v1_id: int, v2_id: int) -> Optional[Edge]:
        """Get the edge connecting two vertices (if exists)"""
        for e_id in self.adj.get(v1_id, []):
            edge = self.edges[e_id]
            if (edge.v1_id == v1_id and edge.v2_id == v2_id) or \
               (edge.v1_id == v2_id and edge.v2_id == v1_id):
                return edge
        return None
    
    def get_edges_from_vertex(self, vertex_id: int) -> List[Edge]:
        """Get all edges connected to a vertex"""
        return [self.edges[e_id] for e_id in self.adj.get(vertex_id, [])]
    
    def trigger_random_collapse(self, probability: float = 0.05) -> List[int]:
        """
        Randomly collapse some unstable tunnels
        Returns list of collapsed edge IDs
        """
        collapsed = []
        for edge in self.edges.values():
            if not edge.blocked and edge.edge_type == EdgeType.UNSTABLE_TUNNEL:
                if random.random() < probability:
                    edge.blocked = True
                    collapsed.append(edge.id)
        return collapsed
    
    def spawn_random_monsters(self, probability: float = 0.1, monster_types: List[str] = None) -> List[int]:
        """
        Randomly spawn monsters in vertices
        Returns list of vertex IDs where monsters spawned
        """
        if monster_types is None:
            monster_types = ["Goblin", "Orc", "CaveSpirit", "StoneGolem"]
        
        spawned = []
        for vertex in self.vertices.values():
            # NEVER spawn in player starting chambers (v0 and v1)
            if vertex.id == 0 or vertex.id == 1:
                continue
                
            if not vertex.has_monster and not vertex.explored:
                if random.random() < probability:
                    vertex.has_monster = True
                    vertex.monster_type = random.choice(monster_types)
                    spawned.append(vertex.id)
        return spawned
    
    def add_random_resources(self, probability: float = 0.15) -> List[int]:
        """
        Randomly add resources to unexplored vertices
        Returns list of vertex IDs where resources were added
        """
        resource_types = ["gold", "gems", "keys", "potions"]
        added = []
        
        for vertex in self.vertices.values():
            if not vertex.explored:
                if random.random() < probability:
                    resource_type = random.choice(resource_types)
                    amount = random.randint(5, 20)
                    vertex.add_resource(resource_type, amount)
                    added.append(vertex.id)
        return added
    
    def configure_tunnel_stamina_costs(self, monster_positions: Dict[int, int]):
        """
        Configure stamina costs for tunnels based on nearby monsters.
        Strategic twist: Tunnels to STRONGER monsters cost LESS stamina (high risk, low cost)
                        Tunnels to WEAKER monsters cost MORE stamina (low risk, high cost)
        
        Args:
            monster_positions: Dict of {vertex_id: monster_level}
        """
        for edge in self.edges.values():
            # Check if either endpoint has a monster
            v1_monster_level = monster_positions.get(edge.v1_id, 0)
            v2_monster_level = monster_positions.get(edge.v2_id, 0)
            
            max_monster_level = max(v1_monster_level, v2_monster_level)
            
            if max_monster_level == 0:
                # No monster - default cost
                edge.stamina_cost = 3
                edge.monster_level_hint = 0
            else:
                # INVERSE COST: Higher level monsters = Lower stamina cost
                # Level 1 monster: 5 stamina (safe but expensive)
                # Level 2 monster: 4 stamina
                # Level 3 monster: 3 stamina
                # Level 4 monster: 2 stamina
                # Level 5+ monster: 1 stamina (dangerous but cheap!)
                edge.stamina_cost = max(1, 6 - max_monster_level)
                edge.monster_level_hint = max_monster_level
                
        print(f"[GRAPH] Configured tunnel stamina costs based on {len(monster_positions)} monster positions")
    
    @staticmethod
    def sample_graph() -> 'Graph':
        """Create a sample graph for testing"""
        g = Graph()
        
        # Level 1 (Start)
        v0 = g.add_vertex("Entrada", 100, 300, BiomeType.CAVE)
        
        # Level 2
        v1 = g.add_vertex("Caverna Azul", 300, 150, BiomeType.CRYSTAL_CAVERN)
        v2 = g.add_vertex("Salão dos Ecos", 300, 450, BiomeType.CAVE)
        
        # Level 3
        v3 = g.add_vertex("Túnel Escuro", 500, 100, BiomeType.CAVE, [HazardType.DARKNESS])
        v4 = g.add_vertex("Ponte de Pedra", 500, 300, BiomeType.CAVE)
        v5 = g.add_vertex("Lago Subterrâneo", 500, 500, BiomeType.UNDERGROUND_LAKE)
        
        # Level 4 (Treasure)
        v6 = g.add_vertex("Câmara do Tesouro", 700, 300, BiomeType.ANCIENT_RUINS)
        
        # Edges with varied types
        g.add_edge(v0.id, v1.id, weight=3, edge_type=EdgeType.NORMAL_TUNNEL)
        g.add_edge(v0.id, v2.id, weight=4, edge_type=EdgeType.NORMAL_TUNNEL)
        
        g.add_edge(v1.id, v3.id, weight=2, edge_type=EdgeType.UNSTABLE_TUNNEL)
        g.add_edge(v1.id, v4.id, weight=5, edge_type=EdgeType.NORMAL_TUNNEL)
        
        g.add_edge(v2.id, v4.id, weight=3, edge_type=EdgeType.NORMAL_TUNNEL)
        g.add_edge(v2.id, v5.id, weight=4, edge_type=EdgeType.UNDERWATER_PASSAGE)
        
        g.add_edge(v3.id, v6.id, weight=6, edge_type=EdgeType.SECRET_PASSAGE)
        g.add_edge(v4.id, v6.id, weight=2, edge_type=EdgeType.NORMAL_TUNNEL)
        g.add_edge(v5.id, v6.id, weight=5, edge_type=EdgeType.UNSTABLE_TUNNEL)
        
        # Cross connections
        g.add_edge(v1.id, v2.id, weight=2, edge_type=EdgeType.NARROW_PASSAGE)
        g.add_edge(v3.id, v4.id, weight=3, edge_type=EdgeType.NORMAL_TUNNEL)
        g.add_edge(v4.id, v5.id, weight=2, edge_type=EdgeType.NORMAL_TUNNEL)
        
        # Add some initial resources
        v1.add_resource("gold", 10)
        v3.add_resource("gems", 5)
        v5.add_resource("potions", 2)
        
        return g
