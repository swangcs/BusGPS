import pandas as pd
import time
import os

__author__ = "swang"


def load_data(gtfs_dir):
    """
    Given the home folder of GTFS data files, return loaded dataframes
    :param gtfs_dir: the home folder of GTFS data files
    :return: dataframes for each major GTFS data files
    """
    df_routes = pd.read_csv(gtfs_dir + "routes.txt")
    df_trips = pd.read_csv(gtfs_dir + "trips.txt")
    df_stops = pd.read_csv(gtfs_dir + "stops.txt")
    df_stoptimes = pd.read_csv(gtfs_dir + "stop_times.txt")
    df_shapes = pd.read_csv(gtfs_dir + "shapes.txt")
    return df_routes, df_trips, df_stops, df_stoptimes, df_shapes


def write_data(df_list, def_trips_dir):
    """
    Write processed dataframe into csv by each trip (one trip per csv file).
    :param df_list: each element in this list is a dataframe of a processed single trip
    :param def_trips_dir: the directory of the output csv files
    :return: none
    """
    for i in df_list:
        trip_id = i["trip_id"].iloc[0]  # use trip_id as the output file name
        i = i.drop(["trip_id"], axis=1)  # remove the data column "trip_id" from the output file
        i.to_csv(def_trips_dir+trip_id+".csv", index=False)  # do not output the dataframe index


def get_freq_shapes(df_trips, thresh=0.9):
    """
    Get the id of the two most frequently used route shapes for filtering stoptimes trips.
    :param df_trips: this dataframe should be filtered by the given route_id beforehand
    :param thresh: percentile of the definition for "frequent".
    E.g. 0.9, means frequency of the route shapes greater or equal to 90%
    :return: Two most frequently appeared shape trips' id.
    """
    # df_trips already filtered by route_id
    freq_pair = df_trips["shape_id"].value_counts(normalize=True)
    print("\nThis is the full list of route shapes and its frequency:")
    print(freq_pair)
    if len(freq_pair) < 2:
        # if only one shape trip match, return it directly
        return [freq_pair.index[0]]
    if freq_pair.iloc[0] + freq_pair.iloc[1] > thresh:
        return [freq_pair.index[0], freq_pair.index[1]]
    else:
        return "The frequency of the first two route shapes is less than the given threshold."


def def_trip_gen(df_gtfs, bus_line_number):
    """
    Generate pre-defined trips
    :param df_gtfs: the home folder of GTFS data files
    :param bus_line_number: bus line number e.g. 145
    :return: a list of processed pre-defined trips in dataframe
    """

    df_routes, df_trips, df_stops, df_stoptimes, df_shapes = df_gtfs

    # Step 1. route.txt -> get route_id
    route_id = df_routes.loc[df_routes["route_short_name"] == bus_line_number, "route_id"].iloc[0]

    # Step 2. trip.txt -> get trip ids that match given route_id
    df_trips = df_trips.loc[df_trips["route_id"] == route_id]

    # Step 3. get two most frequent shape_id used in df_trips
    freq_shape_ids = get_freq_shapes(df_trips)

    # Step 4. based on each route shape, add stop name and arrival time when the location is identified as a bus stop
    df_processed_trips = []
    for i in freq_shape_ids:
        def_trip = pd.DataFrame(
            columns=["trip_id", "sequence", "arrival_time", "shape_dist_traveled", "stop_name", "lat", "lon"])

        # get the trip_id of the *first* trip that matches the given shape_id
        trip_id = df_trips.loc[(df_trips["shape_id"] == i).idxmax(), "trip_id"]
        # get the trip with stop and time info
        trip = df_stoptimes.loc[df_stoptimes["trip_id"] == trip_id]
        # get stop locations and remove unnecessary data columns
        trip = pd.merge(trip, df_stops, how="left", on="stop_id").drop(
            ["stop_id", "departure_time", "pickup_type", "drop_off_type"], axis=1)
        trip = trip.drop_duplicates("shape_dist_traveled")

        # get the route shape and remove duplicated rows
        shape = df_shapes.loc[df_shapes["shape_id"] == i]
        shape = shape.drop_duplicates("shape_dist_traveled")

        sequence_id = 1
        stop_index = 0
        for index, row in shape.iterrows():
            stop_trip_row = trip.iloc[stop_index]
            stop_dist = float(stop_trip_row["shape_dist_traveled"])
            shape_dist = float(row["shape_dist_traveled"])
            if stop_dist == shape_dist:
                def_trip = def_trip.append({"trip_id": trip_id,
                                            "sequence": sequence_id,
                                            "arrival_time": stop_trip_row["arrival_time"],
                                            "shape_dist_traveled": shape_dist,
                                            "stop_name": stop_trip_row["stop_name"],
                                            "lat": row["shape_pt_lat"],
                                            "lon": row["shape_pt_lon"]}, ignore_index=True)
                stop_index += 1
            else:
                def_trip = def_trip.append({"trip_id": trip_id,
                                            "sequence": sequence_id,
                                            "arrival_time": None,
                                            "shape_dist_traveled": shape_dist,
                                            "stop_name": None,
                                            "lat": row["shape_pt_lat"],
                                            "lon": row["shape_pt_lon"]}, ignore_index=True)
            sequence_id += 1

        df_processed_trips.append(def_trip)

    return df_processed_trips


def main():
    home_dir = "/Users/letv/Desktop/IntelligentTraffic/datasets/"
    # inputs
    gtfs_dir = home_dir + "gtfs/20130315/"
    bus_line_number = "46A"

    # output
    def_trips_dir = home_dir + "processed/2013/def_trips/" + bus_line_number + "/"
    if not os.path.exists(def_trips_dir):
        # create if not exists
        os.mkdir(def_trips_dir)

    time_1 = time.time()
    print("\nStart loading GTFS data files...")
    df_gtfs = load_data(gtfs_dir)
    time_2 = time.time()
    print("\n1. GTFS data successfully loaded!")
    print("---- %s seconds ----" % (time_2-time_1))
    df_processed_trips = def_trip_gen(df_gtfs, bus_line_number)
    time_3 = time.time()
    print("\n2. Trips data successfully processed!")
    print("---- %s seconds ----" % (time_3-time_2))
    write_data(df_processed_trips, def_trips_dir)
    time_4 = time.time()
    print("\n3. CSV files successfully written!")
    print("---- %s seconds ----" % (time_4-time_3))


if __name__ == '__main__':
    main()
