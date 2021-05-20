-- Use CoronaVirus
-- GO

-- InitScheduerApp


IF OBJECT_ID ( 'InitScheduerApp', 'P' ) IS NOT NULL
    DROP PROCEDURE InitScheduerApp;
GO  

--- Drop commands to restructure the DB
DROP TABLE IF EXISTS VaccineAppointments
DROP TABLE IF EXISTS Vaccines
DROP TABLE IF EXISTS Patients
DROP TABLE IF EXISTS CareGiverSchedule
DROP TABLE IF EXISTS AppointmentStatusCodes
DROP TABLE IF EXISTS VaccinationStatusCodes
DROP TABLE IF EXISTS Caregivers
Go

--- DDL to define the VaccineReservationScheduler Tables 
CREATE PROCEDURE InitScheduerApp
   AS

Create Table Caregivers(
	CaregiverId INT IDENTITY PRIMARY KEY,
	CaregiverName varchar(50)
);

Create Table AppointmentStatusCodes(
	StatusCodeId INT PRIMARY KEY,
	StatusCode   varchar(30)
);

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
INSERT INTO AppointmentStatusCodes (statusCodeId, StatusCode)
	VALUES (5, 'Rescheduled');

Create Table VaccinationStatusCodes(
	StatusCodeId INT PRIMARY KEY,
	StatusCode varchar(30)
);

INSERT INTO VaccinationStatusCodes (statusCodeId, StatusCode)
	VALUES (0, 'New');
INSERT INTO VaccinationStatusCodes (statusCodeId, StatusCode)
	VALUES (1, 'Queued for 1st Dose');
INSERT INTO VaccinationStatusCodes (statusCodeId, StatusCode)
	VALUES (2, '1st Dose Scheduled');
INSERT INTO VaccinationStatusCodes (statusCodeId, StatusCode)
	VALUES (3, '1st Dose Administered');
INSERT INTO VaccinationStatusCodes (statusCodeId, StatusCode)
	VALUES (4, 'Queued for 2nd Dose');
INSERT INTO VaccinationStatusCodes (statusCodeId, StatusCode)
	VALUES (5, '2nd Dose Scheduled');
INSERT INTO VaccinationStatusCodes (statusCodeId, StatusCode)
	VALUES (6, '2nd Dose Administered');
INSERT INTO VaccinationStatusCodes (statusCodeId, StatusCode)
	VALUES (7, 'Vaccination Complete');

Create Table CaregiverSchedule(
	CaregiverSlotSchedulingId INT Identity PRIMARY KEY, 
	CaregiverId INT DEFAULT 0 NOT NULL
		CONSTRAINT FK_CaregiverScheduleCaregiverId FOREIGN KEY (caregiverId)
			REFERENCES Caregivers(CaregiverId),
	WorkDay DATE,
	SlotTime TIME,
	SlotHour INT DEFAULT 0 NOT NULL,
	SlotMinute INT DEFAULT 0 NOT NULL,
	SlotStatus INT  DEFAULT 0 NOT NULL
		CONSTRAINT FK_CaregiverScheduleSlotStatus FOREIGN KEY (SlotStatus) 
		     REFERENCES AppointmentStatusCodes(StatusCodeId),
	VaccineAppointmentId INT DEFAULT 0 NOT NULL
		CONSTRAINT FK_CaregiverScheduleVaccineAppointmentId FOREIGN KEY (VaccineAppointmentId) 
		     REFERENCES VaccineAppointments(VaccineAppointmentId)
);

Create Table Patients(
	PatientId INT IDENTITY PRIMARY KEY,
	PatientName VARCHAR(50),
	PatientBirthdate DATE ,
	PatientEmail VARCHAR(254),
	PatientPhone VARCHAR(10)
);

Create Table Vaccines(
	VaccineName  VARCHAR(50) PRIMARY KEY,
	VaccineSupplier VARCHAR(50) PRIMARY KEY,
	VaccineBrand VARCHAR(50), 
	DoseSeries INT,
	DoseVolume INT,
	IntervalBetweenDoses INT,
	VaccineMinAge INT,
	MinAgeOfEUA INT
);

CREATE TABLE VaccineOrders(
	OrderId INT IDENTITY PRIMARY KEY,
	VaccineSupplier VARCHAR(50) NOT NULL
		CONSTRAINT FK_VaccineOrdersVaccineSupplier FOREIGN KEY (VaccineSupplier)
			REFERENCES Vaccines(VaccineSupplier),
	InvoiceDate DATE 
);

CREATE TABLE VaccineLineItems(
	OrderId INT
		CONSTRAINT FK_VaccineLineItemsOrderId FOREIGN KEY (OrderId)
			REFERENCES VaccineOrders(OrderId),
	VaccineName VARCHAR(50) NOT NULL
		CONSTRAINT FK_VaccineLineItemsVaccineName FOREIGN KEY (VaccineName)
			REFERENCES Vaccines(VaccineName),
	VaccineLotNumber VARCHAR(12) PRIMARY KEY,
	ExpirationDate DATE,
	Quantity INT,
	DeliveryDate DATE,
	Inactive BIT
);

Create Table VaccineAppointments(
	VaccineAppointmentId INT Identity PRIMARY KEY, 
	VaccineName varchar(50) ,
	VaccineLotNumer VARCHAR(12)
		CONSTRAINT FK_VaccineAppointmentsLotNumber FOREIGN KEY (VaccineLotNumber)
			REFERENCES VaccineLineItems(VaccineLotNumber),
	PatientId int
		CONSTRAINT FK_VaccineAppointmentsPatientID FOREIGN KEY (PatientId)
			REFERENCES Patients(PatientId),
	ReservationDate DATE ,
	DateCheckedIn DATETIME,
	DateAdministered DATETIME,
	VaccinationStatus INT NOT NULL
		CONSTRAINT FK_VaccineAppointmentsStatusCodes FOREIGN KEY (VaccinationStatus) 
			REFERENCES VaccinationStatusCodes(StatusCodeId),
	RescheduledAppointmentId INT
		CONSTRAINT FK_VaccineAppointmentsRescheduledId FOREIGN KEY (RescheduledAppointmentId) 
			REFERENCES VaccineAppointments(VaccineAppointmentId)
);

-- -- Create data tables for application
-- EXECUTE InitScheduerApp;    
