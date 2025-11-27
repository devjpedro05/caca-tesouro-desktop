import unittest
from core.game_state import GameState
from core.cards import CardType

class TestGameState(unittest.TestCase):
    def setUp(self):
        self.gs = GameState.new_default_game()
        self.p1 = self.gs.players[0]
        self.p2 = self.gs.players[1]

    def test_initial_state(self):
        self.assertEqual(self.gs.current_player_index, 0)
        self.assertEqual(self.p1.current_vertex_id, 0)
        self.assertEqual(self.p1.total_cost, 0)

    def test_turn_switching(self):
        self.gs.end_turn()
        self.assertEqual(self.gs.current_player_index, 1)
        self.gs.end_turn()
        self.assertEqual(self.gs.current_player_index, 0)

    def test_movement(self):
        # Assuming v0 is connected to v1 in sample graph
        # Find edge between 0 and 1
        edge = self.gs.graph.get_edge(0, 1)
        self.assertIsNotNone(edge)
        
        success = self.gs.move_player(self.p1.id, edge.id)
        self.assertTrue(success)
        self.assertEqual(self.p1.current_vertex_id, 1)
        self.assertEqual(self.p1.total_cost, edge.weight)

    def test_blocked_movement(self):
        edge = self.gs.graph.get_edge(0, 1)
        edge.blocked = True
        
        success = self.gs.move_player(self.p1.id, edge.id)
        self.assertFalse(success)
        self.assertEqual(self.p1.current_vertex_id, 0)
        self.assertEqual(self.p1.total_cost, 0)

if __name__ == '__main__':
    unittest.main()
