import datetime
import random

class Block:
    #initialize the block
    def __init__(self, index, previous_hash, transactions):
        self.header = { 'Index': index, 
                        'Timestamp': datetime.datetime.now(), 
                        'Nonce': self.nonceGenerator(ind= index), 
                        'Previous hash': previous_hash }
        self.body = {'Transactions': transactions}

    #returns the block as a dictionary
    def to_dict(self):
        dic = { 'Header': self.header, 'Body': self.body }
        return dic

    #nonce value generator
    def nonceGenerator(self, ind):
        start = int(10 ** (ind - 1))
        end = int((10 ** ind) - 1)
        return(random.randint(start, end) + random.randint(100, 10000))