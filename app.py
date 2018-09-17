from uuid import uuid4
from flask import Flask, jsonify, request
from blockchain import Blockchain
import sys

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

@app.route('/nodes/subscribe', methods=['POST'])
def subscribe_nodes():
    data = request.get_json()

    nodes = data.get('nodes')
    if nodes is None:
        return "Error: Incorrect nodes list", 400
    print('list of nodes to subscribe endpoints')
    print(nodes, '\n')
    for node in nodes:
        blockchain.register_node(node)

    response = {
        'response': 'New nodes have been added',
        'list_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201

@app.route('/nodes/getAll', methods=['GET'])
def getAllNodes():
    response = {
        'network': 'List of nodes',
        'list_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201

@app.route('/nodes/consensus', methods=['GET'])
def consensus():
    updated = blockchain.consensus()

    if updated:
        response = {
            'response': 'Current chain updated',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain' : blockchain.chain,
        'size' : len(blockchain.chain),
    }
    return jsonify(response), 200

if __name__ == '__main__':
    if len(sys.argv) > 1:
        param = sys.argv[1]
    else:
        param = 5000
    app.run(host='0.0.0.0', port=param)