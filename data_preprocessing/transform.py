import process
import split_dataset
from extract_route import get_route_info


def create_trip(lon, lat, timestamp, stop_id, primary):
    return {'lon': [lon], 'lat': [lat], 'timestamp': [timestamp], 'travel_time': [0],
            'travel_distance': [0], 'start_stop': stop_id, 'stop': [stop_id], 'speed': [0],
            'name': primary, 'end_stop': end_stop[root_stop.index(stop_id)],
            'info': ['travel time:{}s,travel distance:{}m,speed:{}km/h,stop id:{}-start'.format(0, 0, 0, stop_id)]}


def split_route(data, line_id):
    trajectories = {}
    use_stop_id_filter, use_distance_filter, use_delta_filter, use_speed_filter, use_length_filter, use_start_filter, use_accumulated_filter = 0, 1, 1, 1, 1, 1, 1
    '''
    - filter 1: stop id filter, if stop id that the bus hold is not in the line 15, then skip.(depend on the reliability of the data of that column)
    - filter 2: distance filter, the distance which is between bus and bus stop, if the distance is too far(>1000 meters), then skip.
    - filter 3: delta time filter, if the delta time between the current bus timestamp and last bus timestamp is too high(>1000 seconds), then skip.
    - filter 4: speed filter, if the speed of bus is too high(>120km/h) or too low(<1km/h), then skip.
    - filter 5: accumulated distance filter, if the accumulated distance of bus is longer than the total distance of standard trip, then skip.
    - filter 6: if the final trajectory is too short(has less than 100 points), then remove the trajectory.
    - filter 7: only choose the route begin with a standard start stop, skip the trajectory that is not begin with a start stop. 
    '''
    for line in data:
        '''
        the meaning of index about a line in data
        0: timestamp 1: line_id 2: direction 3:journey_pattern_id 4:time_frame  5: vehicle_journey_id 
        6: operator 7: congestion 8: lon 9:lat 10: delay 11: block_id 12 vehicle_id 13 stop_id (eg: 6282.0)
        '''
        if str(line[1]) != line_id:
            continue
        stop_id = line[13].split('.')[0]
        primary = '{}#{}#{}'.format(line[1], line[12], line[3])
        lon, lat, timestamp = line[8], line[9], line[0]
        if primary not in trajectories:
            trajectories[primary] = []
        # create trajectory
        if stop_id in root_stop and (
                not trajectories[primary] or (
                trajectories[primary] and (stop_id != trajectories[primary][-1]['end_stop']
                                           or trajectories[primary][-1]['stop'][
                                               -1] in root_stop))):

            trajectories[primary].append(create_trip(lon, lat, timestamp, stop_id, primary))
        elif trajectories[primary]:
            tmp = trajectories[primary][-1]
            traveled_distance = process.cal_distance([tmp['lat'][-1], tmp['lon'][-1]], [lat, lon])
            delta = (timestamp - tmp['timestamp'][-1]) / 10e5  # second
            speed = round((traveled_distance / 1000) / (delta / 3600), 2) if delta != 0 else 0
            # filter 1: using stop_id
            if stop_id not in abbr_stops_location and use_stop_id_filter:
                continue
            else:
                # if stop id is not in the route or missing, using the last position's stop id
                stop_id = stop_id if stop_id in abbr_stops_location else tmp['stop'][-1]
                stop_distance = float(
                    process.cal_distance([float(line[9]), float(line[8])], abbr_stops_location[stop_id]))
                # filter 2: using distance to closet stop
                if stop_distance > 1000 and use_distance_filter:
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


def compare(route_short_name='15'):
    trips, stops_location = get_route_info(route_short_name=route_short_name,
                                           trips_json='trips{}.json'.format(route_short_name),
                                           stops_location_json='stops_location{}.json'.format(route_short_name))
    # choose one day data
    print('Total lines before filtered:')
    one_day_data = split_dataset.select_one_day(route_short_name)
    trajectories = extract_bus_route(one_day_data)
    trips_gps = extract_trips(trajectories, trips, stops_location)
    trips_sep = {}
    for trip in trips_gps:
        trip['id'] = trips_gps.index(trip)
        if trip['start'] not in trips_sep:
            trips_sep[trip['start']] = []
        trips_sep[trip['start']].append(trip)
    plot(trips_sep, trips, debug=False, x='travel_distance', y='travel_time')


if __name__ == '__main__':
    route_short_name = '15'
    # trips:{'stop_id':[], 'lon':[], 'lat':[], 'travel_time':[], 'travel_distance':[], 'timestamp':[]}
    trips, stops_location = get_route_info(route_short_name=route_short_name)
    # each route has its own stops list
    route_stops = []
    # transform the format of stop id to the format that belong to dataset
    abbr_stops_location = dict()
    for trip in trips.values():
        temp = []
        for s in trip['stop_id']:
            stop = s[8:] if s[8] != '0' else s[9:]
            temp.append(stop)
            abbr_stops_location[stop] = stops_location[s]
        # route_stops contains stops id of a single route
        route_stops.append(temp)
    root_stop = [temp[0] for temp in route_stops]
    end_stop = [temp[-1] for temp in route_stops]
    # choose one day data
    print('Total lines before filtered:')
    one_day_data = split_dataset.split('2013-01-07', '2013-01-07', line_id=route_short_name)
    trajectories_filtered = split_route(one_day_data, route_short_name)
    process.dump_json(trajectories_filtered, 'trajectories.json')
    process.dump_json(root_stop, 'start_stops.json')
    for start_stop, trajectory in trajectories_filtered.items():
        print('From {}, the number of trajectories:'.format(start_stop), len(trajectory))
