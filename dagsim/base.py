import numpy as np
from typing import Union
from graphviz import Source
import pandas as pd
import igraph as ig
from dagsim.utils.processPlates import get_plate_dot
import time
from inspect import getfullargspec
import datetime
import copy


class _Node:
    def __init__(self, name: str, function, plates=None, observed=True, args=None, kwargs=None, size_field=None,
                 visible=True):
        if kwargs is None:
            kwargs = {}
        if args is None:
            args = []
        if plates is None:
            plates = []
        self._constructor = {"args": args, "kwargs": kwargs}
        self._args, self._kwargs = self._parse_func_arguments()
        self.name = name
        self.parents = []
        self._update_parents()
        self.function = function
        self.output = None
        self.observed = observed
        self.visible = visible
        self.plates = plates
        self.size_field = size_field

    def _parse_func_arguments(self):
        args, kwargs = self._constructor.values()
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

    def _update_parents(self):
        # print(f'before update: parents: {[par.name for par in self.parents]}')
        print(f'before update: parents: {[par.name for par in self.parents]}')
        self.parents = list(set([v for v in self._constructor["args"] if isinstance(v, Node)] + list(
            v for v in self._constructor["kwargs"].values() if isinstance(v, Node))))
        # print(f'after update: parents: {[par.name for par in self.parents]}')
        print(f'after  update: parents: {[par.name for par in self.parents]}')


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
    def __init__(self, name: str, function, args=None, kwargs=None, visible=True):
        super().__init__(name=name, function=function, args=args, kwargs=kwargs, visible=visible)

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
    def __init__(self, name: str, function, args=None, kwargs=None, visible=True):
        super().__init__(name=name, function=function, args=args, kwargs=kwargs, visible=visible)

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
    def __init__(self, name: str, underlying_value: Node, index_node: Node, visible=True):
        super().__init__(name=name, function=self._node_simulate, visible=visible)
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

    def _node_simulate(self, *args):
        index_output = self.index_node.output
        output = [x if not y else 'NaN' for x, y in zip(self.underlying_value.output, index_output)]
        self.output = output


class Graph:
    def __init__(self, list_nodes, name="Graph"):
        self._check_args(list_nodes)
        self.name = name
        self.nodes = list_nodes  # [None] * num_nodes
        self.plates = {}
        self.plates_reps = {"1": 3}  # replication of each node
        # self._update_plate_embedding()
        self.adj_mat = pd.DataFrame()
        self.top_order = []
        self._update_topol_order()
        # self.draw()
        # time.sleep(2)
        # self.draw()
        # print("before build\n", [node.name for node in self.nodes])
        print("before build\n", self)
        self.removed_nodes = self._replicate_nodes()  # When a node in a plate is replicated, the original one is removed
        # todo reserve _agg names if there are plates in the graph
        # self._update_parents()
        print("after replication\n", self, "\n---")
        # print("after build\n", [node.name for node in self.nodes], "---\n")
        self._update_topol_order()
        self._update_plate_embedding()
        self._update_nodes()
        print("after build\n", self, "\n---")
        # print("after update top_order\n", self)
        # print("all nodes ", [node for node in self.nodes])
        # print("before update")
        # for node in self.nodes:
        #     print([arg for arg in node._constructor["args"]])
        # self._update_nodes()
        # print("after update")
        # for node in self.nodes:
        #     print(node.name, [arg for arg in node._constructor["args"]])
        # self._update_topol_order()
        print(self.top_order)
        self.draw()

    @staticmethod
    def _check_args(list_nodes):
        assert len([select for select in list_nodes if isinstance(select, Selection)]) <= 1, "A graph can have at " \
                                                                                             "most one Selection node. "
        assert len([strat for strat in list_nodes if isinstance(strat, Stratify)]) <= 1, "A graph can have at most " \
                                                                                         "one Stratify node. "

    def _build_graph_old(self):
        plates_reps = {"n1": 3, "n2": 4}  # replication of each node

        nodes_to_remove = []
        for node_name in self.top_order:
            print("Configuring node ", node_name)
            # remember to remove the original node
            node = self._get_node_by_name(node_name)
            if node.plates:
                # todo change to not necessarily in the same plate, and place it outside the if statement
                parents_in_same_plate = [parent for parent in node.parents if parent.plates == node.plates]
                # node_replication = [node] * plates_reps[node.name]
                # node_replication = [node for _ in range(plates_reps[node.name])]
                new_nodes = [copy.copy(node) for _ in range(self.plates_reps[node.name])]
                for i in range(len(new_nodes)):
                    setattr(new_nodes[i], "name", node.name + f'_{i}')
                for parent in parents_in_same_plate:
                    print("Name of parent ", parent.name)
                    print("Current node ", node._constructor)
                    # todo the case where the node is not a parent
                    ind = node._constructor["args"].index(parent) if parent in node._constructor["args"] else None
                    if ind:
                        for replica_index in range(len(new_nodes)):
                            setattr(new_nodes[replica_index], node._constructor["args"][ind],
                                    self._get_node_by_name(parent.name + f'_{replica_index}'))
                        # assume each parent is used in one argument
                    else:
                        key = list(node._constructor["kwargs"].keys())[
                            list(node._constructor["kwargs"].values()).index(parent)]
                        for replica_index in new_nodes:
                            setattr(new_nodes[replica_index], node._constructor["kwargs"][key],
                                    self._get_node_by_name(parent.name + f'_{replica_index}'))
                self.nodes.extend(new_nodes)
            else:
                parents_in_plates = [parent for parent in node.parents if parent.plates]
                for parent in parents_in_plates:
                    # Node(name=parent.name + "_agg_", function=lambda x: [val for sublist in x for val in sublist],
                    self.nodes.extend([Node(name=parent.name + "_agg_", function=lambda x: x,
                                            args=[self._get_node_by_name(parent.name + f'_{replica_index}') for
                                                  replica_index
                                                  in range(plates_reps[parent.name])])])

                    ind = node._constructor["args"].index(parent) if parent in node._constructor["args"] else None
                    node_replication = plates_reps[parent.name]
                    if ind is not None:
                        node._constructor["args"][ind] = self._get_node_by_name(parent.name + "_agg_")
                    # assume each parent is used in one argument
                    else:
                        key = list(node._constructor["kwargs"].keys())[
                            list(node._constructor["kwargs"].values()).index(parent)]
                        node._constructor["kwargs"][key] = self._get_node_by_name(parent.name + "_agg_")

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

    def _replicate_nodes(self):
        # Replicates all the nodes found in plates based on plates_reps. Also set 'plates' to None on these nodes.
        parents_to_aggregate = self._get_nodes_to_aggregate()
        print("Nodes to aggregate ", [n.name for n in parents_to_aggregate])
        nodes_to_remove = []
        new_nodes = []
        for node in self.nodes:
            print("Configuring node ", node.name)
            if node.plates:
                nodes_to_remove.append(node)
                node_replicas = [copy.deepcopy(node) for _ in range(self.plates_reps[node.plates[0]])]
                new_nodes.extend(node_replicas)
                for i in range(len(node_replicas)):
                    setattr(node_replicas[i], "name", node.name + f'_{i}_')
                    # todo check if necessary
                    # setattr(node_replicas[i], "plates", None)
                if node in parents_to_aggregate:
                    new_nodes.append(Node(name=f'{node.name}_agg', function=lambda x: x, args=node_replicas))
                    print(f'aggregated {node.name}')
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

    def _update_nodes2(self):
        for child_name in self.top_order:
            child = self._get_node_by_name(child_name)
            for parent in child.parents:
                if parent in self.removed_nodes:  # this avoids modifying nodes in plates with parents not in a plate
                    if child.plates == parent.plates:  # todo change when you allow for nested plates
                        # for replica in range(self.plates_reps[child.plates[0]]):
                        replica = child_name.rfind("_", 0, child_name.rfind("_"))
                        # child_replica_name = child_name[:idx+1] + str(replica) + "_"
                        # print(child_replica_name)
                        # child_replica_name = child_name.split("_")[-2]
                        child_replica = self._get_node_by_name(child.name + f'_{replica}_')
                        setattr(child_replica, "plates", None)
                        ind = child._constructor["args"].index(parent) if parent in child._constructor[
                            "args"] else None
                        if ind is not None:
                            child_replica._constructor["args"][ind] = self._get_node_by_name(
                                parent.name + f'_{replica}_')
                        # assume each parent is used in one argument
                        else:
                            key = list(child._constructor["kwargs"].keys())[
                                list(child._constructor["kwargs"].values()).index(parent)]
                            child_replica._constructor["kwargs"][key] = self._get_node_by_name(
                                parent.name + f'_{replica}_')
                        # setattr(child_replica, "parent", self._get_node_by_name(parent.name + f'_{replica}_'))
                    elif child.plates is None:  # whether they are in different plates or the child is not in a plate
                        ind = child._constructor["args"].index(parent) if parent in child._constructor[
                            "args"] else None
                        if ind is not None:
                            child._constructor["args"][ind] = self._get_node_by_name(parent.name + "_agg")
                        # assume each parent is used in one argument
                        else:
                            key = list(child._constructor["kwargs"].keys())[
                                list(child._constructor["kwargs"].values()).index(parent)]
                            child._constructor["kwargs"][key] = self._get_node_by_name(parent.name + "_agg")
                        # setattr(child_replica, "parent", self._get_node_by_name(parent.name + f'_{replica}_'))

            child._parse_func_arguments()
            child._update_parents()

    def _update_nodes(self):
        # update the _constructors of the nodes to include the new parents
        for child_name in self.top_order:
            print(f'{child_name} started')
            child = self._get_node_by_name(child_name)
            for parent in child.parents:
                if parent.name in self.removed_nodes:  # this avoids modifying nodes in plates with parents not in a plate
                    usage = self.get_parent_usage(child, parent)
                    # print(f'child: {child.name}; parent: {parent.name}')
                    # print(f'parent\'s plates: {parent.plates}; child\'s plates: {child.plates}')
                    if child.plates == parent.plates:  # todo change when you allow for nested plates
                        self._match_parents(child, parent, usage)
                    # elif not child.plates or :
                    else:  # if child is in another plate, or not in a plate itfp
                        self._assign_parent_to_child(child, parent, usage)
                    setattr(child, "plates", [])
                    # todo check for other conditions
            print(f'{child_name} passed')
            child._parse_func_arguments()
            child._update_parents()

    def get_parent_usage(self, child, parent):
        print(f'looking for {parent.name}: parent of {child.name}')
        print(f'parents of {child.name} are {[(par, par.name) for par in child.parents]}')
        print(f'args of {child.name} are {[(arg, arg.name) for arg in child._constructor["args"]]}')
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
            print(f'matching {parent.name} for {child.name}: args: {[arg.name for arg in child._constructor["args"]]}')
        else:  # if in kwargs
            child._constructor["kwargs"][usage[0]] = self._get_node_by_name(f'{parent.name}_{replica_index}_')

    def _assign_parent_to_child(self, child, parent, usage):
        if usage[1] == "arg":
            child._constructor["args"][usage[0]] = self._get_node_by_name(parent.name + "_agg")
        else:  # if in kwargs
            child._constructor["kwargs"][usage[0]] = self._get_node_by_name(parent.name + "_agg")
