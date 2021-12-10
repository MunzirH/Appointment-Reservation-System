import sys
sys.path.append("../db/*")
from db.ConnectionManager import ConnectionManager
import pymssql


class Vaccine:
    def __init__(self, vaccine_name=None, available_doses=0, vaccine_id=None):
        self.vaccine_name = vaccine_name
        self.available_doses = available_doses
        self.vaccine_id = vaccine_id

    # getters
    def get(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

        get_vaccine = "SELECT VaccineID, Doses FROM Vaccines WHERE VaccineName = %s"
        try:
            cursor.execute(get_vaccine, self.vaccine_name)
            for row in cursor:
                self.vaccine_id = row['VaccineID']
                self.available_doses = row['Doses']
                return self
        except pymssql.Error:
            print("Error occurred when getting Vaccine")
            cm.close_connection()
        cm.close_connection()
        return None

    def get_by_id(self, vaccine_id):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

        get_vaccine = "SELECT VaccineName, Doses FROM Vaccines WHERE VaccineID = %s"
        try:
            cursor.execute(get_vaccine, vaccine_id)
            for row in cursor:
                self.vaccine_id = vaccine_id
                self.vaccine_name = row['VaccineName']
                self.available_doses = row['Doses']
                return self
        except pymssql.Error:
            print("Error occurred when getting Vaccine")
            cm.close_connection()
        cm.close_connection()
        return None

    def get_vaccine_name(self):
        return self.vaccine_name

    def get_vaccine_id(self):
        return self.vaccine_id

    def get_available_doses(self):
        return self.available_doses

    def save_to_db(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        add_doses = "INSERT INTO VACCINES VALUES (%s, %d)"
        try:
            cursor.execute(add_doses, (self.vaccine_name, self.available_doses))
            # you must call commit() to persist your data if you don't set autocommit to True
            conn.commit()
        except pymssql.Error:
            print("Error occurred when insert Vaccines")
            cm.close_connection()
        cm.close_connection()

    # Increment the available doses
    def increase_available_doses(self, num, cursor):
        if num <= 0:
            raise ValueError("Argument cannot be negative!")
        self.available_doses += num

        update_vaccine_availability = "UPDATE vaccines SET Doses = %d WHERE VaccineID = %s"
        try:
            cursor.execute(update_vaccine_availability, (self.available_doses, self.vaccine_id))
        except pymssql.Error:
            print("Error occurred when updating vaccine availability")
            raise pymssql.Error

    # Decrement the available doses
    def decrease_available_doses(self, num, cursor):
        if self.available_doses - num < 0:
            raise ValueError("Not enough available doses!")
        self.available_doses -= num
        update_vaccine_availability = "UPDATE vaccines SET Doses = %d WHERE VaccineID = %s"
        try:
            cursor.execute(update_vaccine_availability, (self.available_doses, self.vaccine_id))
        except pymssql.Error:
            print("Error occurred when updating vaccine availability")
            raise pymssql.Error

    def __str__(self):
        return f"(Vaccine Name: {self.vaccine_name}, Available Doses: {self.available_doses})"

