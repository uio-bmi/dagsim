import yaml
from baseDS import Graph, Generic, Selection, Stratify
from inspect import getmembers, isfunction
import importlib
import pandas as pd
import igraph as ig


# import numpy as np
# import scipy as sp


def parse_yaml(file_name: str):
    def build_adj_matrix(nodes: dict):
        # TODO add a note to make sure that no string unintentionally has the same name as a node
        node_names = nodes.keys()
        parents_dict = {k: [v for v in nodes[k]["arguments"].values() if v in node_names] for k in node_names}
        pd_dict = pd.DataFrame(0, columns=node_names, index=node_names)
        for child in node_names:
            for parent in parents_dict[child]:
                pd_dict[child][parent] = 1
        return pd_dict.to_numpy(), list(node_names)

    def get_top_order(pdDAG, names):
        G = ig.Graph.Weighted_Adjacency(pdDAG.tolist())
        top_order = G.topological_sorting()
        top_order = [names[i] for i in top_order]
        return top_order

    def check_acyclicity(adj_mat):
        pdDAGGraph = ig.Graph.Weighted_Adjacency(adj_mat.tolist())
        return ig.Graph.is_dag(pdDAGGraph)

    def get_func_by_name(functions_list: list, func_name: str):
        for name, func in functions_list:
            if name == func_name:
                return func
        try:
            func = get_implicit_func(func_name=func_name)
            return func
        except (AttributeError, ModuleNotFoundError):
            raise ImportError("Couldn't find the function \"" + func_name + "\"")

    def get_implicit_func(func_name: str):
        first_part = func_name.rfind(".")
        module_name = func_name[:first_part]
        func_name = func_name[first_part + 1:]
        module = importlib.import_module(module_name)
        func = getattr(module, func_name)
        return func

        # try:
        #     print("succ1")
        #     library = importlib.import_module(library)
        #     print("succ2")
        #     try:
        #         func = getattr(library, func_name)
        #         print(func)
        #         print("succ")
        #         return func
        #     except AttributeError:
        #         print("no func")
        #         return None
        # except ModuleNotFoundError:
        #     raise ModuleNotFoundError("no lib")
        #     return None

    def split_func_and_args(func_expression: str):
        func_expression = func_expression.replace(" ", "")
        args_str = func_expression[func_expression.find("(") + 1: func_expression.find(")")]
        args_str = args_str.split(",")
        args_dict = {}
        for arg in args_str:
            arg_name = arg[:arg.find("=")]
            args_dict[arg_name] = arg[arg.find("=")+1:]
            try:
                args_dict[arg_name] = float(args_dict[arg_name])
            except ValueError:
                pass
        func_name = func_expression[:func_expression.find("(")]
        return func_name, args_dict

    def parse_string_args(nodes):
        for key in nodes.keys():
            if "(" in nodes[key]["function"]:
                print(key)
                nodes[key]["function"], nodes[key]["arguments"] = split_func_and_args(
                    nodes[key]["function"])
        return nodes

    def populate_graph_from_nodes(nodes: dict, functions: list):
        nonlocal my_graph
        for key in top_order:

            nodes[key] = {**nodes[key], **{"name": key}}
            nodes[key]["function"] = get_func_by_name(functions, nodes[key]["function"])
            nodes[key]["arguments"] = {
                k: my_graph.get_node_by_name(v) if my_graph.get_node_by_name(v) is not None else v for k, v in
                nodes[key]["arguments"].items()}

            node_type = nodes[key].get("type")
            if node_type is not None:
                nodes[key].pop("type")

            if node_type == "Generic" or node_type is None:
                node = Generic.build_object(**nodes[key])
                my_graph.add_node(node)

            elif node_type == "Selection":
                node = Selection.build_object(**nodes[key])
                my_graph.add_node(node)

            elif node_type == "Stratify":
                node = Stratify.build_object(**nodes[key])
                my_graph.add_node(node)

            else:
                raise TypeError("\"" + node_type + "\" is not a valid node type. \"type\" should be either Generic, "
                                                   "Selection, or Stratify.")
        return my_graph

    with open(file_name, 'r') as stream:
        yaml_file = yaml.safe_load(stream)

    nodes_dict = yaml_file["graph"]["nodes"]
    nodes_dict = parse_string_args(nodes_dict)

    adj_matrix, node_names = build_adj_matrix(nodes_dict)

    assert check_acyclicity(adj_matrix), "The graph is not acyclic."

    top_order = get_top_order(adj_matrix, node_names)
    print(top_order)

    functions_file = importlib.import_module(yaml_file["graph"]["python_file"])
    # print(functions)
    functions_list = getmembers(functions_file, isfunction)
    # print(functions_list)

    my_graph = Graph(yaml_file["graph"]["name"], [])
    my_graph = populate_graph_from_nodes(nodes_dict, functions_list)

    print(my_graph)
    data = my_graph.simulate(**yaml_file["instructions"]["simulation"])
    my_graph.draw()
    return data


if __name__ == "__main__":
    data = parse_yaml(file_name="testyml.yml")
    # data = graph.simulate(2)
    print(data)
