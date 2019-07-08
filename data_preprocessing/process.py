import json
import os
import pandas as pd
from geopy.distance import vincenty


def cal_distance(ne, cl):
    """
    :param ne: (lat, lon)
    :param cl: (lat, lon)
    :return: distance in meters
    """
    return vincenty(ne, cl, ellipsoid='WGS-84').meters


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


def load_json(json_file):
    with open(json_file) as f:
        return json.load(f)


def dump_json(data, json_file):
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=2)
