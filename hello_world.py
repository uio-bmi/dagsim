from baseDS import Graph, Prior, Generic, Selection
import numpy as np


def add(params0, params1):
    return params0 + params1


def square(param, add_param):
    return np.square(param) + add_param


def double(param, add1, add2):
    return np.square(param) + add1 - add2


Prior1 = Prior(name="Prior1", function=np.random.normal)
Prior2 = Prior(name="Prior2", function=np.random.normal)
Prior3 = Prior(name="Prior3", function=np.random.normal)
Node1 = Generic(name="Node1", parents=[Prior2], function=double, additional_params=[2, 1])
Node2 = Generic(name="Node2", parents=[Prior1], function=double, additional_params=[2, 1])
Node3 = Generic(name="Node3", parents=[Node1], function=square, additional_params=[1])
Node4 = Generic(name="Node4", parents=[Node3, Prior1], function=add)

listNodes = [Prior1, Prior2, Prior3, Node1, Node2, Node3, Node4]
my_graph = Graph("Graph1", listNodes)
my_graph.draw()
n = my_graph.simulate(num_samples=2, csv_name="test")
print(n)
