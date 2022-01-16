import unittest

from dagsim.base import Graph, Node
import numpy as np


class TestVectorize(unittest.TestCase):

    def setUp(self) -> Graph:
        def get_normal(counter=[0]):
            index_list = [0, 1, 2, 3, 4]
            counter[0] += 1
            return index_list[counter[0] - 1]

        Normal = Node(name="Normal", function=get_normal)
        Vectorized = Node(name="Vectorized", function=np.arange, kwargs={"start": 0}, size_field="stop")
        my_graph = Graph(name="graph1", list_nodes=[Normal, Vectorized])
        return my_graph

    def test_vectorized(self):
        data = self.setUp().simulate(5)
        print(data)
        self.assertEqual([0, 1, 2, 3, 4], data["Normal"])
        self.assertEqual([0, 1, 2, 3, 4], list(data["Vectorized"]))
        self.assertEqual(data["Normal"], list(data["Vectorized"]))


if __name__ == '__main__':
    unittest.main()
