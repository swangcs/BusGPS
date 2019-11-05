import numpy as np
from data_preprocessing.utils import get_route_info
import data_preprocessing.split_dataset as split_dataset
import data_preprocessing.utils as utils


def extract_bus_route(data):
    trajectories_temp = {}
    for line in data:
        '''
        the meaning of index about a line in data
        0: timestamp 1: line_id 2: direction 3:journey_pattern_id 4:time_frame  5: vehicle_journey_id 
        6: operator 7: congestion 8: lon 9:lat 10: delay 11: block_id 12 vehicle_id 13 stop_id (eg: 6282.0)
        '''
        stop_id = line[13].split('.')[0] if line[13] is not None else None
        primary = '{}#{}'.format(line[1], line[12])
        lon, lat, timestamp = line[8], line[9], line[0]
        if primary not in trajectories_temp:
            trajectories_temp[primary] = \
                {'lon': [lon], 'lat': [lat], 'timestamp': [timestamp], 'travel_time': [0],
                 'travel_distance': [0], 'stop': [stop_id], 'speed': [0], 'name': primary,
                 'info': ['primary:{},speed:{}km/h,stop id:{}-start'.format(primary, 0, stop_id)]}
        else:
            traveled_distance = utils.haversine(
                [trajectories_temp[primary]['lat'][-1], trajectories_temp[primary]['lon'][-1]],
                [lat, lon])
            delta = (timestamp - trajectories_temp[primary]['timestamp'][-1]) / 10e5  # second
            travel_time = round(trajectories_temp[primary]['travel_time'][-1] + delta, 3)
            travel_distance = round(trajectories_temp[primary]['travel_distance'][-1] + traveled_distance, 2)
            speed = round((traveled_distance / 1000) / (delta / 3600), 2) if delta != 0 else 0
            info = 'primary:{},speed:{}km/h,stop id:{}'.format(primary, speed, stop_id)
            add_point(trajectories_temp[primary], lon, lat, timestamp, travel_time, travel_distance, stop_id, speed,
                      info)
    print('Total vehicles: {}'.format(len(trajectories_temp)))
    count, trajectories = 0, []
    for t in trajectories_temp.values():
        trajectories.append(t)
        count += len(t['lon'])
    print('The number of bus locations in total:', count)
    return trajectories


def add_point(current, lon, lat, timestamp, travel_time, travel_distance, stop, speed, info):
    current['lon'].append(lon)
    current['lat'].append(lat)
    current['timestamp'].append(timestamp)
    current['travel_time'].append(travel_time)
    current['travel_distance'].append(travel_distance)
    current['stop'].append(stop)
    current['speed'].append(speed)
    current['info'].append(info)


def extract_trajectories(trajectories: list, trips: dict, stops_location: dict):
    trips_gps, wrong_trips, point_count = [], [], 0
    start_stops = list(trips.keys())
    length = max([len(trips[start_stop]['stop_id']) for start_stop in start_stops])
    for trajectory in trajectories:
        trip_start_index, trip_end_index = [], []
        # find the start point
        for index in range(len(trajectory['lon'])):
            lon, lat, stop, travel_distance = trajectory['lon'][index], trajectory['lat'][index], trajectory['stop'][
                index], trajectory['travel_distance'][index]
            tmp = [utils.haversine(stops_location[start_stop], (lat, lon)) for start_stop in start_stops]
            distance_to_start = min(tmp)
            start_stop = start_stops[tmp.index(distance_to_start)]
            if distance_to_start < 100:
                # verify if it is a start point
                route_direction = np.array([trips[start_stop]['lon'][1] - trips[start_stop]['lon'][0],
                                            trips[start_stop]['lat'][1] - trips[start_stop]['lat'][0]])
                current_direction = np.array(
                    [lon - trajectory['lon'][max(index - 1, 0)], lat - trajectory['lat'][max(index - 1, 0)]])
                if np.dot(route_direction, current_direction) < 0:
                    continue
                if not len(trip_start_index) or (
                        len(trip_start_index) and index - trip_start_index[-1]['index'] > length):
                    trip_start_index.append(
                        {'start': start_stop, 'current': stop, 'index': index, 'distance': distance_to_start})
                else:
                    tmp_index = trip_start_index[-1]['index']
                    if distance_to_start < trip_start_index[-1]['distance'] or index - tmp_index > 5 \
                            or travel_distance - trajectory['travel_distance'][tmp_index] < 5:
                        trip_start_index[-1]['distance'] = distance_to_start
                        trip_start_index[-1]['index'] = index
        # extract trips
        for trip_start in trip_start_index:
            start_index = int(trip_start['index'])
            current = trip_start_index.index(trip_start)
            next_index = trip_start_index[current + 1]['index'] if current != len(trip_start_index) - 1 else len(
                trajectory['lon'])
            start_stop = trip_start['start']
            route_stops = trips[start_stop]['stop_id']
            maximum_travel_distance = trips[start_stop]['travel_distance'][-1]
            for index in range(start_index, next_index):
                lon, lat, timestamp, travel_time, travel_distance, stop, speed, info \
                    = (trajectory['lon'][index], trajectory['lat'][index], trajectory['timestamp'][index],
                       trajectory['travel_time'][index],
                       trajectory['travel_distance'][index], trajectory['stop'][index], trajectory['speed'][index],
                       trajectory['info'][index])
                if index == start_index:
                    trips_gps.append(
                        {'lon': [], 'lat': [], 'timestamp': [], 'travel_time': [], 'travel_distance': [], 'stop': [],
                         'speed': [], 'info': [], 'name': trajectory['name'], 'start': start_stop})
                    add_point(trips_gps[-1], lon, lat, timestamp, 0, 0, route_stops.index(trip_start['start']), speed,
                              info)
                else:
                    stop = route_stops.index(stop) if stop in route_stops else trips_gps[-1]['stop'][-1]
                    if stop < len(route_stops) / 15:
                        distance_to_start = utils.haversine(stops_location[start_stop], (lat, lon))
                        if distance_to_start < trip_start['distance']:
                            trip_start['distance'] = distance_to_start
                            start_index = index
                            trips_gps.remove(trips_gps[-1])
                            trips_gps.append({'lon': [], 'lat': [], 'timestamp': [], 'travel_time': [],
                                              'travel_distance': [], 'stop': [], 'speed': [], 'info': [],
                                              'name': trajectory['name'], 'start': start_stop})
                    travel_time = travel_time - trajectory['travel_time'][start_index]
                    travel_distance = travel_distance - trajectory['travel_distance'][start_index]
                    reached_end = False
                    if stop > len(route_stops) - len(route_stops) / 30:
                        if travel_distance > maximum_travel_distance - maximum_travel_distance * 0.01 and speed < 1 or speed == 0:
                            reached_end = True
                        distance_to_end = utils.haversine(stops_location[route_stops[-1]], (lat, lon))
                        if distance_to_end < 100:
                            reached_end = True
                    if travel_distance > maximum_travel_distance + maximum_travel_distance * 0.005:
                        reached_end = True
                    if reached_end:
                        add_point(trips_gps[-1], lon, lat, timestamp, travel_time, travel_distance, stop, speed, info)
                        break
                    else:
                        add_point(trips_gps[-1], lon, lat, timestamp, travel_time, travel_distance, stop, speed, info)
            if trips_gps[-1]['stop'][-1] < len(route_stops) - len(route_stops) / 10:
                distance_to_end = utils.haversine(stops_location[route_stops[-1]],
                                                  (trips_gps[-1]['lat'][-1], trips_gps[-1]['lon'][-1]))
                if distance_to_end > 100 or len(trips_gps[-1]['lon']) < len(route_stops):
                    trips_gps.remove(trips_gps[-1])
    for trip in trips_gps:
        point_count += len(trip['lon'])
        # stop list check, this can be enhanced to the whole stop list
        for index in range(len(trip['stop'])):
            delta = trip['stop'][index] - trip['stop'][max(0, index - 1)]
            if delta > len(trips[trip['start']]['stop_id']) / 10:
                wrong_trips.append(trip)
    for trip in wrong_trips:
        point_count -= len(trip['lon'])
        trips_gps.remove(trip)
    print('The location of bus in total after filtered:', point_count)
    print('The number of trips in total: ', len(trips_gps))
    return trips_gps


def extract_trips(route_short_name='15'):
    trips, stops_location = get_route_info(route_short_name=route_short_name)
    # choose one day data
    print('Total lines before filtered:')
    one_day_data = split_dataset.select_one_day(route_short_name)
    trajectories = extract_bus_route(one_day_data)
    trips_gps = extract_trajectories(trajectories, trips, stops_location)
    trips_sep = {}
    for trip in trips_gps:
        trip['id'] = trips_gps.index(trip)
        if trip['start'] not in trips_sep:
            trips_sep[trip['start']] = []
        trips_sep[trip['start']].append(trip)
    # plot(trips_sep, trips, debug=False, x='travel_distance', y='travel_time')
    return trips_sep

