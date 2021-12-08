# DagSim

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/uio-bmi/dagsim/binder_check?filepath=hello_world.ipynb)

A framework and specification language for simulating data based on graphical models.

## Installation
DagSim can be installed directly using pip.

### Installing DagSim using pip
To install the DagSim package using `pip`, run:

```bash
pip install dagsim
```

#### Installing graphviz
If you use `pip`, you need to install graphviz on the system level in order to use the drawing functionality in DagSim. Please follow the instrcutions [here](https://graphviz.org/download/) on how to install graphviz depending on the 
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

- For X, we can use the numpy.random.normal function
- For Y, we can use either numpy.power or define our own function. We will use the second to show how you can use user-define functions.

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

Then, we define the nodes in our graph/model by giving each one a name, the function to use in order to evaluate its value, and the arguments of the function, if any:
```python
X = ds.Generic(name="X", function=np.random.normal)
Y = ds.Generic(name="Y", function=square, arguments={"arg": X})
```

After that, we define the graph by giving it a name and a list containing all the nodes to be included:
```python
graph = ds.Graph(name="demo_graph", list_nodes=[X, Y])
```

If you wish, you can draw the graph by calling the following function:
```python
graph.draw()
```

Finally, you can simulate data from the graph by calling the simulate method, and giving it the number of samples you want to simulate, and a name for the csv_file (optional) where the data should be saved
```python
data = graph.simulate(num_samples=10, csv_name="demo_data")
```

Here, `data` would be a dictionary with the keys being equal to the names of the nodes, and the corresponding values being the simulated values for each node.

For other examples, please refer to the `tutorials` folder.