import numpy as np


def training(training_sets):
    """

    :param training_sets: It is a sequence of timestamp with traveled distance as index. eg:[[0, 5, ..., 1389],...,[]]
    :return: the average of history timestamp is returned, and it is a list like: [0, 5, 15, ..., 1400]
    """
    training_sets = np.array(training_sets)
    average = np.mean(training_sets, axis=0)
    return average




