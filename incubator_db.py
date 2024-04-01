import sqlite3
import random
import time
from datetime import datetime
from tkinter import *
from tkinter import ttk

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

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

def create_table():
    """
    Create a table named 'incubator_readings' in the database if it doesn't exist.
    """
    conn = sqlite3.connect('incubator.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS incubator_readings
                 (timestamp TEXT, temperature REAL, humidity REAL)''')
    conn.commit()
    conn.close()

def insert_data(data):
    """
    Insert the given data into the 'incubator_readings' table in the database.

    Parameters:
        data (dict): The data to be inserted into the table.

    Returns:
        None
    """
    conn = sqlite3.connect('incubator.db')
    c = conn.cursor()
    c.execute("INSERT INTO incubator_readings VALUES (?, ?, ?)",
              (data['timestamp'], data['temperature'], data['humidity']))
    conn.commit()
    conn.close()

def plot_line_graph():
    """
    Create a line graph of temperature and humidity over time.
    """
    conn = sqlite3.connect('incubator.db')
    c = conn.cursor()
    c.execute("SELECT timestamp, temperature, humidity FROM incubator_readings")
    data = c.fetchall()
    x = [item[0] for item in data]
    y_temp = [item[1] for item in data]
    y_hum = [item[2] for item in data]
    plt.plot_date(x, y_temp, '-', label='Temperature')
    plt.plot_date(x, y_hum, '--', label='Humidity')
    plt.xlabel('Time')
    plt.ylabel('Temperature (°C) and Humidity (%)')
    plt.legend()
    plt.gcf().autofmt_xdate()
    plt.show()

def plot_bar_graph():
    """
    Create a bar graph of temperature and humidity over time.
    """
    conn = sqlite3.connect('incubator.db')
    c = conn.cursor()
    c.execute("SELECT strftime('%H', timestamp), temperature, humidity FROM incubator_readings")
    data = c.fetchall()
    x = [item[0] for item in data]
    y_temp = [item[1] for item in data]
    y_hum = [item[2] for item in data]
    fig, axs = plt.subplots(ncols=2, sharey=True)
    axs[0].bar(x, y_temp)
    axs[0].set_ylabel('Temperature (°C)')
    axs[1].bar(x, y_hum)
    axs[1].set_ylabel('Humidity (%)')
    plt.xlabel('Time (hour)')
    plt.show()

def view_data(choice):
    """
    View the data in table form, line graph, or bar graph based on the choice.

    Parameters:
        choice (str): The choice made from the dropdown menu.

    Returns:
        None
    """
    if choice == 'Table':
        conn = sqlite3.connect('incubator.db')
        c = conn.cursor()
        c.execute("SELECT * FROM incubator_readings")
        data = c.fetchall()
        for row in data:
            print(row)
        conn.close()
    elif choice == 'Line Graph':
        plot_line_graph()
    elif choice == 'Bar Graph':
        plot_bar_graph()

if __name__ == "__main__":
    create_table()

    root = Tk()
    root.title("Data Viewer")

    # Dropdown menu
    choices = ['Table', 'Line Graph', 'Bar Graph']
    selected_choice = StringVar(root)
    selected_choice.set(choices[0])
    dropdown = OptionMenu(root, selected_choice, *choices)
    dropdown.pack()

    # Button to view data
    view_button = Button(root, text="View Data", command=lambda: view_data(selected_choice.get()))
    view_button.pack()

    root.mainloop()
