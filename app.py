from flask import *
from pymongo import MongoClient
from blockchain import Blockchain
import time


connected_nodes = []
transactions = []
blocks = []

#flask object
app = Flask(__name__)

#configure database
client = MongoClient("mongodb://localhost:27017/")
db = client.get_database('Database')
voter_col = db.get_collection('Voter')
volunteer_col = db.get_collection('Volunteer')
cand_col = db.get_collection('Candidates')
elec_comm = db.get_collection('ElectionCommission')

#blockchain object
bc = Blockchain()

#login page
#returnd login page
@app.route('/', methods=['POST', 'GET'])
def login():
    return render_template('login.html')

#voter
#verifies voter's identity and returns voter home page
@app.route('/voter_login', methods=['POST'])
def voter_login():
    voter_id = request.form['voter_id']
    dob = request.form['DOB']
    voter_doc = voter_col.find_one({'_id': voter_id})
    if(voter_doc is not None):
        if(voter_doc['DOB'] == dob):
            if('Public_key' in voter_doc and 'Private_key' in voter_doc):
                session['_id'] = voter_id
                session['public key'] = voter_doc['Public_key']
                session['private key'] = voter_doc['Private_key']

                key = {'Public_key': session['public key'], 'Private_key': session['private key']}
                candidate_lst = cand_col.find({}, {'_id': 0, 'Name': 1, 'Public_key': 1})
                return render_template('VoterHome.html', wallet= key, candidates= candidate_lst)
            else:
                node = bc.new_node()
                session['_id'] = voter_id
                session['public key'] = node.public_key
                session['private key'] = node.private_key
                voter_col.update_one({'_id': voter_id}, {'$set': {'Private_key': session['private key'], 'Public_key': session['public key']}})

                #update candidate record if the voter is a candidate
                cand_col.update_one({'_id': voter_id}, {'$set': {'Public_key': session['public key']}})
                
                key = {'Public_key': session['public key'], 'Private_key': session['private key']}
                candidate_lst = cand_col.find({}, {'_id': 0, 'Name': 1, 'Public_key': 1})
                return render_template('VoterHome.html', wallet= key, candidates= candidate_lst)
        else:
            flash('Invalid DOB')
            return render_template('login.html')
    else:
        flash('Invalid ID')
        return render_template('login.html')


#voter's vote
@app.route('/new_transaction_voter', methods=['POST'])
def new_transaction_voter():
    voter_pub_key = session['public key']
    voter_pri_key = session['private key']
    candidate_name = request.form['cand_name']
    candidate_pub_key = request.form['pub_key']
    success = bc.new_transaction(voter_pub_key, voter_pri_key, candidate_pub_key)

    key = {'Public_key': session['public key'], 'Private_key': session['private key']}
    cand_lst = cand_col.find({}, {'_id': 0, 'Name': 1, 'Public_key': 1})
    
    if(success is not None):
        flash('Voting successful')
        return render_template('VoterHome.html', wallet= key, candidates= cand_lst)
    else:
        flash('Voting unsuccessful')
        return render_template('VoterHome.html', wallet= key, candidates= cand_lst)


#volunteer
#returns volunteer signup page
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    return render_template('signup.html')


#creates new volunteer account
@app.route('/signedup', methods=['POST'])
def signedup():
    volunteer_id = request.form['volunteer_id']
    name = request.form['name']
    password = request.form['cpwd']
    elec_com_rec = elec_comm.find_one({'_id': volunteer_id})
    if(elec_com_rec is not None):
        node = bc.new_validator()
        volunteer_col.insert_one({'_id': volunteer_id, 'Name': name, 'Password': password, 'Private_key': node.private_key, 'Public_key': node.public_key})
        flash('Account created successfully')
        return render_template('login.html')
    else:
        flash('Account creation unsuccessful')
        return render_template('login.html')

#logs into volunteer home page
@app.route('/volunteer_login', methods=['POST'])
def volunteer_login():
    volunteer_id = request.form['volunteer_id']
    password = request.form['pwd']
    volunteer_doc = volunteer_col.find_one({'_id': volunteer_id})
    if(volunteer_doc is not None):
        if(password == volunteer_doc['Password']):
            session['_id'] = volunteer_id
            session['public key'] = volunteer_doc['Public_key']
            session['private key'] = volunteer_doc['Private_key']

            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            port = 80
            ip_address = ip + ':' + str(port)
            connected_nodes.append(ip_address)

            key = {'Public_key': session['public key'], 'Private_key': session['private key']}
            cand_lst = cand_col.find({}, {'_id': 0, 'Name': 1, 'Public_key': 1})
            
            poll_result = []
            for candidate in cand_col.find({}):
                cand_result = {'Name': candidate['Name'], 'Count': 0}
                poll_result.append(cand_result)
            
            return render_template('VolunteerHome.html', wallet= key, candidates= cand_lst, result = poll_result)
        else:
            flash('Invalid password')
            return render_template('login.html')
    else:
        flash('Invalid ID')
        return render_template('login.html')

#volunteer's new transaction
@app.route('/new_transaction_volunteer', methods=['POST'])
def new_transaction_volunteer():
    voter_pub_key = session['public key']
    voter_pri_key = session['private key']
    candidate_name = request.form['cand_name']
    candidate_pub_key = request.form['pub_key']

    key = {'Public_key': session['public key'], 'Private_key': session['private key']}
    cand_lst = cand_col.find({}, {'_id': 0, 'Name': 1, 'Public_key': 1})
    poll_result = []
    for candidate in cand_col.find({}):
        cand_result = {'Name': candidate['Name'], 'Count': 0}
        poll_result.append(cand_result)

    success = bc.new_transaction(voter_pub_key, voter_pri_key, candidate_pub_key)
    if(success is not None):
        flash('Voting successful')
        return render_template('VolunteerHome.html', wallet= key, candidates= cand_lst, result= poll_result)
    else:
        flash('Voting unsuccessful')
        return render_template('VolunteerHome.html', wallet= key, candidates= cand_lst, result= poll_result)




#returns the final result
@app.route('/result', methods=['POST', 'GET'])
def result():
    poll_result = []
    for candidate in cand_col.find({}):
        cand_result = {'Name': candidate['Name'], 'Count': bc.transaction_count(candidate['Public_key'])}
        poll_result.append(cand_result)
    
    key = {'Public_key': session['public key'], 'Private_key': session['private key']}
    cand_lst = cand_col.find({}, {'_id':0, 'Name': 1, 'Public_key': 1})
    return render_template('VolunteerHome.html', wallet= key, candidates= cand_lst, result= poll_result)


#logout route function
@app.route('/logout', methods=['POST', 'GET'])
def logout():
    session.pop('_id', None)
    session.pop('public key', None)
    session.pop('private key', None)
    return render_template('login.html')

if __name__ == '__main__':
    app.secret_key = 'secret key'
    app.config['SESSION TYPE'] = 'mongodb'
    app.run(debug= True)