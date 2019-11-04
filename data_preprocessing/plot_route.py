from utils import get_route_info
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go


if __name__ == '__main__':
    '''
    plot route on local server
    '''
    trips, stops_location = get_route_info(route_short_name='121')
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
    app.layout = html.Div([
        html.Div([
            html.H1('Standard Route travel distance-time'),
        ]),
        html.Div([
            html.Div([
                dcc.Graph(
                    id='trip no.{}'.format(k),
                    figure={
                        'data': [
                            go.Scatter(
                                x=test['travel_distance'],
                                y=test['travel_time'],
                                text=test['stop_id'],
                                mode='lines',
                                opacity=1,
                                marker={
                                    'size': 100,
                                    'line': {'width': 1, 'color': 'white'}
                                },
                                name=k
                            )
                        ],
                        'layout': go.Layout(
                            xaxis={'title': 'Traveled distance'},
                            yaxis={'title': 'Traveled time'},
                            margin={'l': 60, 'b': 40, 't': 10, 'r': 10},
                            legend={'x': 0, 'y': 1},
                            hovermode='closest'
                        )
                    }
                )]) for k, test in trips.items()
        ])
    ])
    app.run_server(debug=True)
