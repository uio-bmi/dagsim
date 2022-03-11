Specifying a simulation
=======================

Simulations using DagSim can be specified either using a YAML specification file or using python code directly. Nonetheless, the main components of a simulation are the same regardless of the used method. To run any simulation, the user needs to define three things:

1. The functions that encode how to simulate each node in the graph.
2. The nodes that form the graph.
3. The simulation details.


In this section, you will learn how to specify a simulation using either method.

How to specify a simulation using python code
---------------------------------------------

1. **Functions:**

These functions encode how to calculate the value of a node based on the values of its parent nodes and/or other additional parameters.

For a standard :code:`Node`, the return value of the corresponding function would be the value of that node. In that case, the returned value can be of any data type depending on the problem at hand.
For the other nodes, the return value has a different significance depending on the type of the corresponding node, see :ref:`Special nodes`.

2. **Nodes and Graph:**

The nodes represent variables in the model that interact with each other based on functions specified by the user. A node can be one of four possible types:

 * **Standard node** :code:`(Node)`: a node that can receive values from its parents, if any, in addition to optional additional parameters, as arguments to its function.
 * **Selection node** :code:`(Selection)`: a node that simulates selection bias in the data by selecting which data points to keep according to some criteria defined by the user.
 * **Stratify node** :code:`(Stratify)`: a node that stratifies the simulation output into different files depending on criteria defined by the user.
 * **Missing node** :code:`(Missing)`: a node that simulates missing entries in the data based on criteria defined by the user.

Please check :ref:`this tutorial<Special nodes>` for more information on how to use **Selection**, **Stratify**, and **Missing** nodes.

    2.1 **Nodes**

To define a standard :code:`Node`, you need to specify the following:
 
 * :code:`name (str)`: A name for the node.
 * :code:`function`: The function to evaluate to get the value of the node. Note that here you need to specify only the **name** of the function without any arguments.
 * :code:`args (list)` (Optional): A list of positional arguments. An argument can be either another node in the graph or an object of the correct data type for the corresponding argument.
 * :code:`kwargs (dict)` (Optional): A dictionary of key word arguments with key-value pairs in the form "name_of_argument":value. A value can be either another node in the graph or an object of the correct data type for the corresponding argument.
 * :code:`visible (bool)` (Optional): Default is :code:`True` to show the node when drawing the graph. :code:`False` hides the node in the graph.
 * :code:`observed (bool)` (Optional): Default is :code:`True` to show the output of the node when drawing the graph. :code:`False` hides the node in the graph.
 * :code:`size_field (str)` (Optional): The name of the argument representing the size in the used function. This is used to speed up the simulation when the used function comes with a vectorized implementation.
 * :code:`handle_multi_cols (bool)` (Optional): Default is :code:`False`. If :code:`True`, vector-valued outputs will be split into different columns, each with the name of the original node appended by its index.
 * :code:`handle_multi_return (function)` (Optional): The name of the function that would specify how to handle outputs of functions with multiple return values.
 * :code:`plates (list)` (Optional): The names of the plates in which the node resides.


 2.2 **Graph**

After defining all the nodes in your model, you construct a graph by creating an instance of the class :code:`Graph` and giving it two arguments:

 * :code:`list_nodes (list)`: A list of all the nodes that you have defined.
 * :code:`name (str)` (Optional): A name for the graph. This would be used as the name of the .png drawing of the graph.

3. **Simulation details:**
 
Now that you have defined the functions and the graph, you can simulate data by calling the :code:`simulate` method of the graph using these arguments:

 * :code:`num_samples (int)`: The number of samples to simulate.
 * :code:`csv_name (str)` (Optional): The name of the CSV file to which to save the simulated data. If not provided, the data will not be saved to a file, only returned in the code.
 * :code:`output_path (str)` (Optional): The path where the CSV file would be saved. This path would be automatically passed to any used function that defines :code:`output_path` as one of its arguments, if that is needed. Default is :code:`None`, and the CSV file is saved to the current working directory when running the simulation.
 * :code:`selection (bool)` (Optional): :code:`True` to simulate Selection bias, :code:`False` to do otherwise.
 * :code:`stratify (bool)` (Optional): :code:`True` to stratify the data, :code:`False` to do otherwise.
 * :code:`missing (bool)` (Optional): :code:`True` to simulate missing data, :code:`False` to do otherwise.

This method will return a Python dictionary where the :code:`keys` are the names of the nodes and the :code:`values` are the simulated values of each node.

For an example of defining a simulation using Python code, see :ref:`Quickstart`.

How to specify a simulation using YAML
--------------------------------------

The YAML file has two main components, the definition of the graph itself including all the nodes and functions that connect them to each other, and the simulation details including the number of samples to be simulated and the name of the csv file to save the simulated data to.

Within the graph component, you provide a name (optional) for that graph, the path to the python file having all the functions to be used in the simulation, and the definition of the nodes in the "nodes" component.

.. note::
    Functions provided by standard libraries do not need to be included in the python file. However, these functions should use the whole library name instead of abbreviations, for example, :code:`numpy` instead of :code:`np`.

    :code:`numpy` and :code:`scipy` are automatically installed when you install DagSim. Should you need another library, please install it manually.


.. note::
    The nodes do not need to be provided in a topological order, i.e a child node could be defined before its parents node(s). DagSim will sort the nodes topologically after checking for acyclicity.

The type of a given node (whether it is Node, Selection, Stratify, or Missing) is specified in the "type" key, as shown below. The other keys are the same as the arguments that you would use to specify a node in Python code (see :ref:`Node`.)

The general structure of the YAML file would look like this:

.. highlight:: yaml
.. code-block:: yaml

    graph:
      python_file: path/to/file # (optional) A .py file containing the user-defined functions, if any, to be used in the simulation.
      name: "user-defined name" # An optional name for the graph.
      nodes: # A list of all the nodes in the graph. For each node you provide the same arguments as when specifying it with code.
        name_of_node1:
          function: function_name # user-defined or one provided by an external library, with default arguments.
        name_of_node2:
          function: function_name # user-defined or one provided by an external library, along with the kwargs.
          kwargs:
            name_of_argument1: value_of_argument1 # The name and value of an argument. This could be a python object or another node in the graph.
            name_of_argument2: value_of_argument2
          type: Node # This could be :code:`Node`, :code:`Selection`, :code:`Stratify`, or :code:`Missing`. Specifying it as :code:`Node` is optional.
          ⋮(other optional arguments)
        name_of_node3:
          function: function_name(*args, **kwargs) # This is another way of defining a function, without separately defining the arguments.

    instructions:
      simulation:
        num_samples: 4 # The number of samples to simulate
        csv_name: parser # The name of the CSV file to which to save the file, if desired.
        ⋮(other optional arguments. See :ref:`Simulation details` above.)

For a sample simulation definition using a YAML file, please see :ref:`Quickstart`.

.. toctree::
   :maxdepth: 2
