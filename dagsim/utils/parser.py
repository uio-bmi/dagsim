import yaml
from dagsim.base import Graph, Node, Selection, Stratify
from dagsim.utils._misc import parse_string_args
from inspect import getmembers, isfunction
import importlib
import pandas as pd
import igraph as ig
import os.path


class DagSimSpec:
    def __init__(self, file_name: str):
        self.top_order = []
        self.graph = None
        with open(file_name, 'r') as stream:
            self.yaml_file = yaml.safe_load(stream)

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
            functions_list = getmembers(functions_file, isfunction)
        except KeyError:
            functions_list = []

        self._build_graph_from_nodes(nodes_dict, functions_list)
        if verbose:
            print(self.graph)
        if draw:
            self.graph.draw()
        data = self._simulate_data()
        return data

    def _build_adj_matrix(self, nodes: dict):
        node_names = nodes.keys()
        parents_dict = {k: [v for v in (list(nodes[k]["kwargs"].values()) + nodes[k]["args"]) if v in node_names] for k
                        in node_names}
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

    def _build_graph_from_nodes(self, nodes: dict, functions: list):
        list_nodes = []
        for key in self.top_order:
            nodes[key] = {**nodes[key], **{"name": key}}
            nodes[key]["function"] = self._get_func_by_name(functions, nodes[key]["function"])
            nodes[key]["kwargs"] = {
                k: self._get_node_by_name(v, list_nodes) if self._get_node_by_name(v, list_nodes) is not None else v for k, v in
                nodes[key]["kwargs"].items()}

            nodes[key]["args"] = [
                self._get_node_by_name(v, list_nodes) if self._get_node_by_name(v, list_nodes) is not None else v for v in
                nodes[key]["args"]]

            nodes[key] = self._clear_strs(nodes[key])

            if "plates" in nodes[key]:
                nodes[key]["plates"] = str(nodes[key].get("plates")).replace(" ", "").split(",")

            node_type = nodes[key].get("type")
            if node_type is not None:
                nodes[key].pop("type")

            if node_type == "Node" or node_type is None:
                node = Node._build_object(**nodes[key])
                # self.graph._add_node(node)

            elif node_type == "Selection":
                node = Selection._build_object(**nodes[key])
                # self.graph._add_node(node)

            elif node_type == "Stratify":
                node = Stratify._build_object(**nodes[key])
                # self.graph._add_node(node)

            else:
                raise TypeError("\"" + node_type + "\" is not a valid node type. \"type\" should be either Node, "
                                                   "Selection, or Stratify.")
            list_nodes.append(node)

        if "name" not in self.yaml_file["graph"]:
            self.yaml_file["graph"]["name"] = "Graph"

        plate_reps = self._get_plates_reps()

        self.graph = Graph(name=self.yaml_file["graph"]["name"], list_nodes=list_nodes, plates_reps=plate_reps)

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
        plate_dict = {str(key): val for key, val in plate_dict.items()}
        return plate_dict

    def _get_node_by_name(self, name, list_nodes):
        try:
            node = [i for i in list_nodes if i.name == name][0]
        except (ValueError, IndexError):
            node = None
        return node

    def _simulate_data(self):
        data = self.graph.simulate(**self.yaml_file["instructions"]["simulation"])
        return data


if __name__ == "__main__":
    parser = DagSimSpec(file_name="testyml.yml")
    data = parser.parse()
    print(data)
