import numpy as np
import scipy.stats as sts
from typing import Union, List
import time
from graphviz import Source
import csv
import pandas as pd
import copy as cp


# https://graphviz.org/doc/info/attrs.html#d:shape
# https://networkx.org/documentation/stable//reference/drawing.html

class Node:
    def __init__(self, name: str, parents: list, function, observed: bool, additional_params=[]):
        self.name = name
        self.parents = parents
        self.function = function
        self.additional_params = additional_params
        self.output = None
        self.observed = observed

    def forward(self, idx):
        return self.function(*[p.output[idx] for p in self.parents])

    def node_simulate(self, num_samples):
        self.output = [self.forward(i) for i in range(num_samples)]

    def __len__(self):
        return len(self.parents)


class Prior(Node):
    def __init__(self, name: str, function, additional_params=[], observed=True):
        super().__init__(name=name, parents=None, function=function, additional_params=additional_params,
                         observed=observed)

    def forward(self):
        return self.function(*self.additional_params)

    def node_simulate(self, num_samples):
        self.output = [self.forward() for _ in range(num_samples)]


class Generic(Node):
    def __init__(self, name: str, parents, function, additional_params=[], observed=True):
        super().__init__(name=name, parents=parents, function=function, additional_params=additional_params,
                         observed=observed)


class Selection(Node):
    def __init__(self, name: str, parents, function, additional_params=[], observed=True):
        super().__init__(name=name, parents=parents, function=function, additional_params=additional_params,
                         observed=observed)


class Graph:
    def __init__(self, name, list_nodes):
        self.name = name
        self.nodes = list_nodes  # [None] * num_nodes
        self.adj_dict = {}
        self.top_order = []
        self.topol_order()

    def add_node(self, node: Node):
        if node not in self.nodes:
            self.nodes.append(node)
        # update the topological order whenever a new node is added
        self.topol_order()

    def get_node_by_name(self, name: str):
        if not isinstance(name, str):
            print("Please enter a valid node name")
        else:
            node = next((item for item in self.nodes if item.name == name), None)
            if node is None:
                print("No node with the name '" + name + "' was found")
            else:
                return node

    def adj_list(self):
        adj_dict = {k.name: [] for k in self.nodes}
        for childNode in range(len(self)):
            if type(self[childNode]).__name__ != "Prior":
                for parentNode in range(len(self[childNode])):
                    adj_dict[self[childNode].parents[parentNode].name].append(self[childNode].name)
        self.adj_dict = adj_dict

    def adj_mat(self):
        # TODO replace the two lists by one
        generic = [node for node in self.nodes if node.__class__.__name__ == "Generic"]
        generic_names = [node.name for node in generic]
        matrix = pd.DataFrame(data=np.zeros([len(generic), len(generic)], dtype=np.bool),
                              columns=generic_names,
                              index=generic_names)
        print(generic)
        for node in generic:
            for parent in node.parents:
                matrix[node.name][parent.name] = 1
        print(matrix)

    def topol_order(self):
        # https://courses.cs.washington.edu/courses/cse326/03wi/lectures/RaoLect20.pdf
        self.adj_list()
        indegree = {k.name: 0 for k in self.nodes if k.__class__.__name__ != "Selection"}
        for node in self.nodes:
            if node.parents is not None:
                indegree[node.name] = len(node.parents)
        queue = [k for k in indegree if indegree[k] == 0]
        top_order = []
        while queue:
            drop = queue[0]
            top_order.append(drop)
            queue.pop(0)
            indegree.pop(drop)
            drop = self.get_node_by_name(drop)
            for node in self.adj_dict[drop.name]:
                indegree[node] -= 1
            queue.extend([node for node in indegree if indegree[node] == 0])
            queue = list(set(queue))
        self.top_order = top_order

    # TODO change get by index to get by name
    def __getitem__(self, item):
        return self.nodes[item]

    def __len__(self):
        return len(self.nodes)

    def generate_dot(self):
        self.adj_list()

        shape_dict = {'Prior': "invhouse", 'Generic': "ellipse", 'Selection': "doublecircle"}
        dot_str = 'digraph G{\n'
        for childNode in range(len(self)):
            my_str = self[childNode].name + " [shape=" + shape_dict[type(self[childNode]).__name__] + "];\n"
            dot_str = dot_str + my_str

        for node in self.adj_dict.keys():
            if self.adj_dict[node]:
                tmp_str = node + "->" + ",".join(self.adj_dict[node]) + ";\n"
                dot_str += tmp_str

        dot_str = dot_str + '}'
        return dot_str

    # def get_node_by_name(self, name: str):
    #     return self.nodes[self.nodes.index(name)]

    def draw(self):
        dot_str = self.generate_dot()
        s = Source(dot_str, filename=self.name + str(np.random.randint(low=0, high=5, size=1)[0]) + ".gv", format="png")
        s.view(cleanup=True, quiet_view=True)

    def simulate(self, num_samples, csv_name=""):
        output_dict = {}
        for node in self.top_order:
            node = self.get_node_by_name(node)
            # if node.__class__.__name__ == "Prior":
            #     node.output = [node.forward() for _ in range(num_samples)]
            # else:
            #     node.output = [node.forward(i) for i in range(num_samples)]
            node.node_simulate(num_samples)
            output_dict[node.name] = node.output
        if csv_name:
            pd.DataFrame(output_dict).to_csv(csv_name + '.csv', index=False)
        return output_dict


def add(params0, params1):
    return params0 + params1
    # return np.add(params0, params1)


def square(input):
    # return np.square(params[0])
    return np.square(input)


def double(input):
    # return np.square(params[0])
    return np.square(input)


Prior1 = Prior(name="Age", function=np.random.normal)
Prior2 = Prior(name="HLA", function=np.random.normal)
Node1 = Generic(name="Node1", parents=[Prior1, Prior2], function=add)
Node2 = Generic(name="Node2", parents=[Prior1], function=double)
Node3 = Generic(name="Node3", parents=[Node1, Node2], function=add, observed=False)
Node4 = Generic(name="Node4", parents=[Node3, Prior1], function=add)
Node5 = Selection(name="Node5", parents=[Node2, Node3], function=add)

listNodes = [Prior1, Prior2, Node1, Node2, Node3, Node4]
my_graph = Graph("Graph1", listNodes)
my_graph.add_node(Node5)
# my_graph.draw()
ord = my_graph.top_order
n = my_graph.simulate(num_samples=2, csv_name="test")
print(n)
