import utils
from data_preprocessing import transform


def prepare(route_id='15', step=100):
    # get training set
    trajectories_filtered = transform.extract_trips(route_short_name=route_id)
    trips, stops_location = utils.get_route_info(route_short_name=route_id)
    trajectories_length, trajectories_timestamp, training_sets_all = {}, {}, {}
    for stop_id in trips.keys():
        if stop_id not in trajectories_timestamp:
            trajectories_length[stop_id] = int((int(trips[stop_id]['travel_distance'][-1] / 10) + 1) * 10)
            trajectories_timestamp[stop_id] = [[0 for _ in range(trajectories_length[stop_id])]
                                               for _ in range(len(trajectories_filtered[stop_id]))]
    for start_stop, trajectories_list in trajectories_timestamp.items():
        for i in range(len(trajectories_list)):
            trajectory_real = trajectories_filtered[start_stop][i]  # dict{'travel_time':[], 'travel_distance':[]}
            real_pointer = 0
            for j in range(len(trajectories_list[i])):
                real_pointer = min(real_pointer, len(trajectory_real['travel_distance']) - 1)
                real_distance = trajectory_real['travel_distance'][real_pointer]
                if j == real_distance:
                    trajectories_timestamp[start_stop][i][j] = trajectory_real['travel_time'][real_pointer]
                    real_pointer += 1
                else:
                    delta_distance = j - real_distance
                    speed = trajectory_real['speed'][real_pointer]
                    delta_time = (delta_distance * 3.6) / speed if speed != 0 else 0
                    trajectories_timestamp[start_stop][i][j] = trajectory_real['travel_time'][real_pointer] + delta_time
                    if delta_distance > 0:
                        real_pointer += 1
    var_filter = 100000
    for start_stop, training_sets in trajectories_timestamp.items():
        route_travel = trips[start_stop]['travel_distance']
        route_time = trips[start_stop]['travel_time']
        for training_set in training_sets:
            var = sum([abs(training_set[int(t)] - route_time[route_travel.index(t)]) for t in route_travel])
            if var < var_filter:
                if start_stop not in training_sets_all:
                    training_sets_all[start_stop] = []
                # interpolation
                training_sets_all[start_stop].append([training_set[i] for i in range(0, len(training_set) - 1, step)])
    utils.dump_json(training_sets_all, 'training_sets.json')
    utils.dump_json(trajectories_length, 'trajectories_length.json')
    return training_sets_all, trajectories_length
