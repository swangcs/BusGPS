import process
import numpy as np
from pygam import LinearGAM, s, f, te
from model_training.translation_timestamp import timeTrans
from model_training.translation_timestamp import isWeekend
import operator

start_stops = process.load_json('one_month_start_stops.json')
trajectories_filtered = process.load_json('one_month_trajectories.json')
trips = process.load_json('trips.json')
trajectories_length = {}
trajectories_timestamp = {}
departure_time = []
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


trajectories_timestamp_start = trajectories_timestamp["6318"][:][:]

# data set for BAM

'''X = [[0 for x in range(2)] for _ in range(1679*57)]
y = [0 for x in range(1679*57)]

# filter
for i in range(len(trajectories_timestamp_start)):
    for i1 in range(len(trajectories_timestamp_start[i])):
        if i1 % 400 == 0 and trajectories_timestamp_start[i][i1] < 25000:
            X[i1//400+(22820//400)*i][0] = i1
            X[i1//400+(22820//400)*i][1] = trajectories_filtered['6318'][i]['timestamp'][0]
            y[i1//400+(22820//400)*i] = trajectories_timestamp_start[i][i1]
X = np.array(X)
y = np.array(y)
for i in range(len(y)):
    if y[i] > 10000:
        lb = (i // 57) * 57
        ub = (i // 57+1) * 57
        X[lb:ub, :] = -1
        y[lb:ub] = -1

y = np.array(list(filter(lambda _: _ != -1, y)))
X = np.array(list(filter(lambda _: _[0] != -1, X)))
stop_location = np.array(trips['6318']['travel_distance'])
np.save('BAM_factors.npy', X)
np.save('BAM_time.npy', y)
np.save('stop_location.npy', stop_location)'''


# Data sets for EAM

X = [[0 for x in range(5)] for _ in range(1679*57)]

for i in range(len(trajectories_timestamp_start)):
    for i1 in range(len(trajectories_timestamp_start[i])):
        if i1 % 400 == 0:
            X[i1//400+57*i][0] = trajectories_timestamp_start[i][i1]
            X[i1//400+57*i][1] = i1
            X[i1//400+57*i][2] = trajectories_filtered['6318'][i]['timestamp'][0]
            timestamp = trajectories_filtered['6318'][i]['timestamp'][0]
            X[i1//400+57*i][3] = isWeekend(timeTrans(timestamp))
            X[i1//400+57*i][4] = trajectories_filtered['6318'][i]['timestamp'][0]

# set the lsat column of X to the traveling time of the last bus
'''X.sort(key=operator.itemgetter(4), reverse = False)
for i in range(len(trajectories_timestamp_start)):
    for i1 in range(len(trajectories_timestamp_start[i])):
        if i1 % 400 == 0:
            if i == 0:
                X[i1 // 400+57 * i][4] = X[i1 // 400+57 * i][0]
            else:
                X[i1 // 400+57 * i][4] = X[i1 // 400+57 * (i-1)][0]'''


EAM_factors = np.transpose([X[:, 1], X[:, 2], X[:, 3], X[:, 4]])
EAM_time = np.transpose([X[:, 0]])
np.save('EAM_factors.npy', EAM_factors)
np.save('EAM_time.npy', EAM_time)



