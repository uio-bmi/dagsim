import yaml
from dagsim.base import Graph, Generic, Selection, Stratify
from inspect import getmembers, isfunction
import importlib
import pandas as pd
import igraph as ig


class Parser:
    def __init__(self, file_name: str):
        self.top_order = []
        self.graph = None
        self.node_names = []
        self.adj_matrix = None
        with open(file_name, 'r') as stream:
            self.yaml_file = yaml.safe_load(stream)

    def parse(self):

        nodes_dict = self._parse_string_args(self.yaml_file["graph"]["nodes"])

        self.adj_matrix, self.node_names = self._build_adj_matrix(nodes_dict)

        assert self._check_acyclicity(self.adj_matrix), "The graph is not acyclic."

        self._find_top_order(self.adj_matrix, self.node_names)

        functions_file = importlib.import_module(self.yaml_file["graph"]["python_file"])
        functions_list = getmembers(functions_file, isfunction)

        self._build_graph_from_nodes(nodes_dict, functions_list)
        print(self.graph)

        self.graph.draw()
        data = self._simulate_data()
        return data

    def _parse_string_args(self, nodes):

        for key in nodes.keys():
            if "(" in nodes[key]["function"]:
                nodes[key]["function"], nodes[key]["arguments"] = self._split_func_and_args(
                    nodes[key]["function"])
        return nodes

    def _split_func_and_args(self, func_expression: str):
        func_expression = func_expression.replace(" ", "")
        args_str = func_expression[func_expression.find("(") + 1: func_expression.find(")")]
        args_str = args_str.split(",")
        args_dict = {}
        for arg in args_str:
            arg_name = arg[:arg.find("=")]
            args_dict[arg_name] = arg[arg.find("=") + 1:]
            try:
                args_dict[arg_name] = float(args_dict[arg_name])
            except ValueError:
                pass
        func_name = func_expression[:func_expression.find("(")]
        return func_name, args_dict

    def _build_adj_matrix(self, nodes: dict):
        # TODO add a note to make sure that no string unintentionally has the same name as a node
        node_names = nodes.keys()
        parents_dict = {k: [v for v in nodes[k]["arguments"].values() if v in node_names] for k in node_names}
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
        self.graph = Graph(self.yaml_file["graph"]["name"], [])

        for key in self.top_order:
            nodes[key] = {**nodes[key], **{"name": key}}
            nodes[key]["function"] = self._get_func_by_name(functions, nodes[key]["function"])
            nodes[key]["arguments"] = {
                k: self.graph.get_node_by_name(v) if self.graph.get_node_by_name(v) is not None else v for k, v in
                nodes[key]["arguments"].items()}

            node_type = nodes[key].get("type")
            if node_type is not None:
                nodes[key].pop("type")

            if node_type == "Generic" or node_type is None:
                node = Generic.build_object(**nodes[key])
                self.graph.add_node(node)

            elif node_type == "Selection":
                node = Selection.build_object(**nodes[key])
                self.graph.add_node(node)

            elif node_type == "Stratify":
                node = Stratify.build_object(**nodes[key])
                self.graph.add_node(node)

            else:
                raise TypeError("\"" + node_type + "\" is not a valid node type. \"type\" should be either Generic, "
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
        first_part = func_name.rfind(".")
        module_name = func_name[:first_part]
        func_name = func_name[first_part + 1:]
        module = importlib.import_module(module_name)
        func = getattr(module, func_name)
        return func

    def _simulate_data(self):
        data = self.graph.simulate(**self.yaml_file["instructions"]["simulation"])
        return data


if __name__ == "__main__":
    parser = Parser(file_name="testyml.yml")
    data = parser.parse()
    print(data)
