from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from model.Availability import Availability
from model.Appoint import Appointment
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime

'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
current_patient = None

current_caregiver = None


def create_patient(tokens):
    # create_patient <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Tokens length is not correct, Please try again!")
        add_input_delay()
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_patient(username):
        print("Username taken, try again!")
        add_input_delay()
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    try:
        patient = Patient(username, salt=salt, hash=hash)
        # save to caregiver information to our database
        try:
            patient.save_to_db()
        except:
            print("Create failed, Cannot save")
            add_input_delay()
            return
        print(" *** Account created successfully *** ")
        add_input_delay()
    except pymssql.Error:
        print("Create failed")
        add_input_delay()
        return


def username_exists_patient(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Patients WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error:
        print("Error occurred when checking username")
        cm.close_connection()
    cm.close_connection()
    return False


def create_caregiver(tokens):
    # create_caregiver <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Token length is incorrect, Please try again!")
        add_input_delay()
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_caregiver(username):
        print("Username taken, try again!")
        add_input_delay()
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    try:
        caregiver = Caregiver(username, salt=salt, hash=hash)
        # save to caregiver information to our database
        try:
            caregiver.save_to_db()
        except:
            print("Create failed, Cannot save")
            add_input_delay()
            return
        print(" *** Account created successfully *** ")
        add_input_delay()
    except pymssql.Error:
        print("Create failed")
        add_input_delay()
        return


def username_exists_caregiver(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Caregivers WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error:
        print("Error occurred when checking username")
        cm.close_connection()
    cm.close_connection()
    return False


def login_patient(tokens):
    # login_patient <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_patient
    global current_caregiver
    if current_caregiver is not None or current_patient is not None:
        print("Already logged-in!")
        add_input_delay()
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Token length is incorrect. Please try again!")
        add_input_delay()
        return

    username = tokens[1]
    password = tokens[2]

    patient = None
    try:
        try:
            patient = Patient(username, password=password).get()
        except:
            print("Get Failed")
            add_input_delay()
            return
    except pymssql.Error:
        print("Error occurred when logging in")
        add_input_delay()

    # check if the login was successful
    if patient is None:
        print("Please try again!")
        add_input_delay()
    else:
        print("Patient logged in as: " + username)
        current_patient = patient
        add_input_delay()


def login_caregiver(tokens):
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver
    if current_caregiver is not None or current_patient is not None:
        print("Already logged-in!")
        # add delay so user can read the output
        input("Press any key to continue...")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        # add delay so user can read the output
        input("Press any key to continue...")
        return

    username = tokens[1]
    password = tokens[2]

    caregiver = None
    try:
        try:
            caregiver = Caregiver(username, password=password).get()
        except:
            print("Get Failed")
            add_input_delay()
            return
    except pymssql.Error:
        print("Error occurred when logging in")
        add_input_delay()

    # check if the login was successful
    if caregiver is None:
        print("Please try again!")
        # add delay so user can read the output
        input("Press any key to continue...")
    else:
        print("Caregiver logged in as: " + username)
        current_caregiver = caregiver
        add_input_delay()


def search_caregiver_schedule(tokens):
    """
    # search_caregiver_schedule <date>
    * both caregivers and patients can perform this operation
    * outputs the username of the caregivers that are available for the date,
    along with the number of doses left for each vaccine
    """
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()

    # check 1: a caregiver or patient should be logged in
    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        add_input_delay()
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Tokens are not correct, Please try again!")
        return

    # getting the available caregivers
    get_username = """select  UserName from Caregivers c WHERE CaregiverID IN
    (select CaregiverID from Availabilities a where time = %s)"""

    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    try:
        d = datetime.datetime(year, month, day)
        try:
            cursor.execute(get_username, d)
            available_caregivers = cursor.fetchall()
            if len(available_caregivers)  == 0:
                print("No available caregivers at this date!")
                add_input_delay()
                return
            else:
                print("the available caregivers are: ")
                for row in available_caregivers:
                    print(row[0])
        except:
            print("getting caregivers failed!")
    except ValueError:
        print("Please enter a valid date!")
    except pymssql.Error as db_err:
        print("Error occurred when getting availability")

    # getting the available doses
    try:
        cursor.execute("select VaccineName, Doses from Vaccines")
        print("the available Vaccines are: ")
        for row in cursor:
            print(row[0], ': ', row[1])
    except pymssql.Error:
        print("Error when getting the available doses")
    add_input_delay()


def reserve(tokens):
    """
    # reserve <date> <vaccine>
    * patients perform this operation to reserve an appointment
    * you will be randomly assigned a caregiver for the reservation on that date
    * output the assigned caregiver and the appointment ID for the reservation
    """
    global current_patient
    # check 1: user must be logged in as a patient
    if current_patient is None:
        print("No patient is logged in. Kindly log-in as a patient!")
        add_input_delay()
        return
    # check 2: tokens must be 2 tokens
    if len(tokens) != 3:
        print("Tokens are not correct, Please try again!")
        add_input_delay()
        return

    # parse the data from input
    date = tokens[1]
    vaccine_name = tokens[2]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    try:
        d = datetime.datetime(year, month, day)
    except ValueError:
        print("Please enter a valid date!")
        add_input_delay()
        return

    # getting a random availability
    random_availability = Availability().get(d)
    if random_availability is None:
        print("No available caregiver! Please choose a different time!")
        add_input_delay()
        return

    # getting the vaccines data
    try:
        vaccine = Vaccine(vaccine_name).get()
    except pymssql.Error:
        print("Error occurred when getting Vaccine data")
        add_input_delay()
        return

    # check 3: if getter returns null, it means that we need to create the vaccine
    if vaccine is None:
        print('Vaccine not available!')
        add_input_delay()
        return

    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()
    # create the appointment object
    current_appointment = Appointment(current_patient, random_availability, vaccine)
    try:
        vaccine.decrease_available_doses(1, cursor)
        random_availability.change_to_reserved(cursor)
        current_appointment.save_to_db(cursor)
        conn.commit()
    except:
        print("This vaccine is out of stock. please choose a different one!")
        conn.rollback()
        cm.close_connection()
        return
    cm.close_connection()
    print("Appointment reserved!")


def upload_availability(tokens):
    #  upload_availability <date>
    #  date format should be mm-dd-yyyy
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Tokens are not correct, Please try again!")
        return

    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    try:
        d = datetime.datetime(year, month, day)
        try:
            current_caregiver.upload_availability(d)
        except:
            print("Upload Availability Failed")
            return
        print("Availability uploaded!")
    except ValueError:
        print("Please enter a valid date!")
    except pymssql.Error as db_err:
        print("Error occurred when uploading availability")


def cancel(tokens):
    """
    # cancel <appointment_id>
    * Both caregivers and patients should be able to cancel an existing appointment.
    """
    # check 1: a user must be logged in
    if current_caregiver is None and current_patient is None:
        print("No user logged-in, please log-in as patient or caregiver!")
        add_input_delay()
        return

    # check 2: tokens must be 2 tokens
    if len(tokens) != 2:
        print("Tokens are not correct, Please try again!")
        add_input_delay()
        return
    appointment_id = tokens[1]

    # get the appointment data
    canceled_appointment = Appointment().get(appointment_id)
    vaccine = Vaccine().get_by_id(canceled_appointment.vaccine_id)
    availability = Availability().get_by_id(canceled_appointment.availability_id)

    if canceled_appointment is None or vaccine is None or availability is None:
        print("Appointment data is not available!")
        add_input_delay()
        return

    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()
    try:
        vaccine.increase_available_doses(1, cursor)
        availability.change_to_available(cursor)
        canceled_appointment.delete_from_db(cursor)
        conn.commit()
    except pymssql.Error as db_err:
        print("Error Cancelling the appointment. please try again!")
        print("Exception code: " + str(db_err))
        conn.rollback()
        cm.close_connection()
        return
    cm.close_connection()
    print("Appointment canceled!")


def add_doses(tokens):
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    #  check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    vaccine_name = tokens[1]
    doses = int(tokens[2])
    vaccine = None
    try:
        try:
            vaccine = Vaccine(vaccine_name, doses).get()
        except:
            print("Failed to get Vaccine!")
            return
    except pymssql.Error:
        print("Error occurred when adding doses")

    # check 3: if getter returns null, it means that we need to create the vaccine and insert it into the Vaccines
    #          table

    if vaccine is None:
        try:
            vaccine = Vaccine(vaccine_name, doses)
            try:
                vaccine.save_to_db()
            except:
                print("Failed To Save")
                return
        except pymssql.Error:
            print("Error occurred when adding doses")
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            try:
                vaccine.increase_available_doses(doses)
            except:
                print("Failed to increase available doses!")
                return
        except pymssql.Error:
            print("Error occurred when adding doses")

    print("Doses updated!")


def show_appointments(tokens):
    #   show_appointments
    # * output the scheduled appointments for the current user (both patients and caregivers)
    # * for caregivers, you should print the appointment ID, vaccine name, date, and patient name
    # * for patients, you should print the appointment ID, vaccine name, date and caregiver name

    global current_caregiver
    global current_patient
    # check 1: a user must be logged in
    if current_caregiver is None and current_patient is None:
        print("Kindly log-in as a patient or caregiver!")
        add_input_delay()
        return

    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()

    # get the data as a caregiver
    if current_caregiver is not None:
        get_appointment_caregiver = "select a.AppointmentID, v.VaccineName, a2.Time, p.UserName " \
                      "from Appointments a JOIN Caregivers c on a.CaregiverID = c.CaregiverID " \
                      "JOIN Patients p on a.PatientID = p.PatientID " \
                      "JOIN Availabilities a2 on a.AvailabilityID = a2.AvailabilityID " \
                      "JOIN Vaccines v on a.VaccineID = v.VaccineID where a.CaregiverID = %s"
        try:
            cursor.execute(get_appointment_caregiver, current_caregiver.get_caregiver_id())
            for row in cursor:
                print("* Appointment no:", row[0], ",Vaccine:", row[1], ", date:", row[2], ", to be given to:", row[3])
            add_input_delay()
            return
        except pymssql.Error as db_err:
            print("fetching appointment data failed. try again later!")
            add_input_delay()
            return
    else:
        get_appointment_patient = "select a.AppointmentID, v.VaccineName, a2.Time, c.UserName " \
                          "from Appointments a JOIN Caregivers c on a.CaregiverID = c.CaregiverID " \
                          "JOIN Patients p on a.PatientID = p.PatientID " \
                          "JOIN Availabilities a2 on a.AvailabilityID = a2.AvailabilityID " \
                          "JOIN Vaccines v on a.VaccineID = v.VaccineID where a.PatientID = %s"
        try:
            print(current_patient.get_patient_id())
            cursor.execute(get_appointment_patient, current_patient.get_patient_id())
            for row in cursor:
                print("* Appointment no:", row[0], ",Vaccine:", row[1], ", date:", row[2], ", to be given by:", row[3])
            add_input_delay()
            return
        except pymssql.Error as db_err:
            print("fetching appointment data failed. try again later!")
            add_input_delay()
            return


def logout(tokens):
    global current_caregiver
    global current_patient
    if current_caregiver is not None:
        print("Logging out from caregiver account: " + current_caregiver.get_username())
        current_caregiver = None
        add_input_delay()
        return
    elif current_patient is not None:
        print("Logging out from caregiver account: " + current_patient.get_username())
        current_patient = None
        add_input_delay()
        return
    print("No User Logged in, please login as a patient or caregiver")
    add_input_delay()
    return


def start():
    stop = False
    while not stop:
        print()
        print(" *** Please enter one of the following commands *** ")
        print("> create_patient <username> <password>")
        print("> create_caregiver <username> <password>")
        print("> login_patient <username> <password>")
        print("> login_caregiver <username> <password>")
        print("> search_caregiver_schedule <date>")
        print("> reserve <date> <vaccine>")
        print("> upload_availability <date>")
        print("> cancel <appointment_id>")
        print("> add_doses <vaccine> <number>")
        print("> show_appointments")
        print("> logout")
        print("> Quit")
        print()
        print("> Enter: ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Type in a valid argument")
            break

        response = response.lower()
        tokens = response.split(" ")
        if len(tokens) == 0:
            ValueError("Try Again")
            continue
        operation = tokens[0]
        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            reserve(tokens)
        elif operation == "upload_availability":
            upload_availability(tokens)
        elif operation == cancel:
            cancel(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_appointments":
            show_appointments(tokens)
        elif operation == "cancel":
            cancel(tokens)
        elif operation == "logout":
            logout(tokens)
        elif operation == "quit":
            print("Thank you for using the scheduler, Goodbye!")
            stop = True
        else:
            print("Invalid Argument")


def add_input_delay():
    # add delay so user can read the output
    input("Press any key to continue...")


if __name__ == "__main__":
    '''
    // pre-define the three types of authorized vaccines
    // note: it's a poor practice to hard-code these values, but we will do this ]
    // for the simplicity of this assignment
    // and then construct a map of vaccineName -> vaccineObject
    '''

    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")

    start()







