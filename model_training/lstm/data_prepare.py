import pandas as pd
import numpy as np
import csv


def preprocessing(root_dir, output_dir):
    df = pd.read_csv(root_dir)
    group_by_direction = df.groupby(["direction"])
    columns = [["trip_id", "start", "cur_time", "cur_dis", "next_dis", "target"]]
    training_sets = {"I": columns.copy(), "O": columns.copy()}
    for name, group in group_by_direction:
        print("process", name, "data")
        group_by_id = group.groupby(["trip_id"])
        for trip_id, trip in group_by_id:
            print("process trip", trip_id)
            # TODO: add an inbound and outbound notation
            X = np.array([[trip_id for _ in range(len(trip["np_time"]) - 1)], np.array(trip["np_time"][:-1]) / 10e5, trip["cum_time"][:-1], trip["cum_distance"][:-1],
                          trip["cum_distance"][1:],  trip["cum_time"][1:]]).T
            training_sets[name].extend(X)
    print("---Write data---")
    for key, value in training_sets.items():
        with open(output_dir+key+".csv", "w", encoding='utf-8') as csv_out:
            cw = csv.writer(csv_out)
            cw.writerows(value)


def main():
    home_dir = "/Users/ruixinhua/Documents/BusGPS/BusGPS/"
    bus_number = "46"
    root_meters_dir = home_dir + "processed/gps_meters_trips/" + bus_number + "/gps_meters.csv"
    root_stops_dir = home_dir + "processed/gps_stop_trips/" + bus_number + "/gps_stops.csv"
    rnn_trips_dir = home_dir + "processed/rnn_trips/" + bus_number + "/"
    preprocessing(root_meters_dir, rnn_trips_dir+"lstm_meters")
    preprocessing(root_stops_dir, rnn_trips_dir+"lstm_stops")


if __name__ == "__main__":
    main()

