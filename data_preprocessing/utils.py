import json
import os
import utils
import dbhelper
import pandas as pd
from geopy.distance import vincenty
import math


def get_stop_loc(stop_id: str, cursor):
    """
    get stop location using stop id
    :param stop_id:
    :return: the location of stop(lat, lon)
    """
    select_stop = "select stop_lat, stop_lon from public.stops where stop_id='{}'".format(stop_id)
    return execute_sql(select_stop, cursor)


def get_shapes_id(route_short_name: str, cursor):
    """
    get all the trips using route id
    :param route_short_name: the route id, e.g., 15
    :return: the distinct trip that this route has
    """
    select_all_shapes_id = "select Distinct shape_id from public.trips left join public.routes using(route_id) " \
                           "where route_short_name='{}'".format(route_short_name)
    return execute_sql(select_all_shapes_id, cursor)


def get_trips_id(shape_id: str, cursor):
    """
    get all trips id using shape id
    :param shape_id:
    :return:
    """
    select_all_trips_id = "select trip_id from trips where shape_id='{}'".format(shape_id)
    return execute_sql(select_all_trips_id, cursor)


def get_stops_id_using_trip_id(trip_id: str, cursor):
    """
    get all stops id, departure time and shape_dist_traveled which the trip contains
    :param trip_id:
    :return:
    """
    select_all_stops_id = "select stop_id, departure_time, shape_dist_traveled from public.stop_times " \
                          "where trip_id='{}' order by departure_time;".format(trip_id)
    return execute_sql(select_all_stops_id, cursor)


def execute_sql(sql, cursor):
    cursor.execute(sql)
    return cursor.fetchall()


def convert_to_timestamp(format_time: str):
    """
    convert standard time to timestamp
    :param format_time: has format hh:mm:ss
    :return:
    """
    split_time = format_time.split(':')
    return int(split_time[0]) * 3600 + int(split_time[1]) * 60 + int(split_time[2])


def extract_route_to_json(route_short_name='15', trips_json='trips.json', stops_location_json='stops_location.json'):
    """
    extract specific route from gtfs data
    :param route_short_name: default value is 15
    :param trips_json: default value is trips.json
    :param stops_location_json: default value is stops_location.json
    :return: trips and stops_location
    """
    connection = dbhelper.connect()
    cursor = connection.cursor()
    trips, stops_location = {}, {}
    for shape_id in get_shapes_id(route_short_name, cursor):
        shape_id = shape_id[0]
        trip_id = get_trips_id(shape_id, cursor)[0][0]
        trips[trip_id] = {'stop_id': [], 'lon': [], 'lat': [], 'travel_time': [], 'travel_distance': [],
                          'timestamp': []}
        for stop_id, departure_time, shape_dist_traveled in get_stops_id_using_trip_id(trip_id, cursor):
            if shape_dist_traveled == '0':
                trips[trip_id]['travel_time'].append(0)
            else:
                trips[trip_id]['travel_time'].append(
                    convert_to_timestamp(departure_time) - trips[trip_id]['timestamp'][0])
            stop_id_nor = stop_id[-4:] if stop_id[-4] != '0' else stop_id[-3:]
            if stop_id_nor not in stops_location:
                # stops location: (lat, lon)
                stops_location[stop_id_nor] = get_stop_loc(stop_id, cursor)[0]
            trips[trip_id]['stop_id'].append(stop_id_nor)
            trips[trip_id]['travel_distance'].append(float(shape_dist_traveled))
            trips[trip_id]['timestamp'].append(convert_to_timestamp(departure_time))
            trips[trip_id]['lon'].append(float(stops_location[stop_id_nor][1]))
            trips[trip_id]['lat'].append(float(stops_location[stop_id_nor][0]))
    # remove redundant routes
    trips_stops, trip_remove = {}, []
    for trip_id, trip in trips.items():
        start_stop = trip['stop_id'][0]
        if start_stop not in trips_stops:
            trips_stops[start_stop] = trip_id
        else:
            if len(trips[trip_id]['stop_id']) > len(trips[trips_stops[start_stop]]['stop_id']):
                trip_remove.append(trips_stops[start_stop])
            else:
                trip_remove.append(trip_id)
    for trip_id in trip_remove:
        trips.pop(trip_id)
    trips_convert = {}
    for trip in trips.values():
        trips_convert[trip['stop_id'][0]] = trip
    utils.dump_json(trips_convert, trips_json)
    utils.dump_json(stops_location, stops_location_json)
    return trips, stops_location


def get_route_info(route_short_name='15', trips_json='trips.json', stops_location_json='stops_location.json'):
    """
    get route information(trips and stops) with specific route short name
    :param route_short_name: default value is '15'
    :param trips_json: default is 'trips.json'
    :param stops_location_json: default is 'stops_location.json'
    :return: trips and stops_location
    """
    if os.path.exists(trips_json) and os.path.exists(stops_location_json):
        trips, stops_location = json.load(open(trips_json)), json.load(open(stops_location_json))
    else:
        trips, stops_location = extract_route_to_json(route_short_name, trips_json, stops_location_json)
    return trips, stops_location


def cal_distance(ne, cl):
    """
    :param ne: (lat, lon)
    :param cl: (lat, lon)
    :return: distance in meters
    """
    return vincenty(ne, cl, ellipsoid='WGS-84').meters


def read_csv(file: str, sep=',', header=None, names=None):
    if names is None:
        names = ['timestamp', 'lineId', 'direction', 'journeyId', 'timeFrame', 'vehicleJourneyId',
                 'operator', 'congestion', 'lon', 'lat', 'delay', 'blockId', 'vehicleId', 'stopId',
                 'atStop']
    return pd.read_csv(file, header=header, sep=sep, na_values=['null'], dtype={'lineId': str},
                       names=names)


def load_json(json_file):
    with open(json_file) as f:
        return json.load(f)


def dump_json(data, json_file):
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=2)


def haversine(coord1, coord2):
    # for quick calculation
    R = 6372800  # Earth radius in meters
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    lat1, lat2, lon1, lon2 = float(lat1), float(lat2), float(lon1), float(lon2)

    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2

    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))
