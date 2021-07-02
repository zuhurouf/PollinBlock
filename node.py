import base64
from bitcoin import *
from binascii import hexlify

class Node:
    #initialize a new node
    #private_key: random private key
    #public_key: public key derived from private key
    #transaction_history: list of past transactions
    def __init__(self, chain):
        self.chain = chain
        self.private_key, self.public_key = self.key_pair_generator()
        self.past_transactions = self.transaction_history()


        
    #returns private and public key
    def key_pair_generator(self):
        private_key = random_key()
        public_key = privtopub(private_key)
        return private_key, public_key
    
    #returns past transactions if any
    def transaction_history(self):
        transactions = []
        for i in range(0, len(self.chain)):
            block = self.chain[i]
            block_trans = block['Body']['Transactions']
            for j in range(0, len(block_trans)):
                if(block_trans[j]['Sender'] == self.public_key):
                    transactions.append(block_trans[j])
                elif(block_trans[j]['Reciever'] == self.public_key):
                    transactions.append(block_trans[j])
        return len(transactions)    