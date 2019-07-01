import random
import dbhelper
import json
import os


def get_stop_loc(stop_id: str):
    """
    :param stop_id:
    :return: (lat, lon)
    """
    select_stop = "select stop_lat, stop_lon from public.stops where stop_id='{}'".format(stop_id)
    cursor.execute(select_stop)
    return cursor.fetchall()


def get_trips_id(route_short_name: str):
    select_all_trips_id = "select Distinct trip_id from public.trips left join public.routes using(route_id) " \
                          "where route_short_name='{}'".format(route_short_name)
    cursor.execute(select_all_trips_id)
    return cursor.fetchall()


def get_stops_id_using_trip_id(trip_id: str):
    select_all_stops_id = "select stop_id, departure_time, shape_dist_traveled from public.stop_times " \
                          "where trip_id='{}' order by departure_time;".format(trip_id)
    cursor.execute(select_all_stops_id)
    return cursor.fetchall()


def random_color():
    color_arr = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
    color_ = ""
    for i in range(6):
        color_ += color_arr[random.randint(0, 14)]
    return "#" + color_


trips_json, stops_location_json = 'trips.json', 'stops_location.json'
test_route_short_name = '15'
if not os.path.exists(trips_json) or not os.path.exists(stops_location_json):
    trips, stops_location = {}, {}
    connection = dbhelper.connect()
    cursor = connection.cursor()
    for trip_id in get_trips_id(test_route_short_name):
        trip_id = trip_id[0]
        trips[trip_id] = {}
        for stop_id, departure_time, shape_dist_traveled in get_stops_id_using_trip_id(trip_id):
            if stop_id not in stops_location:
                stops_location[stop_id] = get_stop_loc(stop_id)[0]
            trips[trip_id][stop_id] = [departure_time, shape_dist_traveled]
    with open(trips_json, 'w') as f:
        json.dump(trips, f, indent=2)
    with open(stops_location_json, 'w') as f:
        json.dump(stops_location, f, indent=2)
with open(trips_json, 'r') as f:
    trips = json.load(f)
with open(stops_location_json, 'r') as f:
    stops_location = json.load(f)
lon, lat, color, trips_seq = [], [], set(), set()
count_trip = {}
for trip_id, trip in trips.items():
    trip_seq = []
    for stop_id, trip_info in trip.items():
        trip_seq.append(stop_id)
    trip_seq = '-'.join(trip_seq)
    if trip_seq not in count_trip:
        count_trip[trip_seq] = 0
    count_trip[trip_seq] += 1
    add = 1
    for seq in trips_seq:
        if trip_seq in seq:
            add = 0
    if add:
        trips_seq.add(trip_seq)
print(len(trips_seq))
for k, v in count_trip.items():
    print(len(k), v)
trips_stops = {}
trip_name = 1
with open('trip_sequence.json', 'w') as f:
    json.dump(list(trips_seq), f, indent=2)
