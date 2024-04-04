import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import sqlite3
import dash_bootstrap_components as dbc

class DashApp:
    def __init__(self, flask_app):
        self.app = dash.Dash(__name__, server=flask_app, external_stylesheets=[dbc.themes.BOOTSTRAP])  # Use Bootstrap theme
        self.flask_app = flask_app

        # Initialize the Dash app layout
        self.layout = html.Div([
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

        # Define callback to update the graph
        @self.app.callback(
            Output('incubator-graph', 'figure'),
            [Input('graph-type-dropdown', 'value')]
        )
        def update_graph(graph_type):
            # Dummy username for demonstration
            current_user = 'username'

            # Retrieve the serial numbers for the current user
            serial_numbers = self.get_user_serials(current_user)

            # Retrieve data for the given serial numbers
            df = self.get_data(serial_numbers)

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

    def get_user_serials(self, username):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT serial_number FROM incubators WHERE user_id=(SELECT id FROM users WHERE username=?)", (username,))
        serial_numbers = [row[0] for row in cursor.fetchall()]
        conn.close()
        return serial_numbers

    def get_data(self, serial_numbers):
        conn = sqlite3.connect('users.db')
        df_list = []
        for serial_number in serial_numbers:
            query = f"SELECT * FROM incubator_readings WHERE serial_number='{serial_number}'"
            df = pd.read_sql_query(query, conn)
            df_list.append(df)
        conn.close()
        return pd.concat(df_list)

    def run_server(self):
        self.app.layout = self.layout  # Assign layout to the Dash app
        self.app.run_server(debug=True, port=8050)  # Run Dash server on a different port
