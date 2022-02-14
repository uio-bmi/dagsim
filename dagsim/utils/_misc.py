def parse_string_args(nodes):
    # For each node, separate the function's name from its arguments, if not separated already
    for key in nodes.keys():
        nodes[key]["args"] = []
        if "kwargs" not in nodes[key]:
            nodes[key]["kwargs"] = {}

        if "(" in nodes[key]["function"]:
            if nodes[key]["kwargs"]:
                raise SyntaxError("Using a python-like definition with separate kwargs is not allowed. "
                                  "Use one way or the other.")
            elif "()" in nodes[key]["function"]:
                nodes[key]["function"] = nodes[key]["function"][:-2]
            else:
                nodes[key]["function"], nodes[key]["args"], nodes[key]["kwargs"] = split_func_and_args(
                    nodes[key]["function"])
    return nodes


def split_func_and_args(func_expression: str):
    # Split a string of the form "func_name(arg1, arg2,.., kwarg1=val1, kwarg2=val2,..)" into
    # func_name, [arg1, arg2,..], {kwarg1=val1, kwarg2=val2,..}
    func_expression = func_expression.replace(" ", "")
    inputs = func_expression[func_expression.find("(") + 1: func_expression.find(")")]
    first_kwarg_index = check_args_order(inputs)
    inputs = inputs.split(",")
    args = inputs[:first_kwarg_index]
    for arg_idx in range(len(args)):
        try:
            args[arg_idx] = float(args[arg_idx])
        except (ValueError, TypeError):
            pass
    inputs = inputs[first_kwarg_index:]
    kwargs = {}
    for kwarg in inputs:
        arg_name = kwarg[:kwarg.find("=")]
        kwargs[arg_name] = kwarg[kwarg.find("=") + 1:]
        try:
            kwargs[arg_name] = float(kwargs[arg_name])
        except (ValueError, TypeError):
            pass
    func_name = func_expression[:func_expression.find("(")]
    return func_name, args, kwargs


def check_args_order(all_args_str: str):
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
