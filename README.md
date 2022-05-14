# DagSim

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/uio-bmi/dagsim/main?labpath=tutorials%2Fhello_world.ipynb)

DagSim is a Python-based framework and specification language for simulating data based on a Directed Acyclic Graph (DAG)
structure, without any constraints on variable types or functional relations. A succinct YAML format for
defining the structure of the simulation model promotes transparency, while separate user-provided functions for
generating each variable based on its parents ensure the modularization of the simulation code.

## Installation

DagSim can be easily installed using pip.

### Installing DagSim using [pip](https://pypi.org/project/dagsim/)

To install the DagSim package using `pip`, run:

```bash
pip install dagsim
```

#### Quickstart

To check that DagSim is installed properly, run the following command in the console/terminal:

```bash
dagsim-quickstart
```

#### Installing graphviz

If you use `pip`, you need to install graphviz on the system level in order to use the drawing functionality in DagSim.
Please follow the instrcutions [here](https://graphviz.org/download/) on how to install graphviz depending on the
operating system.


[//]: # (### Installing DagSim using conda)

[//]: # (To install the DagSim package using `conda`, run:)

[//]: # (```bash)

[//]: # (conda install dagsim)

[//]: # (```)

[//]: # (With `conda`, graphviz is automatically installed, both, as a python package and at the system level.)

## Simple example

Suppose we are interested in simulating two variables, X and Y, where X follows a standard Gaussian distribution, and Y
is the square of X.

For each node we need a function to simulate the node's values:

- For X, we can use the `numpy.random.normal` function
- For Y, we can use either `numpy.power` or define our own function. We will use the second to illustrate how one can use
  user-define functions.

```python
# needed imports
import dagsim.base as ds
import numpy as np
```

Here, we define our own `square` function:

```python
def square(arg):
    return arg * arg
```

Then, we define the nodes in our graph/model by giving each node a name, the function to use in order to evaluate its
value, and the arguments of the function, if any:

```python
X = ds.Node(name="X", function=np.random.normal)
Y = ds.Node(name="Y", function=square, kwargs={"arg": X})
```

After that, we define the graph itself by giving it a name (optional) and a list of all the nodes to be included:

```python
graph = ds.Graph(name="demo_graph", list_nodes=[X, Y])
```

If you wish, you can draw the graph by calling the `draw` method, as follows:

```python
graph.draw()
```

Finally, we simulate data from this graph by calling the `simulate` method, and giving it the number of samples you
want to simulate, and a name for the csv_file (optional) where the data should be saved.

```python
data = graph.simulate(num_samples=10, csv_name="demo_data")
```

Here, `data` would be a dictionary with keys being the names of the nodes in the graph, and the corresponding values
being the simulated values for each node returned as a Python `list`.

For other simple examples, please refer to the `tutorials` folder.