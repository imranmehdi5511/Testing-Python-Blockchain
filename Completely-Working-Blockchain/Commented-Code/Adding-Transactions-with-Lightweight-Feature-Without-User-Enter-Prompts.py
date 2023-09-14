#The required modules are imported
import json
import requests
#Function is made to add transactions. There are two Inputs to the function. One is the text file containing the sensor data, and the other is the intended block size or the number of transactions we want to send at a time. The process of mining can also be automated using similar python scripts.
def add_transactions(text_file, block_size):
#The text file is read using "r", and opened.
    with open(text_file, "r") as f:
#Read the lines in the text file and store them, using the readlines() built-in function
        lines = f.readlines()

    current_index = 0
    while current_index < len(lines):
        block_transactions = [line.rstrip("\n") for line in lines[current_index:current_index + block_size]]
        transaction_data = " <br> ".join(block_transactions)
        transactions = [{
            "sender": "0x0",
            "recipient": "0x0",
            "amount": 0,
            "data": transaction_data
        }]
#You can change the url to the url of your server
        # Send the transactions to the server
        url = "http://172.16.21.157:5000/transactions/new"
        headers = {'Content-Type': 'application/json'}
        for transaction in transactions:
            response = requests.post(url, data=json.dumps(transaction), headers=headers)
            if response.status_code != 200:
                print(f"Error adding transaction. Status code: {response.status_code}, Response: {response.text}")

        # Mine a new block for each batch of transactions
        #print(f"Mining Block {current_index // block_size + 1}")
        #requests.get("http://172.16.21.157:5000/mine")

        # Wait for user input
        input("Press Enter to add the next batch of transactions...")

        current_index += block_size
        print("Current_index: {current_index}")
if __name__ == "__main__":
#Replace the path to file with the path to your text file. 
    text_file = "/home/imran/Benchmark-Stream/mega_text_file.txt"
#Number of lines you want to be sent each time as part of transaction, to the transaction pool
    block_size = 100000
#Transaction added
    add_transactions(text_file, block_size)
