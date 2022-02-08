import dagsim.base as ds
import numpy as np


def square(arg):
    return arg * arg


def main():

    X = ds.Node(name="X", function=np.random.normal)
    Y = ds.Node(name="Y", function=square, kwargs={"arg": X})
    graph = ds.Graph(name="demo_graph", list_nodes=[X, Y])

    data = graph.simulate(num_samples=2)
    print("Simulated data", data)


if __name__ == "__main__":
    main()
