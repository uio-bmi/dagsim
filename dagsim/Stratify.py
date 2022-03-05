from dagsim.Node import _Node


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