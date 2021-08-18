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

These functions should encode how the value of a node depends on the parent nodes, and possibly some additional parameters. Each function would return a value that represents the value of a given node. The returned value can be of any data type depending on the problem at hand.

2. **Nodes and Graph:**

The nodes represent variables in the model that interact with each other based on functions specified by the user. A node can be one of three possible types:

 * **Generic node** :code:`(Generic)`: a node that can receive values from its parents, if any, in addition to optional additional parameters.
 * **Selection node** :code:`(Selection)`: a node that simulates selection bias in the data by selecting which data points to keep according to some criteria defined by the user.
 * **Stratify node** :code:`(Stratify)`: a node that stratifies the simulation output into different files depending on criteria defined by the user in the form of a function.
 Please check this tutorial for more information on how to use **Selection** and **Stratify**.

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
 * :code:`csv_name (str)` (Optional): The name of the CSV file to which to save the simulated data. If no name is provided, the data will not be saved, only returned in the code.
 
This method will return a Python dictionary where the :code:`keys` are the names of the nodes and the :code:`values` are the simulated values of each node.
 
.. toctree::
   :maxdepth: 2
