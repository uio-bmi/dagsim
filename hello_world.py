from Graph import Graph, Prior, Generic, Selection
import numpy as np


def add(params0, params1):
    return params0 + params1


def square(param, add_param):
    return np.square(param) + add_param


def double(param, add1, add2):
    return np.square(param) + add1 - add2


Prior1 = Prior(name="Prior1", function=np.random.normal)
Prior2 = Prior(name="Prior2", function=np.random.normal)
Node1 = Generic(name="Node1", parents=[Prior1, Prior2], function=add, observed=False)
Node2 = Generic(name="Node2", parents=[Prior1], function=double, additional_params=[2, 1])
Node3 = Generic(name="Node3", parents=[Node1], function=square, additional_params=[1])
Node4 = Generic(name="Node4", parents=[Node3, Prior1], function=add)
Node5 = Selection(name="Node5", parents=[Node2, Node3], function=add)

listNodes = [Prior1, Prior2, Node1, Node2, Node3, Node4]
my_graph = Graph("Graph1", listNodes)
my_graph.add_node(Node5)
my_graph.draw()
ord = my_graph.top_order
n = my_graph.simulate(num_samples=2, csv_name="test")
print(n)
