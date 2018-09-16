import hashlib
import json
from time import time
from hashlib import sha512

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

    def new_payload(self, sender, recipient, amount):

        self.current_tx.append({
            'sender' : sender,
            recipient : recipient,
            'amount' : amount
        })

        return self.get_last_block['index'] + 1

    @staticmethod
    def hash(block):
        block_json = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha512(block_json).hexdigest()

    @property
    def get_last_block(self):
        return self.chain[-1]
