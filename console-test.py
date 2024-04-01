# console-test.py

from flask import Flask, render_template, request
import sqlite3
import pandas as pd

app = Flask(__name__) 

@app.route('/')
def index():

    # Query data
    conn = sqlite3.connect('incubator.db')
    df = pd.read_sql_query("SELECT * FROM incubator_readings ORDER BY timestamp DESC", conn)
    
    # Filter data if query params provided
    filtered_df = df
    if 'timestamp' in request.args:
        filtered_df = df[df['timestamp'].astype(str).str.contains(request.args['timestamp'])]
    if 'temperature' in request.args:
        filtered_df = df[df['temperature'].astype(str).str.contains(request.args['temperature'])]
    if 'humidity' in request.args:
        filtered_df = df[df['humidity'].astype(str).str.contains(request.args['humidity'])]
        
    # Render HTML template
    return render_template('index.html', df=filtered_df)

@app.template_filter('datetime')
def format_datetime(value):
    return pd.to_datetime(value).dt.strftime("%Y-%m-%d %H:%M:%S")

if __name__ == '__main__':
    app.run(debug=False, port=2000)
