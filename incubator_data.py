import json
import random
import time
from datetime import datetime
import os

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


def append_to_json(data):
    """
    Appends the given data to the 'incubator_readings.json' file.

    Parameters:
        data (Any): The data to be appended to the JSON file.

    Returns:
        None

    Raises:
        JSONDecodeError: If there is an error decoding the JSON file.

    This function checks if the 'incubator_readings.json' file exists and is not empty. If it doesn't exist or is empty,
    it creates an empty JSON array and writes it to the file. Then, it opens the file in read and write mode and loads the
    existing JSON data into the 'readings' variable. If there is an error decoding the JSON file, it catches the
    JSONDecodeError exception and initializes 'readings' as an empty list.

    The function appends the given data to the 'readings' list, seeks to the beginning of the file, and writes the updated
    'readings' list to the file in JSON format with an indentation of 4 spaces.

    Note: The 'data' parameter can be of any type, as the function does not perform any type checking on the input data.
    """
    if not os.path.exists('incubator_readings.json') or os.path.getsize('incubator_readings.json') == 0:
        with open('incubator_readings.json', 'w') as file:
            json.dump([], file)

    with open('incubator_readings.json', 'r+') as file:
        try:
            readings = json.load(file)
        except json.decoder.JSONDecodeError:
            readings = []

        readings.append(data)
        file.seek(0)
        json.dump(readings, file, indent=4)

if __name__ == "__main__":
    try:
        while True:
            data = generate_data()
            append_to_json(data)
            print("Data appended to JSON file:", data)
            time.sleep(5)  # Wait for 5 seconds before generating the next data
    except KeyboardInterrupt:
        print("\nData generation stopped by user. JSON file saved.")
