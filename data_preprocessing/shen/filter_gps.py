import pandas as pd
import numpy as np
import time
import os
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime


__author__ = "swang"


def load_gps(gps_path, columns, bus_line_number):
    """
    Load raw gps data which is filtered by given bus line.
    :param gps_path: the file path of a gps raw data file
    :param columns: the full columns of this raw data file
    :param bus_line_number: the bus line number you want to study
    :return: filtered dataframe
    """
    df_gps = pd.read_csv(gps_path, names=columns, dtype=str)
    return df_gps.loc[df_gps["line"] == bus_line_number, ["time", "lon", "lat", "vehicle", "vehicle_journey"]]


def get_def_trip_info(def_trips_dir):
    """
    Get basic info of pre-defined trips for filtering GPS data
    :param def_trips_dir: the home directory of pre-defined trips
    :return: travelled distance, duration, direction_vector, O/D locations
    """
    info = {}
    time_format = "%H:%M:%S"
    with os.scandir(def_trips_dir) as entries:
        for entry in entries:
            entry_name = entry.name
            if entry.is_file() and entry_name.endswith(".csv"):
                df_def_trip = pd.read_csv(def_trips_dir+entry_name)
                df_def_trip = df_def_trip[df_def_trip["stop_name"].notnull()]
                first_stop = df_def_trip.iloc[0]
                last_stop = df_def_trip.iloc[-1]
                dist = last_stop["shape_dist_traveled"]  # meters
                dep_time = first_stop["arrival_time"]
                arr_time = last_stop["arrival_time"]
                duration = (datetime.strptime(arr_time, time_format) - datetime.strptime(dep_time, time_format)).seconds
                # origin_lat, origin_lon, dest_lat, dest_lon
                od_loc = ((first_stop["lat"], first_stop["lon"]), (last_stop["lat"], last_stop["lon"]))
                direction_vector = (od_loc[1][0]-od_loc[0][0], od_loc[1][1]-od_loc[0][1])
                info[entry_name[:-4]] = (dist, duration, direction_vector, od_loc)
    return info


def write_data(df_dict, gps_trips_dir):
    """
    Write processed dataframe into csv by each gps trip (one trip per csv file).
    :param df_dict: each key-value pair represents a dataframe of a processed gps trip and its name
    :param gps_trips_dir: the directory of the output csv files
    :return: none
    """
    for key, value in df_dict.items():
        value.to_csv(gps_trips_dir + key + ".csv", index=False)  # do not output the dataframe index


def haversine(loc1, loc2, to_radians=True, earth_radius=6371):
    """
    slightly modified version: of http://stackoverflow.com/a/29546836/2901002

    Calculate the great circle distance (meters) between two points
    on the earth (specified in decimal degrees or in radians)

    All (lat, lon) coordinates must have numeric dtypes and be of equal length.

    """
    (lat1, lon1) = loc1
    (lat2, lon2) = loc2
    if to_radians:
        lat1, lon1, lat2, lon2 = np.radians([lat1, lon1, lat2, lon2])

    a = np.sin((lat2-lat1)/2.0)**2 + \
        np.cos(lat1) * np.cos(lat2) * np.sin((lon2-lon1)/2.0)**2

    return earth_radius * 2 * np.arcsin(np.sqrt(a)) * 1000.0


def split_gps_trip(df_gps, groupby_labels, thresh_time, def_trips_info):
    """
    Trip segmentation.
    :param df_gps: loaded gps data in dataframe
    :param groupby_labels: a list of strings
    :param thresh_time: time interval threshold
    :param def_trips_info: basic info of pre-defined trips
    :return: a dictionary of segmented trips. (k: string, v:dataframe)
    """
    gps_trips = {}  # key: trip_name, value: processed trajectory in dataframe
    grouped_df_gps = df_gps.groupby(groupby_labels)
    for name, group in grouped_df_gps:
        print("...processing group: %s ..." % str(name))
        # step 1. only keep the first, when consecutive rows have duplicated location
        new_group = group.drop_duplicates(["lat", "lon"], keep="first").drop(groupby_labels, axis=1)

        # step 2. split trajectory when time interval is beyond the given threshold
        new_group = new_group.reset_index(drop=True)
        new_group["dTime"] = (new_group["time"] - new_group["time"].shift(1))/(10**6)
        time_flags = new_group.index[new_group["dTime"] > thresh_time].tolist()
        # calculate distance interval to get the total travelled distance later.
        cur_loc = (new_group["lat"], new_group["lon"])
        next_loc = (new_group["lat"].shift(1), new_group["lon"].shift(1))
        new_group["dDistance"] = haversine(cur_loc, next_loc)
        small_groups = []
        if len(time_flags) > 0:
            time_flags.append(new_group.shape[0])
            start = 0
            for i in time_flags:
                df_tmp = new_group.iloc[start:i].copy().reset_index(drop=True)
                df_tmp.at[0, "dDistance"] = 0.0
                small_groups.append(df_tmp)
                start = i
        else:
            small_groups = [new_group]

        count = 0
        for each_group in small_groups:

            # step 3. judge direction
            if each_group.shape[0] > 30:
                first_loc = each_group.iloc[0]
                last_loc = each_group.iloc[30]
                end_loc = each_group.iloc[-1]
                group_direction = (last_loc["lat"] - first_loc["lat"], last_loc["lon"] - first_loc["lon"])
                gps_trip_name = str(name) + "_" + str(count)
                dist = 0.0
                duration = 0.0
                od_loc = ()
                for key, value in def_trips_info.items():
                    if float(cosine_similarity([group_direction], [value[2]])[0][0]) > 0.0:
                        # direction matched when cosine is positive
                        gps_trip_name += ("_"+key)
                        dist, duration, _, od_loc = value
                if not od_loc:
                    continue
                o_dist = haversine(od_loc[0], (first_loc["lat"], first_loc["lon"]))
                d_dist = haversine(od_loc[1], (end_loc["lat"], end_loc["lon"]))

                # step 4. remove trips that are too short, or too far from both ends.
                if o_dist < 300 and d_dist < 300:
                    #  the GPS points at both ends should be within 1/6 of total trip distance
                    group_time = each_group["dTime"].sum(skipna=True)
                    group_dist = each_group["dDistance"].sum(skipna=True)
                    if group_time > duration/2 and group_dist > dist/2.0:
                        # segmented trip should be long enough in terms of travelled time and distance
                        print("\n", gps_trip_name)
                        print("Duration in seconds: gps_trip %f, gtfs_trip %f" % (group_time, duration))
                        print("Distance in meters: gps_dist %f, gtfs_trip %f \n" % (group_dist, dist))
                        gps_trips[gps_trip_name] = each_group

            count += 1

    return gps_trips


def main():
    home_dir = "/Users/shenwang/Documents/datasets/dublin_bus/"
    # input
    bus_line_number = "145"
    def_trips_dir = home_dir + "processed/def_trips/" + bus_line_number + "/"
    groupby_labels = ["vehicle", "vehicle_journey"]
    thresh_time = 900  # seconds
    gps_path = home_dir + "gps/Nov2012/siri.20121121.csv"
    def_trips_info = get_def_trip_info(def_trips_dir)
    columns = ["time", "line", "direction", "journey_pattern", "date", "vehicle_journey", "operator", "congestion",
               "lon", "lat", "delay", "block", "vehicle", "stop", "at_stop"]

    # output
    gps_trips_dir = home_dir + "processed/gps_trips/" + bus_line_number + "/"
    if not os.path.exists(gps_trips_dir):
        # create if not exists
        os.mkdir(gps_trips_dir)

    time_1 = time.time()
    print("\nStart loading GPS data file...")
    df_gps = load_gps(gps_path, columns, bus_line_number)
    time_2 = time.time()
    print("\nGPS data successfully loaded!")
    print("---- %s seconds ----" % (time_2 - time_1))
    gps_trips = split_gps_trip(df_gps, groupby_labels, thresh_time, def_trips_info)
    time_3 = time.time()
    print("\nGPS trips are successfully segmented!")
    print("---- %s seconds ----" % (time_3 - time_2))
    write_data(gps_trips, gps_trips_dir)
    time_4 = time.time()
    print("CSV files successfully written!")
    print("---- %s seconds ----" % (time_4 - time_3))


if __name__ == '__main__':
    main()
