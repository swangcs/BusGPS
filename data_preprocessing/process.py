import json
import os
import pandas as pd
from matplotlib import pyplot as plt
from geopy.distance import vincenty


def read_csv(file: str, sep=',', header=None,
             names=None):
    if names is None:
        names = ['timestamp', 'lineId', 'direction', 'journeyId', 'timeFrame', 'vehicleJourneyId',
                 'operator', 'congestion', 'lon', 'lat', 'delay', 'blockId', 'vehicleId', 'stopId',
                 'atStop']
    return pd.read_csv(file, header=header, sep=sep, na_values=['null'], dtype={'lineId': str},
                       names=names)


def get_files(path):
    return os.listdir(path)


def find_bus_line_with_id(path_dir: str, bus_line_id: str):
    files = get_files(path_dir)
    bus_line = pd.DataFrame()
    for file in files:
        f = path_dir + '/' + file
        # no head exist, using ',' as separator, rename the index, set null value as Na
        raw_data = read_csv(f)
        for index, row in raw_data.iterrows():
            row_id = row['lineId']
            if bus_line_id == row_id:
                print(row)
                bus_line = bus_line.append(row)
    return bus_line


def cal_distance(ne, cl):
    """
    :param ne: (lat, lon)
    :param cl: (lat, lon)
    :return: distance in meters
    """
    return vincenty(ne, cl, ellipsoid='WGS-84').meters


def get_x_y(test_line: list):
    lon_x, lat_y, journeyId, vehicleJourneyId = [], [], [], []
    for timestamp in test_line:
        for point in timestamp.values():
            lon_x.append(point[0])
            lat_y.append(point[1])
            journeyId.append(point[2])
            vehicleJourneyId.append(point[3])
    return lon_x, lat_y, journeyId, vehicleJourneyId


def plot_trip_in_line(lon_x: list, lat_y: list, title='temp', color='r', style='line', file='tmp.png', show=True):
    plt.title(title)
    plt.xlabel('longitude')
    plt.ylabel('latitude')
    if style == 'line':
        plt.plot(lon_x, lat_y, c=color, marker='o', mec='k', mfc='w', linestyle=':')
    else:
        plt.scatter(lon_x, lat_y, c=color)
    if show:
        show_trip(file=file)


def show_trip(file='tmp.png'):
    plt.savefig(file)
    plt.show()


# load origin csv file
def load_data():
    processed_data = {}
    # no head exist, using ',' as separator, rename the index, set null value as Na
    raw_data = read_csv('siri.20121125.csv')
    for row in raw_data.itertuples(index=True, name='Pandas'):
        primary_key = str(getattr(row, 'lineId')) + '#' + str(getattr(row, 'direction')) + '#' + \
                      str(getattr(row, 'vehicleId')) + '#' + str(getattr(row, 'timeFrame'))
        if primary_key not in processed_data:
            processed_data[primary_key] = []
        processed_data[primary_key].append({getattr(row, 'timestamp'): [getattr(row, 'lon'), getattr(row, 'lat'),
                                                                        getattr(row, 'journeyId'),
                                                                        getattr(row, 'vehicleJourneyId')]})
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
