from dagsim.base import Graph, Generic, Selection
from scipy.stats import norm, binom


def is_eight(inp):
    return inp == 8


# def identity():
#     return 0.5

def binom_wrapper(prob, trials):
    return binom.rvs(n=trials, p=prob)


Prior = Generic(name="Prior1", function=norm.rvs, additional_params=[0.5, 0.1])
Node = Generic(name="Node1", function=binom_wrapper, parents=[Prior], additional_params=[10])
Selection = Selection(name="Selection", function=is_eight, parents=[Node])

listNodes = [Prior, Node, Selection]
my_graph = Graph("Graph1", listNodes)
my_graph.draw()
n = my_graph.simulate(num_samples=50, csv_name="test")
print(n)
