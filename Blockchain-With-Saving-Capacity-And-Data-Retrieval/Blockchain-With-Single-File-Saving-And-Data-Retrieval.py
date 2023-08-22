from urllib.parse import urlparse
from uuid import uuid4
from flask import Flask
import os
import json
import hashlib
import time
import platform
import subprocess
from datetime import datetime
from flask import Flask, request, jsonify, render_template
import requests
import multiprocessing
import shutil
import flask
html_data = None
from threading import Thread
import requests
from flask import Flask, jsonify, request
BLOCKCHAIN_FILE = "blockchain_data.json"
#Replace all instances of localhost with your IP Address[IP Address of the Node], and put your desired port number instead of port number 5000
#Remove the Mining Capability for blockchain to Act as Lightweight
class Block:
    def __init__(self, index, previous_hash, timestamp, transactions, current_hash, proof):
        self.index = index
        self.timestamp = timestamp
        self.proof = proof
        self.previous_hash = previous_hash
        self.current_hash = current_hash
        self.transactions = transactions  # Change 'data' to 'transactions'

    def to_dict(self):
        """
        Convert the Block object to a dictionary
        """
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "proof": self.proof,
            "previous_hash": self.previous_hash,
            "current_hash": self.current_hash,
            "transactions": self.transactions,  # Change 'data' to 'transactions'
        }

    @staticmethod
    def from_dict(dict_block):
        return Block(
            dict_block.get("index", 0),
            dict_block.get("previous_hash", ""),
            dict_block.get("timestamp", ""),
            dict_block.get("transactions", ""),  # Change 'data' to 'transactions'
            dict_block.get("current_hash", ""),
            dict_block.get("proof", ""),  # Provide a default value for the 'proof' key
        )

class Blockchain:
    def __init__(self):
        self.current_transactions = []
        self.chain = []
        self.nodes = set()
        self.current_data = []

        # Create the genesis block
        #self.new_block(previous_hash='1', proof=100)
        #self.new_block(timestamp=time.time(), previous_hash='1', proof=100)
        self.load_blockchain()
    def add_block(self, block):
        self.chain.append(block)
    def get_block_by_index(self, index):
        for block in self.chain:
            if block.index == index:
                return block
        return None


    def register_node(self, address):
        """
        Add a new node to the list of nodes

        :param address: Address of node. Eg. 'http://192.168.0.5:5000'
        """

        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            # Accepts an URL without scheme like '192.168.0.5:5000'.
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')

    def valid_chain(self, chain):
        """
        Determine if a given blockchain is valid

        :param chain: A blockchain
        :return: True if valid, False if not
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")
            # Check that the hash of the block is correct
            last_block_hash = self.hash(last_block)
            if block['previous_hash'] != last_block_hash:
                return False

            # Check that the Proof of Work is correct
            if not self.valid_proof(last_block['proof'], block['proof'], last_block_hash):
                return False

            last_block = block
            current_index += 1

        return True
    def resolve_conflicts(self):
        """
        This is our consensus algorithm, it resolves conflicts
        by replacing our chain with the longest one in the network.

        :return: True if our chain was replaced, False if not
        """

        neighbours = self.nodes
        new_chain = None

        # We're only looking for chains longer than ours
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Check if the length is longer and the chain is valid
                if length > len(self.chain) and self.valid_chain(chain):
                #if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            # Save the updated blockchain to the file
            self.save_blockchain()
            return True

        return False

    def new_transaction(self, sender, recipient, amount, data):
        """
        Creates a new transaction to go into the next mined Block

        :param sender: Address of the Sender
        :param recipient: Address of the Recipient
        :param amount: Amount
        :param data: Additional data
        :return: The index of the Block that will hold this transaction
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
            'data': data
        })

        return self.last_block['index'] + 1



    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        """
        Creates a SHA-256 hash of a Block

        :param block: Block
        """

        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_block):
        """
        Simple Proof of Work Algorithm:

         - Find a number p' such that hash(pp') contains leading 4 zeroes
         - Where p is the previous proof, and p' is the new proof

        :param last_block: <dict> last Block
        :return: <int>
        """

        last_proof = last_block['proof']
        last_hash = self.hash(last_block)

        proof = 0
        while self.valid_proof(last_proof, proof, last_hash) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof, last_hash):
        """
        Validates the Proof

        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :param last_hash: <str> The hash of the Previous Block
        :return: <bool> True if correct, False if not.

        """

        guess = f'{last_proof}{proof}{last_hash}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"
    def load_blockchain(self):
        if os.path.exists(BLOCKCHAIN_FILE) and os.path.getsize(BLOCKCHAIN_FILE) > 0:
            try:
                with open(BLOCKCHAIN_FILE, "r") as f:
                    data = json.load(f)
                    if "chain" in data:
                        self.chain = data["chain"]
                    if "current_transactions" in data:
                        self.current_transactions = data["current_transactions"]
            except FileNotFoundError:
                pass
        else:
            # If the file does not exist or is empty, create the genesis block
            self.new_block(timestamp=time.time(), previous_hash='1', proof=100)
            self.save_blockchain()

    def save_blockchain(self):
        data = {
            "chain": self.chain,
            "current_transactions": self.current_transactions
        }
        with open(BLOCKCHAIN_FILE, "w") as f:
            json.dump(data, f)

    def new_block(self, proof, previous_hash, timestamp):
        """
        Create a new Block in the Blockchain

        :param proof: The proof given by the Proof of Work algorithm
        :param previous_hash: Hash of previous Block
        :return: New Block
        """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time.time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Check if the blockchain has been resolved after a graceful restart
        if len(self.chain) > 0:
            # Only add the block if the index is greater than the index of the last block in the blockchain
            if block['index'] > len(self.chain):
                self.current_transactions = []
                self.chain.append(block)
                self.save_blockchain()  # Save the updated blockchain to the file

        return block
def calculate_hash(index, previous_hash, timestamp, data):
    block_string = f"{index}{previous_hash}{timestamp}{data}"
    return hashlib.sha256(block_string.encode()).hexdigest()
# Instantiate the Node
app = Flask(__name__)
app = Flask(__name__)
blockchain = Blockchain()

# Generate a globally unique address for this node
node_identifier = "http://localhost:5000"

# Register the initial node
blockchain.register_node(node_identifier)

@app.route('/mine', methods=['GET'])
def mine():
    # We run the proof of work algorithm to get the next proof...
    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block)

    # We must receive a reward for finding the proof.
    # The sender is "0" to signify that this node has mined a new coin.
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
        data=None,
    )

    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    #block = blockchain.new_block(proof, previous_hash)
    timestamp = datetime.now()
    block = blockchain.new_block(proof, previous_hash, timestamp)
    # Extract the 'data' field from each transaction
    transactions_with_data = []
    for transaction in block['transactions']:
        transaction_data = transaction['data']
        transactions_with_data.append(transaction_data)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': transactions_with_data,
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    for node in blockchain.nodes:
        if node != node_identifier:
            url = f"http://{node}/sync_blocks"
            headers = {'Content-Type': 'application/json'}
            requests.post(url, json=block)

    
    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ['sender', 'recipient', 'amount', 'data']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'], values['data'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201



@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201


@app.route('/nodes', methods=['GET'])
def get_nodes():
    nodes = list(blockchain.nodes)
    response = {
        'nodes': nodes
    }
    return jsonify(response), 200


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200

@app.route('/sync_blocks', methods=['POST'])
def sync_blocks():
    new_block_data = request.get_json()

    # Validate the received block data
    required_fields = ['index', 'timestamp', 'transactions', 'proof', 'previous_hash', 'current_hash']
    if not all(field in new_block_data for field in required_fields):
        return 'Invalid block data', 400

    # Check if the block already exists in the local chain
    local_block = blockchain.get_block_by_index(new_block_data['index'])
    if local_block:
        return 'Block already exists', 409

    # Add the received block to the local chain
    blockchain.add_block(new_block_data)

    return 'Block added to the chain', 201
@app.route('/get_blocks', methods=['GET'])
def get_blocks():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

@app.route('/get_blocks/<int:index>', methods=['GET'])
def get_block_by_index(index):
    block = blockchain.get_block_by_index(index)
    if block:
        return jsonify(block), 200
    else:
        return "Block not found", 404


@app.route('/exit', methods=['POST'])
def graceful_exit():
    # Save the blockchain data before exiting
    blockchain.save_blockchain()
    # Perform any other cleanup or shutdown tasks here
    # ...

    # Exit the application gracefully
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if shutdown:
        shutdown()

    return 'Exiting blockchain node gracefully...', 200
@app.route('/restart', methods=['POST'])
def restart():
    # Save the blockchain data before restarting
    blockchain.save_blockchain()
    # Perform any other cleanup or restart tasks here
    # ...

    # Restart the application gracefully
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if shutdown:
        shutdown()

    # Start the application again in a new process
    new_process = multiprocessing.Process(target=start_app, args=())
    new_process.start()
    # Resolve conflicts after restart
    blockchain.resolve_conflicts()

    return 'Restarting blockchain node gracefully...', 200
def start_app():
    # Start the app again on the same port
    app.run(debug=True, host='localhost', port=5000)
@app.route('/get_data', methods=['GET'])
def get_data():
    data_blocks = []
    for block in blockchain.chain:
        if block['transactions'] and block['transactions'][0]['data'] is not None:
            data_blocks.append(block['transactions'][0]['data'])

    response = {
        'data_blocks': data_blocks
    }
    return jsonify(response), 200

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(debug='True', host='localhost', port=5000)

