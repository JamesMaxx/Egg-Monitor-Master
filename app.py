# Import necessary libraries
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
import sqlite3
from dash_app import DashApp
import random
from datetime import datetime
import threading
import time

# Initialize Flask app
app = Flask(__name__)
app.secret_key = b'\xe58\xc6Q^\xb6\xee\x99\ru\x84mj2\xc4\x85$\xe8\xa9cE\xaa\xefa'

# Initialize Bcrypt for password hashing
bcrypt = Bcrypt(app)

# Define database file
DATABASE_FILE = 'users.db'

# User Management class for database operations
class UserManagement:
    def __init__(self):
        self.create_tables()

    # Create necessary tables if they don't exist
    def create_tables(self):
        try:
            conn = sqlite3.connect(DATABASE_FILE)
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS users
                         (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')
            c.execute('''CREATE TABLE IF NOT EXISTS incubators
                         (id INTEGER PRIMARY KEY, user_id INTEGER, serial_number TEXT UNIQUE,
                         FOREIGN KEY (user_id) REFERENCES users(id))''')
            c.execute('''CREATE TABLE IF NOT EXISTS incubator_readings
                         (id INTEGER PRIMARY KEY, serial_number TEXT, timestamp TEXT,
                         temperature REAL, humidity REAL)''')
            conn.commit()
        except sqlite3.Error as e:
            print("SQLite error:", e)
        finally:
            conn.close()

    # Get database connection
    @staticmethod
    def get_connection():
        return sqlite3.connect(DATABASE_FILE, check_same_thread=False)

# User Authentication class for managing user authentication
class UserAuthentication(UserManagement):
    def __init__(self):
        super().__init__()
        self.generate_data_thread = threading.Thread(target=self.generate_data_continuously)
        self.generate_data_thread.daemon = True  # Daemonize the thread

    # Generate mock data for incubator readings every 5 seconds
    def generate_data_continuously(self):
        while True:
            conn = self.get_connection()
            c = conn.cursor()
            c.execute("SELECT serial_number FROM incubators")
            serial_numbers = [row[0] for row in c.fetchall()]
            conn.close()

            for serial_number in serial_numbers:
                incubator_data = self.generate_data(serial_number)
                self.insert_data(incubator_data)
            time.sleep(5)

    # Start the thread
    def start_data_generation_thread(self):
        self.generate_data_thread.start()

    # Generate mock data for incubator readings
    @staticmethod
    def generate_data(serial_number):
        temperature = round(random.uniform(36, 37.5), 2)
        humidity = round(random.uniform(45, 55), 2)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return {"serial_number": serial_number, "timestamp": timestamp, "temperature": temperature, "humidity": humidity}

    # Insert incubator reading data into the database
    @staticmethod
    def insert_data(data):
        conn = UserManagement.get_connection()
        with conn:
            c = conn.cursor()
            c.execute("INSERT INTO incubator_readings (serial_number, timestamp, temperature, humidity) VALUES (?, ?, ?, ?)",
                      (data['serial_number'], data['timestamp'], data['temperature'], data['humidity']))

# Initialize UserAuthentication instance
auth = UserAuthentication()

# Route for user signup
@app.route('/', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        serial_numbers = request.form.getlist('serial_number')

        try:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

            conn = UserManagement.get_connection()
            with conn:
                c = conn.cursor()
                c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
                user_id = c.lastrowid
                for serial_number in serial_numbers:
                    c.execute("INSERT INTO incubators (user_id, serial_number) VALUES (?, ?)", (user_id, serial_number))

            flash('Signup successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.Error as e:
            flash('An error occurred during signup. Please try again.', 'error')
            print("SQLite error:", e)

    return render_template('signup.html')

# Route for user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = UserManagement.get_connection()
        with conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username=?", (username,))
            user = c.fetchone()

            if user and bcrypt.check_password_hash(user[2], password):
                session['username'] = username
                session['user_id'] = user[0]
                flash(f'Welcome back, {username}!', 'success')
                return redirect(url_for('profile'))
            else:
                flash('Invalid username or password. Please try again.', 'error')

    return render_template('login.html')

# Route for user profile
@app.route('/profile')
def profile():
    if 'username' not in session:
        flash('You need to login first.', 'error')
        return redirect(url_for('login'))

    return render_template('profile.html')

# Route for user logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    auth.start_data_generation_thread()  # Start the data generation thread
    app.run(debug=True)
