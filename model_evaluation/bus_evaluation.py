import numpy as np


def evaluate(test_set, predict_set):
    """
    calculate the sum of AE, APE and count for late calculation.
    :param test_set: It only contains the unknown part of the whole test_set. If test_set is[0, 5, 10, 15,...,1500],
    and it predicts from the third point, then test_set_left is [15,...,1500].
    :param predict_set: It is the same as test_set_left.
    :return: it returns the sum of absolute error and absolute percentage error along with prediction counts.
    """
    test_set, predict_set = np.array(test_set), np.array(predict_set)
    error = np.abs(test_set - predict_set)
    absolute_error = np.sum(error)

    absolute_per_error = np.sum(error / test_set)
    predict_count = len(test_set)
    return absolute_error, absolute_per_error, predict_count

