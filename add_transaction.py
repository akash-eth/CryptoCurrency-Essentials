#----------------------------Building up an Crypto-Currency-------------------------------
"""WE ARE GOING TO DEVELOP AN DECENTRALISED CRYPTO-CURRENCY"""
#-----------------------------Importing Libraries------------------------------------------

import hashlib
import datetime
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse


#----------------------------------Generating a blockchain---------------------------------

class Blockchain:
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.create_block(proof=1, previous_hash='0')
        self.nodes = set() # adding nodes for obtain http address of the users.
    
    def create_block(self, proof, previous_hash): # generating a new block!!
        block = {'index': len(self.chain) +1,
                  'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash,
                 'transactions': self.transactions
                 }
        self.transactions = []
        self.chain.append(block)
        return block
    
    def get_previous_block(self): # getting the previous block!!
        return self.chain[-1]
    
    def proof_of_work(self, previous_proof): # generating a P-O-W!!
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof +=1
        return new_proof
    
    def hash(self, block): # separately calling the encrypted hash function!!
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self, chain): # validating the chain!!
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index +=1
        return True
    
    def add_transaction(self, sender, receiver, amount): # adding transactions to the chain!!
        self.transactions.append({'sender': sender,
                                  'receiver': receiver,
                                  'amount': amount
                                  })
        previous_block = self.get_previous_block()
        return previous_block['index'] +1
    
#----------Adding Consensus Protocol to the blockchain network----------------
    def add_node(self, address): # this will allow different participants to participate in our blockchain network!!
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
        
    def replace_chain(self): # the will replace the Current-chain with longest chain in the blockchain network!!
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain') # node = 127.0.0.1:5000, to access the get_chain function below, we generate requests.get
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            longest_chain = self.chain
            return True
        return False
            
        
        



#-------------------------------Creating a webApp------------------------------------------

app = Flask(__name__)

#------------------Adding an reward node for the miner at port 5000---------------

node_address = str(uuid4()).replace('-','') # uuid4 generates an random UUID(unique identity)!!
    
#-------------------Creating an objeect of the Above Blockchan Class----------------------

blockchain = Blockchain()

#-----------------------------Mining a new Block------------------------------------------

@app.route('/mine_block', methods = ['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transaction(sender = node_address, receiver = 'Miner', amount = 10 ) # rewarding the miner
    block = blockchain.create_block(proof, previous_hash)
    
    response = {'message':'Congratulations!!!!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash':  block['previous_hash'],
                'transactions': block['transactions']
                }
    return jsonify(response), 200

#------------------------------Checking the validity of th Chain--------------------------

@app.route('/is_valid', methods = ['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'chain valid :)'}
    else:
        response = {'message': 'not valid :('}
    
    return  jsonify(response), 200

#------------------------------------Getting the whole Chain------------------------------

@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)
                }
    return jsonify(response), 200

#------------------------Adding transaction to the blockchain--------------------

@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all (key in json for key in transaction_keys):
        return 'Something is missing!! Please check all the fields', 400
    index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'])
    response = {'message': 'Your transaction has been uploded to the blockchain at {index}'}
    return jsonify(response), 201

#--------------------------------Running the webApp---------------------------------------

app.run(host = '0.0.0.0', port = 5000)
    
