.. DagSim documentation master file, created by
   sphinx-quickstart on Thu Jun 17 18:28:53 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to DagSim's documentation!
==================================
DagSim is a framework and specification language for simulating data based on user-defined graphical models,
specifically Directed Acyclic Graphs, or DAGs. To get started with DagSim check out :ref:`this<Simulate data from a simple model>` tutorial.

Simulating data using DagSim follows this workflow:

- **Defining the functions** that will be used for the simulation. This can be any Python function, whether it is user-definedor provided by some Python library.

- **Defining the graph** that you want to simulate data from. This mainly entails defining the different nodes in the graph, by giving each node a name, the function to evaluate the value of that node, and the arguments of that function. These arguments could be nodes in the graph or any other Python objects.

- **Simulating data** from the defined graph.

For more details on this workflow, check :ref:`this<How to specify a simulation using python code>` extended tutorial

To install DagSim, see :ref:`Installing DagSim`

.. toctree::
   :maxdepth: 1
   :caption: Content:

   installation
   specify_with_code
   tutorials

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
