import requests

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
    url = "http://localhost:5000/get_blocks"
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
