from baseDS import Graph, Generic
import numpy as np
from sklearn.linear_model import LinearRegression as LinReg
import pandas as pd


# define the function of the ground truth
def ground_truth(x, size: int):
    # assert len(x) == size
    y = 2 * x + 1  # + np.random.normal(0, size=len(x))
    return y


# define a node for the input feature, and another node for the outcome of a linear regression model
Nodex = Generic(name="x", function=np.random.normal, vectorize="size")
Nodey = Generic(name="y", function=ground_truth, arguments={"x": Nodex}, vectorize="size")

# define a list of all nodes, then instantiate the graph
listNodes = [Nodex, Nodey]
my_graph = Graph("testVectorize", listNodes)

my_graph.draw()

# simulate data for training and testing, with different sample sizes and filenames
train = my_graph.simulate(num_samples=4, csv_name="train")

y = np.array(Nodey.output)
x = np.array(Nodex.output)

# z = y - 2 * x - 1
# print(x)
# print(y)
# print(z)

# 1 for i in num_:
#       genx()

# genx(num_)

# 1 for i in num_:
#       geny()

# geny()
