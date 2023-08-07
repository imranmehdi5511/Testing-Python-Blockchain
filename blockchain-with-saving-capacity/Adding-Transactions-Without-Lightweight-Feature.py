import json
import requests

def add_transactions(text_file, block_size):
    with open(text_file, "r") as f:
        lines = f.readlines()

    for block_number, i in enumerate(range(0, len(lines), block_size), start=1):
        block_transactions = [line.rstrip("\n") for line in lines[i:i + block_size]]
        transaction_data = " <br> ".join(block_transactions)
        transactions = [{
            "sender": "0x0",
            "recipient": "0x0",
            "amount": 0,
            "data": transaction_data
        }]

        # Send the transactions to the server
        url = "http://172.16.21.157:5000/transactions/new"
        headers = {'Content-Type': 'application/json'}
        for transaction in transactions:
            response = requests.post(url, data=json.dumps(transaction), headers=headers)
            if response.status_code != 200:
                print(f"Error adding transaction. Status code: {response.status_code}, Response: {response.text}")

        # Mine a new block for each batch of transactions
        print(f"Mining Block {block_number}")
        requests.get("http://172.16.21.157:5000/mine")

if __name__ == "__main__":
    text_file = "/home/imran/Benchmark-Stream/mega_text_file.txt"
    block_size = 100000
    add_transactions(text_file, block_size)
