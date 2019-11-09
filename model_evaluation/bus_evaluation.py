import numpy as np


def evaluate(pred_results):
    """
    calculate the sum of AE, APE and count for late calculation.
    :param pred_results: It is the prediction sets with data format 3 which includes all test results
    :return: it returns the mean of absolute error and absolute percentage error of this directory.
    """
    MAE, MAPE, RMSE, count = 0, 0, 0, 0
    N = len(pred_results)
    for pred_result in pred_results:
        rmse = 0
        test_set = np.array(pred_result[-1])
        K = len(test_set)
        for l in range(len(pred_result) - 1):
            if min(test_set[l + 1:]) <= 0.0:
                continue
            predict_set = pred_result[l][l + 1:]
            error = np.abs(test_set[l + 1:] - predict_set)
            rmse += np.sqrt(np.sum(error ** 2) / (K - l - 1))
            MAE += np.sum(error)
            MAPE += np.sum(error / test_set[l + 1:])
            count += len(predict_set)
        RMSE += rmse / (K - 1)
    MAE, MAPE = MAE / count, MAPE / count
    RMSE = RMSE / N
    return MAE, MAPE, RMSE
