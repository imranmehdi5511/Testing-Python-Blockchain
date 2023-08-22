import re
import os
from collections import defaultdict

def detect_sensor_names(file_path):
    """Detects the sensor names from a file.

    Args:
        file_path: The path to the file.

    Returns:
        A list of sensor names.
    """
    sensor_names = set()
    with open(file_path, 'r') as f:
        for line in f:
            match = re.match(r'^(.*?):', line)
            if match:
                sensor_names.add(match.group(1))
    return list(sensor_names)

def sort_data(file_path, sensor_names):
    """Sorts the data for each sensor and creates a new file for each sensor.

    Args:
        file_path: The path to the file.
        sensor_names: A list of sensor names.
    """
    sensor_data = defaultdict(list)

    with open(file_path, 'r') as f:
        for line in f:
            match = re.match(r'^(.*?):', line)
            if match:
                sensor_name = match.group(1)
                sensor_data[sensor_name].append(line)

    for sensor_name, data in sensor_data.items():
        data.sort()  # Sort the data for each sensor
        new_file_path = sensor_name + '.txt'
        with open(new_file_path, 'w') as f:
            f.writelines(data)

if __name__ == "__main__":
    input_file_path = 'mega_text_file.txt'
    sensor_names = detect_sensor_names(input_file_path)
    sort_data(input_file_path, sensor_names)
