import numpy as np
import pickle
from bus_prediction import delay_predict
from bus_evaluation import evaluate


def kern(tl, tl_m, b, var):
    return np.exp(-np.sum((tl - tl_m) ** 2 / var) / b)


def training(training_sets):
    """

    :param training_sets: It is a sequence of timestamp with traveled distance as index. eg:[[0, 5, ..., 1389],...,[]]
    :return: the average of history timestamp is returned, and it is a list like: [0, 5, 15, ..., 1400]
    """
    training_sets = np.array(training_sets)
    average = np.mean(training_sets, axis=0)
    return average


sets_all = pickle.load(open('training_sets1.pkl', 'rb'))
sets_all = sets_all[603]
np.random.shuffle(sets_all)
test_ratio = int(0.2 * len(sets_all))
training_sets_all, test_sets = sets_all[test_ratio:], sets_all[:test_ratio]
delay = training(training_sets_all)
MAE, MAPE, count = 0, 0, 0
for test_set in test_sets:
    for l in range(1, len(test_set)):
        predict_set = delay_predict(test_set[:l], delay)
        ae, ape, c = evaluate(test_set[l:], predict_set[l:])
        MAE, MAPE, count = ae + MAE, ape + MAPE, count + c
K = len(test_sets[0])
MAE, MAPE = MAE / count, MAPE / count

