from dagsim.base import Graph, Generic
import numpy as np


def add(params0, params1):
    return params0 + params1


def square(param, add_param):
    return np.square(param) + add_param


def double(param, add1, add2):
    return np.square(param) + add1 - add2


Prior1 = Generic(name="Prior1", function=np.random.normal)
Prior2 = Generic(name="Prior2", function=np.random.normal)
Node1 = Generic(name="Node1", kwargs={"param": Prior2, "add1": 2, "add2": 1}, function=double)
Node2 = Generic(name="Node2", kwargs={"param": Prior1, "add1": 2, "add2": 1}, function=double)
Node3 = Generic(name="Node3", kwargs={"param": Node1, "add_param": 1}, function=square)
Node4 = Generic(name="Node4", kwargs={"params0": Node3, "params1": Prior1}, function=add)

listNodes = [Prior1, Prior2, Node1, Node2, Node3, Node4]
my_graph = Graph("Graph1", listNodes)
my_graph.draw()
n = my_graph.simulate(num_samples=2, csv_name="test")
print(n)
