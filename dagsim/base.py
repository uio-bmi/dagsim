import numpy as np
from typing import Union
from graphviz import Source
import pandas as pd
import igraph as ig
from dagsim.utils.processPlates import get_plate_dot
import time
from inspect import getfullargspec


class _Node:
    def __init__(self, name: str, function, plates=None, observed=True, args=None, kwargs=None, size_field=None,
                 visible=True):
        if kwargs is None:
            kwargs = {}
        if args is None:
            args = []
        self._args, self._kwargs = self._parse_func_arguments(args, kwargs)
        self.name = name
        self.parents = list(set([v for v in args if isinstance(v, Node)] + list(
            v for v in kwargs.values() if isinstance(v, Node))))
        self.function = function
        self.output = None
        self.observed = observed
        self.visible = visible
        self.plates = plates
        self.size_field = size_field

    def _parse_func_arguments(self, args, kwargs):
        args = [
            (lambda x: (lambda index: x.output[index]))(a) if isinstance(a, Node) else (lambda x: (lambda index: x))(
                a) for a in args]
        kwargs = dict(
            [(k, (lambda x: (lambda index: x.output[index]))(v)) if isinstance(v, Node) else (
                k, (lambda x: (lambda index: x))(v)) for k, v in kwargs.items()])
        return args, kwargs

    def _get_func_args(self, index):
        return [a(index) for a in self._args]

    def _get_func_kwrgs(self, index, output_path):
        d = dict([(k, v(index)) for k, v in self._kwargs.items()])
        try:  # This would throw a TypeError in case the function is ufunc
            if "output_path" in getfullargspec(self.function).args:
                d["output_path"] = output_path
        except TypeError:
            pass
        return d

    def __str__(self):
        main_str = ""
        main_str += "\tname: " + self.name + "\n"
        main_str += "\ttype: " + self.__class__.__name__ + "\n"
        main_str += "\tfunction: " + self.function.__name__ + "\n"
        if self.parents:
            main_str += "\tparents: " + ", ".join([par.name for par in self.parents]) + "\n"
        else:
            main_str += "\tparents: None"
        return main_str

    def _forward(self, idx, output_path):
        return self.function(*self._get_func_args(idx), **self._get_func_kwrgs(idx, output_path))

    def _node_simulate(self, num_samples, output_path):
        if self.size_field is None:
            self.output = [self._forward(i, output_path) for i in range(num_samples)]
        else:
            self.output = self._vectorize_forward(num_samples, output_path)

    def _vectorize_forward(self, size, output_path):
        #  Args and KwArgs would be used once. Index just for convenience
        return self.function(*self._get_func_args(0), **self._get_func_kwrgs(0, output_path),
                             **{self.size_field: size})  # .tolist()

    def __len__(self):
        return len(self.parents)


class Node(_Node):
    def __init__(self, name: str, function, args=None, kwargs=None, plates=None, size_field=None, observed=True,
                 visible=True,
                 handle_multi_cols=False, handle_multi_return=None):
        super().__init__(name=name, function=function, args=args, kwargs=kwargs,
                         plates=plates, observed=observed, visible=visible, size_field=size_field)
        self.handle_multi_cols = handle_multi_cols
        self.handle_multi_return = handle_multi_return

    @staticmethod
    def _build_object(**kwargs):
        # check params
        generic = Node(**kwargs)
        return generic


class Selection(_Node):
    def __init__(self, name: str, function, args=None, kwargs=None):
        super().__init__(name=name, function=function, args=args, kwargs=kwargs)

    @staticmethod
    def _build_object(**kwargs):
        # check params
        selection = Selection(**kwargs)
        return selection

    def _filter_output(self, output_dict):
        for key, value in output_dict.items():
            output_dict[key] = [value[i] for i in range(len(value)) if self.output[i]]
        return output_dict


class Stratify(_Node):
    def __init__(self, name: str, function, args=None, kwargs=None):
        super().__init__(name=name, function=function, args=args, kwargs=kwargs)

    @staticmethod
    def _build_object(**kwargs):
        # check params
        stratify = Stratify(**kwargs)
        return stratify

    def _filter_output(self, output_dict):
        node_names = output_dict.keys()
        strata = list(set(self.output))
        # A dictionary of dictionaries. Outer dictionary with keys=strata, and inner dictionaries with keys=node_names
        new_dict = {key: {node: [] for node in node_names} for key in strata}

        for i, stratum in enumerate(self.output):
            for k, v in output_dict.items():
                new_dict[stratum][k].append(v[i])

        return new_dict


class Missing(_Node):
    def __init__(self, name: str, underlying_value: Node, index_node: Node):
        super().__init__(name=name, function=self._filter_output)
        self.underlying_value = underlying_value
        self.parents = [underlying_value, index_node]
        self.index_node = index_node
        self.handle_multi_cols = underlying_value.handle_multi_cols
        self.handle_multi_return = underlying_value.handle_multi_return

    @staticmethod
    def _build_object(**kwargs):
        # check params
        missing = Missing(**kwargs)
        return missing

    def _filter_output(self):
        index_output = self.index_node.output
        output = [x if y == 1 else 'NaN' for x, y in zip(self.underlying_value.output, index_output)]
        self.output = output


class Graph:
    def __init__(self, name, list_nodes):
        self.name = name
        self.nodes = list_nodes  # [None] * num_nodes
        self.adj_mat = pd.DataFrame()
        self.plates = self._plate_embedding()
        self.top_order = []
        self._update_topol_order()

    def __str__(self):
        main_str = ""
        for idx, node in enumerate(self.nodes):
            main_str += "_Node " + str(idx + 1) + ":\n"
            main_str += node.__str__() + "\n"
        return main_str[:-1]

    def _plate_embedding(self):
        def get_key_by_label(label):
            for key in plateDict.keys():
                if plateDict[key][0] == label:
                    return key

        plateDict = {0: (None, [])}
        idx = 1
        labels = []
        for node in self.nodes:
            if node.plates:
                for label in node.plates:
                    if label not in labels:
                        plateDict[idx] = (label, [])
                        labels.append(label)
                        idx += 1
                    plateDict[get_key_by_label(label)][1].append(node.name)
            else:
                plateDict[0][1].append(node.name)
        return plateDict

    def _add_node(self, node: Union[Node, Selection, Stratify, Missing]):
        if node not in self.nodes:
            self.nodes.append(node)
        # update the topological order whenever a new node is added
        self._update_topol_order()

    def _get_selection(self):
        # todo change to missing way
        check_for_selection = next((item for item in self.nodes if item.__class__.__name__ == "Selection"), None)
        if check_for_selection is not None:
            return self.nodes.index(check_for_selection)
        else:
            return None

    def _get_stratify(self):
        check_for_stratify = next((item for item in self.nodes if item.__class__.__name__ == "Stratify"), None)
        if check_for_stratify is not None:
            return self.nodes.index(check_for_stratify)
        else:
            return None

    def _get_missing(self):
        check_for_missing = [item for item in self.nodes if item.__class__.__name__ == "Missing"]
        return check_for_missing if check_for_missing else None

    def _get_node_by_name(self, name: str):
        if not isinstance(name, str):
            return None
        else:
            node = next((item for item in self.nodes if item.name == name), None)
            return node

    def _update_adj_mat(self):
        nodes_names = [node.name for node in self.nodes]
        matrix = pd.DataFrame(data=np.zeros([len(self.nodes), len(self.nodes)]), dtype=int,
                              columns=nodes_names,
                              index=nodes_names)
        for node in self.nodes:
            if node.parents is not None:
                for parent in node.parents:
                    matrix[node.name][parent.name] = 1
        self.adj_mat = matrix

    def _update_topol_order(self):
        self._update_adj_mat()
        G = ig.Graph.Weighted_Adjacency(self.adj_mat.to_numpy().tolist())
        top_order = G.topological_sorting()
        top_order = [list(self.adj_mat.columns)[i] for i in top_order]
        self.top_order = top_order

    def __getitem__(self, item):
        return self.nodes[item]

    def __len__(self):
        return len(self.nodes)

    def _generate_dot(self):

        shape_dict = {'Node': "ellipse", 'Selection': "doublecircle", 'Stratify': "doubleoctagon",
                      "Missing": "Mcircle"}
        dot_str = 'digraph G{\n'
        # add the visible nodes
        for child_node in range(len(self)):
            if self[child_node].visible:
                my_str = self[child_node].name + " [shape=" + shape_dict[type(self[child_node]).__name__] + "];\n"
                dot_str = dot_str + my_str

        # add the edges of both vertices are visible
        for parent_node in self.adj_mat:
            if self._get_node_by_name(parent_node).visible:
                for child_node in self.adj_mat.loc[parent_node].index:
                    if self.adj_mat.loc[parent_node].loc[child_node] == 1:
                        if self._get_node_by_name(child_node).visible:
                            tmp_str = parent_node + "->" + child_node + ";\n"
                            dot_str += tmp_str

        # check if there are any plates defined in the graph
        if len(self.plates) > 1:
            dot_str += get_plate_dot(self.plates)
        dot_str += "}"
        return dot_str

    def draw(self):
        dot_str = self._generate_dot()
        with open(self.name + "_DOT.txt", "w") as file:
            file.write(dot_str)

        s = Source(dot_str, filename=self.name, format="png")
        try:
            s.view(cleanup=True, quiet_view=True)
        except (TypeError, FileNotFoundError):
            from IPython.display import display
            s.render()
            display(Source(dot_str))

    def simulate(self, num_samples, output_path="./", selection=True, stratify=True, missing=True, csv_name=""):

        tic = time.perf_counter()
        print("Simulation started")
        output_dict = self._traverse_graph(num_samples, output_path, missing)

        selectionNode = self._get_selection()
        if selection:
            if selectionNode is not None:
                output_dict = self.nodes[selectionNode]._filter_output(output_dict=output_dict)
                while len(list(output_dict.values())[0]) < num_samples:
                    temp_output = self.nodes[selectionNode]._filter_output(output_dict=self._traverse_graph(1, output_path, missing))
                    output_dict = {k: output_dict[k] + temp_output[k] for k in output_dict.keys()}

        output_dict = {k: v for k, v in output_dict.items() if self._get_node_by_name(k).observed}
        output_dict = self._prettify_output(output_dict)

        stratifyNode = self._get_stratify()
        if stratify:
            if stratifyNode is not None:
                output_dict = self.nodes[stratifyNode]._filter_output(output_dict=output_dict)

        if csv_name:
            if stratifyNode is not None:
                for key in output_dict.keys():
                    pd.DataFrame(output_dict[key]).to_csv(output_path + csv_name + '_' + key + '.csv', index=False)
            else:
                pd.DataFrame(output_dict).to_csv(output_path + csv_name + '.csv', index=False)

        toc = time.perf_counter()
        print(f"Simulation finished in {toc - tic:0.4f} seconds")
        return output_dict

    def _traverse_graph(self, num_samples, output_path, missing):
        output_dict = {}
        for node_name in self.top_order:
            node = self._get_node_by_name(node_name)
            if node.__class__.__name__ == "Missing" and missing:
                node._filter_output()
            else:
                node._node_simulate(num_samples, output_path)
            if node.__class__.__name__ == "Selection":
                assert all(isinstance(x, bool) for x in node.output), "The selection node function should return " \
                                                                      "a boolean"
            elif node.__class__.__name__ == "Stratify":
                assert all(isinstance(x, str) for x in node.output), "The stratification node function should " \
                                                                     "return a string"
            else:
                output_dict[node.name] = node.output
        return output_dict
    
    def _prettify_output(self, output_dict: dict):
        keys_to_remove = []
        for key in output_dict:
            node = self._get_node_by_name(key)
            # check if subscriptible
            if node.handle_multi_cols:
                node_output = output_dict[key]
                keys_to_remove.append(key)
                try:
                    unfolded_output = self._vec2dict(key, node_output)
                    output_dict = {**output_dict, **unfolded_output}
                except IndexError:
                    raise RuntimeError("All vectors returned by " + node.function.__name__ + " must be of the same "
                                                                                             "length")
                except TypeError:
                    raise RuntimeError("The output of " + node.function.__name__ + " either is not subscriptable "
                                                                                   "or has no __len__ method")
            elif node.handle_multi_return is not None:
                output_dict[key] = [node.handle_multi_return(elem) for elem in node.output]
        for key in keys_to_remove:
            output_dict.pop(key)

        return output_dict
    
    @staticmethod
    def _vec2dict(key: str, node_output):
        num_reps = len(node_output[0])
        node_dict = {key + "_" + str(rep): [] for rep in range(num_reps)}
        for sample in range(len(node_output)):
            for rep in range(num_reps):
                node_dict[key + "_" + str(rep)].append(node_output[sample][rep])
        return node_dict

    def ml_simulation(self, num_samples, train_test_ratio, stratify=False, include_external=False, csv_prefix=""):
        if csv_prefix:
            csv_prefix = csv_prefix + "_"
        num_tr_samples = int(num_samples * train_test_ratio)
        num_te_samples = num_samples - num_tr_samples
        train_dict = self.simulate(num_samples=num_tr_samples, stratify=stratify, csv_name=csv_prefix + "train")
        test_dict = self.simulate(num_samples=num_te_samples, stratify=stratify, csv_name=csv_prefix + "test")
        output = [train_dict, test_dict]
        if include_external:
            exter_dict = self.simulate(num_samples=num_te_samples, stratify=stratify, selection=False,
                                       csv_name=csv_prefix + "external")
            output.append(exter_dict)
        return output
