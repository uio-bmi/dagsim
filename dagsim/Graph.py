import numpy as np
from typing import Union
from graphviz import Source
import pandas as pd
import igraph as ig
from dagsim.utils.processPlates import get_plate_dot
import time
import datetime
import copy
from dagsim.Node import Node
from dagsim.Missing import Missing
from dagsim.Selection import Selection
from dagsim.Stratify import Stratify


class Graph:
    def __init__(self, list_nodes, name="Graph", plates_reps: dict = None):
        self._check_args(list_nodes)
        self.name = name
        self.nodes = list_nodes  # [None] * num_nodes
        self.plates = {}
        self.adj_mat = pd.DataFrame()
        self.top_order = []
        self._update_topol_order()
        self._update_plate_embedding()
        self.folded_dot_str = self._generate_dot()
        if plates_reps is not None:
            self.unfolded_dot_str = ""
            self.unfold_graph(plates_reps)

    def unfold_graph(self, reps):
        removed_nodes = self._replicate_nodes(reps)  # When a node is replicated, the original one is removed
        # todo reserve _agg names if there are plates in the graph
        self._update_topol_order()
        self._update_nodes(removed_nodes)
        self._update_topol_order()
        self._update_plate_embedding()
        self.unfolded_dot_str = self._generate_dot()

    @staticmethod
    def _check_args(list_nodes):
        assert len([select for select in list_nodes if isinstance(select, Selection)]) <= 1, "A graph can have at " \
                                                                                             "most one Selection node. "
        assert len([strat for strat in list_nodes if isinstance(strat, Stratify)]) <= 1, "A graph can have at most " \
                                                                                         "one Stratify node. "

    def _get_nodes_to_aggregate(self):
        # Returns all the nodes that are in plates if their children are outside that plate.
        # This is used to check whether to aggregate the replications or not.
        nodes_to_aggregate = []
        for node in self.nodes:
            parents = node.parents
            for parent in parents:
                node_plates = set(node.plates)
                parent_plates = set(parent.plates)
                if not node_plates & parent_plates:
                    nodes_to_aggregate.append(parent)
        return nodes_to_aggregate

    def _replicate_nodes(self, plates_reps):
        # todo check if plates and not plate_reps
        # Replicates all the nodes found in plates based on plates_reps. Also set 'plates' to None on these nodes.
        parents_to_aggregate = self._get_nodes_to_aggregate()
        nodes_to_remove = []
        new_nodes = []
        for node in self.nodes:
            if node.plates:
                nodes_to_remove.append(node)
                node_replicas = [copy.deepcopy(node) for _ in range(plates_reps[node.plates[0]])]
                new_nodes.extend(node_replicas)
                for i in range(len(node_replicas)):
                    setattr(node_replicas[i], "name", node.name + f'_{i}_')
                if node in parents_to_aggregate:
                    new_nodes.append(
                        Node(name=f'{node.name}_agg', function=lambda *x: list(x), args=node_replicas, observed=False))
        self.nodes.extend(new_nodes)
        self.nodes = list(set(self.nodes) - set(nodes_to_remove))
        # deepcopy will copy the parent with the same name to different references, so checking for name solves it
        # copy updates all copies upon updating any of them, so keep the names instead:
        removed_nodes_names = [rmnode.name for rmnode in nodes_to_remove]
        return removed_nodes_names

    def __str__(self):
        main_str = ""
        for idx, node in enumerate(self.nodes):
            main_str += "Node " + str(idx + 1) + ":\n"
            main_str += node.__str__() + "\n"
        return main_str[:-1]

    def _update_plate_embedding(self):
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
        self.plates = plateDict

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
            if node is None:
                print(name, " not found")
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
        # todo reorder in chronological order after the topological one
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
        for node_idx in range(len(self)):
            if self[node_idx].visible:
                my_str = '"%s"' % self[node_idx].name
                my_str += " [shape=" + shape_dict[type(self[node_idx]).__name__] + "];\n"
                dot_str = dot_str + my_str

        # add the edges of both vertices are visible
        for parent_node in self.adj_mat:
            if self._get_node_by_name(parent_node).visible:
                for node_idx in self.adj_mat.loc[parent_node].index:
                    if self.adj_mat.loc[parent_node].loc[node_idx] == 1:
                        if self._get_node_by_name(node_idx).visible:
                            tmp_str = '"%s" -> "%s";\n' % (parent_node, node_idx)
                            dot_str += tmp_str

        # check if there are any plates defined in the graph
        if len(self.plates) > 1:
            dot_str += get_plate_dot(self.plates)
        dot_str += "}"
        return dot_str

    def draw(self, folded=True):
        dot_str = self.folded_dot_str if folded else self.unfolded_dot_str
        with open(self.name + "_DOT.txt", "w") as file:
            file.write(dot_str)

        s = Source(dot_str, filename=self.name, format="png")
        try:
            s.view(cleanup=True, quiet_view=True)
        except (TypeError, FileNotFoundError):
            from IPython.display import display
            s.render()
            display(Source(dot_str))

    def simulate(self, num_samples, csv_name="", output_path="./", selection=True, stratify=True, missing=True):

        tic = time.perf_counter()
        print(f"{datetime.datetime.now()}: Simulation started.", flush=True)
        output_dict = self._traverse_graph(num_samples, output_path, missing, True)

        selectionNode = self._get_selection()
        if selection:
            if selectionNode is not None:
                print(f"{datetime.datetime.now()}: Simulating selection bias.", flush=True)
                output_dict = self.nodes[selectionNode]._filter_output(output_dict=output_dict)
                while len(list(output_dict.values())[0]) < num_samples:
                    temp_output = self.nodes[selectionNode]._filter_output(
                        output_dict=self._traverse_graph(1, output_path, missing, False))
                    output_dict = {k: output_dict[k] + temp_output[k] for k in output_dict.keys()}

        output_dict = {k: v for k, v in output_dict.items() if self._get_node_by_name(k).observed}
        output_dict = self._prettify_output(output_dict)

        stratifyNode = self._get_stratify()
        if stratify:
            if stratifyNode is not None:
                print(f"{datetime.datetime.now()}: Stratifying the data.", flush=True)
                output_dict = self.nodes[stratifyNode]._filter_output(output_dict=output_dict)

        if csv_name:
            if csv_name.endswith(".csv"):
                csv_name = csv_name[:-4]
            if stratifyNode is not None:
                for key in output_dict.keys():
                    pd.DataFrame(output_dict[key]).to_csv(output_path + csv_name + '_' + key + '.csv', index=False)
            else:
                pd.DataFrame(output_dict).to_csv(output_path + csv_name + '.csv', index=False)

        toc = time.perf_counter()
        print(f"{datetime.datetime.now()}: Simulation finished in {toc - tic:0.4f} seconds.", flush=True)
        return output_dict

    def _traverse_graph(self, num_samples, output_path, missing, show_log):
        output_dict = {}
        for node_name in self.top_order:

            node = self._get_node_by_name(node_name)
            if show_log and (isinstance(node, Missing) or isinstance(node, Node)):
                print(f"{datetime.datetime.now()}: Simulating node \"{node.name}\".", flush=True)
            node._node_simulate(num_samples, output_path)
            if isinstance(node, Selection):
                assert all(isinstance(x, bool) for x in node.output), "The selection node's function should return " \
                                                                      "a boolean"
            elif isinstance(node, Missing) and missing:
                assert all(isinstance(x, bool) for x in node.index_node.output), "The index node's function should " \
                                                                                 "return a boolean"
                output_dict[node.name] = node.output
            elif isinstance(node, Stratify):
                assert all(isinstance(x, str) for x in node.output), "The stratification node's function should " \
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

    def _update_nodes(self, removed_nodes):
        # update the _constructors of the nodes to include the new parents
        for child_name in self.top_order:
            child = self._get_node_by_name(child_name)
            for parent in child.parents:
                usage = self.get_parent_usage(child, parent)
                if parent.name in removed_nodes:  # avoid modifying nodes in plates with parents not in a plate
                    if child.plates == parent.plates:  # todo change when you allow for nested plates
                        self._match_parents(child, parent, usage)
                    else:  # if child is in another plate, or not in a plate itfp
                        self._assign_parent_to_child(child, parent, usage)
                else:  #
                    if child.plates:
                        self._assign_parent_to_child(child, self._get_node_by_name(parent.name), usage, agg=0)
            child._args, child._kwargs = child._parse_func_arguments()
            child._update_parents()

    def get_parent_usage(self, child, parent):
        ind = child._constructor["args"].index(parent) if parent in child._constructor["args"] else None
        if ind is not None:
            tuple_usage = (ind, "arg")
        # assume each parent is used in one argument
        else:
            key = list(child._constructor["kwargs"].keys())[
                list(child._constructor["kwargs"].values()).index(parent)]
            tuple_usage = (key, "kwarg")
        assert tuple_usage is not None, f'{parent.name} is not a parent of {child.name}'
        return tuple_usage

    def _match_parents(self, child, parent, usage):
        replica_index = child.name.split("_")[-2]
        if usage[1] == "arg":
            child._constructor["args"][usage[0]] = self._get_node_by_name(f'{parent.name}_{replica_index}_')
        else:  # if in kwargs
            child._constructor["kwargs"][usage[0]] = self._get_node_by_name(f'{parent.name}_{replica_index}_')

    def _assign_parent_to_child(self, child, parent, usage, agg=1):
        parent_name = parent.name + "_agg" if agg else parent.name
        if usage[1] == "arg":
            child._constructor["args"][usage[0]] = self._get_node_by_name(parent_name)
        else:  # if in kwargs
            child._constructor["kwargs"][usage[0]] = self._get_node_by_name(parent_name)
