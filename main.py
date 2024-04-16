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
from dash import dcc, html
import plotly.graph_objs as go
from dash.dependencies import Input, Output
from flask import Flask, redirect, render_template, request, session, url_for
from sqlalchemy import Column, Float, Integer, create_engine, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

import data_generator

"""Flask app setup"""
app = Flask(__name__, static_url_path='/static', template_folder='templates')
app.secret_key = os.urandom(24)  # Secret key for session management

"""SQLAlchemy setup"""
engine = create_engine('sqlite:///users.db', connect_args={'check_same_thread': False})

"""SQLAlchemy models"""
Base = declarative_base()

""" Define IncubatorReadings table """
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

""" UserManagement class for user registration, login, and password reset """
class UserManagement:
    def __init__(self, db_name='users.db'):
        """
        Initializes a new instance of the class.

        Parameters:
            db_name (str): The name of the database to connect to. Defaults to 'users.db'.

        Returns:
            None
        """
        self.db_name = db_name
        self.create_table()

    def connect(self):
        """
        Connects to the SQLite database specified by `db_name`.

        Parameters:
            self (object): The instance of the class.

        Returns:
            None
        """
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.conn.execute('PRAGMA foreign_keys = ON;')
        except sqlite3.Error as e:
            logging.error(f"Error connecting to database: {e}")

    def create_table(self):
        """
        Creates a new table 'users' in the database if it doesn't already exist.
        The table has columns 'id' as INTEGER PRIMARY KEY AUTOINCREMENT,
        'username' as TEXT UNIQUE NOT NULL, and 'password' as TEXT NOT NULL.

        Parameters:
            self (object): The instance of the class.

        Returns:
            None
        """
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
        """
        Closes the connection to the database if it is open.

        This function checks if the 'conn' attribute exists and is not None. If it is, the connection is closed.

        Parameters:
            self (object): The instance of the class.

        Returns:
            None
        """
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()

    def register(self, username, password):
        """
        Registers a new user with the given username and password.

        Parameters:
            username (str): The username of the user.
            password (str): The password of the user.

        Returns:
            bool: True if the user is successfully registered, False otherwise.
        """
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
        """
        Logs a user into the system with the provided username and password.

        Parameters:
            username (str): The username of the user.
            password (str): The password of the user.

        Returns:
            bool: True if the login is successful, False otherwise.
        """
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
        """
        Resets the password for a given username.

        Parameters:
            username (str): The username for which the password needs to be reset.

        Returns:
            bool: True if the password reset was successful, False otherwise.
        """
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
        """
        Hashes a password using the SHA256 algorithm and a given salt.

        :param password: The password to be hashed.
        :type password: str
        :param salt: The salt to be used in the hashing process.
        :type salt: str
        :return: The hashed password.
        :rtype: str
        """
        hashed_password = hashlib.sha256((password + salt).encode()).hexdigest()
        return hashed_password


""" DataGeneratorThread for generating data in the background """
class DataGeneratorThread(threading.Thread):
    def run(self):
        """
        Run method for the DataGeneratorThread class.

        This method is responsible for executing the data generation process.
        It calls the `generate_data` function from the `data_generator` module.

        Parameters:
            self (DataGeneratorThread): The instance of the DataGeneratorThread class.

        Returns:
            None
        """
        data_generator.generate_data()


""" Landing page route """
@app.route('/')
def landing():
    """
    Route decorator for the landing page of the web application.

    This function renders the landing.html template and returns it to the client.

    Parameters:
        None

    Returns:
        The rendered landing.html template.
    """
    return render_template('landing.html')


""" Login form route """
@app.route('/login')
def login_form():
    """
    Route decorator for the login form page of the web application.

    This function renders the login.html template and returns it to the client.

    Parameters:
        None

    Returns:
        The rendered login.html template.
    """
    return render_template('login.html')


""" User registration route """
@app.route('/register', methods=['POST'])
def register():
    """
    Registers a new user with the given username and password.

    This function is a route handler for the '/register' endpoint, which is accessed via the POST method. It expects the request to contain a 'username' and a 'password' field. If either of these fields is missing, it returns an error message indicating that all required fields must be filled out.

    If both fields are present, it creates a new instance of the UserManagement class and calls its register method with the provided username and password. If the registration is successful, it redirects the user to the login form page. If the registration fails, it returns an error message indicating that the user should try again.

    Parameters:
        None

    Returns:
        - If the registration is successful, it redirects the user to the login form page.
        - If the registration fails, it returns an error message indicating that the user should try again.
        - If any required fields are missing, it returns an error message indicating that all required fields must be filled out.
    """
    username = request.form.get('username')
    password = request.form.get('password')
    if not (username and password):
        return "Registration failed. Please fill out all required fields."
    user_manager = UserManagement()
    success = user_manager.register(username, password)
    if success:
        return redirect(url_for('login_form'))
    else:
        return "Registration failed. Please try again."


""" User login route """
@app.route('/login', methods=['POST'])
def login():
    """
    Logs a user into the system with the provided username and password.

    This function is a route handler for the '/login' endpoint, which is accessed via the POST method. It expects the request to contain a 'username' and a 'password' field. If either of these fields is missing, it returns an error message indicating that all required fields must be filled out.

    If both fields are present, it creates a new instance of the UserManagement class and calls its login method with the provided username and password. If the login is successful, it sets the 'username' in the session and redirects the user to the profile page. If the login fails, it redirects the user to the login form page.

    Parameters:
        None

    Returns:
        - If the login is successful, it redirects the user to the profile page.
        - If the login fails, it redirects the user to the login form page.
        - If any required fields are missing, it returns an error message indicating that all required fields must be filled out.
    """
    username = request.form.get('username')
    password = request.form.get('password')
    if not (username and password):
        return "Login failed. Please provide username and password."
    user_manager = UserManagement()
    success = user_manager.login(username, password)
    if success:
        session['username'] = username
        return redirect(url_for('profile'))
    else:
        return redirect(url_for('login_form'))


""" User profile route """
@app.route('/profile')
def profile():
    """
    Route decorator for the profile page of the web application.

    This function is a route handler for the '/profile' endpoint. It checks if the 'username' is present in the session. If it is, it retrieves the username from the session and renders the 'profile.html' template with the username as a parameter. If the 'username' is not present in the session, it redirects the user to the login form page.

    Parameters:
        None

    Returns:
        - If the 'username' is present in the session, it renders the 'profile.html' template with the username as a parameter.
        - If the 'username' is not present in the session, it redirects the user to the login form page.
    """
    if 'username' in session:
        username = session['username']
        return render_template('profile.html', username=username)
    else:
        return redirect(url_for('login_form'))


@app.route('/logout', methods=['POST'])
def logout():
    """
    Logs out the current user by removing the username from the session.

    This function is a route handler for the '/logout' endpoint, which is accessed via the POST method.
    It removes the 'username' from the session and redirects the user to the landing page.

    Returns:
        Redirect: Redirects the user to the landing page.
    """
    session.pop('username', None)
    return redirect(url_for('landing'))

""" Dash app initialization """
dash_app = dash.Dash(__name__, server=app, external_stylesheets=[dbc.themes.BOOTSTRAP])

""" Dash layout and callbacks """
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
    """
    Callback function for updating the graph based on the selected graph type.

    Args:
        graph_type (str): The type of graph to display. Possible values are 'bar', 'line', 'table', and 'pie'.

    Returns:
        dict: A dictionary containing the data and layout for the graph.
            - 'data' (list): A list of dictionaries representing the data for the graph.
                - Each dictionary has the following keys:
                    - 'x' (list): The x-axis values.
                    - 'y' (list): The y-axis values.
                    - 'name' (str): The name of the data series.
                    - 'type' (str): The type of the data series.
            - 'layout' (dict): A dictionary representing the layout of the graph.
                - 'title' (str): The title of the graph.
                - 'xaxis' (dict): A dictionary representing the x-axis configuration.
                    - 'title' (str): The title of the x-axis.
                - 'yaxis' (dict): A dictionary representing the y-axis configuration.
                    - 'title' (str): The title of the y-axis.
    """
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

""" Data generator thread """
data_thread = DataGeneratorThread()
data_thread.start()

if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True, port=5000)

