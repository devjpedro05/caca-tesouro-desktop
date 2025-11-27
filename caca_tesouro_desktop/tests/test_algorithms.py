import unittest
from core.graph import Graph
from core.algorithms import bfs, dijkstra

class TestAlgorithms(unittest.TestCase):
    def setUp(self):
        self.graph = Graph()
        self.v0 = self.graph.add_vertex("Start", 0, 0)
        self.v1 = self.graph.add_vertex("A", 10, 0)
        self.v2 = self.graph.add_vertex("B", 0, 10)
        self.v3 = self.graph.add_vertex("End", 10, 10)
        
        self.graph.add_edge(self.v0.id, self.v1.id, weight=1)
        self.graph.add_edge(self.v0.id, self.v2.id, weight=5)
        self.graph.add_edge(self.v1.id, self.v3.id, weight=2)
        self.graph.add_edge(self.v2.id, self.v3.id, weight=1)

    def test_bfs(self):
        dists = bfs(self.graph, self.v0.id)
        self.assertEqual(dists[self.v0.id], 0)
        self.assertEqual(dists[self.v1.id], 1)
        self.assertEqual(dists[self.v2.id], 1)
        self.assertEqual(dists[self.v3.id], 2)

    def test_dijkstra(self):
        costs = dijkstra(self.graph, self.v0.id)
        self.assertEqual(costs[self.v0.id], 0)
        self.assertEqual(costs[self.v1.id], 1)
        self.assertEqual(costs[self.v2.id], 4) # 1 + 2 + 1 via v1->v3->v2 is better than 5
        self.assertEqual(costs[self.v3.id], 3) # 1 + 2 via v1

if __name__ == '__main__':
    unittest.main()
