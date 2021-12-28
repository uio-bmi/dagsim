How to specify a simulation
=========================================================================

Simulations using DagSim can be specified either using a YAML specification file or using python code directly. Nonetheless, the main components of a simulation are the same regardless of the used method. To run any simulation, the user needs to define three things:

1. The functions that encode how to simulate each node in the graph.
2. The nodes that form the graph.
3. The simulation details.


In this tutorial, you will learn how to specify a simulation using either method.

How to specify a simulation using python code
---------------------------------------------

1. **Functions:**

These functions should encode how the value of a node depends on the parent nodes, and possibly some additional parameters.

For a :code:`(Generic)` node, the return value of the corresponding function would be the value of that node. In that case, the returned value can be of any data type depending on the problem at hand.
For the other nodes, the return value has a different significance depending on the type of the corresponding node.

2. **Nodes and Graph:**

The nodes represent variables in the model that interact with each other based on functions specified by the user. A node can be one of four possible types:

 * **Generic node** :code:`(Generic)`: a node that can receive values from its parents, if any, in addition to optional additional parameters, as arguments to its function.
 * **Selection node** :code:`(Selection)`: a node that simulates selection bias in the data by selecting which data points to keep according to some criteria defined by the user.
 * **Stratify node** :code:`(Stratify)`: a node that stratifies the simulation output into different files depending on criteria defined by the user.
 * **Missing node** :code:`(Missing)`: a node that simulates missing entries in the data based on criteria defined by the user.
 Please check this tutorial for more information on how to use **Selection**, **Stratify**, and **Missing** nodes.

To define a node, you need to specify the following things:
 
 * :code:`name (str)`: A name for the node.
 * :code:`function`: The function to evaluate to get the value of the node. Note that here you need to specify only the **name** of the function without any arguments.
 * :code:`arguments (dict)` (Optional): A dictionary of key-value pairs in the form "name_of_argument":value. A value can be either another node in the graph or an object of the correct data type for the corresponding argument.
 * :code:`plates (list of str)` (Optional): The names of the plates in which the node resides.

After defining all the nodes in your model, you construct a graph by creating an instance of the class :code:`Graph` and giving it two arguments:

 - :code:`name (str)`: A name for the graph.
 - :code:`list_nodes (list)`: A list of all the nodes that you have defined.
 
3. **Simulation details:**
 
Now that you have defined the functions and the graph, you can simulate data by calling the :code:`simulate` method of the graph and giving it two arguments:

 * :code:`num_samples (int)`: The number of samples to simulate.
 * :code:`csv_name (str)` (Optional): The name of the CSV file to which to save the simulated data. If not provided, the data will not be saved, only returned in the code.
 
This method will return a Python dictionary where the :code:`keys` are the names of the nodes and the :code:`values` are the simulated values of each node.

How to specify a simulation using YAML
--------------------------------------

The YAML file has two main components, the definition of the graph itself including all the nodes and functions that connect them to each other, and the simulation details including the number of samples to be simulated and the name of the csv file to save the simulated data to.

Within the graph component, you provide a name for that graph, the path to the python file having all the functions to be used in the simulation, and the definition of the nodes within the "nodes" key.

.. note::
    Functions provided by standard libraries do not need to be included in the python file. However, these functions should use the whole library name instead of abbreviations, for example, :code:`numpy` instead of :code:`np`.

    :code:`numpy` and :code:`scipy` are automatically installed when you install DagSim. Should you need another library, please install it manually.

Each key inside "nodes" would correspond to a node in the graph, with the name of that node being the key itself. For each node, you need to specify the name of the function to use, the arguments needed by that function, if any, in addition to other optional keys.

.. note::
    The nodes do not need to be provided in a topological order, i.e a child node could be defined before its parents node(s). DagSim will sort the nodes topologically after checking for acyclicity.
# TODO add explanation of each component in each main component + fix the sample YAML + add sample YAML for Linear Regression
The general structure of the YAML file would look like this:

.. highlight:: yaml
.. code-block:: yaml

    graph:
      python_file: path/to/file
      name: "user-defined name"
      nodes:
        name_of_node1:
          function: function_name # user-defined or one provided by an external library
          arguments:
            name_of_argument1: value_of_argument1 # an appropriate python object or the name of a parent node
            name_of_argument2: value_of_argument2
          type: Generic
        ⋮

    instructions:
      simulation:
        num_samples: 4
        csv_name: "parser"

For a sample simulation definition using a YAML file, please see :ref:`Define the simulation using a YAML file`.

.. toctree::
   :maxdepth: 2
