import yaml
from dagsim.base import Graph, Node, Selection, Stratify
from inspect import getmembers, isfunction
import importlib
import pandas as pd
import igraph as ig
import os.path


class Parser:
    def __init__(self, file_name: str):
        self.top_order = []
        self.graph = None
        with open(file_name, 'r') as stream:
            self.yaml_file = yaml.safe_load(stream)

    def parse(self, verbose: bool = True, draw: bool = True):

        nodes_dict = self._parse_string_args(self.yaml_file["graph"]["nodes"])

        adj_matrix, node_names = self._build_adj_matrix(nodes_dict)

        assert self._check_acyclicity(adj_matrix), "The graph is not acyclic."

        self._find_top_order(adj_matrix, node_names)

        python_file = self.yaml_file["graph"]["python_file"]
        assert python_file.endswith(".py"), "Please use a proper python file."
        assert os.path.isfile(python_file), "The file \"" + python_file + "\" doesn't exist."
        python_file = python_file[:-3]

        functions_file = importlib.import_module(python_file)
        functions_list = getmembers(functions_file, isfunction)

        self._build_graph_from_nodes(nodes_dict, functions_list)
        if verbose:
            print(self.graph)

        if draw:
            self.graph.draw()
        data = self._simulate_data()
        return data

    def _parse_string_args(self, nodes):
        # For each node, separate the function's name from its arguments, if not separated already
        for key in nodes.keys():
            if "(" in nodes[key]["function"]:
                if "kwargs" in nodes[key]:
                    raise SyntaxError("Using a python-like definition with separate kwargs is not allowed. "
                                      "Use one way or the other.")
                else:
                    nodes[key]["function"], nodes[key]["args"], nodes[key]["kwargs"] = self._split_func_and_args(
                        nodes[key]["function"])
            else:
                nodes[key]["args"] = []
        return nodes

    def _split_func_and_args(self, func_expression: str):
        # Split a string of the form "func_name(arg1, arg2,.., kwarg1=val1, kwarg2=val2,..)" into
        # func_name, [arg1, arg2,..], {kwarg1=val1, kwarg2=val2,..}
        func_expression = func_expression.replace(" ", "")
        inputs = func_expression[func_expression.find("(") + 1: func_expression.find(")")]
        first_kwarg_index = self._check_args_order(inputs)
        inputs = inputs.split(",")
        args = inputs[:first_kwarg_index]
        for arg_idx in range(len(args)):
            if args[arg_idx].startswith(("'", '"')):
                args[arg_idx] = args[arg_idx][1:-1]
            else:
                try:
                    args[arg_idx] = float(args[arg_idx])
                except (ValueError, TypeError):
                    pass
        inputs = inputs[first_kwarg_index:]
        kwargs = {}
        for kwarg in inputs:
            arg_name = kwarg[:kwarg.find("=")]
            kwargs[arg_name] = kwarg[kwarg.find("=") + 1:]
            if kwargs[arg_name].startswith(("'", '"')):
                kwargs[arg_name] = kwargs[arg_name][1:-1]
            else:
                try:
                    kwargs[arg_name] = float(kwargs[arg_name])
                except (ValueError, TypeError):
                    pass
        func_name = func_expression[:func_expression.find("(")]
        return func_name, args, kwargs

    def _check_args_order(self, all_args_str: str):
        # Check that no positional args come after kwargs
        all_args_str = all_args_str.split(",")
        first_kwarg_index = next((all_args_str.index(x) for x in all_args_str if "=" in x), None)
        if first_kwarg_index is not None:
            for kwargs in range(first_kwarg_index, len(all_args_str)):
                if "=" not in all_args_str[kwargs]:
                    raise RuntimeError("Positional argument after keyword argument")
        else:
            first_kwarg_index = len(all_args_str)
        return first_kwarg_index

    def _build_adj_matrix(self, nodes: dict):
        # TODO add a note to make sure that no string unintentionally has the same name as a node
        node_names = nodes.keys()
        parents_dict = {k: [v for v in (list(nodes[k]["kwargs"].values())+nodes[k]["args"]) if v in node_names] for k in node_names}
        # parents_dict = {**parents_dict, }
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
            nodes[key]["kwargs"] = {
                k: self.graph._get_node_by_name(v) if self.graph._get_node_by_name(v) is not None else v for k, v in
                nodes[key]["kwargs"].items()}

            nodes[key]["args"] = [
                self.graph._get_node_by_name(v) if self.graph._get_node_by_name(v) is not None else v for v in
                nodes[key]["args"]]

            node_type = nodes[key].get("type")
            if node_type is not None:
                nodes[key].pop("type")

            if node_type == "Node" or node_type is None:
                node = Node._build_object(**nodes[key])
                self.graph._add_node(node)

            elif node_type == "Selection":
                node = Selection._build_object(**nodes[key])
                self.graph._add_node(node)

            elif node_type == "Stratify":
                node = Stratify._build_object(**nodes[key])
                self.graph._add_node(node)

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
        # For functions not define in the python file, but rather coming from external libraries, such as numpy.
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
