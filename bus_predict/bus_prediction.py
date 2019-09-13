import numpy as np


def delay_predict(test_set_known, history_average):
    """
    predict the left part time sequence using current test set and history average.
    :param test_set_known: it is only contain the part of test date that is known. eg:Given [0, 5, 15], and predicting
     left part using model.
    :param history_average: it is the average of history data.
    :return: it contains the whole list, eg: predict set can be [0, 5, 15,...,1500]
    """
    test_set_known = np.array(test_set_known)
    predict_set = np.append(test_set_known, test_set_known[-1] + history_average[len(test_set_known):]
                            - history_average[len(test_set_known) - 1])
    return predict_set


def kern(tl, tl_m, var, b=1):
    """
    Gaussian kernel
    :param tl: current test data
    :param tl_m: the one of training data
    :param var: the variance of training data at l
    :param b: the super parameter b is 1
    :return:
    """
    return np.exp(-np.sum((tl - tl_m) ** 2 / var) / b)


def kernel_predict(test_set_known, training_sets, training_sets_variance):
    """
    predict the left part time sequence using current test set and training sets with variance.
    :param test_set_known: it is only contain the part of test date that is known. eg:Given [0, 5, 15], and predicting
     left part using model.
    :param training_sets: the whole training sets. eg: [[0, 5, 15, ..., 1500],...,[0, 5, 15, ..., 1500]]
    :param training_sets_variance: the variance of training sets. eg: [1, 100, 50, ..., 300]
    :return: it contains the whole list, eg: predict set can be [0, 5, 15,...,1500]
    """
    test_set_known, training_sets = np.array(test_set_known), np.array(training_sets)
    tl, l = test_set_known, len(test_set_known)
    delta_time = (training_sets.T[l:] - training_sets.T[l - 1]).T
    Tl_m = training_sets[..., :l]
    kern_weight = np.array([kern(tl, tl_m, training_sets_variance[:l]) for tl_m in Tl_m])
    predict_set = np.append(tl, tl[-1] + np.sum(np.multiply(kern_weight[:, np.newaxis], delta_time), axis=0) / np.sum(kern_weight))
    return predict_set

