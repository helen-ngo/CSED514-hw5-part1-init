-- Remove procedure to create data tables if it exists
DROP PROCEDURE IF EXISTS initDataModel;  
GO 

-- Implement data tables as a stored procedure
CREATE PROCEDURE initDataModel
AS

-- Drop tables if they exists
DROP TABLE IF EXISTS CaregiverSchedule;
DROP TABLE IF EXISTS VaccineAppointments;
DROP TABLE IF EXISTS Patients; 
DROP TABLE IF EXISTS Vaccines; 
DROP TABLE IF EXISTS AppointmentStatusCodes;
DROP TABLE IF EXISTS Caregivers;

-- Create Caregivers table  
CREATE TABLE Caregivers(
	CaregiverId INT IDENTITY(0,1) PRIMARY KEY,
	CaregiverName varchar(50)
	);

-- Create Appointment Status table
CREATE TABLE AppointmentStatusCodes(
	StatusCodeId INT PRIMARY KEY,
	StatusCode VARCHAR(30)
);

-- Create Vaccines table  
CREATE TABLE Vaccines(
	VaccineId INT PRIMARY KEY,
	VaccineBrand varchar(50),
    DosesOnHand INT,
    DosesReserved INT,
    VaccineMinAge INT,
    DoseSeries INT,
    IntervalBetweenDoses INT,
    DoseVolume FLOAT,
	);

-- Create Patients table  
CREATE TABLE Patients(
	PatientId INT IDENTITY(0,1) PRIMARY KEY,
	PatientName VARCHAR(50),
    PatientBirthdate DATE,
    PatientEmail VARCHAR(254),
    PatientPhone VARCHAR(10)
	);

-- Create Vaccine Appointment table
CREATE TABLE VaccineAppointments(
	VaccineAppointmentId INT IDENTITY(0,1) PRIMARY KEY,
    VaccineId INT DEFAULT 0 NOT NULL
		CONSTRAINT FK_VaccinesVaccineId FOREIGN KEY (VaccineId)
			REFERENCES Vaccines(VaccineId),
	PatientId INT DEFAULT 0 NOT NULL
		CONSTRAINT FK_PatientsPatientId FOREIGN KEY (PatientId)
			REFERENCES Patients(PatientId),
    DoseNumber INT
    );

-- Create Caregiver Schedule table
CREATE TABLE CaregiverSchedule(
	CaregiverSlotSchedulingId INT IDENTITY(0,1) PRIMARY KEY, 
	CaregiverId INT DEFAULT 0 NOT NULL
		CONSTRAINT FK_CareGiverScheduleCaregiverId FOREIGN KEY (caregiverId)
			REFERENCES Caregivers(CaregiverId),
	WorkDay DATE,
	SlotTime TIME,
	SlotHour INT DEFAULT 0 NOT NULL,
	SlotMinute INT DEFAULT 0 NOT NULL,
	SlotStatus INT DEFAULT 0 NOT NULL
		CONSTRAINT FK_CaregiverStatusCode FOREIGN KEY (SlotStatus) 
		     REFERENCES AppointmentStatusCodes(StatusCodeId),
	VaccineAppointmentId INT 
        CONSTRAINT FK_VaccineAppointmentsVaccineAppointmentId FOREIGN KEY (VaccineAppointmentId)
			REFERENCES VaccineAppointments(VaccineAppointmentId)
    );

-- Insert anonymous adult Patient
INSERT INTO Patients (PatientName)
	VALUES ('Anonymous');

-- Insert approved Vaccines
INSERT INTO Vaccines (VaccineId, VaccineBrand, VaccineMinAge, DoseSeries, DoseVolume)
	VALUES (0, 'Johnson & Johnson’s Janssen', 18, 1, 0.5);
INSERT INTO Vaccines (VaccineId, VaccineBrand, VaccineMinAge, DoseSeries, IntervalBetweenDoses, DoseVolume)
	VALUES (1, 'Pfizer-BioNTech', 16, 2, 21, 0.3);
INSERT INTO Vaccines (VaccineId, VaccineBrand, VaccineMinAge, DoseSeries, IntervalBetweenDoses, DoseVolume)
	VALUES (2, 'Moderna', 18, 2, 28, 0.5);

-- Insert Appointment Status Codes
INSERT INTO AppointmentStatusCodes (statusCodeId, StatusCode)
	VALUES (0, 'Open');
INSERT INTO AppointmentStatusCodes (statusCodeId, StatusCode)
	VALUES (1, 'OnHold');
INSERT INTO AppointmentStatusCodes (statusCodeId, StatusCode)
	VALUES (2, 'Scheduled');
INSERT INTO AppointmentStatusCodes (statusCodeId, StatusCode)
	VALUES (3, 'Completed');
INSERT INTO AppointmentStatusCodes (statusCodeId, StatusCode)
	VALUES (4, 'Missed');

GO

-- Create data tables for application
EXECUTE initDataModel;      

-- --- Commands to clear the active database Tables for unit testing
-- Truncate Table CareGiverSchedule
-- DBCC CHECKIDENT ('CareGiverSchedule', RESEED, 0)
-- Delete From Caregivers
-- DBCC CHECKIDENT ('Caregivers', RESEED, 0)
-- GO
