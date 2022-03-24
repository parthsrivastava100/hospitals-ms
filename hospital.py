from pydoc import doc
import requests
import requests
import json
import os
from dotenv import load_dotenv
import sys
import jwt
import psycopg2
from config import config
from flask import Flask,request
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.primitives.asymmetric import  rsa


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

key = None
load_dotenv()

def get_public_key() :
    global key
    r = requests.get(os.environ.get("PUBLIC_KEY_URL"))
    data = r.content
    key = load_pem_public_key(data)

get_public_key()

if key is None :
    print('Unable to retireve public key')
    sys.exit()

# DONE
@app.route("/get_beds_status",methods=['GET'])
def get_beds_status() :
    args = request.get_json()
    hospital_id = args['hospital_id']
    encoded = requests.cookies.get('PatientAuth')
    decoded = jwt.decode(encoded, key, algorithms=["RS256"])
    # patient_id = decoded['nhid']
    # FETCH DATA FROM THE HOSPITAL DATABSE
    query = f'SELECT COUNT(*) FROM bedsdb where hospital_id = %s AND available = %d'
    cur.execute(query,(hospital_id,1))
    result = cur.fetchall()
    available = result[0][0]
    query = f'SELECT COUNT(*) FROM bedsdb where hospital_id = %s AND available = %d'
    cur.execute(query,(hospital_id,0))
    result = cur.fetchall()
    unavailable = result[0][0]
    data = {'occupied' : unavailable,'unoccupied' : available}
    return data



# DONE
@app.route("/change_status",methods=['POST'])
def change_hospital_bed_status() :
    args = request.get_json()
    hospital_id = args['hospital_id']
    req_type = args['type']
    # PERFORM AUTHENTICATION
    encoded = requests.cookies.get('PatientAuth')
    decoded = jwt.decode(encoded, key, algorithms=["RS256"])
    # patient_id = decoded['nhid']
    if req_type == 'book' : 
        # CHECK IF THERE IS AN AVAILABILITY OF BEDS
        query = f'SELECT COUNT(*) FROM bedsdb where hospital_id = %s AND available = %d'
        cur.execute(query,(hospital_id,1))
        result = cur.fetchone()
        if result[0] > 0 :
            query = f'SELECT * FROM bedsdb where hospital_id = %s AND available = %d'
            cur.execute(query,(hospital_id,1))
            record = cur.fetchone()
            bedid = result[0][0]
            query = f'UPDATE bedsdb SET availability = 0 WHERE bed_id = %s'
            cur.execute(query,(bedid))   
            return 'Bed Booked'
        else :
        # DB CODE TO UNBOOK BEDS
            return 'Beds Full'
    
    else :    
        query = f'SELECT * FROM bedsdb where hospital_id = %s AND available = %d'
        cur.execute(query,(hospital_id,0))
        record = cur.fetchone()
        bedid = result[0][0]
        query = f'UPDATE bedsdb SET availability = 1 WHERE bed_id = %s'
        cur.execute(query,(bedid))   
        return 'Bed Unbooked'



# DONE
@app.route("/get_doctor_bills",methods=['GET'])
def get_doctor_bills() :
    args = request.get_json()
    hospital_id = args['hospital_id']
    doc_id = args['doc_id']
    encoded = requests.cookies.get('PatientAuth')
    decoded = jwt.decode(encoded, key, algorithms=["RS256"])
    query = f'SELECT fees FROM doctor_fees WHERE doc_id = %s AND hospital_id = %s '
    cur.execute(query,(doc_id,hospital_id))
    result = cur.fetchall()
    fee = result[0][0]
    return fee


# DONE
@app.route("/get_lab_bills",methods=['GET'])
def get_lab_bills() :

    args = request.get_json()
    lab_id = args['lab_id']
    test_id = args['test_id']
    encoded = requests.cookies.get('PatientAuth')
    decoded = jwt.decode(encoded, key, algorithms=["RS256"])
    # jwt = decoded['nhid']
    # Fetch data from the Database
    query = f'SELECT fees FROM lab_fees WHERE lab_id = %s AND test_id = %s '
    cur.execute(query,(lab_id,test_id))
    result = cur.fetchall()
    fee = result[0][0]
    return fee





# DONE
@app.route("/doctor",methods=['GET'])
def get_doctors() :
    args = request.get_json()
    encoded = requests.cookies.get('PatientAuth')
    decoded = jwt.decode(encoded, key, algorithms=["RS256"])
    # jwt = decoded['nhid']
    hospital_id = args['hospital_id']
    query = f'SELECT doc_id, doctor_name,specialisation from doctorsdb WHERE hospital_id = %s'
    cur.execute(query,(hospital_id))
    record = cur.fetchall()
    return record

# DONE
@app.route("/doctor",methods=['POST'])
def add_doctor() :
    args = request.get_json()
    encoded = requests.cookies.get('PatientAuth')
    decoded = jwt.decode(encoded, key, algorithms=["RS256"])
    # jwt = decoded['nhid']
    hospital_id = args['hospital_id']
    doctor_name = args['doctor_name']
    years_exp = args['years_exp']
    speciality = args['speciality']
    query = f'INSERT INTO doctorsdb (doctor_name,specialisation,hospital_id,years_exp) VALUES (%s, %s,%s, %d)'
    cur.execute(query,(doctor_name,speciality,hospital_id,years_exp))


# DONE
@app.route("/doctor",methods=['DELETE'])
def remove_doctor() :
    args = request.get_json()
    encoded = requests.cookies.get('PatientAuth')
    decoded = jwt.decode(encoded, key, algorithms=["RS256"])
    # jwt = decoded['nhid']
    doctor_id = args['doctor_id']
    # remove the doctor from the list
    query = f'DELETE FROM doctorsdb WHERE doc_id = %s'
    cur.execute(query,(doctor_id))




# THIS WILL CALL THE NHID SERVICE
@app.route("/public-info",methods=['GET'])
def get_public_info() :
    args = request.get_json()
    encoded = requests.cookies.get('PatientAuth')
    decoded = jwt.decode(encoded, key, algorithms=["RS256"])
    nhid = decoded['NHID']
    params = {'jwt' : jwt,'nhid' : nhid}
    # DB CODE TO RETRIEVE THE GENERAL DATA
    return

if __name__ == '__main__':
    app.run()




