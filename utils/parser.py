import yaml
from baseDS import Graph, Generic, Selection, Stratify
from inspect import getmembers, isfunction
import importlib
import pandas as pd
import igraph as ig
import numpy as np
import scipy as sp


def parse_yaml(file_name: str):
    def build_adj_matrix(nodes_yaml: dict):
        # TODO add a note to make sure that no string unintentionally has the same name as a node
        node_names = nodes_yaml.keys()
        parents_dict = {k: [v for v in nodes_yaml[k]["arguments"].values() if v in node_names] for k in node_names}
        pd_dict = pd.DataFrame(0, columns=node_names, index=node_names)
        for child in node_names:
            for parent in parents_dict[child]:
                pd_dict[child][parent] = 1
        print("parents_dict", parents_dict)
        print("pd_dict ", pd_dict)
        return pd_dict

    def check_acyclicity():
        pdDAG = build_adj_matrix(yaml_file["graph"]["nodes"]).to_numpy()
        # print(ppd.to_numpy())
        pdDAGGraph = ig.Graph.Weighted_Adjacency(pdDAG.tolist())
        return ig.Graph.is_dag(pdDAGGraph)

    with open(file_name, 'r') as stream:
        yaml_file = yaml.safe_load(stream)

    assert check_acyclicity(), "The graph is not acyclic"

    def get_func_by_name(functions_list: list, func_name: str):
        ret_func = None
        for name, func in functions_list:
            if name == func_name:
                ret_func = func
                break
        if ret_func is None:
            raise ValueError("Function \"" + func_name + "\" not found")
        else:
            return ret_func

    functions_file = importlib.import_module(yaml_file["graph"]["python_file"])
    # print(functions)
    functions_list = getmembers(functions_file, isfunction)
    # print(functions_list)

    my_graph = Graph("Graph1", [])
    nodes_dict = yaml_file["graph"]["nodes"]
    print(nodes_dict)

    for key in nodes_dict.keys():

        nodes_dict[key] = {**nodes_dict[key], **{"name": key}}
        nodes_dict[key]["function"] = get_func_by_name(functions_list, nodes_dict[key]["function"])
        nodes_dict[key]["arguments"] = {
            k: my_graph.get_node_by_name(v) if my_graph.get_node_by_name(v) is not None else v for k, v in
            nodes_dict[key]["arguments"].items()}

        node_type = nodes_dict[key].get("type")
        if node_type is not None:
            nodes_dict[key].pop("type")

        if node_type == "Generic" or type is None:
            node = Generic.build_object(**nodes_dict[key])
            my_graph.add_node(node)

        elif node_type == "Selection":
            node = Selection.build_object(**nodes_dict[key])
            my_graph.add_node(node)

        elif node_type == "Stratify":
            node = Stratify.build_object(**nodes_dict[key])
            my_graph.add_node(node)

        else:
            raise TypeError("\"" + node_type + "\" is not a valid node type. \"type\" should be either Generic, "
                                               "Selection, or Stratify.")

    print(my_graph)
    data = my_graph.simulate(**yaml_file["instructions"]["simulation"])
    return data


if __name__ == "__main__":
    data = parse_yaml(file_name="testyml.yml")
    # data = graph.simulate(2)
    print(data)
