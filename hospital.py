from pydoc import doc
import requests
import json
import sys
import psycopg2
from config import config
from flask import Flask


conn = None
try:
    # read connection parameters
    params = config()
    conn = psycopg2.connect(**params)
    cur = conn.cursor()
except (Exception, psycopg2.DatabaseError) as error:
    print(error)
    print('Error connecting to Database')
    sys.exit()


app = Flask(__name__)

# DONE
@app.route("/get_beds_status",methods=['GET'])
def get_beds_status() :
    args = requests.args.to_dict()
    hospital_id = args['hospital_id']
    jwt = args['jwt']

    # FETCH DATA FROM THE HOSPITAL DATABSE
    query = f'SELECT COUNT(*) FROM bedsdb where hospital_id = "{hospital_id}" AND available = {1}'
    cur.execute(query)
    result = cur.fetchall()
    available = result[0][0]
    query = f'SELECT COUNT(*) FROM bedsdb where hospital_id = "{hospital_id}" AND available = {0}'
    cur.execute(query)
    result = cur.fetchall()
    unavailable = result[0][0]
    data = {'occupied' : unavailable,'unoccupied' : available}
    return data



# DONE
@app.route("/change_status",methods=['POST'])
def change_hospital_bed_status() :
    args = requests.args.to_dict()
    hospital_id = args['hospital_id']
    jwt = args['jwt']
    nhid = args['nhid']
    req_type = args['type']
    # PERFORM AUTHENTICATION

    if req_type == 'book' : 
        # CHECK IF THERE IS AN AVAILABILITY OF BEDS
        query = f'SELECT COUNT(*) FROM bedsdb where hospital_id = "{hospital_id}" AND available = {1}'
        cur.execute(query)
        result = cur.fetchone()
        if result[0] > 0 :
            query = f'SELECT * FROM bedsdb where hospital_id = "{hospital_id}" AND available = {1}'
            cur.execute(query)
            record = cur.fetchone()
            bedid = result[0][0]
            query = f'UPDATE bedsdb SET availability = 0 WHERE bed_id = {bedid}'
            cur.execute(query)   
            return 'Bed Booked'
        else :
        # DB CODE TO UNBOOK BEDS
            return 'Beds Full'
    
    else :    
        query = f'SELECT * FROM bedsdb where hospital_id = "{hospital_id}" AND available = {0}'
        cur.execute(query)
        record = cur.fetchone()
        bedid = result[0][0]
        query = f'UPDATE bedsdb SET availability = 1 WHERE bed_id = {bedid}'
        cur.execute(query)   
        return 'Bed Unbooked'



# DONE
@app.route("/get_doctor_bills",methods=['GET'])
def get_doctor_bills() :
    args = requests.args.to_dict()
    hospital_id = args['hospital_id']
    doc_id = args['doc_id']
    jwt = args['jwt']
    ## PERFORM AUTHENTICATION

    # Fetch data from the Database
    query = f'SELECT fees FROM doctor_fees WHERE doc_id = "{doc_id}" AND hospital_id = "{hospital_id}" '
    cur.execute(query)
    result = cur.fetchall()
    fee = result[0][0]
    return fee


# DONE
@app.route("/get_lab_bills",methods=['GET'])
def get_lab_bills() :

    args = requests.args.to_dict()
    lab_id = args['lab_id']
    test_id = args['test_id']
    jwt = args['jwt']
    ## PERFORM AUTHENTICATION

    # Fetch data from the Database
    query = f'SELECT fees FROM lab_fees WHERE lab_id = "{lab_id}" AND test_id = "{test_id}" '
    cur.execute(query)
    result = cur.fetchall()
    fee = result[0][0]
    return fee





# DONE
@app.route("/doctor",methods=['GET'])
def get_doctors() :
    args = requests.args.to_dict()
    jwt = args['jwt']
    hospital_id = args['hospital_id']
    query = f'SELECT doc_id, doctor_name,specialisation from doctorsdb WHERE hospital_id = "{hospital_id}"'
    cur.execute(query)
    record = cur.fetchall()
    return record

# DONE
@app.route("/doctor",methods=['POST'])
def add_doctor() :
    args = requests.args.to_dict()
    jwt = args['jwt']
    hospital_id = args['hospital_id']
    doctor_name = args['doctor_name']
    years_exp = args['years_exp']
    speciality = args['speciality']
    query = f'INSERT INTO doctorsdb (doctor_name,specialisation,hospital_id,years_exp) VALUES ("{doctor_name}","{speciality}","{hospital_id}",{years_exp})'
    cur.execute(query)


# DONE
@app.route("/doctor",methods=['DELETE'])
def remove_doctor() :
    args = requests.args.to_dict()
    jwt = args['jwt']
    doctor_id = args['doctor_id']
    # PERFORM AUTHENTICATION

    # remove the doctor from the list
    query = f'DELETE FROM doctorsdb WHERE doc_id = "{doctor_id}"'
    cur.execute(query)




# THIS WILL CALL THE NHID SERVICE
@app.route("/public-info",methods=['GET'])
def get_public_info() :
    args = requests.args.to_dict()
    jwt = args['jwt']
    nhid = args['nhid']
    params = {'jwt' : jwt,'nhid' : nhid}
    # DB CODE TO RETRIEVE THE GENERAL DATA
    return






