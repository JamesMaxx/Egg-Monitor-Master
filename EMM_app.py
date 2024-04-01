from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

import plotly.graph_objs as go

# Create database engine
engine = create_engine('sqlite:///incubator.db')

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Read data into DataFrame
df = pd.read_sql_query('SELECT * FROM incubator_readings', engine)

app.layout = dbc.Container([
    # Layout for dashboard
    html.Div([
        dcc.Dropdown(
            id='graph-type-dropdown',
            options=[
                {'label': 'Bar Graph', 'value': 'bar'},
                {'label': 'Line Graph', 'value': 'line'},
                {'label': 'Table Graph', 'value': 'table'},
                {'label': 'Pie Chart', 'value': 'pie'}
            ],
            value='bar'
        ),
        dcc.Graph(id='incubator-graph')
    ])
])

@app.callback(
    Output('incubator-graph', 'figure'),
    [Input('graph-type-dropdown', 'value')]
)
def update_graph(graph_type):
    if graph_type == 'bar':
        data = [
            {'x': df['timestamp'], 'y': df['temperature'], 'name': 'Temperature', 'type': 'bar'},
            {'x': df['timestamp'], 'y': df['humidity'], 'name': 'Humidity', 'type': 'bar'}
        ]
    elif graph_type == 'line':
        data = [
            {'x': df['timestamp'], 'y': df['temperature'], 'name': 'Temperature', 'type': 'line'},
            {'x': df['timestamp'], 'y': df['humidity'], 'name': 'Humidity', 'type': 'line'}
        ]
    elif graph_type == 'table':
        data = [
            go.Table(
                header=dict(values=['Timestamp', 'Temperature', 'Humidity']),
                cells=dict(values=[df['timestamp'], df['temperature'], df['humidity']])
            )
        ]
    elif graph_type == 'pie':
        data = [
            go.Pie(labels=df['timestamp'], values=df['temperature'], name='Temperature'),
            go.Pie(labels=df['timestamp'], values=df['humidity'], name='Humidity')
        ]
    else:
        data = []
    
    layout = {
        'title': 'Incubator Readings',
        'xaxis': {'title': 'Timestamp'},
        'yaxis': {'title': 'Value'}
    }
    
    return {'data': data, 'layout': layout}

if __name__ == '__main__':
    app.run_server(debug=False, port=2000)

