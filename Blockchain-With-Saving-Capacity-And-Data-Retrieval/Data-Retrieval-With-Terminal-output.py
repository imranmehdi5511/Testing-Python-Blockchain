import requests

def save_data_to_file_and_print(data_blocks, file_path):
    with open(file_path, "w") as file:
        for data_index, data in enumerate(data_blocks):
            formatted_data = data.replace(" <br> ", "\n")  # Replace "<br>" with newline
            file.write(formatted_data + "\n")
            print(f"Data in Block {data_index + 1}:\n{formatted_data}\n")

def get_data_from_blocks_and_save_and_print():
    url = "http://localhost:5000/get_data"
    response = requests.get(url)
    if response.status_code == 200:
        data_blocks = response.json()['data_blocks']
        if data_blocks:
            save_data_to_file_and_print(data_blocks, "data_output.txt")
            print("Data saved to 'data_output.txt'")
        else:
            print("No data found in any blocks.")
    else:
        print(f"Error getting data. Status code: {response.status_code}, Response: {response.text}")

if __name__ == "__main__":
    get_data_from_blocks_and_save_and_print()
