import os
import time
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


def load_bus_trips_format2(home_dir, bus_number):
    """
    load data format 2 bus trips with meters and stops trips
    :param home_dir: it is the dirctory of your home path
    :param bus_number: load the trips of corresponding bus number
    :return: meter
    """
    root_meters_dir = home_dir + "processed/meter_trips/" + bus_number + "/"
    root_stops_dir = home_dir + "processed/stop_trips/" + bus_number + "/"
    meter_trips_in, meter_trips_out = load_trips(root_meters_dir)
    stop_trips_in, stop_trips_out = load_trips(root_stops_dir)
    return meter_trips_in, meter_trips_out, stop_trips_in, stop_trips_out


def load_trips(root_dir):
    """

    :param root_dir: load the files in the directory
    :return:
    """
    trips_gps = {}
    trips_files = os.listdir(root_dir)
    np.random.shuffle(trips_files)
    standard_scale = StandardScaler(with_mean=True, with_std=True)
    # split data to
    for trip_file in trips_files:
        if trip_file.endswith(".csv"):
            df = pd.read_csv(root_dir + trip_file)
            departure_time = int(str(trip_file.split("_")[1]).replace(".csv", ""))
            local_time = time.localtime(departure_time)
            departure_time = local_time.tm_hour * 3600 + local_time.tm_min * 60 + local_time.tm_sec
            agg_dis = np.array(df["aggregated_dist"])
            agg_time = np.array(df["agg_time"])
            departure_time = np.tile(departure_time, agg_time.shape[0])
            dis_time = np.array([departure_time, agg_dis, agg_time], dtype=np.float64).T
            trip_len = len(departure_time)
            if trip_len not in trips_gps:
                trips_gps[trip_len] = []
            trips_gps[trip_len].append(dis_time)
    # apply zero-mean normalization on data
    trips_gps_in_len, trips_gps_out_len = list(trips_gps.keys())[0], list(trips_gps.keys())[1]
    trips_gps_in, trips_gps_out = np.array(trips_gps[trips_gps_in_len]), np.array(trips_gps[trips_gps_out_len])
    trips_gps_in = trips_gps_in.reshape(-1, trips_gps_in.shape[2])
    trips_gps_out = trips_gps_out.reshape(-1, trips_gps_out.shape[2])
    # normalization departure time and aggregated distance
    trips_gps_in = np.concatenate([standard_scale.fit_transform(trips_gps_in[..., :2]), np.array([trips_gps_in[..., 2]]).T], axis=1)
    trips_gps_out = np.concatenate([standard_scale.fit_transform(trips_gps_out[..., :2]), np.array([trips_gps_out[..., 2]]).T], axis=1)
    # reshape to the origin list
    trips_gps_in = trips_gps_in.reshape((-1, trips_gps_in_len, trips_gps_in.shape[1]))
    trips_gps_out = trips_gps_out.reshape((-1, trips_gps_out_len, trips_gps_out.shape[1]))
    # reshape the list and add a new column with next distance
    # trips_gps_in = np.array([np.array([trip[..., 0][:-1], trip[..., 1][:-1], trip[..., 1][1:], trip[..., 2][:-1]]).T for trip in trips_gps_in])
    # trips_gps_out = np.array([np.array([trip[..., 0][:-1], trip[..., 1][:-1], trip[..., 1][1:], trip[..., 2][:-1]]).T for trip in trips_gps_out])

    return trips_gps_in, trips_gps_out


# if __name__ == "__main__":
#     home_dir = "/Users/ruixinhua/Documents/BusGPS/BusGPS/"
#     trips = load_bus_trips_format2(home_dir, "46")
