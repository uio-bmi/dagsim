from dagsim.Node import _Node, Node


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
