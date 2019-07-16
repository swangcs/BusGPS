import os

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

import process


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
            ) for test in trajectories[start_stop]],
        'layout': go.Layout(
            xaxis={'title': 'Traveled distance'},
            yaxis={'title': 'Traveled time'},
            margin={'l': 60, 'b': 40, 't': 10, 'r': 10},
            legend={'x': 0, 'y': -2, 'orientation': 'h'},
            hovermode='closest',
            showlegend=False,
        )
    }


if __name__ == '__main__':
    trajectories_json, start_json = 'trajectories.json', 'start_stops.json'
    if not os.path.exists(trajectories_json) or not os.path.exists(start_json):
        print('run transform.py first')
    else:
        trajectories = process.load_json(trajectories_json)
        start_stops = process.load_json(start_json)
        point_count = []
        for values in trajectories.values():
            for trajectory in values:
                point_count.append(len(trajectory['lon']))
        external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
        app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
        app.layout = html.Div([
            html.Div([
                html.Div([
                    html.H1('Travel from {}'.format(stop_id)),
                    dcc.Graph(id='distance-time-{}'.format(stop_id), figure=get_figure(stop_id))
                ]) for stop_id in start_stops
            ]),
            html.Div([dcc.Graph(id='points-statistic', figure={
                'data': [go.Histogram(x=point_count)],
                'layout': go.Layout(
                    xaxis={'title': 'Number of points'},
                    yaxis={'title': 'Number of trips'},
                )
            })])
        ])
        app.run_server(debug=True)
