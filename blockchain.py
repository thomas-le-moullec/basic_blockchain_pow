import hashlib
import json

from textwrap import  dedent
from time import time
from uuid import uuid4
from flask import Flask, jsonify, request

class Blockchain(object):

    def __init__(self):
        self.chain = []
        self.current_tx = []

        # Genesis block generation (1st block)
        self.new_block(previous_hash=1, proof=100)

    def new_block(self, proof, previous_hash=None):
        newBlock = {
            'index' : len(self.chain) + 1,
            'timestamp' : time(),
            'payloads' : self.current_tx,
            'proof' : proof,
            'previous_hash' : previous_hash or self.hash(self.chain[-1])
        }

        # Reset list of transactions
        self.current_tx = []

        self.chain.append(newBlock)
        return newBlock

    def new_payload(self, sender, recipient, message):

        self.current_tx.append({
            'sender' : sender,
            'recipient' : recipient,
            'message' : message
        })

        return self.get_last_block['index'] + 1

    @staticmethod
    def hash(block):
        block_json = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha512(block_json).hexdigest()

    @property
    def get_last_block(self):
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha512(guess).hexdigest()
        return guess_hash[:4] == "0000"

app = Flask(__name__)

node_identifier = str(uuid4()).replace('-', '')

blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.get_last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # New payload to normally pay the miner
    blockchain.new_payload(
        sender="0",
        recipient=node_identifier,
        message="Thanks for mining"
    )

    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'messages': block['payloads'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200

@app.route('/messages/new', methods=['POST'])
def new_message():
    data = request.get_json()
    required = ['sender', 'recipient', 'message']
    if not all(k in data for k in required):
        return 'Missing Values', 400

    # Create a new message
    index = blockchain.new_payload(data['sender'], data['recipient'], data['message'])

    response = {'response' : f'Tx will be added to Block {index}'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain' : blockchain.chain,
        'size' : len(blockchain.chain),
    }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)