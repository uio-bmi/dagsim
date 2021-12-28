Special nodes
=========================================================================

DagSim has two special types of nodes that could be useful in simulations, namely a :code:`Selection` node and a :code:`Stratify` node. A :code:`Selection` node allows the user to simulate selection bias in the simulated data, such that only the samples that satisfy some user-specified criteria end up in the resulting data set. 

On the other hand, and as the name suggests, a :code:`Stratify` node allows the user to stratify the resulting data set into different strata, again according to user-specified criteria. The results will be returned as a dictionary of different dictionaries, one for each stratum, and the samples from each stratum are saved in a separate .csv file. 

In this tutorial, you will learn how to use each of these nodes.


Selection
---------------------------------------------

Similar to a :code:`Generic` node, to define a :code:`Selection` node, you need to specify the following:

 * :code:`name (str)`: A name for the node.
 * :code:`function`: The function to evaluate to get the value of the node. Note that here you need to specify only the **name** of the function without any arguments.
 * :code:`arguments (dict)`: A dictionary of key-value pairs in the form "name_of_argument":value. A value can be either another node in the graph or an object of the correct data type for the corresponding argument. At least one :code:`value`: in the dictionary should be a node in the graph.

The difference from a :code:`Generic` node is that the function here should return a boolean; :code:`True` to include a sample, and :code:`False` to discard a sample.

The following code shows an example where only the samples that have a value of node Y greater than a certain threshold are included in the data set.

.. code-block:: python
   
	from baseDS import Graph, Generic, Selection
	import numpy as np


	def add(param1, param2):
	    return param1 + param2


	def square(param):
	    return np.square(param)


	def is_greater_than2(node, threshold):
	    if node < threshold:
		return True
	    else:
		return False 


	Node1 = Generic(name="A", function=np.random.normal)
	Node2 = Generic(name="B", function=np.random.normal)
	Node3 = Generic(name="C", arguments={"param1": Node1, "param2": Node2}, function=add)
	Node4 = Generic(name="D", function=square, arguments={"param": Node3})
	Node5 = Selection(name="SB", function=is_greater_than2, arguments={"node": Node3, "threshold":2})

	listNodes = [Node1, Node2, Node3, Node4, Node5]
	my_graph = Graph("Graph1", listNodes)
	output = my_graph.simulate(num_samples=20, csv_name="SelectionExample")


Stratification
---------------------------------------------

The arguments needed to specify a :code:`Stratify` node are exactly the same as for a :code:`Selection` node. However, the function here should return the name :code:`(str)` of the stratum to which a given example should belong. These names will be used as suffixes to the main .csv file name.

.. .. note::
..	Note that the names of the strata should be of the data type :code:`str`.

The following code shows an example where the samples are split into three categories, namely "less than -1", "greater than +1", and "between -1 and +1".

.. code-block:: python

	
	from baseDS import Graph, Generic, Stratify
	import numpy as np


	def add(param1, param2):
	    return param1 + param2


	def square(param):
	    return np.square(param)


	def check_strata(node):
	    if node < -1:
		return "<-1"
	    else:
		if node > 1:
		    return ">1"
		else:
		    return ">-1|<+1"


	Node1 = Generic(name="A", function=np.random.normal)
	Node2 = Generic(name="B", function=np.random.normal)
	Node3 = Generic(name="C", function=add, arguments={"param1": Node1, "param2": Node2})
	Node4 = Generic(name="D", function=square, arguments={"param": Node3})
	Node5 = Stratify(name="St", function=check_strata, arguments={"node": Node3})

	listNodes = [Node1, Node2, Node3, Node4, Node5]
	my_graph = Graph("Graph1", listNodes)
	output = my_graph.simulate(num_samples=20, csv_name="testing")	



Missing
---------------------------------------------

To define a :code:`(Missing)` node, we specify the following:

Note that this type of nodes does not have a :code:`(function)` attribute to specify how the entries would go missing. Instead, the values of another :code:`(Generic)` node would control that process.
We chose this design in order to keep the process of specifying which node would have missing entries and that of how it they would go missing, separate.

 * :code:`name (str)`: A name for the node.
 * :code:`underlying_value (Generic)`: The node whose values will have missing entries down the simulation
 * :code:`index_node (Generic)`: Another node whose value would specify which entries would go missing. The output of this node should be :code:`1` to keep a value, and :code:`0` to remove it.

Note that in the output of the simulation, the original output without missing entries would be saved as values of the :code:`underlying_value (Generic)` node. Those with missing entries would be saved in the corresponding :code:`Missing` node having that node as its :code:`underlying_value` attribute.

.. code-block:: python

    from dagsim.base import Graph, Generic, Missing
    import random

    index = Generic("i", function=random.choice, arguments={"seq": [0,1]})
    toBeMissed = Generic(name="toBeMissed", function=random.normalvariate, arguments={"mu":0, "sigma": 1})
    missingNode = Missing(name="M1", underlying_value=toBeMissed, index_node=index)
    my_graph = Graph(name="graph1", list_nodes=[index, toBeMissed, missingNode])

.. toctree::
   :maxdepth: 2
