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
            # filter 5: accumulated distance filter
            if tmp['travel_distance'][-1] + traveled_distance > 23000 and use_accumulated_filter:
                continue
            # filter 3: delta time filter
            if delta > 1000 and use_delta_filter:
                for trip_stop in route_stops:
                    if tmp['stop'][-1] in trip_stop and trip_stop.index((tmp['stop'][-1])) < 3 and \
                            stop_id in trip_stop and trip_stop.index(stop_id) < 10:
                        trajectories[primary].append(
                            create_trip(lon, lat, timestamp, root_stop[route_stops.index(trip_stop)], primary))
            # filter 4: speed filter
            elif (speed > 120 or speed < 1) and use_speed_filter:
                continue
            else:
                tmp['lon'].append(lon)
                tmp['lat'].append(lat)
                tmp['stop'].append(stop_id)
                tmp['timestamp'].append(timestamp)
                tmp['travel_time'].append(round(tmp['travel_time'][-1] + delta, 3))
                tmp['travel_distance'].append(round(tmp['travel_distance'][-1] + traveled_distance, 2))
                speed = tmp['speed'][-1] if traveled_distance == 0 else speed
                tmp['info'].append('travel time:{}s,travel distance:{}m,speed:{}km/h,stop id:{}'.
                                   format(tmp['travel_time'][-1], tmp['travel_distance'][-1], speed, stop_id))
                tmp['speed'].append(speed)  # km/h
        #  filter 7: begin with a start stop
        elif not use_start_filter:
            trajectories[primary].append(create_trip(lon, lat, timestamp, root_stop[0], primary))
    filtered, count = {}, 0
    for v in trajectories.values():
        for t in v:
            # filter 6: remove short trajectories
            if len(t['lon']) < 100 and use_length_filter:
                continue
            else:
                if t['start_stop'] not in filtered:
                    filtered[t['start_stop']] = []
                filtered[t['start_stop']].append(t)
                count += len(t['lon'])
    print('Total lines after filtered:', count)
    return filtered


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
