import numpy as np
import igraph as ig
from numpy import genfromtxt


def from_matrix(weight_matrix: np.ndarray, sem_type: str = "gauss", script_name: str = "script"):
    def create_function(name, weight_vector, sem_type):
        non_zero_indices = [i for i, e in enumerate(weight_vector) if e != 0]
        parents_names = ", ".join(["x" + str(i) for i in non_zero_indices])
        linear_equation = " + ".join(
            [str(weight_vector[e]) + " * x" + str(non_zero_indices[i]) for i, e in enumerate(non_zero_indices)])
        func_str = "def func_" + name + "(" + parents_names + "):\n\t" + name + " = "
        if sem_type not in ["logistic", "poisson"]:
            func_str += linear_equation + " + "
            if sem_type == "gauss":
                func_str += "np.random.normal(loc=0, scale=1)"
            elif sem_type == 'exp':
                func_str += "np.random.exponential(loc=0, scale=1)"
            elif sem_type == 'gumbel':
                func_str += "np.random.gumbel(loc=0, scale=1)"
            elif sem_type == 'uniform':
                func_str += "np.random.uniform(low=-1, high=1)"
        elif sem_type == 'logistic':
            func_str += "np.random.binomial(1, sigmoid(" + linear_equation + ")) * 1.0"
        elif sem_type == 'poisson':
            func_str += "np.random.poisson(1, np.exp(" + linear_equation + ")) * 1.0"
        else:
            raise ValueError('unknown sem type')
        func_str += "\n\treturn " + name

        return func_str

    def create_node(name: str, parents: list = None):
        # args_str = {"x" + str(i): "Node_x" + str(i) for i in parents}
        node_def = "Node_" + name + " = ds.Node(name='" + name + "', function="
        if parents:
            arg_string = "{"
            for i in parents:
                arg_string += "'x" + str(i) + "': Node_" + "x" + str(i) + ", "
            arg_string = arg_string[:-2] + "}"
            node_def += "func_" + name + ", kwargs=" + arg_string + ")"
        else:
            node_def += "np.random.normal, kwargs={'loc': 0, 'scale': 1})"
        return node_def

    assert weight_matrix.shape[0] == weight_matrix.shape[1], "The weight matrix should be a square matrix"

    G = ig.Graph.Weighted_Adjacency(weight_matrix.tolist())
    top_order = G.topological_sorting()

    imports = "import dagsim.base as ds \n" \
              "import numpy as np \n"

    if sem_type == "logistic":
        imports += "from scipy.special import expit as sigmoid\n"

    imports += "\n\n"

    functions = ""
    for index, column in enumerate(weight_matrix.T):
        if any(column):
            functions += create_function("x" + str(index), column, sem_type)
            functions += "\n\n\n"

    nodes = ""
    for node_index in top_order:
        if any(weight_matrix.T[node_index]):
            non_zero_indices = [i for i, e in enumerate(weight_matrix.T[node_index]) if e != 0]
            nodes += create_node("x" + str(node_index), non_zero_indices)
            nodes += "\n"
        else:
            nodes += create_node("x" + str(node_index))
            nodes += "\n"

    graph_def = "\nlistNodes = ["
    for node_index in top_order:
        graph_def += "Node_x" + str(node_index) + ", "
    graph_def = graph_def[:-2] + "]\n"
    graph_def += "graph = ds.Graph('myGraph', listNodes) \n"

    script = imports + functions + nodes + graph_def
    with open(script_name + ".py", "w") as file:
        file.write(script)


def from_csv(file_name: str, sem_type: str, script_name: str):
    weight_matrix = genfromtxt(file_name+".csv")
    from_matrix(weight_matrix, sem_type=sem_type, script_name=script_name)


if __name__ == "__main__":
    matrix_example = np.array([[0, 0, 2, 1], [0, 0, 3, 0], [0, 0, 0, 1], [0, 0, 0, 0]])

    from_matrix(matrix_example, sem_type="logistic", script_name="gaussDagSim")
