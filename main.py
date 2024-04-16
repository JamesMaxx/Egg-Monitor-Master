import hashlib
import logging
import os
import secrets
import sqlite3
import string
import threading
from datetime import datetime
import pandas as pd

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html  # Updated import statements
import plotly.graph_objs as go
from dash.dependencies import Input, Output
from flask import Flask, redirect, render_template, request, session, url_for
from sqlalchemy import Column, Float, Integer, create_engine, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

import data_generator

# Flask app initialization
app = Flask(__name__, static_url_path='/static', template_folder='templates')
app.secret_key = os.urandom(24)  # Secret key for session management

# SQLAlchemy database setup
engine = create_engine('sqlite:///users.db', connect_args={'check_same_thread': False})

# Define SQLAlchemy Base
Base = declarative_base()

# Define IncubatorReadings table
class IncubatorReadings(Base):
    __tablename__ = 'incubator_readings'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.now)
    temperature = Column(Float)
    humidity = Column(Float)

# Create tables if they don't exist
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
db_session = Session()

df = pd.read_sql_query('SELECT * FROM incubator_readings', engine)

# Setup logging
logging.basicConfig(filename='app.log', level=logging.INFO)

# UserManagement class for user registration, login, and password reset
class UserManagement:
    def __init__(self, db_name='users.db'):
        self.db_name = db_name
        self.create_table()

    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.conn.execute('PRAGMA foreign_keys = ON;')
        except sqlite3.Error as e:
            logging.error(f"Error connecting to database: {e}")

    def create_table(self):
        if not os.path.exists(self.db_name):
            try:
                self.connect()
                self.conn.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL
                    );
                ''')
                logging.info("Database tables created successfully.")
            except sqlite3.Error as e:
                logging.error(f"Error creating table: {e}")
            finally:
                self.close()

    def close(self):
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()

    def register(self, username, password):
        try:
            self.connect()
            salt = secrets.token_hex(8)  # Generate a random salt
            hashed_password = self.hash_password(password, salt)  # Hash password with salt
            hashed_password_with_salt = f"{hashed_password}:{salt}"  # Combine hashed password and salt
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO users (username, password)
                VALUES (?, ?)
            ''', (username, hashed_password_with_salt))  # Pass hashed password with salt to the database
            self.conn.commit()
            logging.info("Registration successful.")
            return True
        except sqlite3.IntegrityError:
            logging.warning("Username already exists. Please choose a different username.")
            return False
        except sqlite3.Error as e:
            logging.error(f"Error registering user: {e}")
            return False
        finally:
            self.close()

    def login(self, username, password):
        try:
            self.connect()
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()
            if user:
                stored_password_with_salt = user[2]
                stored_password_hash, salt = stored_password_with_salt.split(':')
                hashed_password = self.hash_password(password, salt)
                if hashed_password == stored_password_hash:
                    logging.info("Login successful.")
                    return True
            logging.warning("Incorrect username or password. Please try again.")
            return False
        except sqlite3.Error as e:
            logging.error(f"Error logging in: {e}")
            return False
        finally:
            self.close()

    def reset_password(self, username):
        try:
            self.connect()
            cursor = self.conn.cursor()
            new_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(10))
            cursor.execute('''
                UPDATE users SET password = ? WHERE username = ?
            ''', (self.hash_password(new_password), username))
            self.conn.commit()
            logging.info(f"Password reset successful for user {username}. New password: {new_password}")
            return True
        except sqlite3.Error as e:
            logging.error(f"Error resetting password: {e}")
            return False
        finally:
            self.close()

    def hash_password(self, password, salt):
        hashed_password = hashlib.sha256((password + salt).encode()).hexdigest()
        return hashed_password


# DataGeneratorThread for generating data in the background
class DataGeneratorThread(threading.Thread):
    def run(self):
        data_generator.generate_data()


# Landing page route
@app.route('/')
def landing():
    return render_template('landing.html')


# Login form route
@app.route('/login')
def login_form():
    return render_template('login.html')


# User registration route
@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    if not (username and password):
        return "Registration failed. Please fill out all required fields."
    user_manager = UserManagement()
    success = user_manager.register(username, password)
    if success:
        return redirect(url_for('login_form'))  # Redirect to login form
    else:
        return "Registration failed. Please try again."


# User login route
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    if not (username and password):
        return "Login failed. Please provide username and password."
    user_manager = UserManagement()
    success = user_manager.login(username, password)
    if success:
        session['username'] = username
        return redirect(url_for('profile'))  # Redirect to profile.html
    else:
        return redirect(url_for('login_form'))  # Redirect to login form


# User profile route
@app.route('/profile')
def profile():
    if 'username' in session:
        username = session['username']
        return render_template('profile.html', username=username)
    else:
        return redirect(url_for('login_form'))


# Dash app initialization
dash_app = dash.Dash(__name__, server=app, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Dash layout and callbacks
dash_app.layout = dbc.Container([
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

@dash_app.callback(
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

# Data generator thread
data_thread = DataGeneratorThread()
data_thread.start()

if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True, port=5000)
