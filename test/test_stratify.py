import unittest

from dagsim.base import Graph, Generic, Stratify
import random


class TestStratify(unittest.TestCase):

    def setUp(self) -> Graph:
        def get_normal(counter=[0]):
            index_list = [0, 1, 2, 3, 4]  # should have 5 even numbers
            counter[0] += 1
            return index_list[counter[0] - 1]

        def stratify(val):
            if val % 2 == 0:
                return "Even"
            else:
                return "Odd"

        Node = Generic(name="Normal", function=get_normal)
        StratifyNode = Stratify(name="Stratify", function=stratify, arguments={"val": Node})
        my_graph = Graph(name="graph1", list_nodes=[Node, StratifyNode])
        return my_graph

    def test_selection(self):
        data = self.setUp().simulate(5, stratify=True)
        self.assertEqual({'Normal': [1, 3]}, data["Odd"])
        self.assertEqual({'Normal': [0, 2, 4]}, data["Even"])


if __name__ == '__main__':
    unittest.main()
