import numpy as np


def ground_truth(x, std_dev):
    y = 2 * x + 1 + np.random.normal(0, std_dev)
    return y
