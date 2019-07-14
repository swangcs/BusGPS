import json
import random

import numpy as np


trajectories_length = {'6318': 22810, '6282': 21810}
J = 10
training_sets_all = json.load(open('training_sets.json'))
for start_stop, training_sets in training_sets_all.items():
    print('Start stop:{},size:{}'.format(start_stop, len(training_sets)))
    # training set is a sequence of timestamp with traveled distance as index
    training_sets = np.array(training_sets)
    random.shuffle(training_sets)  # 1
    # RMSE = [[0 for _ in range(n)] for _ in range(J)]
    n = trajectories_length[start_stop]
    RMSE = np.zeros([1, n - 1])
    length = int(len(training_sets) / J)
    for j in range(J):  # 3
        print('Iterator {}'.format(j + 1))
        training_set = np.concatenate((training_sets[:j * length], training_sets[(j + 1) * length:])).T  # 4 T-j
        validation_set = training_sets[j * length:(j + 1) * length].T  # 5 Tj
        for l in range(n - 1):  # n = len(t), n is not sure
            delay = np.mean(training_set[l + 1:] - training_set[l], axis=1).reshape((n - l - 1, 1))  # t delay, l+h
            prediction_set = np.tile(validation_set[l], (np.shape(delay)[0], 1)) + delay
            # 7 calculate rmse
            RMSE[j][l] = np.mean(np.sqrt(np.mean(np.power(prediction_set - validation_set[l + 1:], 2), axis=0)))
    RMSEu = np.mean(RMSE, axis=0)
    RMSEv = np.var(RMSE, axis=0)
    print('RMSE average:{}'.format(RMSEu))
    print('RMSE variance:{}'.format(RMSEv))
    print('From stop:{}, '.format(start_stop))
