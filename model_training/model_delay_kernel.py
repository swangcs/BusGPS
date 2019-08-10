import numpy as np
import utils
from matplotlib import pyplot as plt
from prepare_training_set import prepare


def kern(tl, tl_m, b, var):
    return np.exp(-np.sum((tl - tl_m) ** 2 / var) / b)


def training(all_sets: list, n, model, J=10, b=1):
    """
    model training
    :param all_sets: it is a list of training set(each value in a set is the arrival time of that position which is the index * step)
    :param n: each set has the same length which is n
    :param model: it can be kernel or delay
    :param J: it is the iteration times
    :param b: it is the parameter of kernel model
    :return:
    """
    # training set is a sequence of timestamp with traveled distance as index
    all_sets = np.array(all_sets)
    np.random.shuffle(all_sets)
    # RMSE = [[0 for _ in range(n)] for _ in range(J)]
    RMSE = np.zeros((J, n))
    MAE = np.zeros((J, n))
    length = int(len(all_sets) / J)
    for j in range(J):  # 3
        print('Iterator {}'.format(j + 1))
        training_set = np.concatenate((all_sets[:j * length], all_sets[(j + 1) * length:])).T  # 4 T-j
        validation_set = all_sets[j * length:(j + 1) * length].T  # 5 Tj
        tmp = np.var(training_set.T, axis=0)
        Tl_m_var = np.array([max(tmp[v], 1) for v in range(training_set.shape[0])])
        for l in range(0, n - 1):  # n = len(t), n is not sure
            if model == 'kernel':
                delta_time = training_set[l + 1:] - training_set[l]
                Tl_m, Tl = training_set[:l + 1].T, validation_set[:l + 1].T
                kern_weight = np.array([[kern(tl, tl_m, b, Tl_m_var[:l + 1]) for tl_m in Tl_m] for tl in Tl])
                # print(np.sum(kern_weight, axis=1))
                average = np.array([np.sum(delta_time * k_w, axis=1) / np.sum(k_w) for k_w in kern_weight]).T
                prediction_set = validation_set[l] + average
            else:
                delay = np.mean(training_set[l + 1:], axis=1) - np.mean(training_set[l])  # t delay, l+h
                delay = delay.reshape(delay.shape[0], 1)
                prediction_set = np.tile(validation_set[l], (np.shape(delay)[0], 1)) + delay
            # 7 calculate rmse
            RMSE[j][l] = np.mean(np.sqrt(np.mean((prediction_set - validation_set[l + 1:]) ** 2, axis=0)))
            MAE[j][l] = np.mean(np.abs(prediction_set - validation_set[l + 1:]))
            # print(MAE[j][l])
    RMSEu = np.mean(RMSE, axis=0)
    MAEu = np.mean(MAE)
    # RMSEv = np.var(RMSE, axis=0)
    # print('RMSE average:\n{}'.format(RMSEu))
    print('MAE average:\n{}'.format(MAEu))
    print('RMSE average:\n{}'.format(np.mean(RMSEu)))
    # print('RMSE variance:\n{}'.format(RMSEv))
    plt.plot([i for i in range(n)], RMSEu)
    plt.title('{}:{}'.format(model, n))
    plt.show()


if __name__ == '__main__':
    model, step, J, b = 'kernel', 100, 10, 1
    training_sets_all, trajectories_length = prepare(route_id='15', step=step)
    for start_stop, training_sets in training_sets_all.items():
        n = int(trajectories_length[start_stop] / step)
        print('Start stop:{},size:{}'.format(start_stop, len(training_sets)))
        training(training_sets, n, model)

