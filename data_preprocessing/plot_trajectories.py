import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go


def get_scatter(x, y, text, marker: dict, name, opacity=0.7, mode='markers'):
    return go.Scatter(x=x, y=y, text=text, mode=mode, opacity=opacity, marker=marker, name=name)


def get_layout(xaxis: dict, yaxis: dict, showlegend=False):
    return go.Layout(xaxis=xaxis, yaxis=yaxis, margin={'l': 60, 'b': 40, 't': 10, 'r': 10},
                     legend={'x': 0, 'y': -2, 'orientation': 'h'}, hovermode='closest', showlegend=showlegend)


def plot(trajectories: dict, trips: dict, port=8050, debug=True, x='lon', y='lat'):
    point_count = []
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
    trip_marker = {'size': 2, 'line': {'width': 0.01, 'color': 'blue'}}
    route_marker = {'size': 10, 'line': {'width': 0.3, 'color': 'red'}}
    start_stops = list(trajectories.keys())
    data = [[get_scatter(trajectory[x], trajectory[y], trajectory['info'], trip_marker, trajectory['id'], mode='lines')
             for trajectory in trajectories[start_stop]] for start_stop in start_stops]
    for start_stop in start_stops:
        point_count.extend([len(trajectory[x]) for trajectory in trajectories[start_stop]])
        data[start_stops.index(start_stop)].append(
            get_scatter(trips[start_stop][x], trips[start_stop][y], trips[start_stop]['stop_id'], route_marker,
                        start_stop))
    app.layout = html.Div([
        html.Div([
            html.Div([
                dcc.Graph(id=''.format('15'), figure={
                    'data': d,
                    'layout': get_layout({'title': x}, {'title': y})
                }) for d in data
            ])
        ]),
        html.Div([dcc.Graph(id='points-statistic', figure={
            'data': [go.Histogram(x=point_count)],
            'layout': go.Layout(
                xaxis={'title': 'Number of points'},
                yaxis={'title': 'Number of trips'},
            )
        })])
    ])
    app.run_server(debug=debug, port=port)
