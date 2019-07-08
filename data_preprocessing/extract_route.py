import dbhelper
import json


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


def get_routes():
    connection = dbhelper.connect()
    cursor = connection.cursor()
    # extract separate trips from GTFS dataset, and create three temporary json files to check result
    trips_json, stops_location_json = 'trips.json', 'stops_location.json'
    test_route_short_name = '15'
    trips, stops_location = {}, {}
    for shape_id in get_shapes_id(test_route_short_name, cursor):
        shape_id = shape_id[0]
        trip_id = get_trips_id(shape_id, cursor)[0][0]
        trips[trip_id] = {'stop_id': [], 'lon': [], 'lat': [], 'travel_time': [], 'travel_distance': [], 'timestamp': []}
        for stop_id, departure_time, shape_dist_traveled in get_stops_id_using_trip_id(trip_id, cursor):
            if shape_dist_traveled == '0':
                trips[trip_id]['travel_time'].append(0)
            else:
                trips[trip_id]['travel_time'].append(convert_to_timestamp(departure_time) - trips[trip_id]['timestamp'][0])
            if stop_id not in stops_location:
                # stops location: (lat, lon)
                stops_location[stop_id] = get_stop_loc(stop_id, cursor)[0]
            trips[trip_id]['stop_id'].append(stop_id)
            trips[trip_id]['travel_distance'].append(float(shape_dist_traveled))
            trips[trip_id]['timestamp'].append(convert_to_timestamp(departure_time))
            trips[trip_id]['lon'].append(float(stops_location[stop_id][1]))
            trips[trip_id]['lat'].append(float(stops_location[stop_id][0]))
    with open(trips_json, 'w') as f:
        json.dump(trips, f, indent=2)
    with open(stops_location_json, 'w') as f:
        json.dump(stops_location, f, indent=2)
    return trips, stops_location

