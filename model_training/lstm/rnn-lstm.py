import csv
import os
import time

import numpy as np
from tensorflow.losses import huber_loss
from keras import optimizers
from keras.initializers import glorot_normal
from keras.layers import Dense, LSTM
from keras.models import Sequential, load_model
from sklearn.preprocessing import StandardScaler
from bus_evaluation import evaluate
from load_data import load_bus_trips_format2
import threading


def training(train_x, train_y):
    print("---Training model---")
    model = Sequential()
    model.add(LSTM(128, input_shape=(None, 4)))
    # model.add(BatchNormalization())
    model.add(Dense(1))
    # set the parameters of sgd optimizer
    sgd = optimizers.SGD(lr=0.0001, momentum=0.95)
    model.compile(
        loss=huber_loss,
        optimizer=sgd
    )
    # split the training set based on the length of trips
    training_len = {}
    max_len = 0
    for x, y in zip(train_x, train_y):
        x_len = len(x)
        if x_len > max_len:
            max_len = x_len
        if x_len not in training_len:
            training_len[x_len] = {"x": [], "y": []}
        training_len[x_len]["x"].append(x)
        training_len[x_len]["y"].append(y)
    training_x_y = np.array(list(training_len.values()))
    np.random.shuffle(training_x_y)
    for value in training_x_y:
        trip_len = len(value["x"][-1])
        # add iterations
        epochs = 5 if trip_len > 20 else 10
        print("Trip length:", trip_len)
        model.fit(np.array(value["x"]), np.array(value["y"]), epochs=epochs, batch_size=256)
    # lower the learning rate and train again
    sgd = optimizers.SGD(lr=0.00001, momentum=0.95)
    model.compile(
        loss=huber_loss,
        optimizer=sgd
    )
    for value in training_x_y:
        trip_len = len(value["x"][-1])
        print("Trip length:", trip_len)
        model.fit(np.array(value["x"]), np.array(value["y"]), epochs=5, batch_size=128)
    return model


def normalize(trips, standard_scale):
    start_time = time.time()
    # normalize the aggregated time
    trips_tmp = np.array(trips).reshape((-1, trips.shape[2]))
    agg_time = np.array(trips_tmp[..., -1]).reshape(-1, 1)
    agg_time = np.array(standard_scale.fit_transform(agg_time)).reshape(-1, trips.shape[1])
    trips_x = np.array([np.array([trip[..., 0][:-1], trip[..., 1][:-1], trip[..., 1][1:], agg_t[:-1]]).T
                        for trip, agg_t in zip(trips, agg_time)])
    # split train test based on trips, the ratio is 0.1
    train_test_ratio = int(0.1 * len(trips_x))
    trips_train_x, trips_test_x = trips_x[train_test_ratio:], trips_x[:train_test_ratio]
    trips_train_y, trips_test_y = agg_time[train_test_ratio:], agg_time[:train_test_ratio]
    train_y, test_y = np.array(trips_train_y[..., 1:]).reshape(-1), np.array(trips_test_y[..., 1:]).reshape(-1)
    # convert to format which can be trained by lstm neural network
    train_x, test_x = [], []
    for trip in trips_train_x:
        train_x.extend(np.array([trip[:i] for i in range(1, len(trip) + 1)]))
    for trip in trips_test_x:
        test_x.extend(np.array([np.array(trip[:i]) for i in range(1, len(trip) + 1)]))
    print("Normalize target usage:", time.time() - start_time)
    return train_x, train_y, test_x, test_y, trips_test_y


def rnn_predict(model, trips_test_x, trip_len):
    # prediction begins
    start_time = time.time()
    predict_results = []
    for l in range(trip_len):
        # predict the time of position at lth
        x = np.array([tmp[l] for tmp in trips_test_x])
        y = model.predict(x)
        #  use the predict result of last time predicted
        predict_result = np.array([np.append(t[:, 3], p) for t, p in zip(x, y)])
        for k in range(l, trip_len - 1):
            x = np.array([np.concatenate((tmp_x[k + 1][:, :3], np.array([y]).T), axis=1) for tmp_x, y in
                          zip(trips_test_x, predict_result)])
            y = model.predict(x)
            #  use the predict result of last time predicted
            predict_result = np.array([np.append(t[:, 3], p) for t, p in zip(x, y)])
        predict_results.append(predict_result)
    prediction_time_used = time.time() - start_time
    print("Time usage for prediction:", prediction_time_used)
    return predict_results, prediction_time_used


def write_to_csv(out_dir, data):
    with open(out_dir, "w", encoding='utf-8') as csv_out:
        cw = csv.writer(csv_out)
        cw.writerows(data)


def rnn_evaluation(predict_results, standard_scale, trips_test_y):
    # re-arrange the predict result
    predict_results_trip = np.array(
        [[result[i] for result in predict_results] for i in range(np.array(predict_results).shape[1])])
    # add the real trip at the end of the predict result
    predict_results = np.array(
        [np.append(result, [test], axis=0) for result, test in zip(predict_results_trip, trips_test_y)])
    # inverse predict result to origin scale
    predict_results = standard_scale.inverse_transform(predict_results)
    # only stored the integer in the prediction file
    predict_results = np.array(np.round(predict_results), dtype=int)
    # evaluate the result
    MAE, MAPE, RMSE = evaluate(predict_results)
    return MAE, MAPE, RMSE


def run_lstm(trips):
    # rnn_model_root_dir = home_dir + "model_training/lstm/" + bus_number + "/"
    print("Test for trip length:", trips.shape[1])
    standard_scale = StandardScaler(with_mean=True, with_std=True)
    # get the normalised data, trips_test_y is the target data group by trip, it is used for prediction
    train_x, train_y, test_x, test_y, trips_test_y = normalize(trips, standard_scale)
    start_time = time.time()
    # model_file = rnn_model_root_dir + "lstm{}".format(trips.shape[1]) + ".h5"
    # training model
    model = training(train_x, train_y)
    training_time_used = time.time() - start_time
    print("Time usage for training:", training_time_used)
    trip_len = trips.shape[1] - 1
    # group the x by trip
    trips_test_x = np.array(
        [np.array(test_x[i * trip_len:(i + 1) * trip_len]) for i in range(int(len(test_x) / trip_len) - 1)])
    # prediction begins, and get the prediction results
    predict_results, prediction_time_used = rnn_predict(model, trips_test_x, trip_len)
    MAE, MAPE, RMSE = rnn_evaluation(predict_results, standard_scale, trips_test_y)
    rnn_result.append(
        ["LSTM RNN", len(trips), trips.shape[1], training_time_used, prediction_time_used, MAE, MAPE, RMSE])
    print("---Write data---")
    out_dir = result_dir + "Result{}.csv".format(trips.shape[1])
    # write data format3 result file to result directory
    write_to_csv(out_dir, rnn_result)
    model_predict_dir = rnn_output_dir + "{}/".format(trips.shape[1])
    if not os.path.exists(model_predict_dir):
        os.mkdir(model_predict_dir)
    # write result to a file, the final result will stored in a single file
    for results in np.array(predict_results):
        global trip_test
        write_to_csv(model_predict_dir + str(trip_test) + ".csv", results)
        trip_test += 1


def main():
    start_time = time.time()
    trips_gps = load_bus_trips_format2(home_dir, bus_number)
    print("Load data usage:", time.time() - start_time)
    for trips in trips_gps:
        # It may occurs some bugs when operate multi-threading process
        # t = threading.Thread(target=run_lstm, args=(trips,))
        # t.start()
        run_lstm(trips)


if __name__ == "__main__":
    trip_test = 0
    # TODO change directory here
    home_dir = "/Users/ruixinhua/Documents/BusGPS/BusGPS/"
    # The prediction result is stored in the result directory
    result_dir = home_dir + "result/"
    rnn_output_dir = home_dir + "pred_res/rnn/"
    bus_number = "46"
    rnn_result = [["Model", "Trips Size", "Trips Length", "Training Time(s)", "Prediction Time(s)", "MAE", "MAPE", "RMSE"]]
    main()
