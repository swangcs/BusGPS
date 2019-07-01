import json
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import process
import split_dataset

line15_stops = []
stops_all = dict()
trip_sequence = json.load(open('trip_sequence.json'))
stop_location = json.load(open('stops_location.json'))
trip_num = 0
for trip in trip_sequence:
    t = []
    stops = trip.split('-')
    for s in stops:
        stop = s[8:] if s[8] != '0' else s[9:]
        t.append(stop)
        stops_all[stop] = stop_location[s]
    line15_stops.append(t)
one_day_data = split_dataset.split('2013-01-07', '2013-01-07')
one_day_data_clean = []
trips, trajectories = {}, {}
root_stop = [temp[0] for temp in line15_stops]
end_stop = [temp[-1] for temp in line15_stops]
print('Root stop:', root_stop)
print('End stop:', end_stop)
'''
index
0: timestamp 3:journey_pattern_id 4:time_frame  5: vehicle_journey_id 
8: lon 9:lat 11: block_id 12 vehicle_id 13 stop_id
'''
for line in one_day_data:
    stop_id = line[13].split('.')[0]
    # filter 1: using stop_id
    if stop_id in stops_all:
        distance = float(process.cal_distance([float(line[9]), float(line[8])], stops_all[stop_id]))
        # filter 2: using distance to closet stop
        if distance < 1000:
            primary = str(line[12]) + '#' + str(line[3])
            lon, lat, timestamp = line[8], line[9], line[0]
            if primary not in trips:
                trips[primary] = {'lon': [], 'lat': [], 'stop_id': [], 'timestamp': [], 'info': []}
                trajectories[primary] = []
            if stop_id in root_stop and (not trajectories[primary] or
                                         (trajectories[primary] and stop_id != trajectories[primary][-1]['end_stop'])):
                trajectories[primary].append({'lon': [lon], 'lat': [lat], 'timestamp': [timestamp],
                                              'travel_distance': [0], 'start_stop': stop_id,
                                              'end_stop': end_stop[root_stop.index(stop_id)]})
            elif trajectories[primary]:
                tmp = trajectories[primary][-1]
                traveled_distance = process.cal_distance([tmp['lat'][-1], tmp['lon'][-1]], [lat, lon])
                tmp['lon'].append(lon)
                tmp['lat'].append(lat)
                tmp['timestamp'].append(timestamp)
                tmp['travel_distance'].append(tmp['travel_distance'][-1] + traveled_distance)
            trips[primary]['lon'].append(lon)
            trips[primary]['lat'].append(lat)
            trips[primary]['stop_id'].append(stop_id)
            trips[primary]['timestamp'].append(timestamp)
            trips[primary]['info'].append(
                'timestamp:' + str(timestamp) + ',stop_id:' + stop_id + ',vehicle_journey_id:' +
                str(line[5]) + ',block_id:' + str(line[11]) + ',distance_stop:' + str(distance))
            one_day_data_clean.append(line)
print('Count of total trips', len(trips))
print('Count after cleansing', len(one_day_data_clean))
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
test_id = '33498#00150001'
test_tra = [tmp for tmp in trajectories[test_id] if len(tmp['lon']) > 2]
print('Trajectories count:', len(test_tra))
app.layout = html.Div([
    dcc.Graph(
        id=test_id,
        figure={
            'data': [
                go.Scatter(
                    x=test['lon'],
                    y=test['lat'],
                    text='travel distance:' + str(test['travel_distance']),
                    mode='markers',
                    opacity=0.7,
                    marker={
                        'size': 15,
                        'line': {'width': 0.5, 'color': 'white'}
                    },
                    name=test_id
                ) for test in test_tra
            ],
            'layout': go.Layout(
                xaxis={'title': 'Latitude'},
                yaxis={'title': 'Longitude'},
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest'
            )
        }
    )
])
app.run_server(debug=True)
