import argparse

import yaml
from dagsim.base import Graph, Node, Selection, Stratify, Missing
from dagsim.utils._misc import parse_string_args
from inspect import getmembers, isfunction
import importlib
import pandas as pd
import igraph as ig
import os.path


class DagSimSpec:
    def __init__(self, file_name: str, output_path: str = None):
        self.output_path = output_path
        self.functions_list = None
        self.top_order = []
        self.graph = None
        with open(file_name, 'r') as stream:
            self.yaml_file = yaml.safe_load(stream)
        # todo check parsing floats or integers

    def parse(self, verbose: bool = True, draw: bool = True):

        nodes_dict = parse_string_args(self.yaml_file["graph"]["nodes"])

        adj_matrix, node_names = self._build_adj_matrix(nodes_dict)

        assert self._check_acyclicity(adj_matrix), "The graph is not acyclic."

        self._find_top_order(adj_matrix, node_names)

        try:
            python_file = self.yaml_file["graph"]["python_file"]
            assert python_file.endswith(".py"), "Please use a proper python file."
            assert os.path.isfile(python_file), "The file \"" + python_file + "\" doesn't exist."
            python_file = python_file[:-3]

            functions_file = importlib.import_module(python_file)
            self.functions_list = getmembers(functions_file, isfunction)
        except KeyError:
            self.functions_list = []

        self._build_graph_from_nodes(nodes_dict)
        if verbose:
            print(self.graph)
        if draw:
            self.graph.draw()
        data = self._simulate_data()
        return data

    def _build_adj_matrix(self, nodes: dict):
        node_names = nodes.keys()
        # allow for non-boolean Missing-index output
        parents_dict = {k: [v for v in (list(nodes[k]["kwargs"].values()) + nodes[k]["args"]) if
                            v in node_names] for k in node_names if nodes[k]["type"] != "Missing"}
        parents_dict.update({k: [nodes[k]["underlying_value"], nodes[k]["index_node"]] for k in node_names if
                             nodes[k]["type"] == "Missing"})

        pd_dict = pd.DataFrame(0, columns=node_names, index=node_names)
        for child in node_names:
            for parent in parents_dict[child]:
                pd_dict[child][parent] = 1
        return pd_dict.to_numpy(), list(node_names)

    def _check_acyclicity(self, adj_mat):
        pdDAGGraph = ig.Graph.Weighted_Adjacency(adj_mat.tolist())
        return ig.Graph.is_dag(pdDAGGraph)

    def _find_top_order(self, adj_mat, names):
        G = ig.Graph.Weighted_Adjacency(adj_mat.tolist())
        top_order = G.topological_sorting()
        top_order = [names[i] for i in top_order]
        self.top_order = top_order

    def _build_graph_from_nodes(self, nodes: dict):
        self.list_nodes = []
        for key in self.top_order:
            node_type = self._get_node_type(nodes[key])
            nodes[key] = {**nodes[key], **{"name": key}}
            if node_type == "Missing":
                node = self._build_missing_node(nodes[key])
            else:
                node = self._build_other_node(nodes[key], node_type)
            self.list_nodes.append(node)

        if "name" not in self.yaml_file["graph"]:
            self.yaml_file["graph"]["name"] = "Graph"

        plate_reps = self._get_plates_reps()

        self.graph = Graph(name=self.yaml_file["graph"]["name"], list_nodes=self.list_nodes, plates_reps=plate_reps)

    def _build_missing_node(self, node: dict) -> Missing:
        assert "underlying_value" in node, "'underlying_value' is not specified"
        assert "index_node" in node, "'index_node' is not specified"

        node["underlying_value"] = self._get_node_by_name(node["underlying_value"])
        node["index_node"] = self._get_node_by_name(node["index_node"])

        return Missing(**node)

    def _build_other_node(self, node, node_type):
        node["function"] = self._get_func_by_name(self.functions_list, node["function"])
        node["kwargs"] = {
            k: self._get_node_by_name(v) if self._get_node_by_name(v) is not None else v for
            k, v in node["kwargs"].items()}

        node["args"] = [
            self._get_node_by_name(v) if self._get_node_by_name(v) is not None else v for v
            in node["args"]]

        node = self._clear_strs(node)

        if node_type == "Node":
            if "plates" in node:
                node["plates"] = str(node.get("plates")).replace(" ", "").split(",")
            node = Node._build_object(**node)

        elif node_type == "Selection":
            node = Selection._build_object(**node)

        elif node_type == "Stratify":
            node = Stratify._build_object(**node)

        return node

    def _get_node_type(self, node):
        node_type = node.get("type")  # always not None because parse_string_args adds the type
        node.pop("type")
        if node_type in ["Node", "Selection", "Missing", "Stratify"]:
            return node_type
        else:
            raise TypeError("\"" + node_type + "\" is not a valid node type. \"type\" should be either Node, "
                                               "Selection, or Stratify.")

    def _get_func_by_name(self, functions_list: list, func_name: str):
        for name, func in functions_list:
            if name == func_name:
                return func
        try:
            func = self._get_implicit_func(func_name=func_name)
            return func
        except (AttributeError, ModuleNotFoundError):
            raise ImportError("Couldn't find the function \"" + func_name + "\"")

    def _get_implicit_func(self, func_name: str):
        # For functions not defined in the python file, but rather coming from external libraries, such as numpy.
        first_part = func_name.rfind(".")
        module_name = func_name[:first_part]
        func_name = func_name[first_part + 1:]
        module = importlib.import_module(module_name)
        func = getattr(module, func_name)
        return func

    def _clear_strs(self, node):
        for ind in range(len(node["args"])):
            if isinstance(node["args"][ind], str):
                if node["args"][ind].startswith(("'", '"')):
                    node["args"][ind] = node["args"][ind][1:-1]
        for k, v in node["kwargs"].items():
            if isinstance(v, str):
                if v.startswith(("'", '"')):
                    node["kwargs"][k] = v[1:-1]
        return node

    def _get_plates_reps(self):
        plate_dict = self.yaml_file["graph"].get("plates_reps")
        if plate_dict is not None:
            plate_dict = {str(key): val for key, val in plate_dict.items()}
        return plate_dict

    def _get_node_by_name(self, name):
        try:
            node = [i for i in self.list_nodes if i.name == name][0]
        except (ValueError, IndexError):
            node = None
        return node

    def _simulate_data(self):
        simulation_instructions = self.yaml_file["instructions"]["simulation"]
        if self.output_path is not None:
            simulation_instructions.update({"output_path": self.output_path})
        print(simulation_instructions)
        data = self.graph.simulate(**simulation_instructions)
        return data


def main():
    args_parser = argparse.ArgumentParser(description="dagsim command line tool")
    args_parser.add_argument("specification_path",
                             help="Path to specification YAML file. Always used to define the simulation.")
    args_parser.add_argument("-v", "--verbose", action="store_true", help="Set verbosity to True")
    args_parser.add_argument("-d", "--draw", action="store_true", help="Set draw to True")
    args_parser.add_argument("-o", "--output", type=str, help="The output path to the simulated data")

    args = args_parser.parse_args()
    dagsim_parser = DagSimSpec(file_name=args.specification_path, output_path=args.output)
    _ = dagsim_parser.parse(verbose=args.verbose, draw=args.draw)


if __name__ == "__main__":
    # parser = DagSimSpec(file_name="test_yaml_missing.yml")
    parser = DagSimSpec(file_name="testyml2.yml", output_path="/home/ghadi/gitvigs/")
    data = parser.parse()
    print(data)
