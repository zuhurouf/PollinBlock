import pymongo, time, datetime
from blockchain import Blockchain

client = pymongo.MongoClient("mongodb://localhost:27017/")

db = client.get_database('Database')
bc = Blockchain()

vot = db.get_collection('Voter')
vol = db.get_collection('Volunteer')
candidate = db.get_collection('Candidates')
ec = db.get_collection('ElectionCommission')
voter_lst = [{'_id': 'XTU5671827', 'Name': 'Yukesh', 'DOB': '08-09-1960'},
             {'_id': 'XTU6781960', 'Name': 'Vasanth', 'DOB': '12-12-1967'},
             {'_id': 'XTU6781043', 'Name': 'Kumar', 'DOB': '05-04-1965'},
             {'_id': 'XTU6803421', 'Name': 'Eaghalaivan', 'DOB': '03-03-1999'},
             {'_id': 'XTU6809235', 'Name': 'Thamizharasan', 'DOB': '05-07-1999'},
             {'_id': 'XTU6781294', 'Name': 'Bhavin', 'DOB': '31-02-2000'}]

ec_lst = [{'_id': 'ECS6782340', 'Name': 'Zuhurouf'},
          {'_id': 'ECS7893452', 'Name': 'Arun'},
          {'_id': 'ECS6782341', 'Name': 'Dhinesh'},
          {'_id': 'ECS8904527', 'Name': 'Dhinesh kumar'}]

cand_lst = [{'_id': 'XTU6781960', 'Name': 'Vasant'}, {'_id': 'XTU6781043', 'Name': 'Kumar'}]
for i in candidate.find({}):
    print(i)


