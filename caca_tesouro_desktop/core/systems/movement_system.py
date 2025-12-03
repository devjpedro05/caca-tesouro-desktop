# core/systems/movement_system.py
from ..graph import Graph
from ..player import Player

class MovementSystem:
    """Helper movement system - centralize stamina & cost logic"""
    def __init__(self, game_state):
        self.gs = game_state
        self.graph: Graph = game_state.graph

    def get_stamina_cost_for_edge(self, edge) -> int:
        """Return stamina cost for traversing an edge"""
        base = edge.weight
        return base * 2

    def can_move_player(self, player: Player, edge) -> (bool, str):
        """Check preconditions for moving"""
        if player.stamina < self.get_stamina_cost_for_edge(edge):
            return False, "Stamina insuficiente"
        if edge.blocked:
            return False, "Túnel bloqueado"
        return True, ""
