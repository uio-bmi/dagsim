import unittest

from dagsim.base import Graph, Node, Selection
import random


class TestSelection(unittest.TestCase):

    def setUp(self) -> Graph:
        def get_normal(counter=[0]):
            index_list = [0, 1, 2, 3, 4, 5, 6, 7, 8]  # should have 5 even numbers
            counter[0] += 1
            return index_list[counter[0] - 1]

        def select(val):
            if val % 2 == 0:
                return True
            else:
                return False

        Normal = Node(name="Normal", function=get_normal)
        Select = Selection(name="Select", function=select, kwargs={"val": Normal})
        my_graph = Graph(name="graph1", list_nodes=[Normal, Select])
        return my_graph

    def test_selection(self):
        data = self.setUp().simulate(5)
        self.assertEqual([0, 2, 4, 6, 8], data["Normal"])


if __name__ == '__main__':
    unittest.main()
