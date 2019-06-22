import pandas as pd
import json
import os
from matplotlib import pyplot as plt


def get_x_y(test_line: list):
    lon_x, lat_y = [], []
    for timestamp in test_line:
        for point in timestamp.values():
            lon_x.append(point[0])
            lat_y.append(point[1])
    return lon_x, lat_y


def plot_trip_in_line(lon_x: list, lat_y: list, title: str):
    plt.title(title)
    plt.xlabel('longitude')
    plt.ylabel('latitude')
    plt.plot(lon_x, lat_y,  c='r', marker='o', mec='k', mfc='w', linestyle=':')
    plt.show()


# load origin csv file
def load_data():
    processed_data = {}
    # no head exist, using ',' as separator, rename the index, set null value as Na
    raw_data = pd.read_csv('siri.20121125.csv', header=None, sep=',', na_values=['null'], dtype={'lineId': str},
                           names=['timestamp', 'lineId', 'direction', 'journeyId', 'timeFrame', 'vehicleJourneyId',
                                  'operator', 'congestion', 'lon', 'lat', 'delay', 'blockId', 'vehicleId', 'stopId',
                                  'atStop']
                           )
    for row in raw_data.itertuples(index=True, name='Pandas'):
        primary_key = str(getattr(row, 'lineId')) + '#' + str(getattr(row, 'direction')) + '#' + \
                      str(getattr(row, 'vehicleId')) + '#' + str(getattr(row, 'timeFrame'))
        if primary_key not in processed_data:
            processed_data[primary_key] = []
        processed_data[primary_key].append({getattr(row, 'timestamp'): [getattr(row, 'lon'), getattr(row, 'lat')]})
    with open(processed_json_file, 'w') as f:
        json.dump(processed_data, f, indent=2)
    return processed_data


def load_json(json_file):
    with open(json_file) as f:
        return json.load(f)


def dump_json(data, json_file):
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=2)


def load_trip():
    if not os.path.exists(processed_json_file):
        processed_data = load_data()
    else:
        processed_data = load_json(processed_json_file)
    return processed_data


processed_json_file = 'siri.20121125.json'
