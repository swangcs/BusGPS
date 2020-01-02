import os
import csv
import time
import math
import numpy as np
from final.models import delay, knn, kr, additive


def load_data(home_dir):
    full_data_dict = {}
    full_data_list = []
    with os.scandir(home_dir) as entries:
        for entry in entries:
            entry_name = entry.name
            if entry.is_file() and entry_name.endswith(".csv"):
                seq_id = int(entry_name.split("_")[0])
                each_traj = []
                with open(home_dir + entry_name, "r") as csv_in:
                    cr = csv.reader(csv_in)
                    next(cr, None)  # skip header
                    for row in cr:
                        each_traj.append(int(row[1]))
                full_data_dict[seq_id] = each_traj
    for i in range(0, len(full_data_dict.keys())):
        full_data_list.append(full_data_dict[i])
    return np.array(full_data_list)


def epoch_2_sec(epoch_time):
    local_time = time.localtime(epoch_time)
    hours = local_time.tm_hour
    mins = local_time.tm_min
    secs = local_time.tm_sec
    return hours * 3600 + mins * 60 + secs


def load_data_additive(home_dir):
    full_data_dict = {}
    full_data_list = []
    with os.scandir(home_dir) as entries:
        for entry in entries:
            entry_name = entry.name
            if entry.is_file() and entry_name.endswith(".csv"):
                names = entry_name.split("_")
                seq_id = int(names[0])
                dep_time = epoch_2_sec(int(names[1][:-4]))
                each_traj = []
                with open(home_dir + entry_name, "r") as csv_in:
                    cr = csv.reader(csv_in)
                    next(cr, None)  # skip header
                    for row in cr:
                        each_traj.append([float(row[0]), dep_time, int(row[1])])
                full_data_dict[seq_id] = each_traj
    for i in range(0, len(full_data_dict.keys())):
        full_data_list.append(full_data_dict[i])
    return np.array(full_data_list)


def split_X_y(loaded_additive_data, train=True):
    X=[]
    y=[]
    num_traj = loaded_additive_data.shape[0]
    num_seq = loaded_additive_data.shape[1]
    for ind_traj in range(0, num_traj):
        traj = loaded_additive_data[ind_traj]
        for ind_seq in range(0, num_seq):
            ele = traj[ind_seq]
            if train:
                X.append([ele[0], ele[1]])
                y.append([ele[2]])
            else:
                if ele[0] > 0.0:  # do not test the first bus stop
                    X.append([ele[0], ele[1]])
                    y.append([ele[2]])
    return np.array(X), np.array(y)


def split_data(full_data, data_count):
    training_count = int(data_count * 0.8)
    training_data = full_data[:training_count]
    testing_data = full_data[training_count:data_count]
    return np.array(training_data), np.array(testing_data)


def write_pred(out_dir, pred_dict):
    for k, v in pred_dict.items():
        out_file_name = str(k) + ".csv"
        with open(out_dir+out_file_name, "w") as csv_out:
            cw = csv.writer(csv_out)
            cw.writerows(v)


def error_analysis(pred_dict, test_data):
    N = len(test_data)
    K = len(test_data[0])
    mae, rmse, mape = 0.0, 0.0, 0.0
    # i:(1 -> N)
    for traj_count, traj_item in enumerate(test_data):
        # k:(1 -> K-1)
        for k in range(0, K-1):
            rmse_inner = 0.0
            for i in range(k+1, K):
                act_value = traj_item[i]
                pred_value = pred_dict[k][traj_count][i-k-1]
                diff = abs(act_value - pred_value)
                mae += diff
                rmse_inner += (diff**2)
                if act_value > 0:
                    mape += (diff/act_value)
            rmse += ((rmse_inner/(K-k))**0.5)
    mae = (mae*2)/(N*K*(K-1))
    rmse = rmse/(N*(K-1))
    mape = (mape*2*100)/(N*K*(K-1))
    print("MAE:", mae)
    print("RMSE:", rmse)
    print("MAPE(%):", mape)


def error_analysis_additive(y_pred, y_test):
    abs_diff = np.abs(y_pred-y_test)
    relative = np.divide(abs_diff, y_test, out=np.zeros_like(abs_diff), where=y_test!=0)
    sq_diff = np.square(y_pred-y_test)
    print("MAE:", np.mean(abs_diff))
    print("RMSE:", math.sqrt(np.sum(sq_diff))/sq_diff.shape[0])
    print("MAPE(%):", np.mean(relative)*100)


def main():
    traj_type_group = ["dist", "stop"]
    data_count_group = [500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4311]

    # traj_type_group = ["stop"]
    # data_count_group = [500]

    for traj_type in traj_type_group:
        home_dir = "/Users/shenwang/Desktop/busgps/data/46_outbound_trips/" + traj_type + "/"
        input_data_dir = home_dir + "input/"
        full_data = load_data(input_data_dir)
        print("====== New Test ======")
        print("Trajectory Type: ", traj_type)
        for data_count in data_count_group:

            # out_pred_dir = home_dir+"output/"+str(data_count)+"/"

            train_data, test_data = split_data(full_data, data_count)

            print("====== DELAY MODEL ======")
            print("Total Trips: ", data_count)
            start_time = time.time()
            paras = delay.train(train_data)
            print("Training: ", time.time()-start_time)

            start_time = time.time()
            pred_res = delay.predict(paras, test_data)
            print("Predicting: ", time.time()-start_time)
            # write_pred(out_pred_dir, pred_res)
            error_analysis(pred_res, test_data)

            print("====== KNN MODEL ======")
            start_time = time.time()
            pred_res = knn.predict(train_data, test_data)
            print("Predicting: ", time.time()-start_time)
            error_analysis(pred_res, test_data)

            print("====== KR MODEL ======")
            start_time = time.time()
            paras = kr.train(train_data)
            print("Training: ", time.time()-start_time)

            start_time = time.time()
            pred_res = kr.predict(paras, train_data, test_data)
            print("Predicting: ", time.time()-start_time)
            # # write_pred(out_pred_dir, pred_res)
            error_analysis(pred_res, test_data)
            print("====== Group END ======")

    # for traj_type in traj_type_group:
    #     home_dir = "/Users/shenwang/Desktop/busgps/data/46_outbound_trips/" + traj_type + "/"
    #     input_data_dir = home_dir + "input/"
    #     full_data = load_data_additive(input_data_dir)
    #     print("====== New Test ======")
    #     print("Trajectory Type: ", traj_type)
    #     for data_count in data_count_group:
    #
    #         train_data, test_data = split_data(full_data, data_count)
    #
    #         X_train, y_train = split_X_y(train_data)
    #         X_test, y_test = split_X_y(test_data, train=False)
    #
    #         start_time = time.time()
    #         bam = additive.train(X_train, y_train)
    #         print("Training: ", time.time()-start_time)
    #
    #         start_time = time.time()
    #         y_pred = additive.predict(bam, X_test)
    #         print("Predicting: ", time.time()-start_time)
    #         error_analysis_additive(y_pred, y_test)
    #         print("====== Group END ======")


if __name__ == '__main__':
    main()
