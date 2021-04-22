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
        # self.ready = False

    def forward(self, idx):
        # print(self.name + str([i() for i in self.parents]))
        # print("called")
        # self.output = self.function(*[i() for i in self.parents])
        # self.output = self.function(*[p.output[idx] for p in self.parents])
        # print(*[p.name for p in self.parents])
        # print([p.output for p in self.parents])
        # print(self.output)
        # return self.output
        return self.function(*[p.output[idx] for p in self.parents])
        # pass

    # def __call__(self, *args, **kwargs):
    #     # print(self.name)
    #     time.sleep(0.3)
    #     self.output = self.forward()
    #     return self.output

    def __len__(self):
        return len(self.parents)


class Prior(Node):
    def __init__(self, name: str, function, additional_params=[], observed=True):
        super().__init__(name=name, parents=None, function=function, additional_params=additional_params,
                         observed=observed)
        # self.ready = True

    def forward(self):
        # return self.function(self.additional_params[0], self.additional_params[1])
        # self.output = self.function(*self.additional_params)  # for i in range(num_samples)]
        # return self.output
        return self.function(*self.additional_params)

    # def __call__(self, *args, **kwargs):
    #     return self.forward()

    # def __getitem__(self, item):
    #     return self.forward()


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
        # def __init__(self, name, num_nodes):

        self.name = name
        # self.num_nodes = num_nodes
        self.nodes = list_nodes  # [None] * num_nodes
        self.adj_dict = self.adj_list()

    def add_node(self, node: Node):
        # def add_node(self, index: int, node: Node):
        if node not in self.nodes:
            self.nodes.append(node)

    def get_node_by_name(self, name: str):
        if not isinstance(name, str):
            print("Please enter a valid node name")
        else:
            node = next((item for item in self.nodes if item.name == name), None)
            if node is None:
                print("No node with the name '" + name + "' was found")
            else:
                return node

    # def __setitem__(self, key, value):
    #     # def __setitem__(self, key, value):
    #     self.add_node(value)
    def adj_list(self):
        adj_dict = {k.name: [] for k in self.nodes}
        for childNode in range(len(self)):
            if type(self[childNode]).__name__ != "Prior":
                for parentNode in range(len(self[childNode])):
                    adj_dict[self[childNode].parents[parentNode].name].append(self[childNode].name)
        print(adj_dict)
        return adj_dict

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

    def top_order(self):
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
        return top_order

    # def topologicalSortUtil(self, v, visited, stack):
    #
    #     # Mark the current node as visited.
    #     visited[v] = True
    #     print(self.adj_dict[v])
    #     # Recur for all the vertices adjacent to this vertex
    #     for i in self.adj_dict[v]:
    #         print(i)
    #         if visited[i] == False:
    #             self.topologicalSortUtil(i, visited, stack)
    #
    #     # Push current vertex to stack which stores result
    #     stack.append(v)
    #
    # def topologicalSort(self):
    #     # Mark all the vertices as not visited
    #     # visited = [False] * len(self)
    #     visited = {x: False for x in self.adj_dict}
    #     stack = []
    #
    #     # Call the recursive helper function to store Topological
    #     # Sort starting from all vertices one by one
    #     for i in self.nodes:
    #         i = i.name
    #         print(i)
    #         if visited[i] == False:
    #             self.topologicalSortUtil(i, visited, stack)
    #
    #     # Print contents of the stack
    #     print(stack[::-1])  # return list in reverse order

    # TODO change get by index to get by name
    def __getitem__(self, item):
        return self.nodes[item]

    def __len__(self):
        return len(self.nodes)

    # def compile(self, list_nodes):
    #     for i in range(len(list_nodes)):
    #         my_graph[i] = list_nodes[i]

    def generate_dot(self):
        self.adj_list()

        shape_dict = {'Prior': "invhouse", 'Generic': "ellipse", 'Selection': "doublecircle"}
        dot_str = 'digraph G{\n'
        for childNode in range(len(self)):
            my_str = self[childNode].name + " [shape=" + shape_dict[type(self[childNode]).__name__] + "];\n"
            dot_str = dot_str + my_str

        # for childNode in range(len(self)):
        #     if type(self[childNode]).__name__ is not "Prior":
        #         for parentNode in range(len(self[childNode])):
        #             my_str = my_graph[childNode].parents[parentNode].name + "->" + my_graph[childNode].name + ";\n"
        #             dot_str = dot_str + my_str
        #             self.adj_dict[my_graph[childNode].parents[parentNode].name].append(my_graph[childNode].name)
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

    # def simulate(self):
    #     # ready_list = [node for node in self.nodes if node.ready == True]
    #     initial_list = self.nodes
    #     done_list = []
    #     output_dict = {}
    #     while initial_list:
    #         print("initial_list ", [nodev.name for nodev in initial_list])
    #         for idx, node in enumerate(initial_list):
    #             # print("node ", node.name)
    #             if node.ready:
    #                 # print(node.name)
    #                 output_dict[node.name] = node.forward()
    #                 # print(node.output)
    #                 initial_list.pop(idx)
    #                 done_list.append(node.name)
    #                 # break
    #
    #             if node.parents is not None:
    #                 # print([par.name for par in node.parents])
    #                 if set([par.name for par in node.parents]).issubset(done_list):
    #                     # print([par.name for par in node.parents])
    #                     node.ready = True
    #         # print([node.name for node in ready_list])
    #     # print(output_dict)
    #     return output_dict

    def simulate(self, num_samples, csv_name=""):
        self.adj_mat()
        output_dict = {}
        done_list = []
        prior_list = [node for node in self.nodes if node.__class__.__name__ == "Prior"]
        generic_list = [node for node in self.nodes if node.__class__.__name__ == "Generic"]

        for prior in prior_list:
            prior.output = [prior.forward() for _ in range(num_samples)]
            output_dict[prior.name] = prior.output
            done_list.append(prior.name)

        while generic_list:
            for idx, generic in enumerate(generic_list):
                if generic not in done_list:
                    if set([par.name for par in generic.parents]).issubset(done_list):  # if the node is ready to emit
                        # print(generic.name)
                        generic.output = [generic.forward(i) for i in range(num_samples)]
                        output_dict[generic.name] = generic.output
                        generic_list.pop(idx)
                        done_list.append(generic.name)

        if csv_name:
            pd.DataFrame(output_dict).to_csv(csv_name + '.csv', index=False)

        return output_dict


# def add(params: List[int]):
#     # print("gh", params)
#     return params[0] + params[1]

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
# my_graph.draw()
my_graph.add_node(Node5)
my_graph.draw()
ord = my_graph.top_order()
n = my_graph.simulate(num_samples=2, csv_name="test")
print(n)
# print(type(Node1))
# print(type(Node1).__bases__[0].__name__)

# print(Prior1.forward())
# print(Node1.forward())
# print(Node2.forward())
# print(Node2.forward())

# print(Node3())
#
# my_graph.get_node_by_name("Node3")
# dot_str = 'digraph G{\n'
# for i in range(len(my_graph)):
#     # if type(my_graph[i]).__bases__[0].__name__ == "Node":
#     if type(my_graph[i]).__name__ == "Generic":
#         print(my_graph[i].name)

# for childNode in range(len(my_graph)):
#     print(my_graph[childNode].name + ":")
#     if type(my_graph[childNode]).__name__ == "Generic":
#         for parentNode in range(len(my_graph[childNode])):
#             # print(my_graph[childNode].parents[parentNode].name)
#             my_str = my_graph[childNode].parents[parentNode].name + "->" + my_graph[childNode].name + ";\n"
#             print(my_str)
#             dot_str = dot_str + my_str
#             # if type(my_graph[i]).__name__ == "Generic":
#             #     print(my_graph[i].name)
#
# dot_str = dot_str + '}'
#
# s = Source(dot_str, filename="test.gv", format="png")
# s.view()
# with open('test.csv', 'w') as f:
#     for key in my_dict.keys():
#         f.write("%s,%s\n"%(key,my_dict[key]))
