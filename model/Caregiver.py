import sys
sys.path.append("../util/*")
sys.path.append("../db/*")
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql


class Caregiver:
    def __init__(self, username, password=None, salt=None, hash=None, caregiver_id=None):
        self.caregiver_id = caregiver_id
        self.username = username
        self.password = password
        self.salt = salt
        self.hash = hash

    # getters
    def get(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

        get_caregiver_details = "SELECT CaregiverID, Salt, Hash FROM Caregivers WHERE Username = %s"
        try:
            cursor.execute(get_caregiver_details, self.username)
            for row in cursor:
                curr_caregiver_id = row['CaregiverID']
                curr_salt = row['Salt']
                curr_hash = row['Hash']
                calculated_hash = Util.generate_hash(self.password, curr_salt)
                if not curr_hash == calculated_hash:
                    cm.close_connection()
                    return None
                else:
                    self.salt = curr_salt
                    self.hash = calculated_hash
                    self.caregiver_id = curr_caregiver_id
                    return self
        except pymssql.Error:
            print("Error occurred when getting Caregivers")
            cm.close_connection()

        cm.close_connection()
        return None

    def get_username(self):
        return self.username

    def get_salt(self):
        return self.salt

    def get_hash(self):
        return self.hash

    def get_caregiver_id(self):
        return self.caregiver_id

    def save_to_db(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        add_caregivers = "INSERT INTO Caregivers VALUES (%s, %s, %s)"
        try:
            cursor.execute(add_caregivers, (self.username, self.salt, self.hash))
            # you must call commit() to persist your data if you don't set autocommit to True
            conn.commit()
        except pymssql.Error as db_err:
            print("Error occurred when inserting Caregivers")
            sqlrc = str(db_err.args[0])
            print("Exception code: " + str(sqlrc))
            cm.close_connection()
        cm.close_connection()

    # Insert availability with parameter date d
    def upload_availability(self, d):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        add_availability = "INSERT INTO Availabilities VALUES (%s ,0, %s)"
        try:
            cursor.execute(add_availability, (self.caregiver_id, d))
            # you must call commit() to persist your data if you don't set autocommit to True
            conn.commit()
        except pymssql.Error:
            print("Error occurred when updating caregiver availability")
            cm.close_connection()
        cm.close_connection()

