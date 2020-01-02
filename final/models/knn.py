import numpy as np
from collections import defaultdict


def nearest_neighbors(training_data, act_seq_id, act_time, k=10):
    diff_array = np.abs(training_data[:, act_seq_id] - act_time)
    return training_data[diff_array.argsort()[:k]]


def predict(training_data, testing_data):
    res_dict = defaultdict(list)
    traj_len = len(testing_data[0])
    for each_traj in testing_data:
        for seq_id in range(0, traj_len-1):
            knn_traj = nearest_neighbors(training_data, seq_id, each_traj[seq_id])
            tmp_traj = knn_traj[:, seq_id+1:]
            tmp_traj = tmp_traj - knn_traj[:, seq_id].reshape(10, 1)
            delta_pred_traj = np.mean(tmp_traj, axis=0)
            res_dict[seq_id].append((delta_pred_traj + each_traj[seq_id]).tolist())
    return res_dict
