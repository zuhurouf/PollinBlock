import random
import hashlib
from block import Block
from transaction import Transaction
from node import Node
from bitcoin import *

class Blockchain:
    #initialize the blockcain
    #chain: list of valid blocks
    #valid_transactions: list of valid transactions
    #nodes: a set of nodes(voters and validators)
    #validators: a set of validators
    def __init__(self):
        self.chain = []
        self.valid_transactions = []
        self.nodes = set()
        self.validators = set()
        #initial block
        self.create_genesis([])      

    #creates genesis block
    #param:: index: index of the block(value: 0)
    #param:: previous_hash: hash of previous block(value: '0'*64)
    #param:: transactions: list of transactions(value: []) 
    def create_genesis(self, transactions):
        index = len(self.chain)
        previous_hash = '0' * 64
        gb = Block(index= index, previous_hash= previous_hash, transactions= transactions)
        gb_dic = gb.to_dict()
        if(self.valid_block(gb_dic, {})):
            gb_dic['Header']['Hash'] = self.hash(gb_dic)
            gb_dic['Header']["Seal"] = self.block_sealing(gb_dic)
            self.chain.append(gb_dic)
            self.valid_transactions = []

    
    #returns the seal of the block
    def block_sealing(self, block_dic):
        transactions = block_dic['Body']['Transactions']
        sha = hashlib.sha256()
        if(len(transactions) == 0):
            msg = ' ' + str(random.randint(100, 1000) % 26) + str(block_dic['Header']['Hash'])
            sha.update(msg.encode('utf-8'))
            seal = sha.digest()
        else:
            i = 1
            concatTrans = str(transactions[0])
            hashedTrans = ' '
            while(i < len(transactions)):
                concatTrans += str(transactions[i])
                hashedTrans += str(hashlib.sha256(concatTrans.encode('utf-8')).digest())
                i += 1
            msg = str(hashedTrans) + str(random.randint(100, 1000) % 26) + str(block_dic['Header']['Hash'])
            sha.update(msg.encode('utf-8'))
            seal = sha.digest()
        return seal

    
    #returns hash value of the block
    #param:: block_dic: dictionary representation of block
    def hash(self, block_dic):
        index = block_dic['Header']['Index']
        nonce = block_dic['Header']['Nonce']
        previous_hash = block_dic['Header']['Previous hash']
        string = str(index) + str(nonce) + str(previous_hash)
        sha = hashlib.sha256()
        sha.update(string.encode('utf-8'))
        return sha.digest()


    #returns true if a block is valid
    #param:: block_dic: dictionary representation of block
    def valid_block(self, block_dic, previous_block):
        if( (block_dic['Header']['Index'] == 0) or (block_dic['Header']['Index'] == previous_block['Header']['Index'] + 1) ):
            if( (block_dic['Header']['Previous hash'] == '0'*64) or (block_dic['Header']['Previous hash'] == previous_block['Header']['Hash']) ):
                return True
            else:
                return False
        else:
            return False

    
    #creates new block
    def new_block(self, transactions):
        index = len(self.chain)
        previous_hash = self.chain[-1]['Header']['Hash']
        b = Block(index= index, previous_hash= previous_hash, transactions= transactions)
        block_dic = b.to_dict()
        if(self.valid_block(block_dic, self.chain[-1])):
            block_dic['Header']['Hash'] = self.hash(block_dic)
            block_dic['Header']['Seal'] = self.block_sealing(block_dic)
            self.chain.append(block_dic)
            return index
        else:
            return None


    #returns a list of past transactions
    def past_transactions(self, sender):
        if(len(self.valid_transactions) != 0):
            for transaction in self.valid_transactions:
                if(transaction['Sender'] == sender):
                    return False

        for block in self.chain:
            transactions = block['Body']['Transactions']
            for transaction in transactions:
                if(transaction['Sender'] == sender):
                    return False
        return True


    #returns true if signature is valid
    def valid_signature(self, transaction_dic):
        message = transaction_dic['Message']
        signature = transaction_dic['Signature']
        public_key = transaction_dic['Sender']
        return ecdsa_verify(message, signature, public_key)

    #returns true if transaction is valid
    #cond1:: returns true if signature is valid
    #cond2:: returns true if there is no past transactions
    def valid_transaction(self, transaction_dic):
        if(self.valid_signature(transaction_dic)):
            if(self.past_transactions(transaction_dic['Sender'])):
                return True
            else:
                return False
        else:
            return False

    #creates new transaction
    def new_transaction(self, sender, sender_private_key, reciever):
        t = Transaction(sender= sender, sender_private_key= sender_private_key, reciever= reciever)
        transaction_dic = t.to_dict()
        transaction_dic['Signature'] = t.sign_transaction()
        if(self.valid_transaction(transaction_dic)):
            transaction_dic['TxID'] = t.transaction_id()
            self.valid_transactions.append(transaction_dic)
            if(len(self.valid_transactions) == 2):
                rslt = self.new_block(self.valid_transactions)
                self.valid_transactions = []
                return rslt            
            else:
                return transaction_dic['TxID']
        else:
            return None

    
    #returns the number of transactions
    def transaction_count(self, reciever):
        count = 0
        for transaction in self.valid_transactions:
            if(transaction['Reciever'] == reciever):
                count += 1

        for block in self.chain:
            transactions = block['Body']['Transactions']
            for transaction in transactions:
                if(transaction['Reciever'] == reciever):
                    count += 1
        return count

            
    #adds a new node
    def new_node(self):
        node = Node(self.chain)
        self.nodes.add(node)
        return node

    #adds a new validator
    def new_validator(self):
        node = Node(self.chain)
        self.nodes.add(node)
        self.validators.add(node)
        return node

    '''def display(self, reciever):
        print('Nodes: ')
        for i in self.nodes:
            print(i)
        print('Validators: ')
        for i in self.validators:
            print(i)
        print('Transactions: ')
        for i in self.valid_transactions:
            print(i)
        print('Blocks: ')
        for i in self.chain:
            print(i)
        print('Count: {}'.format(self.transaction_count(reciever= reciever)))

if __name__ == '__main__':
    bc = Blockchain()
    val = bc.new_validator()
    n1 = bc.new_node()
    n2 = bc.new_node()
    bc.new_transaction(val.public_key, val.private_key, n1.public_key)
    bc.new_transaction(n1.public_key, n1.private_key, n1.public_key)
    bc.display(n1.public_key)'''