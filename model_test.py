import csv
import os
import time

import numpy as np
import pandas as pd

from bus_evaluation import evaluate
from bus_prediction import delay_predict, kernel_predict
from model_training import delay_model, kernel_model


def load_data(gps_dir):
    df = pd.read_csv(gps_dir)
    return np.array(df["cum_time"])


def load_trips(root_dir):
    """

    :param root_dir: load the files in the directory
    :return:
    """
    trips_gps = []
    trips_files = os.listdir(root_dir)
    np.random.shuffle(trips_files)
    for trip_file in trips_files:
        df = pd.read_csv(root_dir + trip_file)
        trips_gps.append(np.array(df["agg_time"], dtype=np.int))
    return trips_gps


def delay(training_sets, test_sets):
    start_time = time.time()
    delay = delay_model.training(training_sets)
    training_time = round(time.time() - start_time, 4)
    K = len(test_sets[0])
    results = []
    predict_time = 0
    start_time = time.time()
    for test_set in test_sets:
        result = [delay_predict(test_set[:l], delay) for l in range(1, K)]
        result.append(test_set)
        results.append(result)
    predict_time += (time.time() - start_time)
    return training_time, predict_time, results


def kern(tl, tl_m, var, b=1):
    """
    Gaussian kernel
    :param tl: current test data
    :param tl_m: the one of training data
    :param var: the variance of training data at l
    :param b: the super parameter b is 1
    :return:
    """
    return np.exp(-np.sum((tl - tl_m) ** 2 / var) / b)


def kernel(training_sets, test_sets):
    start_time = time.time()
    kernel = kernel_model.training(training_sets)
    training_time = round(time.time() - start_time, 4)
    K = len(test_sets[0])
    results = []
    # start prediction
    start_time = time.time()
    for test_set in test_sets:
        # loop the test data
        result = []
        t = test_set
        Tm = training_sets
        kern_weights = np.array([[(ti - tm_i) ** 2 / var for ti, tm_i, var in zip(t, tm, kernel)] for tm in Tm])
        kern_weight_sum = -kern_weights[:, 0]
        for l in range(1, K):
            # for every trip, calculate the left arrival time
            kern_weight_sum -= kern_weights[:, l]
            kern_weight = np.exp(kern_weight_sum)
            if not np.sum(kern_weight):
                kern_weight_sum = np.array(kern_weight_sum, dtype=np.float128)
                kern_weight = np.exp(kern_weight_sum)
                if not np.sum(kern_weight):
                    continue
                print(np.min(kern_weight))
            predict_set = kernel_predict(test_set[:l], training_sets, kern_weight)
            result.append(predict_set)
        result.append(test_set)
        results.append(result)
    predict_time = round(time.time() - start_time, 4)
    return training_time, predict_time, results


def test_model(model, sets, out_dir):
    np.random.shuffle(sets)
    test_ratio = int(0.2 * len(sets))
    training_sets, test_sets = sets[test_ratio:], sets[:test_ratio]
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    training_time, predict_time, results = model(training_sets, test_sets)
    print("Time usage {}: training".format(model.__name__), training_time, "s, predicting", predict_time, "s")
    return training_time, predict_time, results


def test_data(root_dir, result_dir, out_dir):
    result_eva = [
        ["Model", "Trips Size", "Trips Length", "Training Time(s)", "Prediction Time(s)", "MAE", "MAPE", "RMSE"]]
    trips_count = [i for i in range(3000, 4000, 1000)]
    start_time = time.time()
    trips = load_trips(root_dir)
    np.random.shuffle(trips)
    print("Load data, time usage:", time.time() - start_time, "s")
    for count in trips_count:
        print("trips count:", count)
        trip_length = len(trips[0])
        training_sets_in, training_sets_out = [], []
        for trip in trips[:count]:
            if len(trip) == trip_length:
                training_sets_in.append(trip)
            else:
                training_sets_out.append(trip)
        print("In {}, out {}".format(len(training_sets_in), len(training_sets_out)))
        training_model = [delay]
        for model in training_model:
            print("Test {}".format(model.__name__))
            model_predict_dir = out_dir + "{}/{}/".format(model.__name__, count)
            tt1, tp1, test_results = test_model(model, training_sets_in, model_predict_dir)
            tt2, tp2, tmp = test_model(model, training_sets_out, model_predict_dir)
            training_time = tt1 + tt2
            predict_time = tp1 + tp2
            test_results.extend(tmp)
            MAE, MAPE, RMSE = evaluate(test_results)
            for results in np.array(test_results):
                global trip_test
                with open(model_predict_dir + str(trip_test) + ".csv", "w", encoding='utf-8') as csv_out:
                    cw = csv.writer(csv_out)
                    cw.writerows(results)
                    trip_test += 1
            print("Test Finished")
            result_eva.append(
                [model.__name__, count, "{}/{}".format(len(training_sets_in[0]), len(training_sets_out[0])),
                 '%.4f' % training_time, '%.2f' % predict_time, round(MAE, 2), '%.2f' % (MAPE * 100) + '%',
                 round(RMSE, 2)])
    print("---Write data---")
    with open(result_dir, "w", encoding='utf-8') as csv_out:
        cw = csv.writer(csv_out)
        cw.writerows(result_eva)


def main():
    home_dir = "/Users/ruixinhua/Documents/BusGPS/BusGPS/"
    bus_number = "46"
    root_meters_dir = home_dir + "processed/meter_trips/" + bus_number + "/"
    root_stops_dir = home_dir + "processed/stop_trips/" + bus_number + "/"
    out_meters_dir = home_dir + "pred_res/meter_trips/" + bus_number + "/"
    out_stop_dir = home_dir + "pred_res/stop_trips/" + bus_number + "/"
    i = 2
    print("---Test number", (i + 1))
    print("---Test stops data---")
    test_data(root_stops_dir, home_dir + "result/results_stops{}.csv".format(i), out_stop_dir)
    print("---Test meters data---")
    test_data(root_meters_dir, home_dir + "result/results_meters{}.csv".format(i), out_meters_dir)


if __name__ == "__main__":
    trip_test = 0
    main()
