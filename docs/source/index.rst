.. DagSim documentation master file, created by
   sphinx-quickstart on Thu Jun 17 18:28:53 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to DagSim's documentation!
==================================
DagSim is a Python-based framework and specification language for simulating data based on a Directed Acyclic Graph (DAG)
structure, without any constraints on variable types or functional relations. A succinct YAML format for
defining the structure of the simulation model promotes transparency, while separate user-provided functions for
generating each variable based on its parents ensure the modularization of the simulation code.

To get started with DagSim check out :ref:`this<Quickstart>` tutorial.

Typically, simulating data using DagSim would follow this workflow:

- **Define the functions** that will be used for the simulation. This can be any Python functions, whether they are user-defined or provided by another Python library.

- **Define the graph** that you want to simulate data from. This entails defining the different nodes in the graph, by giving each node a name, the function to evaluate, and the arguments of that function. These arguments could be other nodes in the graph or any other Python objects.

- **Simulate data** from the defined graph.

For more details on this workflow, check :ref:`this<Specifying a simulation>` extended tutorial.

To install DagSim, see :ref:`Installing DagSim`.

.. toctree::
   :maxdepth: 1
   :caption: Content:

   quickstart
   installation
   specify_with_code
   tutorials

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
