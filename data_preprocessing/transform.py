import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import process
from extract_route import get_routes
import split_dataset


def create_trip(lon, lat, timestamp, stop_id, primary):
    return {'lon': [lon], 'lat': [lat], 'timestamp': [timestamp], 'travel_time': [0],
            'travel_distance': [0], 'start_stop': stop_id, 'stop': [stop_id], 'speed': [0],
            'name': primary, 'end_stop': end_stop[root_stop.index(stop_id)],
            'info': ['travel time:{}s,travel distance:{}m,speed:{}km/h,stop id:{}-start'.format(0, 0, 0, stop_id)]}


def get_figure(start_stop):
    return {
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
            ) for test in trajectories_filtered[start_stop]],
        'layout': go.Layout(
            xaxis={'title': 'Traveled distance'},
            yaxis={'title': 'Traveled time'},
            margin={'l': 60, 'b': 40, 't': 10, 'r': 10},
            legend={'x': 0, 'y': -2, 'orientation': 'h'},
            hovermode='closest',
            showlegend=False,
        )
    }


# trips:{'stop_id':[], 'lon':[], 'lat':[], 'travel_time':[], 'travel_distance':[], 'timestamp':[]}
trips, stops_location = get_routes()
line15_stops = []
abbr_stops_location = dict()
# transform the format of stop id to the format that belong to dataset
for trip in trips.values():
    temp = []
    for s in trip['stop_id']:
        stop = s[8:] if s[8] != '0' else s[9:]
        temp.append(stop)
        abbr_stops_location[stop] = stops_location[s]
    # line15_stops contains stops id of a single route
    line15_stops.append(temp)
root_stop = [temp[0] for temp in line15_stops]
end_stop = [temp[-1] for temp in line15_stops]
# choose one day data
print('Total line before filtered:')
missing = 0
one_day_data = split_dataset.split('2013-01-07', '2013-01-07')
trajectories = {}
'''
index about one_day_data
0: timestamp 3:journey_pattern_id 4:time_frame  5: vehicle_journey_id 
8: lon 9:lat 11: block_id 12 vehicle_id 13 stop_id
'''
use_stop_id_filter, use_distance_filter, use_delta_filter, use_speed_filter = 1, 1, 1, 1
for line in one_day_data:
    stop_id = line[13].split('.')[0]
    primary = str(line[12]) + '#' + str(line[3])
    lon, lat, timestamp = line[8], line[9], line[0]
    if primary not in trajectories:
        trajectories[primary] = []
    # create trajectory
    if stop_id in root_stop and (not trajectories[primary] or (trajectories[primary] and (stop_id != trajectories[primary][-1]['end_stop']
                                            or trajectories[primary][-1]['stop'][-1] in root_stop))):

        trajectories[primary].append(create_trip(lon, lat, timestamp, stop_id, primary))
    elif trajectories[primary]:
        tmp = trajectories[primary][-1]
        traveled_distance = process.cal_distance([tmp['lat'][-1], tmp['lon'][-1]], [lat, lon])
        delta = (timestamp - tmp['timestamp'][-1]) / 10e5  # second
        speed = round((traveled_distance / 1000) / (delta / 3600), 2) if delta != 0 else 0
        # filter 1: using stop_id
        if stop_id not in abbr_stops_location and use_stop_id_filter:
            continue
        else:
            # if stop id is not in the route or missing, using the last position's stop id
            stop_id = stop_id if stop_id in abbr_stops_location else tmp['stop'][-1]
            distance = float(process.cal_distance([float(line[9]), float(line[8])], abbr_stops_location[stop_id]))
            # filter 2: using distance to closet stop
            if distance > 1000 and use_distance_filter:
                continue
        # delta time filter
        if delta > 1000 and use_delta_filter:
            for trip_stop in line15_stops:
                if tmp['stop'][-1] in trip_stop and trip_stop.index((tmp['stop'][-1])) < 3 and \
                        stop_id in trip_stop and trip_stop.index(stop_id) < 10:
                    trajectories[primary].append(
                        create_trip(lon, lat, timestamp, root_stop[line15_stops.index(trip_stop)], primary))
        # speed filter
        elif (speed > 120 or speed < 1) and use_speed_filter:
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
            tmp['info'].append('travel time:{}s,travel distance:{}m,speed:{}km/h,stop id:{}'.
                               format(tmp['travel_time'][-1], tmp['travel_distance'][-1], speed, stop_id))
print('Missed lines:', missing)
trajectories_filtered, count = {}, 0
for v in trajectories.values():
    for t in v:
        if len(t['lon']) > 100:
            if t['start_stop'] not in trajectories_filtered:
                trajectories_filtered[t['start_stop']] = []
            trajectories_filtered[t['start_stop']].append(t)
            count += len(t['lon'])
for start_stop, trajectory in trajectories_filtered.items():
    print('From {}, the number of trajectories:'.format(start_stop), len(trajectory))
print('Total lines after filtered:', count)
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div([
    html.Div([
        html.H1('Travel from 6318'),
        dcc.Graph(id='distance-time-6318', figure=get_figure('6318')),
        html.H1('Travel from 6282'),
        dcc.Graph(id='distance-time-6282', figure=get_figure('6282'))
    ]),
])
app.run_server(debug=True)
