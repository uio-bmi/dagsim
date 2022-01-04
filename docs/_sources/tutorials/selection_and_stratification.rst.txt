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
   
    import dagsim.base as ds
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


    Node1 = ds.Generic(name="A", function=np.random.normal)
    Node2 = ds.Generic(name="B", function=np.random.normal)
    Node3 = ds.Generic(name="C", arguments={"param1": Node1, "param2": Node2}, function=add)
    Node4 = ds.Generic(name="D", function=square, arguments={"param": Node3})
    Node5 = ds.Selection(name="SB", function=is_greater_than2, arguments={"node": Node3, "threshold":2})

    listNodes = [Node1, Node2, Node3, Node4, Node5]
    my_graph = ds.Graph("SelectionExample", listNodes)
    output = my_graph.simulate(num_samples=20, csv_name="SelectionExample")


Stratification
---------------------------------------------

The arguments needed to specify a :code:`Stratify` node are exactly the same as for a :code:`Selection` node. However, the function here should return the name :code:`(str)` of the stratum to which a given example should belong. These names will be used as suffixes to the main .csv file name.

.. .. note::
..	Note that the names of the strata should be of the data type :code:`str`.

The following code shows an example where the samples are split into three categories, namely "less than -1", "greater than +1", and "between -1 and +1".

.. code-block:: python


    import dagsim.base as ds
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


    Node1 = ds.Generic(name="A", function=np.random.normal)
    Node2 = ds.Generic(name="B", function=np.random.normal)
    Node3 = ds.Generic(name="C", function=add, arguments={"param1": Node1, "param2": Node2})
    Node4 = ds.Generic(name="D", function=square, arguments={"param": Node3})
    Node5 = ds.Stratify(name="St", function=check_strata, arguments={"node": Node3})

    listNodes = [Node1, Node2, Node3, Node4, Node5]
    my_graph = ds.Graph("StratificationExample", listNodes)
    output = my_graph.simulate(num_samples=20, csv_name="StratificationExample")


Missing
---------------------------------------------

To specify a :code:`Missing` node, the user provides the following:

 * :code:`name (str)`: A name for the node,
 * :code:`underlying_value (Generic)`: The node that will eventually have missing values
 * :code:`index_node (Generic)`: A :code:`Generic` node that will provide the indices of the entries that will go missing: :code:`0` for remove, :code:`1` for keep.

We decided on this way of defining the node to keep the processes of specifying the indices of the missing entries and removing the corresponding values separate.

Note that the data with the missing entries would be saved as the output of the :code:`Missing` node itself rather than that of the :code:`underlying_value` node.
The output of the latter would be the complete data without any missing entries. If you with to discard the complete data, you can use the :code:`observed=False` argument when defining the :code:`underlying_value` node.

In the following, we explore how you can simulate missing values according to the three types of missing data models defined in `Rubin (1976) <http://math.wsu.edu/faculty/xchen/stat115/lectureNotes3/Rubin%20Inference%20and%20Missing%20Data.pdf>`_.
Here, the observed data are collectively denoted by :math:`Y_\mathrm{obs}`, and the missing, would-have-been, data are collectively denoted as
:math:`Y_\mathrm{mis}`, and :math:`\psi` refers to the parameters of the missing data model.

Missing Completely At Random (MCAR)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In this case, the missingness pattern is random and the probability of an entry going missing, :math:`Pr(M=0)`, is independent
of any missing or non-missing values of other variables in the data-generating process. In other words,

.. math::
    \Pr(M=0|Y_obs,Y_mis,\psi) = \Pr(M=0|\psi)

.. code-block:: python


    import dagsim.base as ds
    import numpy as np


    underlying_value = ds.Generic(name="underlying_value", function=np.random.normal)
    index_node = ds.Generic(name="index_node", function=np.random.randint, arguments={"low":0, "high":2})
    MCAR = ds.Missing(name="MCAR", underlying_value=underlying_value, index_node=index_node)

    list_nodes = [underlying_value, index_node, MCAR]
    my_graph = ds.Graph(name="MCAR", list_nodes=list_nodes)

    data = my_graph.simulate(num_samples=10, csv_name="MCAR")


Missing At Random (MAR)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In this case, the probability of an entry going missing depends on other observed values in the model, but
does not depend on any unobserved quantities:

.. math::
    \Pr(M=0|Y_obs,Y_mis,\psi) = \Pr(M=0|Y_obs,\psi)

In this case, :math:`\Pr(M=0)` depends on the observed value of :math:`Y_obs`.

.. code-block:: python


    import dagsim.base as ds
    import numpy as np

     def get_index(Y_observed):
        val = 0
        if Y_observed > 0:
            val = 1
        return val


    underlying_value = ds.Generic(name="underlying_value", function=np.random.normal)
    Y_observed = ds.Generic(name="Y_observed", function=np.random.normal)
    index_node = ds.Generic(name="index_node", function=get_index, arguments={"Y_observed": Y_observed})
    MAR = ds.Missing(name="MAR", underlying_value=underlying_value, index_node=index_node)

    list_nodes = [underlying_value, index_node, Y_observed, MAR]
    my_graph = ds.Graph(name="MAR", list_nodes=list_nodes)

    data = my_graph.simulate(num_samples=10, csv_name="MAR")

Missing Not At Random (MNAR)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In the MNAR case, the probability that an entry is missing depends not only on observed quantities but also on missing ones,
so the conditional probability does not simplify:

.. math::
    \Pr(M=0|Y_obs,Y_mis,\psi) = \Pr(M=0|Y_obs,Y_mis,\psi)

In this case, :math:`\Pr(M=0)` depends on the observed value of :math:`Y_obs` and the, possibly, unobserved,
would-have-been value of :math:`Y_mis`.

.. code-block:: python


    import dagsim.base as ds
    import numpy as np

     def get_index(Y_observed, Y_missing):
        val = 0
        if Y_observed + Y_missing > 0.5:
            val = 1
        return val



    underlying_value = ds.Generic(name="underlying_value", function=np.random.normal)
    Y_observed = ds.Generic(name="Y_observed", function=np.random.normal)
    Y_missing = ds.Generic(name="Y_missing", function=np.random.normal)
    index_node_Y = ds.Generic(name="index_node_Y", function=np.random.randint, arguments={"low":0, "high":2})
    index_node = ds.Generic(name="index_node", function=get_index, arguments={"Y_observed":Y_observed, "Y_missing":Y_missing})
    MNAR = ds.Missing(name="MNAR", underlying_value=underlying_value, index_node=index_node)

    list_nodes = [underlying_value, Y_observed, Y_missing, index_node, index_node_Y, MNAR]
    my_graph = ds.Graph(name="MNAR", list_nodes=list_nodes)

    data = my_graph.simulate(num_samples=10, csv_name="MNAR")


.. toctree::
   :maxdepth: 2
