import process


# get training set
start_stops = process.load_json('start_stops.json')
trajectories_filtered = process.load_json('trajectories.json')
trips = process.load_json('trips.json')
trajectories_length = {}
trajectories_timestamp = {}
for stop_id in start_stops:
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
                delta_time = (delta_distance * 3.6) / trajectory_real['speed'][real_pointer]
                trajectories_timestamp[start_stop][i][j] = trajectory_real['travel_time'][real_pointer] + delta_time
                if delta_distance > 0:
                    real_pointer += 1
model_dir = '../model_training/'
process.dump_json(trajectories_timestamp, '{}training_sets.json'.format(model_dir))
process.dump_json(trajectories_length, '{}trajectories_length.json'.format(model_dir))
process.dump_json(start_stops, '{}start_stops.json'.format(model_dir))



