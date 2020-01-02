import numpy as np
from collections import defaultdict


def train(training_data):
    np_var = np.var(training_data, axis=0).reshape(1, len(training_data[0]))
    np_ones = np.ones(np_var.shape)
    return np.maximum(np_var, np_ones)


def kernel(act_traj, train_traj, var, b=1):
    term = np.square(act_traj-train_traj[:, ])/var
    return np.exp((-1.0/b)*(np.sum(term, axis=1)))


def predict(paras, training_data, testing_data):
    res_dict = defaultdict(list)
    traj_len = len(testing_data[0])
    for each_traj in testing_data:
        for seq_id in range(0, traj_len-1):
            tmp_kern = kernel(each_traj[:seq_id + 1], training_data[:, :seq_id + 1],
                              paras[:, :seq_id + 1]).reshape(training_data.shape[0], 1)
            term = training_data[:, seq_id+1:] - training_data[:, seq_id].reshape(training_data.shape[0], 1)
            num = np.sum(np.multiply(tmp_kern, term), axis=0)
            denom = np.sum(tmp_kern, axis=0)
            res_dict[seq_id].append((each_traj[seq_id] + (num/denom)).tolist())
    return res_dict
