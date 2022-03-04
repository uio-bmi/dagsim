Importing models from other libraries
=========================================================================

In some situations, the user might want to simulate data that resembles a real data set instead of simulating a data set with arbitrary parameters. In order to help with this, DagSim builds on other existing libraries for structure and parameter learning to obtain such models. Althouth some of these libraries already provide simulation functionalities, usually they are limited in terms of the types of functional forms you can use and other simulation utilitites. 

DagSim allows you to use the learning capabilities of these other libraries with the additional benefit of having a more flexible simulation pipeline. This, for example, allows the user to modify the functional forms or parameters learned by the libraries, simulate selection bias in the data, among other things.

In this tutorial, you will learn how to import models learned by other libraries, and generate a script in DagSim syntax that is transformed from the learned model.


Create a DagSim model from a weighted adjacency matrix
------------------------------------------------------
Structure learning algorithms and packages such as NOTEARS (Zheng et al. add reference), bnlearn (add reference), etc. allow researchers to learn the structure and the parameters of the causal model governing the data generating process. The result of such algorithms is the estimated weighted adjacency matrix that holds the coefficients of the functional forms relating the variables to each other.

To generate a DagSim script from such a weight matrix, you can use the :code:`from_matrix` function. To use this method, you need to provide the following:
 
 * :code:`weight (ndarray)`: A weight matrix proposed by the user or learned using a given library.
 * :code:`sem_type (str)`: The type of SEMs you want to use in your model. This can be one of the following:
 
 	* "gauss": Linear model with Gaussian noise
 	* "exp": Linear model with exponential noise
 	* "gumbel": Linear model with Gumbel noise
 	* "uniform": Linear model with uniform noise
  	* "logistic": Logistic model
 	* "poisson": Poisson model	


The generated script will use the indices of the variables in the weight matrix for the names of the corresponding variables, by appending them to the generic variable name "x".


The following code is an example showing how a weight matrix would be used:

.. code-block:: python

	import numpy as np
	from dagsim.utils.helper import from_matrix


	weight = np.array([[0, 0, 2], [0, 0, 3], [0, 0, 0]])

	from_matrix(weight, sem_type="gauss", script_name="gaussDagSim")
    
This will create a python file, gaussDagSim.py that has the following script:

.. code-block:: python

	import dagsim.base as ds
	import numpy as np 
	
	
	def func_x2(x0, x1):
	  x2 = 2 * x0 + 3 * x1 + np.random.normal(loc=1, scale=0)
	  return x2


	Node_x0 = ds.Node(name='x0', function=np.random.normal, kwargs={'loc': 1, 'scale': 0})
	Node_x1 = ds.Node(name='x1', function=np.random.normal, kwargs={'loc': 1, 'scale': 0})
	Node_x2 = ds.Node(name='x2', function=func_x2, kwargs={'x0': Node_x0, 'x1': Node_x1})

	listNodes = [Node_x0, Node_x1, Node_x2]
	graph = ds.Graph(listNodes, 'myGraph')

Create a DagSim model from a file
------------------------------------------------------
In case you have a weighted adjacency matrix in the form of a csv file, you can directly use the :code:`from_csv` function to generate a similar script, as in the following:

.. code-block:: python
   	
   	import numpy as np
	from dagsim.utils.helper import from_csv

   	from_csv(csv_file_name, sem_type="gauss", script_name="gaussDagSim")



.. toctree::
   :maxdepth: 2
