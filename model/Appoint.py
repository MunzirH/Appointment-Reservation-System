import sys
sys.path.append("../db/*")
from db.ConnectionManager import ConnectionManager
import pymssql

class Appointment:
    def __init__(self, patient=None, availability=None, vaccine=None):
        self.appointment_id = None
        if availability is not None:
            self.caregiver_id = availability.get_caregiver_id()
            self.availability_id = availability.get_availability_id()
        else:
            self.caregiver_id = None
            self.availability_id = None

        if patient is not None:
            self.patient_id = patient.get_patient_id()
        else:
            self.patient_id = None
        if vaccine is not None:
            self.vaccine_id = vaccine.get_vaccine_id()
        else:
            self.vaccine_id = None

    def get(self, appointment_id):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

        get_appointment_details = "select AppointmentID, CaregiverID , PatientID, AvailabilityID, VaccineID" \
                                  " from Appointments where AppointmentID = %s"
        try:
            cursor.execute(get_appointment_details, appointment_id)
            for row in cursor:
                self.appointment_id = row['AppointmentID']
                self.caregiver_id = row["CaregiverID"]
                self.patient_id = row['PatientID']
                self.availability_id = row['AvailabilityID']
                self.vaccine_id = row['VaccineID']
                return self
        except pymssql.Error:
            print("Error occurred when getting Caregivers")
            cm.close_connection()
        cm.close_connection()
        return None

    def save_to_db(self, cursor):

        add_appointment = "INSERT INTO Appointments VALUES (%s, %s, %s, %s)"
        try:
            cursor.execute(add_appointment,
                           (self.caregiver_id, self.patient_id, self.availability_id, self.vaccine_id))
        except pymssql.Error as db_err:
            print("Error occurred when inserting appointment")
            sqlrc = str(db_err.args[0])
            print("Exception code: " + str(sqlrc))
            raise pymssql.Error

    def delete_from_db(self, cursor):

        delete_appointment = "DELETE from Appointments where AppointmentID = %s"
        try:
            cursor.execute(delete_appointment, self.appointment_id)
        except pymssql.Error as db_err:
            print("Error occurred when inserting appointment")
            print("Exception code: " + str(db_err))
            raise pymssql.Error
