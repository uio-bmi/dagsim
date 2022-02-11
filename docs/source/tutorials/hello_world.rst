Simulate data from a simple model
=========================================================================

In this tutorial, you will learn how to build a simple DAG using DagSim for generating data, using either python code or a YAML configuration. If you are not familiar with the workflow of DagSim, see :ref:`How to specify a simulation`.


Define the simulation using python code
---------------------------------------
To run this tutorial on binder, click on this badge:

.. image:: https://mybinder.org/badge_logo.svg
 :target: https://mybinder.org/v2/gh/uio-bmi/dagsim/HEAD?labpath=https%3A%2F%2Fgithub.com%2Fuio-bmi%2Fdagsim%2Fblob%2Fmain%2Ftutorials%2Fhello_world.ipynb

We begin by importing the following:

.. highlight:: python
.. code-block:: python

  import dagsim.base as ds
  import numpy as np

1. **Defining the functions:**

The first thing that we need to define is the functions that relate the nodes to each other. In our example, we need one function for simulating the value of the feature :math:`x` and another function to specify the true relation between :math:`x` and the output :math:`y`. 

For simplicity, we will simulate X to follow a standard normal distribution,  Y to follow a normal distribution with :math:`loc=1` and :math:`scale=2`, :math:`Z` will be the sum of :math:`X` and :math:`Y`, and W will be the square of :math:`Y` plus a constant.
For :math:`X` and :math:`Y` we can use the :math:`np.random.normal` function from :math:`numpy`, and for the remaining nodes we define two functions:

.. highlight:: python
.. code-block:: python

    def add(x, y):
        return x + y

    def square_plus_constant(z, constant):
        return np.square(z) + constant
    
These functions would inform DagSim how to simulate the values of :math:`Z` and :math:`W` based on the values of their parents.

2. **Defining the graph:**

Since X uses the default arguments of the :math:`np.random.normal` function, we don't provide any arguments for the function, only the name of the node and the function itself.
For the nodes :math:`Y`, :math:`Z` and :math:`W`, we need to give each a name, the function to evaluate, and the values of the arguments of the corresponding function. These arguments can be either keyword arguments in the form of a dictionary with keys as arguments' names and values as arguments' values, arguments provided in the form of a list of the arguments, or a combination of both.

.. highlight:: python
.. code-block:: python

    X = ds.Node(name="X", function=np.random.normal)
    Y = ds.Node(name="Y", function=np.random.normal, kwargs={"loc": 1, "scale": 2})
    Z = ds.Node(name="Z", function=add, kwargs={"x": X, "y": Y})
    W = ds.Node(name="W", function=square_plus_constant, args=[Z], kwargs={"constant": 2})
  
At this stage, we can simply compile the graph as follows:

    
.. highlight:: python
.. code-block:: python

  listNodes = [X, Y, Z, W]
  my_graph = ds.Graph(listNodes, "Graph1")
  
Once we have compiled the graph, we can draw it to get a graphical representation of the underlying model:

.. highlight:: python
.. code-block:: python

  my_graph.draw()

.. figure:: ../_static/images/tutorials/hello_world.png
    :align: center

3. **Running the simulation:**

Now that we have defined everything we need, we simulate the data by calling the :code:`simulate` method and providing the number of samples and the name of the CSV file to which to save the data. We will run two simulations using the same model, one for training data and another for testing data.

.. highlight:: python
.. code-block:: python

  data = my_graph.simulate(num_samples=100, csv_name="hello_world")


Define the simulation using a YAML file
---------------------------------------
To run this tutorial on binder, click on this badge:

.. image:: https://mybinder.org/badge_logo.svg
 :target: https://mybinder.org/v2/gh/uio-bmi/dagsim/HEAD?labpath=tutorials%2FParser.ipynb

Here, hello_world_functions is a python (.py) file containing the user-defined functions that we need in our simulation, in our case a file containing the :code:`square_plus_constant` and :code:`add` functions.

.. highlight:: yaml
.. code-block:: yaml

    graph:
      name: my_graph
      python_file: hello_world_functions.py
      nodes:
        X:
          function: numpy.random.normal
        Y:
          function: numpy.random.normal
          kwargs:
            loc: 1
            scale: 2
        Z:
          function: add(X, Y)
        W:
          function: square_plus_constant(z=Z, constant=2)


    instructions:
      simulation:
        csv_name: parser
        num_samples: 4



To run the simulation defined in the YAML file, you can use the built-in parser as follows:

.. highlight:: python
.. code-block:: python

  from dagsim.utils.parser import DagSimSpec
  parser = DagSimSpec("name∕or/path/to/YAML∕file")

  data = parser.parse()

The method :code:`parse` would build the graph as defined in the YAML file, and then run the instructions given in the :code:`instructions` part.

By default, this method will also print the details of the graph in addition to drawing it. If you wish not to do so, you cen set :code:`verbose` and/or :code:`draw` to :code:`False`, respectively.
