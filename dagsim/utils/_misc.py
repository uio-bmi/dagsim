def parse_string_args(nodes):
    # For each node, separate the function's name from its arguments, if not separated already
    for key in nodes.keys():
        if "type" in nodes[key] and nodes[key]["type"] == "Missing":
            continue
        else:
            nodes[key] = check_node_syntax(nodes[key])
            if "type" not in nodes[key]:
                nodes[key]["type"] = "Node"
            nodes[key]["args"] = []
            if "kwargs" not in nodes[key]:
                nodes[key]["kwargs"] = {}

            if "(" in nodes[key]["function"]:
                if nodes[key]["kwargs"]:
                    raise SyntaxError(
                        "Using a python-like definition, i.e. with parantheses, with separate kwargs is not "
                        "allowed. Use one way or the other.")
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
        args[arg_idx] = get_number(args[arg_idx]) if is_numeric(args[arg_idx]) else args[arg_idx]
    inputs = inputs[first_kwarg_index:]
    kwargs = {}
    for kwarg in inputs:
        arg_name = kwarg[:kwarg.find("=")]
        kwargs[arg_name] = kwarg[kwarg.find("=") + 1:]
        kwargs[arg_name] = get_number(kwargs[arg_name]) if is_numeric(kwargs[arg_name]) else kwargs[arg_name]
    func_name = func_expression[:func_expression.find("(")]
    return func_name, args, kwargs


def get_number(string: str):
    num = float(string)
    if num == int(num):
        num = int(num)
    return num


def is_numeric(string: str):
    try:
        float(string)
        return True
    except ValueError:
        return False


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


def check_node_syntax(node):
    if not isinstance(node, dict):
        assert isinstance(node, str), "One line definitions should contain the function definition itself."
        node_dict = {"function": node}
        return node_dict
    else:
        return node
