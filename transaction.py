import datetime, hashlib, base64, string, random, os
from bitcoin import *
from binascii import hexlify, unhexlify
from Crypto.Cipher import AES

class Transaction:
    #initialize a new transaction
    #param:: sender: address of the sender(voter)
    #param:: reciever: address of the reciever(candidate)
    #param:: amount: coin send to the reciever(1coin = 1vote)
    def __init__(self, sender, sender_private_key, reciever):
        self.sender = sender
        self.sender_private_key = sender_private_key
        self.reciever = reciever
        self.message = 'Voted'
        self.timestamp = datetime.datetime.now()

    #returns the transaction as a dictionary
    def to_dict(self):
        dic = {'Sender': self.sender, 'Reciever': self.reciever, 'Message': self.message}
        print('Tx: {}'.format(dic))
        return dic

    #signs and returns the signature
    def sign_transaction(self):
        message = self.message
        signature = ecdsa_sign(message, self.sender_private_key)
        return signature

    #generates and returns transaction id
    def transaction_id(self):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k= 50))