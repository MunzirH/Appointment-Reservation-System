import sys
sys.path.append("../db/*")
from db.ConnectionManager import ConnectionManager
import pymssql

class Availability:

    def __init__(self, availability_id=None, caregiver_id=None, is_reserved=None, time=None):
        self.availability_id = availability_id
        self.caregiver_id = caregiver_id
        self.is_reserved = is_reserved
        self.time = time

    def get(self, date):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

        get_availability = "SELECT AvailabilityID, CaregiverID, IsReserved, Time" \
                           " FROM Availabilities where IsReserved = 0 and time = %s"
        try:
            cursor.execute(get_availability, date)
            random_result = cursor.fetchone()
            if random_result is None:
                return None
            self.availability_id = random_result['AvailabilityID']
            self.caregiver_id = random_result['CaregiverID']
            self.is_reserved = random_result['IsReserved']
            self.time = random_result['Time']
            return self
        except pymssql.Error:
            print("Error occurred when getting availability data")
            cm.close_connection()
        cm.close_connection()
        return None

    def get_by_id(self, availability_id):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

        get_availability = "SELECT AvailabilityID, CaregiverID, IsReserved, Time" \
                           " FROM Availabilities where AvailabilityID = %s"
        try:
            cursor.execute(get_availability, availability_id)
            result = cursor.fetchone()
            self.availability_id = result['AvailabilityID']
            self.caregiver_id = result['CaregiverID']
            self.is_reserved = result['IsReserved']
            self.time = result['Time']
            return self
        except pymssql.Error:
            print("Error occurred when getting availability data")
            cm.close_connection()
        cm.close_connection()
        return None

    def change_to_reserved(self, cursor):
        toggle_availability = "UPDATE Availabilities set IsReserved = 1 WHERE AvailabilityID = %s"
        try:
            cursor.execute(toggle_availability, self.availability_id)
        except pymssql.Error:
            print("Error when changing reserve state")
            raise pymssql.Error

    def change_to_available(self, cursor):
        toggle_availability = "UPDATE Availabilities set IsReserved = 0 WHERE AvailabilityID = %s"
        try:
            cursor.execute(toggle_availability, self.availability_id)
        except pymssql.Error:
            print("Error when changing reserve state")
            raise pymssql.Error

    def get_availability_id(self):
        return self.availability_id

    def get_caregiver_id(self):
        return self.caregiver_id
