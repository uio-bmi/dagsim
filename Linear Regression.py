from baseDS import Graph, Generic
import numpy as np
from sklearn.linear_model import LinearRegression as lr
import pandas as pd


# define the function of the ground truth
def ground_truth(x, add_param):
    y = 2 * x + 1 + np.random.normal(0, add_param)
    return y


# define a node for the input feature, and another node for the outcome of a linear regression model
Nodex = Generic(name="x", function=np.random.normal)
Nodey = Generic(name="y", parents=[Nodex], function=ground_truth, additional_params=[1])

# define a list of all nodes, then instantiate the graph
listNodes = [Nodex, Nodey]
my_graph = Graph("Linear Regression", listNodes)

my_graph.draw()

# simulate data for training and testing, with different sample sizes and filenames
train = my_graph.simulate(num_samples=70, csv_name="train")
test = my_graph.simulate(num_samples=30, csv_name="test")

# import the saved training data
train_data = pd.read_csv("train.csv")
print(train_data.head())

x_train = train_data.iloc[:, 0].to_numpy().reshape([-1, 1])
print("x_train", x_train.shape)
y_train = train_data.iloc[:, 1].to_numpy().reshape([-1, 1])
print("y_train", y_train.shape)

# define a linear regression model
LR = lr()
# fit the model on the training data
reg = LR.fit(x_train, y_train)
reg.score(x_train, y_train)
print("Coefficient: ", LR.coef_)
print("Intercept: ", LR.intercept_)

# import the saved testing data
test_data = pd.read_csv("test.csv")
x_test = test_data.iloc[:, 0].to_numpy().reshape([-1, 1])
print("x_test", x_test.shape)
y_test = test_data.iloc[:, 1].to_numpy().reshape([-1, 1])
print("y_test", y_test.shape)

# get the R2 score of the model on the testing data
print("R2 score on test data: ", LR.score(x_test, y_test))
