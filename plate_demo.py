from baseDS import Graph, Generic, Selection
import numpy as np


def add(params0, params1):
    return params0 + params1


def square(param, add_param):
    return np.square(param) + add_param


def double(param, add1, add2):
    return np.square(param) + add1 - add2


Prior1 = Generic(name="Prior1", function=np.random.normal, plates=['7', '4'])  # G
Prior2 = Generic(name="Prior2", function=np.random.normal, plates=['6', '4', '2'])  # B
Prior3 = Generic(name="Prior3", function=np.random.normal, plates=['4'])  # F
Node1 = Generic(name="Node1", parents=[Prior2], function=double, additional_params=[2, 1], plates=['1', '2', '4'])  # A
Node2 = Generic(name="Node2", parents=[Prior1], function=double, additional_params=[2, 1], plates=['5', '4'])  # E
Node3 = Generic(name="Node3", parents=[Node1], function=square, additional_params=[1], plates=['3'])  # C
Node4 = Generic(name="Node4", parents=[Node3, Prior1], function=add)

listNodes = [Prior1, Prior2, Prior3, Node1, Node2, Node3, Node4]
my_graph = Graph("Graph1", listNodes)
my_graph.draw()
n = my_graph.simulate(num_samples=2, csv_name="test")
print(n)
