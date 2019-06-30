import json
import process
import split_dataset


line15_stops = []
stops_all = set()
trip_sequence = json.load(open('trip_sequence.json'))
trip_num = 0
for trip in trip_sequence:
    t = []
    stops = trip.split('-')
    for stop in stops:
        stop = stop[8:] if stop[8] != '0' else stop[9:]
        t.append(stop)
        stops_all.add(stop)
    line15_stops.append(t)
print(len(line15_stops))
one_day_data = split_dataset.split('2013-01-07', '2013-01-07')
one_day_data_clean = []
trips = {}
'''
index
0: timestamp 3:journey_pattern_id 4:time_frame  5: vehicle_journey_id 
8: lon 9:lat 11: block_id 12 vehicle_id 13 stop_id
'''
for line in one_day_data:
    stop_id = line[13].split('.')[0]
    if stop_id in stops_all:
        primary = str(line[12]) + '#' + str(line[3])
        if primary not in trips:
            trips[primary] = {'lon': [], 'lat': []}
        trips[primary]['lon'].append(line[8])
        trips[primary]['lat'].append(line[9])
        one_day_data_clean.append(line)
test = trips['33502#00150001']
process.plot_trip_in_line(test['lon'], test['lat'], title='test')
print(len(trips))
print(len(one_day_data_clean))
