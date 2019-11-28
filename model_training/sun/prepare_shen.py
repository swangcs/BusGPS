import pandas as pd
import time
import numpy as np
import os
import re
import csv
from model_evaluation.bus_evaluation import evaluate as evaluate
from model_training.sun.model_KNN import KNN
from model_training.sun.model_additive import predict_additive, additive as additive


def readString(string):
    return re.findall(r'\d+', string)


def read_fileName(file_dir):
    file = []
    for fileName in os.walk(file_dir):
        file.append(fileName)
    return file


def load_trips(root_dir):
    """
    :param root_dir: load the files in the directory
    :return:
    """
    file = []
    trips_gps_time = []
    trips_gps_dist = []
    trips_files = os.listdir(root_dir)
    np.random.shuffle(trips_files)
    for trip_file in trips_files:
        df = pd.read_csv(root_dir + trip_file)
        trips_gps_time.append(np.array(df["agg_time"], dtype=np.int))
        trips_gps_dist.append(np.array(df["aggregated_dist"], dtype=np.int))
        file.append(trip_file)
    return trips_gps_dist, trips_gps_time, file


def read_csv(file: str, sep=',', names=None):
    return pd.read_csv(file, sep=sep, na_values=['null'], dtype={'np_time': int},
                       names=names)


def stamp_transform(stamp):
    timeArray = time.localtime(stamp)
    otherStyleTime = time.strftime("%H:%M:%S", timeArray)
    timeArray = time.strptime(otherStyleTime, '%H:%M:%S')
    timeStamp = int(time.mktime(timeArray))
    return timeStamp


def sampleNum(data_type, direction):
    sample = 0
    if data_type == "meter" and direction == 'I':
        sample = 200
    elif data_type == "meter" and direction == 'O':
        sample = 191
    elif data_type == "stop" and direction == 'I':
        sample = 63
    elif data_type == "stop" and direction == 'O':
        sample = 59
    return sample


def process_data(data_type, data_size, root_meters_dir, root_stops_dir):
    if data_type == 'meter':
        trips_dist, trips_time, departureTime = load_trips(root_meters_dir)
    else:
        trips_dist, trips_time, departureTime = load_trips(root_stops_dir)

    tmp = [[] for _ in range(4)]
    tmp_in = [[] for _ in range(4)]
    tmp_out = [[] for _ in range(4)]

    for i in range(len(departureTime)):
        num = readString(departureTime[i])
        tmp[0].append(int(num[0]))
        tmp[1].append(int(num[1]))
        tmp[2].append(list(trips_time[i]))
        tmp[3].append(list(trips_dist[i]))
    tmp = np.array(tmp).transpose()
    tmp = tmp[np.lexsort(tmp[:, ::-1].T)]
    # for i in range(len(tmp)):
    #     tmp[i][1] = stamp_transform(tmp[i][1])
    np.random.shuffle(tmp)
    trip_length = 63
    count = data_size
    training_sets_in, training_sets_out = [], []
    for trip in tmp[:count]:
        if len(trip[2]) == trip_length:
            training_sets_in.append(trip)
        else:
            training_sets_out.append(trip)
    print("In {}, out {}".format(len(training_sets_in), len(training_sets_out)))
    for i in range(len(training_sets_in)):
        for j in range(len(training_sets_in[i][2])):
            tmp_in[0].append(training_sets_in[i][0])
            tmp_in[1].append(training_sets_in[i][1])
            tmp_in[2].append(training_sets_in[i][2][j])
            tmp_in[3].append(training_sets_in[i][3][j])
    tmp_in = np.array(tmp_in).transpose()
    for i in range(len(training_sets_out)):
        for j in range(len(training_sets_out[i][2])):
            tmp_out[0].append(training_sets_out[i][0])
            tmp_out[1].append(training_sets_out[i][1])
            tmp_out[2].append(training_sets_out[i][2][j])
            tmp_out[3].append(training_sets_out[i][3][j])
    tmp_out = np.array(tmp_out).transpose()
    X_in = tmp_in[:, [1, 3]]
    y_in = tmp_in[:, 2]
    X_out = tmp_out[:, [1, 3]]
    y_out = tmp_out[:, 2]
    return X_in, y_in, X_out, y_out


def test_additive(data_type, data_size, root_meters_dir, root_stops_dir, out_meters_dir, out_stops_dir):
    print("---", "Test additive by", data_type, "with length of", data_size, "---")
    X_in, y_in, X_out, y_out = process_data(data_type, data_size, root_meters_dir, root_stops_dir)
    direction = ['I', 'O']
    training_time = []
    predict_time = []
    time_train = 0
    time_predict = 0
    results = []
    MAE = []
    MAPE = []
    RMSE = []
    for i in range(len(direction)):
        id = 0
        if direction[i] == 'I':
            tra, pre, res = additive(X_in, y_in, len(y_in)/sampleNum(data_type, direction[i]), sampleNum(data_type, direction[i]))
        else:
            tra, pre, res = additive(X_out, y_out, len(y_out)/sampleNum(data_type, direction[i]), sampleNum(data_type, direction[i]))
        training_time.append(tra)
        predict_time.append(pre)
        results.append(res)
        for result in np.array(results[i]):
            with open(out_stops_dir + "matrix" + str(id) + direction[i] + ".csv", "w", encoding='utf-8') as csv_out:
                cw = csv.writer(csv_out)
                cw.writerows(result)
            id += 1
        a, b, c = evaluate(results[i])
        MAE.append(a)
        MAPE.append(b)
        RMSE.append(c)

    for i in range(len(training_time)):
        time_train += training_time[i]
        time_predict += predict_time[i]

    mae = np.mean(MAE)
    mape = np.mean(MAPE)
    rmse = np.mean(RMSE)

    return time_train, time_predict, mae, mape, rmse


def test_KNN(data_type, data_size, root_meters_dir, root_stops_dir, out_meters_dir, out_stops_dir):
    print("---", "Test KNN by", data_type, "with length of", data_size, "---")
    X_in, y_in, X_out, y_out = process_data(data_type, data_size, root_meters_dir, root_stops_dir)
    direction = ['I', 'O']
    predict_time = []
    time_predict = 0
    id = 0
    results = []
    MAE = []
    MAPE = []
    RMSE = []
    for i in range(len(direction)):
        if direction[i] == 'I':
            res, pre = KNN(y_in, int(len(y_in)/sampleNum(data_type, direction[i])), 'I')
            results.append(res)
            predict_time.append(pre)
        else:
            res, pre = KNN(y_out, int(len(y_out)/sampleNum(data_type, direction[i])), 'O')
            results.append(res)
            predict_time.append(pre)

        for result in np.array(results[i]):
            with open(out_stops_dir + "matrix" + str(id) + direction[i] + ".csv", "w", encoding='utf-8') as csv_out:
                cw = csv.writer(csv_out)
                cw.writerows(result)
            id += 1
        a, b, c = evaluate(results[i])
        MAE.append(a)
        MAPE.append(b)
        RMSE.append(c)
    for i in range(len(predict_time)):
        time_predict += predict_time[i]

    mae = np.mean(MAE)
    mape = np.mean(MAPE)
    rmse = np.mean(RMSE)
    return time_predict, mae, mape, rmse


def main():
    home_dir = "/Users/letv/Desktop/IntelligentTraffic/datasets/"
    bus_number = "46"
    root_meters_dir = home_dir+"shen_dataset/meter_trips/"+bus_number+"/"
    root_stops_dir = home_dir+"shen_dataset/stop_trips/"+bus_number+"/"
    out_meters_dir = home_dir+"test_result/meter_trips/"+bus_number+"/"
    out_stops_dir = home_dir+"test_result/stop_trips/"+bus_number+"/"

    # Test for KNN model
    time_predict, mae, mape, rmse = test_KNN('stops', 1000, root_meters_dir, root_stops_dir, out_meters_dir, out_stops_dir)
    print()
    print("Total predicting time is: ", time_predict)
    print("MAE is:", mae)
    print("MAPE is:", mape)
    print("RMSE is:", rmse)

    # Test for Additive model
    tme_train, time_predict, mae, mape, rmse = test_additive('stop', 1000, root_meters_dir, root_stops_dir, out_meters_dir, out_stops_dir)
    print()
    print("Total predicting time is:", time_predict)
    print("MAE is:", mae)
    print("MAPE is:", mape)
    print("RMSE is:", rmse)


if __name__ == "__main__":
    main()

