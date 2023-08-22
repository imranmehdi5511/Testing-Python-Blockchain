import requests

def save_data_to_file(data_blocks, file_path):
    with open(file_path, "w") as file:
        for data in data_blocks:
            formatted_data = data.replace(" <br> ", "\n")  # Replace "<br>" with newline
            file.write(f"{formatted_data}\n\n")

def get_data_from_blocks_and_save():
    url = "http://localhost:5000/get_data"
    response = requests.get(url)
    if response.status_code == 200:
        data_blocks = response.json()['data_blocks']
        if data_blocks:
            save_data_to_file(data_blocks, "data_output.txt")
            print("Data saved to 'data_output.txt'")
        else:
            print("No data found in any blocks.")
    else:
        print(f"Error getting data. Status code: {response.status_code}, Response: {response.text}")

if __name__ == "__main__":
    get_data_from_blocks_and_save()
