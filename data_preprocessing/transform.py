import json
import random

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

import process
import split_dataset


def create_trip(lon, lat, timestamp, stop_id, primary):
    return {'lon': [lon], 'lat': [lat], 'timestamp': [timestamp], 'travel_time': [0],
            'travel_distance': [0], 'start_stop': stop_id, 'stop': [stop_id], 'speed': [0],
            'name': primary, 'end_stop': end_stop[root_stop.index(stop_id)],
            'info': ['travel time:0,travel distance:0,speed:0,stop id:' + str(stop_id)]}


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
trajectories = {}
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
            if primary not in trajectories:
                trajectories[primary] = []
            if stop_id in root_stop and (not trajectories[primary] or
                                         (trajectories[primary] and (stop_id != trajectories[primary][-1]['end_stop']
                                                                     or trajectories[primary][-1]['stop'][
                                                                         -1] in root_stop))):
                # create trajectory
                trajectories[primary].append(create_trip(lon, lat, timestamp, stop_id, primary))
            elif trajectories[primary]:
                tmp = trajectories[primary][-1]
                traveled_distance = process.cal_distance([tmp['lat'][-1], tmp['lon'][-1]], [lat, lon])
                delta = (timestamp - tmp['timestamp'][-1]) / 10e5  # second
                speed = round((traveled_distance / 1000) / (delta / 3600), 2) if delta != 0 else 0
                # delta time filter
                if delta > 1000:
                    for trip_stop in line15_stops:
                        if (tmp['stop'][-1] in trip_stop and trip_stop.index((tmp['stop'][-1])) < 3) and (
                                stop_id in trip_stop and trip_stop.index(stop_id) < 10):
                            trajectories[primary].append(
                                create_trip(lon, lat, timestamp, root_stop[line15_stops.index(trip_stop)], primary))
                    # print(tmp['name'].ljust(14, ' '), stop_id, delta, len(tmp['stop']), tmp['stop'])
                # speed filter
                elif speed > 120 or speed < 1:
                    # fast_point.append([tmp['name'].ljust(14, ' '), speed, 'km/h', traveled_distance, 'm', delta, 's'])
                    continue
                else:
                    tmp['lon'].append(lon)
                    tmp['lat'].append(lat)
                    tmp['stop'].append(stop_id)
                    tmp['timestamp'].append(timestamp)
                    tmp['travel_time'].append(round(tmp['travel_time'][-1] + delta, 3))
                    tmp['travel_distance'].append(round(tmp['travel_distance'][-1] + traveled_distance, 2))
                    speed = tmp['speed'][-1] if traveled_distance == 0 else speed
                    tmp['speed'].append(speed)  # km/h
                    tmp['info'].append(
                        'traveled time:' + str(tmp['travel_time'][-1]) + 's,traveled distance:'
                        + str(tmp['travel_distance'][-1]) + 'm,speed:' + str(speed) + 'km/h,stop id:' + stop_id)
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
trajectories_filtered = []
for v in trajectories.values():
    for t in v:
        if len(t['lon']) > 100:
            trajectories_filtered.append(t)
print('Total number of trajectories:', len(trajectories_filtered))
test_num = random.randint(0, len(trajectories_filtered) - 15)
app.layout = html.Div([
    html.Div([
        html.H1('Distance-Time'),
        dcc.Graph(
            id='distance-time',
            figure={
                'data': [
                    go.Scatter(
                        x=test['travel_distance'],
                        y=test['travel_time'],
                        text=test['info'],
                        mode='lines',
                        opacity=0.7,
                        marker={
                            'size': 15,
                            'line': {'width': 0.5, 'color': 'white'}
                        },
                        # name=test['name']
                    ) for test in trajectories_filtered],
                'layout': go.Layout(
                    xaxis={'title': 'Traveled distance'},
                    yaxis={'title': 'Traveled time'},
                    margin={'l': 60, 'b': 40, 't': 10, 'r': 10},
                    legend={'x': 0, 'y': -2, 'orientation': 'h'},
                    hovermode='closest',
                    showlegend=False,
                    )
            }
        )
    ]),
    # html.Div([
    #     html.Div([
    #         html.H1('trip no.{}'.format(trajectories_filtered.index(test))),
    #         dcc.Graph(
    #             id='trip no.{}'.format(trajectories_filtered.index(test)),
    #             figure={
    #                 'data': [
    #                     go.Scatter(
    #                         x=test['lon'],
    #                         y=test['lat'],
    #                         text=test['info'],
    #                         mode='markers',
    #                         opacity=0.7,
    #                         marker={
    #                             'size': 15,
    #                             'line': {'width': 0.5, 'color': 'white'}
    #                         },
    #                         name=test['name']
    #                     )
    #                 ],
    #                 'layout': go.Layout(
    #                     xaxis={'title': 'Latitude'},
    #                     yaxis={'title': 'Longitude'},
    #                     margin={'l': 60, 'b': 40, 't': 10, 'r': 10},
    #                     legend={'x': 0, 'y': 1},
    #                     hovermode='closest'
    #                 )
    #             }
    #         )]) for test in trajectories_filtered
    # ])
])
html.Div()
app.run_server(debug=True)
