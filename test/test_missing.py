import unittest

from dagsim.base import Graph, Node, Missing
import random


class TestMissing(unittest.TestCase):

    def setUp(self) -> Graph:

        def get_index(counter=[0]):
            index_list = [True, False, True, False, True]
            counter[0] += 1
            return index_list[counter[0] - 1]

        def get_val(counter=[0]):
            index_list = [1, 2, 3, 4, 5]
            counter[0] += 1
            return index_list[counter[0] - 1]

        index = Node("i", function=get_index)
        toBeMissed = Node(name="toBeMissed", function=get_val)
        missingNode = Missing(name="M1", underlying_value=toBeMissed, index_node=index)
        my_graph = Graph(name="graph1", list_nodes=[index, toBeMissed, missingNode])
        return my_graph

    def test_missing(self):
        data = self.setUp().simulate(5)
        self.assertEqual([True, False, True, False, True], data["i"])
        self.assertEqual([1, 2, 3, 4, 5], data["toBeMissed"])
        self.assertEqual([1, 'NaN', 3, 'NaN', 5], data['M1'])


if __name__ == '__main__':
    unittest.main()
