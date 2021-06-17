import numpy as np
import scipy.stats as sts
from typing import Union, List
import time
from graphviz import Source
import csv
import pandas as pd
from utils.processPlates import get_plate_dot
import copy as cp


# https://graphviz.org/doc/info/attrs.html#d:shape
# https://networkx.org/documentation/stable//reference/drawing.html

class Node:
    def __init__(self, name: str, parents: list, function, plate=None, observed=True, additional_params=[]):
        self.name = name
        self.parents = parents
        self.function = function
        self.additional_params = additional_params
        self.output = None
        self.observed = observed
        self.plate = plate

    def forward(self, idx):
        temp_list = []
        if self.parents is not None:
            temp_list += [p.output[idx] for p in self.parents]
        temp_list += self.additional_params
        return self.function(*temp_list)

    def node_simulate(self, num_samples):
        self.output = [self.forward(i) for i in range(num_samples)]

    def __len__(self):
        return len(self.parents)


# class Prior(Node):
#     def __init__(self, name: str, function, additional_params=[], plate=None, observed=True):
#         super().__init__(name=name, parents=None, function=function, additional_params=additional_params,
#                          plate=plate, observed=observed)
#
#     def forward(self):
#         return self.function(*self.additional_params)
#
#     def node_simulate(self, num_samples):
#         self.output = [self.forward() for _ in range(num_samples)]


class Generic(Node):
    def __init__(self, name: str, function, parents=None, additional_params=[], plate=None, observed=True):
        super().__init__(name=name, parents=parents, function=function, additional_params=additional_params,
                         plate=plate, observed=observed)


class Selection(Node):
    def __init__(self, name: str, parents, function, additional_params=[], observed=True):
        super().__init__(name=name, parents=parents, function=function, additional_params=additional_params,
                         observed=observed)


class Graph:
    def __init__(self, name, list_nodes):
        self.name = name
        self.nodes = list_nodes  # [None] * num_nodes
        self.adj_dict = {}
        self.plates = self.plate_embedding()
        self.top_order = []
        self.update_topol_order()

    def plate_embedding(self):
        def get_key_by_label(label):
            for key in plateDict.keys():
                if plateDict[key][0] == label:
                    return key

        plateDict = {0: (None, [])}
        idx = 1
        labels = []
        for node in self.nodes:
            if node.plate:
                for label in node.plate:
                    if label not in labels:
                        plateDict[idx] = (label, [])
                        labels.append(label)
                        idx += 1
                    plateDict[get_key_by_label(label)][1].append(node.name)
            else:
                plateDict[0][1].append(node.name)
        return plateDict

    def add_node(self, node: Node):
        if node not in self.nodes:
            self.nodes.append(node)
        # update the topological order whenever a new node is added
        self.update_topol_order()

    def get_node_by_name(self, name: str):
        if not isinstance(name, str):
            print("Please enter a valid node name")
        else:
            node = next((item for item in self.nodes if item.name == name), None)
            if node is None:
                print("No node with the name '" + name + "' was found")
            else:
                return node

    def update_adj_dict(self):
        adj_dict = {k.name: [] for k in self.nodes}
        for childNode in range(len(self)):
            if self[childNode].parents is not None:
                for parentNode in range(len(self[childNode])):
                    adj_dict[self[childNode].parents[parentNode].name].append(self[childNode].name)
        self.adj_dict = adj_dict

    def adj_mat(self):
        generic = [node for node in self.nodes if node.__class__.__name__ != "Selection"]
        generic_names = [node.name for node in generic]
        matrix = pd.DataFrame(data=np.zeros([len(generic), len(generic)]), dtype=np.int,
                              columns=generic_names,
                              index=generic_names)
        for node in generic:
            if node.parents is not None:
                for parent in node.parents:
                    matrix[node.name][parent.name] = 1
        return matrix

    def update_topol_order(self):
        # https://courses.cs.washington.edu/courses/cse326/03wi/lectures/RaoLect20.pdf
        self.update_adj_dict()
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

    def __getitem__(self, item):
        return self.nodes[item]

    def __len__(self):
        return len(self.nodes)

    def generate_dot(self):

        shape_dict = {'Prior': "invhouse", 'Generic': "ellipse", 'Selection': "doublecircle"}
        dot_str = 'digraph G{\n'
        for childNode in range(len(self)):
            if self[childNode].parents is None:
                my_str = self[childNode].name + " [shape=" + shape_dict['Prior'] + "];\n"
            else:
                my_str = self[childNode].name + " [shape=" + shape_dict[type(self[childNode]).__name__] + "];\n"
            dot_str = dot_str + my_str

        for node in self.adj_dict.keys():
            if self.adj_dict[node]:
                tmp_str = node + "->" + ",".join(self.adj_dict[node]) + ";\n"
                dot_str += tmp_str

        # check if there are any plates defined in the graph
        if len(self.plates) > 1:
            dot_str += get_plate_dot(self.plates)
        dot_str += "}"
        return dot_str

    def draw(self, filename="default"):
        dot_str = self.generate_dot()
        s = Source(dot_str, filename=filename, format="png")
        s.view(cleanup=True, quiet_view=True)

    def simulate(self, num_samples, csv_name=""):
        output_dict = {}
        for node in self.top_order:
            node = self.get_node_by_name(node)
            node.node_simulate(num_samples)
            output_dict[node.name] = node.output
        if csv_name:
            pd.DataFrame(output_dict).to_csv(csv_name + '.csv', index=False)
        return output_dict
