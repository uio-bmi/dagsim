from dagsim.Node import _Node


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
