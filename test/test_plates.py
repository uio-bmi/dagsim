import unittest
from typing import List

from dagsim.Node import Node
from dagsim.base import Node, Graph


class TestPlates(unittest.TestCase):

    def add(self, a, b):
        return a + b

    def setUp(self) -> list[Node]:
        n0 = Node("n0", function=int, args=[1])
        n1 = Node("n1", function=int, args=[1], plates=["1"])
        n2 = Node("n2", function=self.add, args=[n0, n1], plates=["2"])
        n3 = Node("n3", function=lambda x: x, args=[n1])
        return [n0, n1, n2, n3]

    def test_child_in_plate_no_rep(self):
        graph = Graph(self.setUp()[:2])
        data = graph.simulate(2)
        self.assertEqual(data["n0"], [1, 1])
        self.assertEqual(data["n1"], [1, 1])

    def test_child_in_plate_with_rep(self):
        graph = Graph(self.setUp()[:2], plates_reps={"1": 2})
        data = graph.simulate(2)
        self.assertIn("n1_0_", data)
        self.assertIn("n1_1_", data)
        self.assertEqual(data["n0"], [1, 1])
        self.assertEqual(data["n1_1_"], [1, 1])

    def test_parent_in_plate(self):
        nodes = self.setUp()
        n1 = nodes[1]
        n3 = nodes[3]
        graph = Graph([n1, n3], plates_reps={"1": 2})
        data = graph.simulate(2)
        self.assertIn("n1_1_", data)
        self.assertEqual(data["n1_1_"], [1, 1])
        self.assertEqual(data["n3"], [[1, 1], [1, 1]])


if __name__ == '__main__':
    unittest.main()
