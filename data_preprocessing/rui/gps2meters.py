import csv
import os
from collections import defaultdict

import pandas as pd
from scipy import spatial

__author__ = "swang"


def load_def_trips(def_trips_dir, step):
    def_trips = defaultdict(list)
    with os.scandir(def_trips_dir) as entries:
        for entry in entries:
            entry_name = entry.name
            if entry.is_file() and entry_name.endswith(".csv"):
                with open(def_trips_dir + entry_name, "r", encoding='utf-8') as csv_in:
                    cr = pd.read_csv(csv_in)
                    dis_traveled = cr["shape_dist_traveled"]
                    max_dis = dis_traveled[len(dis_traveled) - 1]
                    for i in range(0, int(max_dis), step):
                        def_trips[entry_name].append(i)
    return def_trips


def nearest_meter_gps(gps_trips_dir, def_trips, gps_meters_trips_dir):
    with os.scandir(gps_trips_dir) as entries:
        for entry in entries:
            entry_name = entry.name
            if entry.is_file() and entry_name.endswith(".csv"):

                # 1 construct a kd-tree after iterating each gps_trip
                gps_trips = {}  # key: location
                locations = []
                cum_times = []
                speeds = []
                time_seq = []
                agg_time, cum_dis = 0, 0
                with open(gps_trips_dir + entry_name, "r") as csv_in:
                    cr = csv.reader(csv_in)
                    next(cr, None)  # skip header
                    for i in cr:
                        del_time = float(i[3]) if i[3] else 0
                        del_dis = float(i[4]) if i[4] else 0
                        speed = del_dis / del_time if del_time else 0
                        agg_time += del_time
                        cum_dis += del_dis
                        locations.append((0, cum_dis))
                        speeds.append(speed)
                        cum_times.append(agg_time)
                        time_seq.append(float(i[0]))
                del locations[-1], speeds[0], cum_times[-1]
                for l, t, s in zip(locations, cum_times, speeds):
                    gps_trips[l] = (t, s)
                kd_tree = spatial.cKDTree(locations)
                start_time = int(time_seq[0] / 10e5)

                # 2 for each row in def_trip with bus stops only,
                # generate its corresponding information of its nearest point in gps_trip
                gps_meters_trip = [["aggregated_dist", "agg_time"]]
                def_trip_file = entry_name.split("_")[2]
                print("def_trip_file:", def_trip_file)
                for i in def_trips[def_trip_file]:
                    aggregated_dist = i
                    _, ind = kd_tree.query((0, aggregated_dist))
                    nearest_point = locations[ind]
                    agg_time, speed = gps_trips[nearest_point]
                    del_time = (aggregated_dist - nearest_point[1]) / speed
                    if del_time < 0:
                        kd_tree = spatial.cKDTree(locations[:ind])
                        _, ind = kd_tree.query((0, aggregated_dist))
                        nearest_point = locations[ind]
                        agg_time, speed = gps_trips[nearest_point]
                        del_time = (aggregated_dist - nearest_point[1]) / speed
                        # print("delta time", del_time)
                    agg_time += del_time
                    max_time = gps_trips[locations[min(ind+1, len(locations) - 1)]][0]
                    if agg_time > max_time:
                        # print('error:', agg_time, max_time)
                        agg_time = max_time
                    new_row = [aggregated_dist, int(agg_time)]
                    gps_meters_trip.append(new_row)
                    # del locations[:ind]  # re-construct kd-tree to ensure the timestamp is not decreasing
                    kd_tree = spatial.cKDTree(locations)
                global trip_id
                with open(gps_meters_trips_dir + str(trip_id) + "_" + str(start_time) + ".csv", "w", encoding='utf-8') as csv_out:
                    cw = csv.writer(csv_out)
                    cw.writerows(gps_meters_trip)
                    trip_id += 1
            else:
                print("def_trip_file:" + entry_name)


def main():
    home_dir = "/Users/ruixinhua/Documents/BusGPS/BusGPS/"
    bus_line_number = "46"
    step = 100
    gps_trips_dir = home_dir + "processed/gps_trips/" + bus_line_number + "/"
    def_trips_dir = home_dir + "processed/def_trips/" + bus_line_number + "/"
    gps_meters_trips_dir = home_dir + "processed/meter_trips/" + bus_line_number + "/"
    # 1. load defined trips with bus stops only
    def_trips = load_def_trips(def_trips_dir, step)
    if not os.path.exists(gps_meters_trips_dir):
        # create if not exist
        os.mkdir(gps_meters_trips_dir)
    for gps_trips_day_dir in os.listdir(gps_trips_dir):
        if len(gps_trips_day_dir) != 8:
            continue
        # for each input gps_trip, output gps_meters_trip with the same file name
        nearest_meter_gps(gps_trips_dir + gps_trips_day_dir + "/", def_trips, gps_meters_trips_dir)


if __name__ == '__main__':
    trip_id = 0
    main()
