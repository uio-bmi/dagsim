from baseDS import Graph, Generic, Selection
from scipy.stats import beta, binom


def add_if_diseased(base, signal, state):
    return base + (signal if state is True else 0)


def fas_wrapper(signal):
    return binom.rvs(100, signal)


X = Generic(name="X", function=binom.rvs, additional_params=[1, 0.5])
Y = Generic(name="Y", function=binom.rvs, additional_params=[1, 0.5])

listOfNodes = [X]
my_graph = Graph("yaml5", list_nodes=listOfNodes)
my_graph.draw()
n = my_graph.ml_simulation(num_samples=10, train_test_ratio=0.7, csv_prefix="try")
print(n)
