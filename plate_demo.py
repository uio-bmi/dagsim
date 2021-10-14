from dagsim.baseDS import Graph, Generic
import numpy as np


def add(params1, params2):
    return params1 + params2


def square(param, add_param):
    return np.square(param) + add_param


def double(param, add1, add2):
    return np.square(param) + add1 - add2


Prior1 = Generic(name="Prior1", function=np.random.normal, plates=['7', '4'])  # G
Prior2 = Generic(name="Prior2", function=np.random.normal, plates=['6', '4', '2'])  # B
Prior3 = Generic(name="Prior3", function=np.random.normal, plates=['4'])  # F
Node1 = Generic(name="Node1", function=double, arguments={"param":Prior2, "add1":2, "add2":1}, plates=['1', '2', '4'])  # A
Node2 = Generic(name="Node2", function=double, arguments={"param":Prior1, "add1":2, "add2":1}, plates=['5', '4'])  # E
Node3 = Generic(name="Node3", function=square, arguments={"param":Prior1, "add_param":1}, plates=['3'])  # C
Node4 = Generic(name="Node4", arguments={"params1": Node3, "params2": Prior1}, function=add)

listNodes = [Prior1, Prior2, Prior3, Node1, Node2, Node3, Node4]
my_graph = Graph("Graph1", listNodes)
my_graph.draw()
n = my_graph.simulate(num_samples=2, csv_name="plates")
print(n)
