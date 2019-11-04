import numpy as np
import pickle
from bus_prediction import kernel_predict
from bus_evaluation import evaluate


def training(training_sets):
    """

    :param training_sets: It is a sequence of timestamp with traveled distance as index. eg:[[0, 5, ..., 1400],...,[]]
    :return: the variance of training sets.
    """
    training_sets = np.array(training_sets)
    return np.array([max(np.var(training_sets.T, axis=1)[v], 1) for v in range(training_sets.shape[1])])


