import pandas as pd
import time
import numpy as np


def read_csv(file: str, sep=',', names=None):
    return pd.read_csv(file, sep=sep, na_values=['null'], dtype={'np_time': int},
                       names=names)


def stamp_transform(stamp):
    timeArray = time.localtime(stamp)
    otherStyleTime = time.strftime("%H:%M:%S", timeArray)
    timeArray = time.strptime(otherStyleTime, '%H:%M:%S')
    timeStamp = int(time.mktime(timeArray))
    return timeStamp


homedir = '/Users/letv/Desktop/IntelligentTraffic/datasets'

# gps_meters
# filepath = homedir + '/' + 'shen_dataset' + '/' + 'gps_meters' + '.csv'
# dataset_total_46 = read_csv(filepath)
# dataset_total_46 = dataset_total_46.drop(['Unnamed: 0'], axis=1)
# direction = dataset_total_46['direction'].unique()
# dataset_total_46_in = np.array(dataset_total_46[dataset_total_46['direction'].isin([direction[0]])])
# dataset_total_46_out = np.array(dataset_total_46[dataset_total_46['direction'].isin([direction[1]])])
#
# for i in range(len(dataset_total_46_in)):
#     dataset_total_46_in[i][3] = stamp_transform(dataset_total_46_in[i][3])
#
# for i in range(len(dataset_total_46_out)):
#     dataset_total_46_out[i][3] = stamp_transform(dataset_total_46_out[i][3])
#
# np.save(homedir + '/' + 'shen_dataset' + '/' + 'gps_meters_in_BAM' + '.npy', dataset_total_46_in)
# np.save(homedir + '/' + 'shen_dataset' + '/' + 'gps_meters_out_BAM' + '.npy', dataset_total_46_out)

# gps_stops
filepath = homedir + '/' + 'shen_dataset' + '/' + 'gps_stops' + '.csv'
dataset_total_46_stops = read_csv(filepath)
dataset_total_46_stops = dataset_total_46_stops.drop(['Unnamed: 0'], axis=1)
direction = dataset_total_46_stops['direction'].unique()
dataset_total_46_stops_in = np.array(dataset_total_46_stops[dataset_total_46_stops['direction'].isin([direction[0]])])
dataset_total_46_stops_out = np.array(dataset_total_46_stops[dataset_total_46_stops['direction'].isin([direction[1]])])
for i in range(len(dataset_total_46_stops_in)):
    dataset_total_46_stops_in[i][3] = stamp_transform(dataset_total_46_stops_in[i][3])

for i in range(len(dataset_total_46_stops_out)):
    dataset_total_46_stops_out[i][3] = stamp_transform(dataset_total_46_stops_out[i][3])

np.save(homedir + '/' + 'shen_dataset' + '/' + 'gps_stops_in_BAM' + '.npy', dataset_total_46_stops_in)
np.save(homedir + '/' + 'shen_dataset' + '/' + 'gps_stops_out_BAM' + '.npy', dataset_total_46_stops_out)