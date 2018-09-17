import hashlib
import json

from time import time

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