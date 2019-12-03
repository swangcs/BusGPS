"""
This script is to generate plots for manually verifying
trip segmentation results with the shape of its pre-defined trip.

input: directory of segmented trips; directory of pre-defined trips
output: directory of a plot

"""
import matplotlib.pyplot as plt
import pandas as pd
import os

__author__ = "swang"


def main():
    for i in range(1):
        home_dir = "/Users/letv/Desktop/IntelligentTraffic/datasets/"
        bus_line_number = "46"
        gps_dir = home_dir + "processed/2012/gps_trips/" + bus_line_number + "/" + str(201211) + str('%02d' % (i + 25)) + "/"
        def_trip_dir = home_dir+"processed/2012/def_trips/"+bus_line_number+"/"
        output_dir = home_dir + "plots/2012/" + bus_line_number + "/" + str(201211) + str('%02d' % (i + 25)) + "/"

        if not os.path.exists(output_dir):
            # create if not exists
            os.mkdir(output_dir)
        def_color = "y"
        gps_color = "r"

        o_marker = "^"
        d_marker = "*"

        with os.scandir(gps_dir) as entries:
            for entry in entries:
                if entry.name.endswith(".csv"):
                    trip_id = entry.name.split("_")[-1][:-4]
                    def_trip = pd.read_csv(def_trip_dir+trip_id+".csv")
                    gps_trip = pd.read_csv(gps_dir+entry.name)
                    gps_first = gps_trip.iloc[0]
                    gps_last = gps_trip.iloc[-1]
                    def_first = def_trip.iloc[0]
                    def_last = def_trip.iloc[-1]

                    fig = plt.figure()
                    ax = fig.add_subplot(111)
                    ax.scatter(x=[gps_first["lon"]], y=[gps_first["lat"]], color=gps_color, marker=o_marker)
                    ax.scatter(x=[gps_last["lon"]], y=[gps_last["lat"]], color=gps_color, marker=d_marker)
                    ax.plot(gps_trip["lon"], gps_trip["lat"], marker='o', color=gps_color, linestyle="--", linewidth=0.5)

                    ax.scatter(x=[def_first["lon"]], y=[def_first["lat"]], color=def_color, marker=o_marker)
                    ax.scatter(x=[def_last["lon"]], y=[def_last["lat"]], color=def_color, marker=d_marker)
                    ax.plot(def_trip["lon"], def_trip["lat"], color=def_color, linestyle=":")
                    plt.title(trip_id)
                    plt.savefig(output_dir+entry.name[:-4]+".png")
                    plt.close()
                    plt.show()


if __name__ == '__main__':
    main()
