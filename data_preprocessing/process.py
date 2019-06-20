import pandas as pd
import json
import os
from matplotlib import pyplot as plt


processed_json_file = 'siri.20121125.json'
if not os.path.exists(processed_json_file):
    # no head exist and using ',' as separator, rename the index, set null value as Na
    raw_data = pd.read_csv('siri.20121125.csv', header=None, sep=',', na_values=['null'], dtype={'lineId': str},
                           names=['timestamp', 'lineId', 'direction', 'journeyId', 'timeFrame', 'vehicleJourneyId',
                                  'operator',
                                  'congestion', 'lon', 'lat', 'delay', 'blockId', 'vehicleId', 'stopId', 'atStop']
                           )
    print(raw_data.head())  # test
    processed_data = {}
    for row in raw_data.itertuples(index=True, name='Pandas'):
        primary_key = str(getattr(row, 'lineId')) + '#' + str(getattr(row, 'direction')) + '#' + \
                      str(getattr(row, 'vehicleId')) + '#' + str(getattr(row, 'timeFrame'))
        if primary_key not in processed_data:
            processed_data[primary_key] = []
        processed_data[primary_key].append({getattr(row, 'timestamp'): (getattr(row, 'lon'), getattr(row, 'lat'))})
        # print(primary_key)
    with open(processed_json_file, 'w') as f:
        json.dump(processed_data, f, indent=2)
else:
    with open(processed_json_file) as f:
        processed_data = json.load(f)
# test the bus trip by plotting the line
test_line = processed_data['27#0#33234#2012-11-24']
lon_x, lat_y = [], []
for timestamp in test_line:
    for point in timestamp.values():
        lon_x.append(point[0])
        lat_y.append(point[1])
plt.plot(lon_x, lat_y, 'ok')
plt.xlabel('longitude')
plt.ylabel('latitude')
plt.show()
