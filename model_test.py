import csv
import time

import numpy as np
import pandas as pd

from bus_evaluation import evaluate
from bus_prediction import delay_predict, kernel_predict
from model_training import delay_model, kernel_model


def load_data(gps_dir):
    df = pd.read_csv(gps_dir)
    return np.array(df["cum_time"])


def load_in_and_out(root_dir, n):
    """

    :param root_dir: load
    :param n:
    :return:
    """
    df = pd.read_csv(root_dir)
    group_by_direction = df.groupby(["direction"])
    training_sets = {"I": [], "O": []}
    for name, group in group_by_direction:
        group_by_id = group.groupby(["trip_id"])
        for _, trip in group_by_id:
            training_sets[name].append(np.array(trip["cum_time"]))
    return training_sets["I"][:n], training_sets["O"][:n]


def delay_model_test(sets):
    np.random.shuffle(sets)
    test_ratio = int(0.2 * len(sets))
    training_sets, test_sets = sets[test_ratio:], sets[:test_ratio]
    MAE, MAPE, count = 0, 0, 0
    delay = delay_model.training(training_sets)
    K = len(test_sets[0])
    for test_set in test_sets:
        for l in range(1, K - 1):
            if min(test_set[l:]) <= 0.0:
                continue
            predict_set = delay_predict(test_set[:l], delay)
            ae, ape, c = evaluate(test_set[l:], predict_set[l:])
            MAE, MAPE, count = ae + MAE, ape + MAPE, count + c
    MAE, MAPE = MAE / count, MAPE / count
    MAE, MAPE = round(MAE, 2), round(MAPE, 4)
    print("delay MAE:", MAE)
    print("delay MAPE:", MAPE)
    return MAE, MAPE


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


def kernel_model_test(sets):
    np.random.shuffle(sets)
    test_ratio = int(0.2 * len(sets))
    training_sets, test_sets = sets[test_ratio:], sets[:test_ratio]
    MAE, MAPE, count = 0, 0, 0
    kernel = kernel_model.training(training_sets)
    K = len(test_sets[0])
    for test_set in test_sets:
        t = test_set
        Tm = training_sets
        kern_weights = np.array([[(ti - tm_i) ** 2 / var for ti, tm_i, var in zip(t, tm, kernel)] for tm in Tm])
        kern_weight_sum = -kern_weights[:, 0]
        for l in range(1, K - 1):
            if min(test_set[l:]) <= 0.0:
                continue
            kern_weight_sum -= kern_weights[:, l]
            kern_weight = np.exp(kern_weight_sum)
            if not np.sum(kern_weight):
                print(np.sum(kern_weight))
                continue
            predict_set = kernel_predict(test_set[:l], training_sets, kern_weight)
            ae, ape, c = evaluate(test_set[l:], predict_set[l:])
            MAE, MAPE, count = ae + MAE, ape + MAPE, count + c
    MAE, MAPE = MAE / count, MAPE / count
    MAE, MAPE = round(MAE, 2), round(MAPE, 4)
    print("kernel MAE:", MAE)
    print("kernel MAPE:", MAPE)
    return MAE, MAPE


def test_model(model, sets):
    start_time = time.time()
    MAE, MAPE = model(sets)
    time_finished = round(time.time() - start_time, 2)
    print("Time usage {}:".format(model.__name__), time_finished, "s")
    return time_finished, MAE, MAPE


def test_data(root_dir, out_dir):
    results = [["Model", "Trips Size", "Direction", "Trips Length", "Time Used(s)", "MAE", "MAPE"]]
    trips_count = [500, 2000, -1]
    start_time = time.time()
    training_sets_in, training_sets_out = load_in_and_out(root_dir, -1)
    print("Load data, time usage:", time.time() - start_time, "s")
    for count in trips_count:
        print("trips count:", count)
        training_sets = [training_sets_in[:count], training_sets_out[:count]]
        directions = ["Inbound", "Outbound"]
        for index in range(len(training_sets)):
            sets = training_sets[index]
            direction = directions[index]
            print("Test of", direction, "trips")
            print("delay model test")
            time_used, MAE, MAPE = test_model(delay_model_test, sets)
            results.append(["delay model", len(sets), direction, len(sets[-1]), time_used, MAE, MAPE])
            print("kernel model test")
            time_used, MAE, MAPE = test_model(kernel_model_test, sets)
            results.append(["kernel model", len(sets), direction, len(sets[-1]), time_used, MAE, MAPE])
    print("---Write data---")
    with open(out_dir, "w", encoding='utf-8') as csv_out:
        cw = csv.writer(csv_out)
        cw.writerows(results)


def main():
    home_dir = "/Users/ruixinhua/Documents/BusGPS/BusGPS/"
    bus_number = "46"
    root_meters_dir = home_dir + "processed/gps_meters_trips/" + bus_number + "/gps_meters.csv"
    root_stops_dir = home_dir + "processed/gps_stop_trips/" + bus_number + "/gps_stops.csv"
    for i in range(5):
        print("---Test number", (i+1))
        print("---Test meters data---")
        test_data(root_meters_dir, home_dir + "result/results_meters{}.csv".format(i))
        print("---Test stops data---")
        test_data(root_stops_dir, home_dir + "result/results_stops{}.csv".format(i))


if __name__ == "__main__":
    main()
