from dagsim.baseDS import Graph, Generic, Selection
from scipy.stats import norm, bernoulli


def isEight(inp):
    return inp == 8

# def identity():
#     return 0.5


Prior = Generic(name="Prior1", function=norm.rvs, additional_params=[0.5, 0.1])
Node = Generic(name="Node1", function=bernoulli.rvs, parents=[Prior], additional_params=[7])
Selection = Selection(name="Selection", function=isEight, parents=[Node])

listNodes = [Prior, Node, Selection]
my_graph = Graph("Graph1", listNodes)
my_graph.draw()
n = my_graph.simulate(num_samples=20, csv_name="test")
print(n)
