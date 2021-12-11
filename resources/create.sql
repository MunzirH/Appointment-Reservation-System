CREATE TABLE Caregivers (
    CaregiverID int IDENTITY(1,1) NOT NULL, --perform an auto-increment feature
    UserName varchar(255) NOT NULL, 
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (CaregiverID)
);

CREATE TABLE Patients (
    PatientID int IDENTITY(1,1) NOT NULL, --perform an auto-increment feature
    UserName varchar(255) NOT NULL,
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (PatientID)
);

CREATE TABLE Availabilities (
    AvailabilityID int IDENTITY(1,1) NOT NULL, --perform an auto-increment feature
    CaregiverID int REFERENCES Caregivers,
	IsReserved bit NOT NULL,
	Time date,
    PRIMARY KEY (AvailabilityID)
);

CREATE TABLE Vaccines (
    VaccineID int IDENTITY(1,1) NOT NULL, --perform an auto-increment feature
    VaccineName varchar(255) NOT NULL,
    Doses int NOT NULL,
    PRIMARY KEY (VaccineID)
);

CREATE TABLE Appointments(
    AppointmentID int IDENTITY(1,1) NOT NULL, --perform an auto-increment feature
    CaregiverID int REFERENCES Caregivers,
    PatientID int REFERENCES Patients,
	AvailabilityID int REFERENCES Availabilities,
    VaccineID int REFERENCES Vaccines,
    PRIMARY KEY (AppointmentID)
);