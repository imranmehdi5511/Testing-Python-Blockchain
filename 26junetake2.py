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
class Block:
    def __init__(self, index, previous_hash, timestamp, data, current_hash,
                 status=None, proposed_on=None, transactions=None, proposed_by=None,
                 fee_recipient=None, block_reward=None, difficulty=None, size=None):
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
        #self.name = name
    def compute_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    def index(self):
        return self.index
class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_data = []
    def add_block(self, block):
        self.chain.append(block)
    def get_block_by_index(self, index):
        for block in self.chain:
            if block.index == index:
                return block
        return None
    def __iter__(self):
        return iter(self.chain)
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
def initialize_blockchain():
    blockchain = Blockchain()
    endpoints = ['/blocks', '/block/<index>']
    if os.listdir('blocks'):
        for filename in os.listdir('blocks'):
            if filename.endswith('.json'):
                with open(os.path.join('blocks', filename), 'r') as file:
                    block_data = json.load(file)
                    block = Block(
                        index=block_data['index'],
                        previous_hash=block_data['previous_hash'],
                        timestamp=block_data['timestamp'],
                        data=block_data['data'],
                        current_hash=block_data['current_hash'],
                        status=block_data.get('status'),
                        proposed_on=block_data.get('proposed_on'),
                        transactions=block_data.get('transactions'),
                        proposed_by=block_data.get('proposed_by'),
                        fee_recipient=block_data.get('fee_recipient'),
                        block_reward=block_data.get('block_reward'),
                        difficulty=block_data.get('difficulty'),
                        size=block_data.get('size')
                    )
                    blockchain.add_block(block)
    else:
        genesis_block = Block(
            index=0,
            previous_hash="0",
            timestamp=str(datetime.now()),
            data="Genesis Block",
            current_hash="0",
            status="NULL",
            proposed_on="NULL",
            fee_recipient="NULL",
            block_reward="NULL",
            difficulty="NULL",
            size="NULL"
        )
        blockchain.add_block(genesis_block)
        block_data = {
            'index': genesis_block.index,
            'previous_hash': genesis_block.previous_hash,
            'timestamp': genesis_block.timestamp,
            'data': genesis_block.data.replace('\n', ' <br> '),  # Replace newlines with <br>
            'current_hash': genesis_block.current_hash,
            'status': genesis_block.status,
            'proposed_on': genesis_block.proposed_on,
            'transactions': genesis_block.transactions,
            'proposed_by': genesis_block.proposed_by,
            'fee_recipient': genesis_block.fee_recipient,
            'block_reward': genesis_block.block_reward,
            'difficulty': genesis_block.difficulty,
            'size': genesis_block.size
        }
        filename = f"block{genesis_block.index}.json"
        with open(os.path.join('blocks', filename), 'w') as file:
            json.dump(block_data, file, indent=4) 
    #last_block = blockchain.chain[-1]
    #index, previous_hash = last_block.index, last_block.current_hash
    #while True:
        #time.sleep(5)
        #yield index, previous_hash
    return blockchain, endpoints
def calculate_hash(index, previous_hash, timestamp, data):
    block_string = f"{index}{previous_hash}{timestamp}{data}"
    return hashlib.sha256(block_string.encode()).hexdigest()
app = Flask(__name__)
blockchain, endpoints = initialize_blockchain()
@app.route('/add_block', methods=['POST'])
def add_block():
    try:
        data = request.form['data']
        machine_details = get_machine_details()
        proposed_by = f"IP address: {machine_details['ip_address']}, MAC address: {machine_details['mac_address']}, Username: {machine_details['username']}, Hostname: {machine_details['hostname']}, Operating System: {machine_details['operating_system']}, CPU: {machine_details['cpu']}, Memory (RAM): {machine_details['memory']}, Disk Space: {machine_details['disk_space']}, Network Interfaces: {machine_details['network_interfaces']}, GPU: {machine_details['gpu']}"
        timestamp = str(datetime.now())
        current_hash = calculate_hash(blockchain.chain[-1].index, blockchain.chain[-1].current_hash, timestamp, data)
        #index, previous_hash = update_last_block_info()
        block = Block(
            index=len(blockchain.chain),
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
        blockchain.add_block(block)
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
            response = requests.get(url)
            if response.status_code == 200:
                blocks = response.json()
                for block in blocks:
                    blockchain.add_block(block)
                print("Successfully synced blocks")
            else:
                print("Failed to sync blocks")

        return jsonify({'message': 'Block added successfully!', 'block': block_data}), 201
    except Exception as e:
        return jsonify({'message': str(e), 'status': 'error'}), 500
@app.route('/')
def home():
    return render_template('index.html', data=html_data)
@app.route('/blocks', methods=['GET'])
def get_blocks():
    return jsonify([block.__dict__ for block in blockchain.chain])
@app.route('/block/<index>', methods=['GET'])
def get_block(index):
    block = blockchain.get_block_by_index(int(index))
    if block:
        return jsonify(block.__dict__)
    else:
        return jsonify({'error': 'Block not found'})
def get_time_diff(start_time, end_time):
    start = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S.%f")
    end = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S.%f")
    diff = end - start
    hours, remainder = divmod(diff.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = diff.microseconds / 1000
    time_diff = f"{int(hours)} hours {int(minutes)} minutes {int(seconds)} seconds {int(milliseconds)} milliseconds"
    return time_diff
def get_block_size(data):
    return len(data)
def get_nodes_from_file():
    with open('peers.txt', 'r') as file:
        nodes = file.read().splitlines()
        nodes = [node.strip() for node in nodes]
        #print('The nodes are:', nodes)
        return nodes
def extract_blocks(data):
    blocks = []
    current_block = ""
    block_started = False
    for char in data:
        if char == '{':
            block_started = True
            current_block += char
        elif char == '}':
            current_block += char
            blocks.append(current_block)
            current_block = ""
            block_started = False
        elif block_started:
            current_block += char
    return blocks
def store_block(block, index):
    # The following command will create a 'blocks' directory if it does not exist already
    if not os.path.exists('blocks'):
        os.makedirs('blocks')
    # Generate a unique filename for the block
    filename = f"block{str(index)}.json"  
    # Save the block to a file in the 'blocks' directory
    with open(os.path.join('blocks', filename), 'w') as file:
        file.write(block)
def update_index(index):
    last_block = blockchain.chain[-1]
    last_block.index = index
def update_ledger(blocks):
    # Check if any of the blocks are new.
    new_blocks = []
    for block in blocks:
        block_data = json.loads(block)
        index = block_data['index']
        previous_hash = block_data['previous_hash']
        timestamp = block_data['timestamp']
        data = block_data['data']
        current_hash = block_data['current_hash']
        status = block_data.get('status')
        proposed_on = block_data.get('proposed_on')
        transactions = block_data.get('transactions')
        proposed_by = block_data.get('proposed_by')
        fee_recipient = block_data.get('fee_recipient')
        block_reward = block_data.get('block_reward')
        difficulty = block_data.get('difficulty')
        size = block_data.get('size')
        if block not in blockchain:
            # Update index, previous_hash, and other variables as needed
            index, previous_hash = update_index_previous_hash()
            update_previous_block_hash(index, current_hash)

            block = Block(
                index=index,
                previous_hash=previous_hash,
                timestamp=timestamp,
                data=data,
                current_hash=current_hash,
                status=status,
                proposed_on=proposed_on,
                transactions=transactions,
                proposed_by=proposed_by,
                fee_recipient=fee_recipient,
                block_reward=block_reward,
                difficulty=difficulty,
                size=size
            )

            # Add the block to the ledger.
            blockchain.add_block(block)

    # Only update the ledger if there are new blocks.
    if new_blocks:
        ledger.update(new_blocks)
#the rogue update_ledger
#def update_ledger(blocks):
#    for block in blocks:
#        block_data = json.loads(block)
#        index = block_data['index']
#        previous_hash = block_data['previous_hash']
#        timestamp = block_data['timestamp']
#        data = block_data['data']
#        current_hash = block_data['current_hash']
#        status = block_data.get('status')
#        proposed_on = block_data.get('proposed_on')
#        transactions = block_data.get('transactions')
#        proposed_by = block_data.get('proposed_by')
#        fee_recipient = block_data.get('fee_recipient')
#        block_reward = block_data.get('block_reward')
#        difficulty = block_data.get('difficulty')
#        size = block_data.get('size')
#
#        block = Block(
#            index=index,
#            previous_hash=previous_hash,
#            timestamp=timestamp,
#            data=data,
#            current_hash=current_hash,
#            status=status,
#            proposed_on=proposed_on,
#            transactions=transactions,
#            proposed_by=proposed_by,
#            fee_recipient=fee_recipient,
#            block_reward=block_reward,
#            difficulty=difficulty,
#            size=size
#        )
#
#        blockchain.add_block(block)
#
#        # Update index, previous_hash, and other variables as needed
#        index, previous_hash = update_index_previous_hash()
#       update_previous_block_hash(index, current_hash)
#        #update_other_variables(block_data)


def update_index_previous_hash():
    last_block = blockchain.chain[-1]
    index = last_block.index
    previous_hash = last_block.current_hash
    return index, previous_hash


def update_previous_block_hash(index, current_hash):
    for i in range(1, len(blockchain.chain)):
        block = blockchain.chain[i]
        block.previous_hash = blockchain.chain[i - 1].current_hash
        block.current_hash = block.compute_hash()
#This is working but with repeated synchronizations, hence why it is commented
#@app.route('/sync_blocks', methods=['POST'])
#def sync_blocks():
#    while True:
#        # Check for blocks to copy from other nodes.
#        nodes = get_nodes_from_file()
#        for node in nodes:
#            response = requests.get(f"{node}/blocks")
#            if response.status_code == 200:
#                received_data = response.content.decode('utf-8')
#                blocks = extract_blocks(received_data)
#                update_ledger(blocks)
#                for i, block in enumerate(blocks):
#                    store_block(block, i)  # Store a copy of blocks
#        time.sleep(10)
def save_last_index_to_file(index):
    with open('last_index.txt', 'w') as file:
        file.write(str(index))

#def sync_blocks():
#    #last_index = get_last_index_from_file()  # Retrieve the last synced index
#
#    while True:
#        # Check for blocks to copy from other nodes.
#        nodes = get_nodes_from_file()
#        for node in nodes:
#            response = requests.get(f"{node}/blocks")
#            if response.status_code == 200:
#                received_data = response.content.decode('utf-8')
#                blocks = extract_blocks(received_data)
#
#                if len(blocks) > 0:
#                    # New blocks received, update the ledger
#                    update_ledger(blocks)
#                    last_index = blocks[-1].index  # Update the last synced index
#
#                    for i, block in enumerate(blocks):
#                        store_block(block, i)  # Store a copy of blocks
#
#        # Save the last synced index to a file
#        save_last_index_to_file(last_index)
#
#        time.sleep(10)
def get_last_index_from_file():
    try:
        with open('last_index.txt', 'r') as file:
            last_index = int(file.read())
    except FileNotFoundError:
        last_index = 0
    except ValueError:
        last_index = 0
    return last_index
#Working but with double index
@app.route('/sync_blocks', methods=['POST'])
def sync_blocks():
    blocks_dir = "{PWD}/blocks"  # Replace with the actual path to your blocks directory

    # Retrieve the last synced index.
    last_index = len(os.listdir(blocks_dir)) - 1 if os.path.exists(blocks_dir) else -1

    while True:
        # Check for blocks to copy from other nodes.
        nodes = get_nodes_from_file()
        for node in nodes:
            response = requests.get(f"{node}/blocks")
            if response.status_code == 200:
                received_data = response.content.decode('utf-8')
                blocks = extract_blocks(received_data)

                # Only sync blocks that are not in the local blocks directory.
                new_blocks = []
                for block in blocks:
                    if block.index not in range(last_index + 1):
                        new_blocks.append(block)

                if len(new_blocks) > 0:
                    # New blocks received, update the ledger
                    update_ledger(new_blocks)
                    last_index = blocks[-1].index  # Update the last synced index

                    # Store a copy of blocks
                    for i, block in enumerate(new_blocks):
                        store_block(block, i)
                else:
                    # No new blocks, do nothing
                    pass

        # Save the last synced index to a file
        save_last_index_to_file(last_index)

        time.sleep(10)

     
if __name__ == "__main__":
    # Start a new thread for sync_blocks()
    sync_thread = Thread(target=sync_blocks)
    sync_thread.start()
    # Run the Flask app
    nodes = get_nodes_from_file()
    app.run(debug='True', host='172.16.21.102', port=5000)

