import os
import pandas as pd


def load_data(gps_dir):
    df = pd.read_csv(gps_dir)
    return df


def load_in_and_out(root_dir, n):
    trip_id = 0
    gps_data = {"trip_id": [], "cum_time": [], "cum_distance": [], "np_time": [], "direction": []}
    for gps_dir in os.listdir(root_dir)[:n]:
        direction = gps_dir.split(".")[-2]
        trip_id += 1
        df = load_data(root_dir + gps_dir)
        gps_data["trip_id"].extend([trip_id for _ in range(df.shape[0])])
        gps_data["direction"].extend([direction for _ in range(df.shape[0])])
        gps_data["np_time"].extend([df["np_time"][0] for _ in range(df.shape[0])])
        gps_data["cum_time"].extend(df["cum_time"])
        gps_data["cum_distance"].extend(df["dist_travelled"])
    print("Load data:", trip_id)
    gps_data = pd.DataFrame(gps_data)
    return gps_data


def main():
    home_dir = "/Users/ruixinhua/Documents/BusGPS/BusGPS/"
    bus_number = "46"
    root_meters_dir = home_dir + "processed/gps_meters_trips/" + bus_number + "/"
    root_stops_dir = home_dir + "processed/gps_stop_trips/" + bus_number + "/"
    load_in_and_out(root_meters_dir, -1).to_csv(root_meters_dir + "gps_meters.csv")
    load_in_and_out(root_stops_dir, -1).to_csv(root_stops_dir + "gps_stops.csv")


if __name__ == "__main__":
    main()
