from inspect import getfullargspec


class _Node:
    def __init__(self, name: str, function, plates=None, observed=True, args: list = None, kwargs: dict = None,
                 size_field=None, visible=True):
        if kwargs is None:
            kwargs = {}
        if args is None:
            args = []
        if plates is None:
            plates = []
        self.name = name
        self._constructor = {"args": args, "kwargs": kwargs}
        self._args, self._kwargs = self._parse_func_arguments()
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
        self.parents = list(set([v for v in self._constructor["args"] if isinstance(v, Node)] + list(
            v for v in self._constructor["kwargs"].values() if isinstance(v, Node))))


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
