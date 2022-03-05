Quickstart
==========

In this tutorial, you will learn how you can set up a simple directed acyclic graph (DAG) to generate data from. For a more detailed description of DagSim's workflow, see :ref:`How to specify a simulation`.

Suppose that we have simulate data from a model that has these four variables:

- :math:`X \sim \mathcal{N}(0,1)`, i.e. standard Gaussian Distribution
- :math:`Y \sim \mathcal{N}(1,2)`
- :math:`Z = X + Y`
- :math:`W = Z^2 + c`

We can do that using DagSim by following these steps:

Step 1: Setting up DagSim
-------------------------
To use DagSim for this tutorial, you can either install it on your machine by following the instructions on :ref:`this<Installing DagSim>` page, or start a Binder session by clicking on the badge in one of the tabs below.


Step 2: Defining the simulation
---------------------
Now, that we have DagSim set up, we want to specify and run the simulation. For that, we can use either python code or a YAML specification file.
Regardless of the method you choose, you start by defining your own functions, if any, that will be used for the simulation.

Click on the corresponding tab for more details:

.. tabs::

   .. tab:: Python
    To run this tutorial on binder, click on this badge:
    .. image:: https://mybinder.org/badge_logo.svg
     :target: https://mybinder.org/v2/gh/uio-bmi/dagsim/HEAD?labpath=https%3A%2F%2Fgithub.com%2Fuio-bmi%2Fdagsim%2Fblob%2Fmain%2Ftutorials%2Fhello_world.ipynb


    We begin by importing the following:

    .. highlight:: python
    .. code-block:: python

      import dagsim.base as ds
      import numpy as np

    1. **Defining the functions:**

    The first thing that we need to define is the functions that relate the nodes to each other.
    For the model that we have defined above we would need three functions, one to sample data from a given Gaussian distribution, one that adds two numbers, and one that squares a number and adds a constant to it.

    For :math:`X` and :math:`Y` we can use the :code:`np.random.normal` function from :code:`numpy`. For the remaining nodes we could either use functions from :code:`numpy`, for example, or define our own functions. Here we chose the latter to show how one could use user-defined functions.

    .. highlight:: python
    .. code-block:: python

        def add(x, y):
            return x + y

        def square_plus_constant(z, constant):
            return np.square(z) + constant

    These functions would inform DagSim how to simulate the values of :math:`Z` and :math:`W` based on the values of their parents.

    2. **Defining the graph:**

    Since X uses the default arguments of the :code:`np.random.normal` function, we don't provide any arguments for the function, only the name of the node and the function itself.
    For the nodes :math:`Y`, :math:`Z` and :math:`W`, we need to give each a name, the function to evaluate, and the values of the arguments of the corresponding function.

    Passing these arguments mimics the way this is done in Python. These arguments can be either positional arguments (provided in the form of a list of the arguments' values), keyword arguments (in the form of a dictionary with (arg_name:arg_value) keys-value pairs), or a combination of both, as shown below.

    .. highlight:: python
    .. code-block:: python

        X = ds.Node(name="X", function=np.random.normal)
        Y = ds.Node(name="Y", function=np.random.normal, kwargs={"loc": 1, "scale": 2})
        Z = ds.Node(name="Z", function=add, args=[X, Y])
        W = ds.Node(name="W", function=square_plus_constant, args=[Z], kwargs={"constant": 2})

    At this stage, we can simply compile the graph as follows:


    .. highlight:: python
    .. code-block:: python

      listNodes = [X, Y, Z, W]
      my_graph = ds.Graph(listNodes, "Graph1")

    Once we have compiled the graph, we can draw it to get a graphical representation of the underlying model, as follows:

    .. highlight:: python
    .. code-block:: python

      my_graph.draw()

    .. figure:: ./_static/images/tutorials/hello_world.png
        :align: center

    3. **Running the simulation:**

    Now that we have defined everything we need, we simulate the data by calling the :code:`simulate` method and providing the number of samples and the name of the CSV file to which to save the data.

    .. highlight:: python
    .. code-block:: python

      data = my_graph.simulate(num_samples=100, csv_name="hello_world")

   .. tab:: YAML

    To run this tutorial on binder, click on this badge:

    .. image:: https://mybinder.org/badge_logo.svg
     :target: https://mybinder.org/v2/gh/uio-bmi/dagsim/HEAD?labpath=tutorials%2FParser.ipynb

    For a general description of a YAML file structure, see :ref:`How to specify a simulation using YAML`.

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


.. toctree::
   :maxdepth: 1