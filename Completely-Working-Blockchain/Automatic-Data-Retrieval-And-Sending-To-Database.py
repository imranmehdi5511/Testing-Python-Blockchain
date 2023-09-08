import requests
import re
import os
from collections import defaultdict
import sqlite3

#First We Retrieve Data From The Blockchain
def save_data_to_file_and_print(data_blocks, file_path):
    with open(file_path, "w") as file:
        for index, data_list in enumerate(data_blocks, start=1):
            if data_list:
                non_null_data_list = [data.replace(" <br> ", "\n") for data in data_list if data is not None]
                formatted_data = "\n\n".join(non_null_data_list)  # Join multiple data entries with double newline
                file.write(f"Data in Block {index}:\n{formatted_data}\n\n")
                #print(f"Data in Block {index}:\n{formatted_data}\n")
            else:
                file.write(f"Data in Block {index}: null\n\n")
                #print(f"Data in Block {index}: null\n")

def get_data_from_blocks_and_save_and_print():
    url = "http://localhost:5001/get_blocks"
    response = requests.get(url)
    if response.status_code == 200:
        blockchain = response.json()['chain']
        data_blocks = []

        for block in blockchain:
            transactions = block.get('transactions')
            if transactions:
                data_list = [transaction.get('data', None) for transaction in transactions]
                data_blocks.append(data_list)
            else:
                data_blocks.append([])

        while len(data_blocks) < len(blockchain):
            data_blocks.append([])

        if data_blocks:
            save_data_to_file_and_print(data_blocks, "data_output.txt")
            print("Data saved to 'data_output.txt'")
        else:
            print("No data found in any blocks.")
    else:
        print(f"Error getting data. Status code: {response.status_code}, Response: {response.text}")

if __name__ == "__main__":
    get_data_from_blocks_and_save_and_print()

#Replace Dashed-Colon ":-" with Colon ":"
def replace_colon_dash(text):
    return re.sub(r':-', ':', text)


def main():
    for file_path in os.listdir('.'):
        if file_path.endswith('.txt'):
            with open(file_path, 'r') as f:
                data = f.readlines()

            for i, line in enumerate(data):
                data[i] = replace_colon_dash(line)

            with open(file_path, 'w') as f:
                f.writelines(data)


if __name__ == "__main__":
    main()

#Data is then sorted into files for sensors.
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
            if not line.startswith('Data in Block'):
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
    input_file_path = 'data_output.txt'
    sensor_names = detect_sensor_names(input_file_path)
    sort_data(input_file_path, sensor_names)



#Sending Data to Database  
def divide_lines_into_columns(line):
    return re.split(r'[:,]', line)

def name_table_generically(file_path, index):
    # Use a generic table name with an index
    return f"table{index}"

def create_table(cursor, table_name):
    cursor.execute(f"""CREATE TABLE IF NOT EXISTS {table_name} (
        column1 TEXT
    )""")

def send_data_to_database(cursor, table_name, data):
    for line in data:
        cursor.execute(f"INSERT INTO {table_name} (column1) VALUES (?)", (line.strip(),))

def main():
    connection = sqlite3.connect('sensor_data.db')
    cursor = connection.cursor()
    table_index = 1  # Initialize the table index

    for file_path in os.listdir('.'):
        if file_path == 'data_output.txt':
            continue  # Skip processing this file

        if file_path.endswith('.txt'):
            table_name = name_table_generically(file_path, table_index)
            create_table(cursor, table_name)

            with open(file_path, 'r') as f:
                data = f.readlines()

            send_data_to_database(cursor, table_name, data)

            table_index += 1  # Increment the table index

    connection.commit()
    connection.close()

if __name__ == "__main__":
    main()
