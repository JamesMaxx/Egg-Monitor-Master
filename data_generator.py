import random
from datetime import datetime
import sqlite3
import time

def generate_data():
    """
    Generate data including temperature, humidity, and timestamp.
    No parameters.
    Returns a dictionary with keys 'timestamp', 'temperature', and 'humidity'.
    """
    temperature = round(random.uniform(36, 37.5), 2)
    humidity = round(random.uniform(45, 55), 2)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return {"timestamp": timestamp, "temperature": temperature, "humidity": humidity}

def get_random_user():
    """
    Fetches a random user from the 'users' table in the SQLite database 'users.db'.

    Returns:
        str: A username of a random user.
    """
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users ORDER BY RANDOM() LIMIT 1")
    user = cursor.fetchone()
    conn.close()
    return user[0] if user else None

def save_to_database(data, username):
    """
    Saves the given data to the 'incubator_readings' table in the SQLite database 'users.db'.
    If the table does not exist, it will be created.

    Parameters:
        data (dict): The data to be saved to the database. It must have keys 'timestamp', 'temperature', and 'humidity'.
        username (str): The username associated with the data.

    Returns:
        None
    """
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Check if the table exists, and create it if it doesn't
    cursor.execute('''CREATE TABLE IF NOT EXISTS incubator_readings (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT NOT NULL,
                            timestamp TEXT NOT NULL,
                            temperature REAL NOT NULL,
                            humidity REAL NOT NULL
                        )''')

    cursor.execute("INSERT INTO incubator_readings (username, timestamp, temperature, humidity) VALUES (?, ?, ?, ?)",
                   (username, data['timestamp'], data['temperature'], data['humidity']))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    try:
        while True:
            data = generate_data()
            username = get_random_user()
            if username:
                save_to_database(data, username)
                print("Data appended to database for user", username, ":", data)
            else:
                print("No users found in the database.")
            time.sleep(5)  # Wait for 5 seconds before generating the next data
    except KeyboardInterrupt:
        print("\nData generation stopped by user. Database updated.")
