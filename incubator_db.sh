#!/bin/bash

# Create SQLite database if it doesn't exist
if [ ! -f incubator.db ]; then
  sqlite3 incubator.db "CREATE TABLE incubator_readings (timestamp TEXT, temperature REAL, humidity REAL);"
fi

# Function to generate random sample data
generate_data() {
  timestamp=$(date +'%Y-%m-%d %H:%M:%S')
  temperature=$((RANDOM%41+36))
  humidity=$((RANDOM%10+45))

  echo "INSERT INTO incubator_readings VALUES ('$timestamp', $temperature, $humidity);"
}

# Main loop to continuously generate and insert data
for i in {1..1000}; do
  data=$(generate_data)
  sqlite3 incubator.db "$data"
done

