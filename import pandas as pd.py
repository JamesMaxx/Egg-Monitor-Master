import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px

# Load data from JSON file
df = pd.read_json("incubator_readings.json")

# Convert timestamp to datetime with correct format
df["timestamp"] = pd.to_datetime(df["timestamp"], format='%Y:%m:%d %H:%M:%S')

# Create a Dash app
app = dash.Dash(__name__)

# Define layout
app.layout = html.Div([
    html.H1("Incubator Monitoring Dashboard"),
    html.Div([
        dcc.Dropdown(
            id='chart-type',
            options=[
                {'label': 'Line Chart', 'value': 'line'},
                {'label': 'Bar Chart', 'value': 'bar'}
            ],
            value='line',
            clearable=False
        ),
        dcc.Graph(id='data-graph'),
    ]),
    html.Div([
        html.Label("Date Range:"),
        dcc.DatePickerRange(
            id='date-range',
            start_date=df['timestamp'].min(),
            end_date=df['timestamp'].max(),
            display_format='YYYY-MM-DD'
        ),
        html.Label("Time Range (Hour):"),
        dcc.RangeSlider(
            id='time-range',
            min=0,
            max=23,
            step=1,
            value=[0, 23],
            marks={i: str(i) for i in range(0, 24)}
        )
    ]),
    html.Div(id='historical-data')
])

# Define callback to update graphs based on selected chart type
@app.callback(
    Output('data-graph', 'figure'),
    [Input('date-range', 'start_date'),
     Input('date-range', 'end_date'),
     Input('time-range', 'value'),
     Input('chart-type', 'value')]
)
def update_graphs(start_date, end_date, time_range, chart_type):
    """
    Updates the data graph based on the selected date range, time range, and chart type.

    Parameters:
        start_date (str): The start date of the selected date range.
        end_date (str): The end date of the selected date range.
        time_range (tuple): The range of hours to filter the data by.
        chart_type (str): The type of chart to display.

    Returns:
        fig (plotly.graph_objects.Figure): The updated data graph.
    """
    filtered_df = df.copy()
    filtered_df = filtered_df[(filtered_df['timestamp'] >= start_date) & (filtered_df['timestamp'] <= end_date)]
    filtered_df = filtered_df[filtered_df['timestamp'].dt.hour.between(*time_range)]

    if chart_type == 'line':
        fig = px.line(filtered_df, x='timestamp', y=['temperature', 'humidity'], title='Temperature and Humidity')
    else:
        fig = px.bar(filtered_df, x='timestamp', y=['temperature', 'humidity'], title='Temperature and Humidity',
                     color_discrete_map={'temperature': 'navy', 'humidity': 'darkred'})

    return fig

# Define callback to update historical data
@app.callback(
    Output('historical-data', 'children'),
    [Input('date-range', 'start_date'),
     Input('date-range', 'end_date'),
     Input('time-range', 'value')]
)
def update_historical_data(start_date, end_date, time_range):
    """
    Updates the historical data based on the given start date, end date, and time range.

    Parameters:
        start_date (str): The start date for filtering the data.
        end_date (str): The end date for filtering the data.
        time_range (list): A list containing the start and end time for filtering the data.

    Returns:
        html.Div: The updated historical data as an HTML table.
    """
    filtered_df = df.copy()
    filtered_df = filtered_df[(filtered_df['timestamp'] >= start_date) & (filtered_df['timestamp'] <= end_date)]
    filtered_df = filtered_df[filtered_df['timestamp'].dt.hour.between(*time_range)]

    return html.Div([
        html.H3("Historical Data"),
        html.Table([
            html.Thead(html.Tr([html.Th(col) for col in filtered_df.columns])),
            html.Tbody([
                html.Tr([
                    html.Td(filtered_df.iloc[i][col], style={'border': '1px solid black'}) for col in filtered_df.columns
                ]) for i in range(min(len(filtered_df), 10))  # Display up to 10 rows
            ])
        ])
    ])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
