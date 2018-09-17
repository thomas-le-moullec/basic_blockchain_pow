import hashlib
import json
import requests

from time import time
from urllib.parse import urlparse

class Blockchain(object):

    def __init__(self):
        self.chain = []
        self.current_tx = []
        self.nodes = set()

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

        # Add the new block to the blockchain
        self.chain.append(newBlock)
        return newBlock

    def new_payload(self, sender, recipient, message):

        # New message posted. Currently only a message from an address to another one.
        # For a forum we need to add the name of the channel
        self.current_tx.append({
            'sender' : sender,
            'recipient' : recipient,
            'message' : message
        })

        return self.get_last_block['index'] + 1

    @staticmethod
    def hash(block):
        # Hash with SHA512
        block_json = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha512(block_json).hexdigest()

    @property
    def get_last_block(self):
        # Return the last block of the blockchain
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        # Proof of work.
        # For forum without any remuneration on mining proof of work(PoW) can be replace by another verification method
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        # To validate the proof of work:
        # We check if the hash (SHA512) of last_proof and current one contains 5 leading zeroes.
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha512(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def register_node(self, address):
        # Add a new node in the decentralized network / list of nodes
        url = urlparse(address)
        if url.netloc == "":
            return False
        self.nodes.add(url.netloc)
        return True

    def consensus(self):
        """
        Consensus function.
        If 2 miners solve a block at almost the same time, then we will have 2 different blockchains in the network.
        We need to wait for the next block to resolve the conflict, we just take the longest Blockchain.
        In short, if there is a conflict on the blockchain, then the the longest chain wins.
        :return:
        """

        Network = self.nodes
        longest_chain = None
        self_chain_length = len(self.chain)

        for fullNode in Network:
            # Fetch the chain of the neighbour nodes in the decentralized Network
            response = requests.get(f'http://{fullNode}/chain')

            if response.status_code == 200:
                size = response.json()['size']
                chain = response.json()['chain']

                if size > self_chain_length and self.check_blockchain(chain):
                    self_chain_length = size
                    longest_chain = chain

        # If longest_chain is not NULL, our chain is not up to date anymore
        if longest_chain:
            self.chain = longest_chain
            return True

        return False

    def check_blockchain(self, chain):
        # This function checks the entire blockchain validity.
        # We check the previous block hash and the proof (With our PoW algorithm)
        previous_block = chain[0]
        index = 1

        while index <  len(chain):
            block = chain[index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            if not self.valid_proof(previous_block['proof'], block['proof']):
                return False

            previous_block = block
            index += 1

        return True

