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

class Block:
    def __init__(self, index, previous_hash, timestamp, data, current_hash, status, proposed_on, transactions, proposed_by, fee_recipient, block_reward, difficulty, size):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
        self.current_hash = current_hash
        self.status = status
        self.proposed_on = proposed_on
        self.transactions = transactions
        self.proposed_by = proposed_by
        self.fee_recipient = fee_recipient
        self.block_reward = block_reward
        self.difficulty = difficulty
        self.size = size

class Blockchain:
    def __init__(self):
        self.current_transactions = []
        self.chain = []
        self.nodes = set()
        self.current_data = []

        # Create the genesis block
        #self.new_block(previous_hash='1', proof=100)
        self.new_block(timestamp=time.time(), previous_hash='1', proof=100)
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
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True

        return False
#    def new_block(self, previous_hash='1', proof=100, timestamp=time()):

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

        # Reset the current list of transactions
        self.current_transactions = []

        self.chain.append(block)
        return block

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

def calculate_hash(index, previous_hash, timestamp, data):
    block_string = f"{index}{previous_hash}{timestamp}{data}"
    return hashlib.sha256(block_string.encode()).hexdigest()
# Instantiate the Node
app = Flask(__name__)
app = Flask(__name__)
blockchain = Blockchain()

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Register the initial node
blockchain.register_node(node_identifier)
# Generate a globally unique address for this node
#node_identifier = str(uuid4()).replace('-', '')
def get_machine_details():
    details = {}
    details['hostname'] = platform.node()
    details['operating_system'] = platform.system()
    details['cpu'] = platform.processor()
    details['memory'] = str(round(os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES') / (1024.0 ** 3))) + " GB"
    try:
        details['disk_space'] = subprocess.check_output(['df', '-h']).decode()
    except subprocess.CalledProcessError as e:
        details['disk_space'] = str(e.output)
    try:
        details['network_interfaces'] = subprocess.check_output(['ifconfig']).decode()
    except subprocess.CalledProcessError as e:
        details['network_interfaces'] = str(e.output)
    try:
        details['ip_address'] = subprocess.check_output(['hostname', '-I']).decode().strip()
    except subprocess.CalledProcessError as e:
        details['ip_address'] = str(e.output)
    try:
        # Get MAC address by parsing ifconfig output
        mac_output = subprocess.check_output(['ifconfig']).decode()
        mac_address = ''
        if "HWaddr" in mac_output:
            mac_address = mac_output.split("HWaddr")[1].split()[0]
        details['mac_address'] = mac_address
    except subprocess.CalledProcessError as e:
        details['mac_address'] = str(e.output)
    try:
        details['username'] = os.environ.get('USER')
    except Exception as e:
        details['username'] = str(e)
    try:
        details['gpu'] = subprocess.check_output(['lspci', '-vnn']).decode()
    except subprocess.CalledProcessError as e:
        details['gpu'] = str(e.output)
    return details
# Instantiate the Blockchain
blockchain = Blockchain()
#@app.route('/add_block', methods=['POST'])
@app.route('/add_block', methods=['POST'])
def add_block():
    try:
        data = request.form['data']
        machine_details = get_machine_details()
        proposed_by = f"IP address: {machine_details['ip_address']}, MAC address: {machine_details['mac_address']}, Username: {machine_details['username']}, Hostname: {machine_details['hostname']}, Operating System: {machine_details['operating_system']}, CPU: {machine_details['cpu']}, Memory (RAM): {machine_details['memory']}, Disk Space: {machine_details['disk_space']}, Network Interfaces: {machine_details['network_interfaces']}, GPU: {machine_details['gpu']}"
        timestamp = str(datetime.now())
        current_hash = calculate_hash(blockchain.chain[-1].index, blockchain.chain[-1].current_hash, timestamp, data)

        block = Block(
            index=len(blockchain.chain) + 1,
            previous_hash=blockchain.chain[-1].current_hash,
            timestamp=timestamp,
            data=data,
            current_hash=current_hash,
            status="Accepted",
            proposed_on=timestamp,
            transactions=data,
            proposed_by=proposed_by,
            fee_recipient="ITU Data Chain",
            block_reward="Block Mined!",
            difficulty=get_time_diff(blockchain.chain[-1].timestamp, timestamp),
            size=get_block_size(data)
        )

        blockchain.chain.append(block)


        block_data = {
            'index': block.index,
            'previous_hash': block.previous_hash,
            'timestamp': block.timestamp,
            'data': block.data.replace('\n', ' <br> '),  # Replace newlines with <br>
            'current_hash': block.current_hash,
            'status': block.status,
            'proposed_on': block.proposed_on,
            'transactions': block.transactions,
            'proposed_by': block.proposed_by.replace('\n', ' <br> '),  # Replace newlines with <br>
            'fee_recipient': block.fee_recipient,
            'block_reward': block.block_reward,
            'difficulty': block.difficulty,
            'size': block.size
        }

        filename = f"block{block.index}.json"
        with open(os.path.join('blocks', filename), 'w') as file:
            json.dump(block_data, file, indent=4)

        def sync_blocks(ip_address, port):
            url = f"http://{ip_address}:{port}/sync_blocks"
            requests.get(url)
        
        for node in blockchain.nodes:
            sync_blocks(node['ip_address'], node['port'])

        return jsonify({'message': 'Block added successfully.'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

#@app.route('/mine', methods=['GET'])
#def mine():
#    # We run the proof of work algorithm to get the next proof...
#    last_block = blockchain.last_block
#    proof = blockchain.proof_of_work(last_block)
#
#    # We must receive a reward for finding the proof.
#    # The sender is "0" to signify that this node has mined a new coin.
#    blockchain.new_transaction(
#        sender="0",
#        recipient=node_identifier,
#        amount=1,
#    )
#
#    # Forge the new Block by adding it to the chain
#    previous_hash = blockchain.hash(last_block)
#    block = blockchain.new_block(proof, previous_hash)
#
#    response = {
#        'message': "New Block Forged",
#        'index': block['index'],
#        'transactions': block['transactions'],
#        'proof': block['proof'],
#        'previous_hash': block['previous_hash'],
#        
#    }
#    return jsonify(response), 200

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



if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(debug='True', host='172.16.21.102', port=5000)
    
#With the code above, you can add a new route called '/add_block' to the Flask application. This route accepts a POST request and expects a JSON payload containing the 'proof' and 'previous_hash' values for the new block. 

#The '/add_block' route verifies the validity of the proof and the previous hash by comparing them with the last block in the chain. If they are valid, a new block is added to the blockchain with the provided proof and previous hash.

#Here's an example of how you can use cURL to add a new block:

#```shell
#curl -X POST -H "Content-Type: application/json" -d '{
#    "proof": 12345,
#    "previous_hash": "1234567890abcdef"
#}' http://172.16.21.102:5000/add_block
