import numpy as np
from collections import defaultdict


def train(training_data):
    """

    :param training_data: of shape(traj_seq_id, stop_seq_id, agg_time)
    :return: delay_paras: of shape(stop_seq_id, avg_agg_time)
    """
    return np.mean(training_data, axis=0)


def predict(paras, testing_data):
    res_dict = defaultdict(list)
    traj_len = len(testing_data[0])
    for each_traj in testing_data:
        for seq_id in range(0, traj_len-1):
            res_dict[seq_id].append((np.array(paras[seq_id+1:]) + (each_traj[seq_id] - paras[seq_id])).tolist())
    return res_dict
