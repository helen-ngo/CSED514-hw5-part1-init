import unittest
import os
import datetime
from sql_connection_manager import SqlConnectionManager
from vaccine_caregiver import VaccineCaregiver
from enums import *
from utils import *
from COVID19_vaccine import COVID19Vaccine
from vaccine_patient import VaccinePatient
from vaccine_reservation_scheduler import VaccineReservationScheduler as SlotScheduler

class TestDB(unittest.TestCase):

    def test_db_connection(self):
        try:
            self.connection_manager = SqlConnectionManager(Server=os.getenv("Server"),
                                                           DBname=os.getenv("DBName"),
                                                           UserId=os.getenv("UserID"),
                                                           Password=os.getenv("Password"))
            self.conn = self.connection_manager.Connect()
        except Exception:
            self.fail("Connection to databse failed")


class TestVaccineCaregiver(unittest.TestCase):
    def test_init(self):
        with SqlConnectionManager(Server=os.getenv("Server"),
                                  DBname=os.getenv("DBName"),
                                  UserId=os.getenv("UserID"),
                                  Password=os.getenv("Password")) as sqlClient:
            with sqlClient.cursor(as_dict=True) as cursor:
                try:
                    # clear the tables before testing
                    clear_tables(sqlClient)
                    # create a new VaccineCaregiver object
                    self.caregiver_a = VaccineCaregiver(name="Steve Ma",
                                                    cursor=cursor)
                    # check if the patient is correctly inserted into the database
                    sqlQuery = '''
                               SELECT *
                               FROM Caregivers
                               WHERE CaregiverName = 'Steve Ma'
                               '''
                    cursor.execute(sqlQuery)
                    rows = cursor.fetchall()
                    if len(rows) < 1:
                        self.fail("Creating caregiver failed")
                    # clear the tables after testing, just in-case
                    clear_tables(sqlClient)
                except Exception:
                    # clear the tables if an exception occurred
                    clear_tables(sqlClient)
                    self.fail("Creating caregiver failed")
    
    def test_verify_schedule(self):
        with SqlConnectionManager(Server=os.getenv("Server"),
                                  DBname=os.getenv("DBName"),
                                  UserId=os.getenv("UserID"),
                                  Password=os.getenv("Password")) as sqlClient:
            with sqlClient.cursor(as_dict=True) as cursor:
                try:
                    # clear the tables before testing
                    clear_tables(sqlClient)
                    # create a new VaccineCaregiver object
                    self.caregiver_a = VaccineCaregiver(name="Steve Ma",
                                                    cursor=cursor)
                    # check if schedule has been correctly inserted into CareGiverSchedule
                    sqlQuery = '''
                               SELECT *
                               FROM Caregivers, CareGiverSchedule
                               WHERE Caregivers.CaregiverName = 'Steve Ma'
                                   AND Caregivers.CaregiverId = CareGiverSchedule.CaregiverId
                               '''
                    cursor.execute(sqlQuery)
                    rows = cursor.fetchall()
                    hoursToSchedlue = [10,11]
                    minutesToSchedlue = [0, 15, 30, 45]
                    for row in rows:
                        slot_hour = row["SlotHour"]
                        slot_minute = row["SlotMinute"]
                        if slot_hour not in hoursToSchedlue or slot_minute not in minutesToSchedlue:
                            self.fail("CareGiverSchedule verification failed")
                    # clear the tables after testing, just in-case
                    clear_tables(sqlClient)
                except Exception:
                    # clear the tables if an exception occurred
                    clear_tables(sqlClient)
                    self.fail("CareGiverSchedule verification failed")


class TestCOVID19Vaccine(unittest.TestCase):
    def test_init(self):
        with SqlConnectionManager(Server=os.getenv("Server"),
                                  DBname=os.getenv("DBName"),
                                  UserId=os.getenv("UserID"),
                                  Password=os.getenv("Password")) as sqlClient:
            with sqlClient.cursor(as_dict=True) as cursor:
                try:
                    # clear the tables before testing
                    clear_tables(sqlClient)
                    # create a new VaccineCaregiver object
                    self.vaccine = COVID19Vaccine(name="BNT162b2",
                                                    supplier="Pfizer, Inc.",
                                                    brand="Pfizer-BioNTech",
                                                    cursor=cursor)
                    # check if the vaccine is correctly inserted into the database
                    sqlQuery = '''
                               SELECT *
                               FROM Vaccines
                               WHERE VaccineBrand = 'Pfizer-BioNTech'
                               '''
                    cursor.execute(sqlQuery)
                    rows = cursor.fetchall()
                    if len(rows) < 1:
                        self.fail("Creating vaccine failed.")
                    # clear the tables after testing, just in-case
                    clear_tables(sqlClient)
                except Exception:
                    # clear the tables if an exception occurred
                    clear_tables(sqlClient)
                    self.fail("Creating vaccine failed")
    
    def test_add_doses(self):
        with SqlConnectionManager(Server=os.getenv("Server"),
                                  DBname=os.getenv("DBName"),
                                  UserId=os.getenv("UserID"),
                                  Password=os.getenv("Password")) as sqlClient:
            with sqlClient.cursor(as_dict=True) as cursor:
                try:
                    # clear the tables before testing
                    clear_tables(sqlClient)
                    # create a new COVID19Vaccine object
                    self.vaccine = COVID19Vaccine(name="BNT162b2",
                                                    supplier="Pfizer, Inc.",
                                                    brand="Pfizer-BioNTech",
                                                    cursor=cursor)
                    # create a new AddDoses object
                    self.add_doses = self.vaccine.AddDoses(name="BNT162b2", lot_number="EW0167", quantity=500, cursor=cursor)
                    # check if the doses are correctly inserted into the database
                    sqlQuery = '''
                               SELECT SUM(Quantity) as Total_Doses
                               FROM VaccineLineItems
                               WHERE VaccineName = 'BNT162b2'
                               '''
                    cursor.execute(sqlQuery)
                    _vaccineRow = cursor.fetchone()
                    if _vaccineRow['Total_Doses'] != 500:
                        self.fail("Inccorect number of total BNT162b2 doses.")
                    # clear the tables after testing, just in-case
                    clear_tables(sqlClient)
                except Exception:
                    # clear the tables if an exception occurred
                    clear_tables(sqlClient)
                    self.fail("Adding vaccine doeses failed")
    
    def test_reserve_doses(self):
        with SqlConnectionManager(Server=os.getenv("Server"),
                                  DBname=os.getenv("DBName"),
                                  UserId=os.getenv("UserID"),
                                  Password=os.getenv("Password")) as sqlClient:
            with sqlClient.cursor(as_dict=True) as cursor:
                try:
                    # clear the tables before testing
                    clear_tables(sqlClient)
                    # create a new COVID19Vaccine object
                    self.vaccine = COVID19Vaccine(name="BNT162b2",
                                                    supplier="Pfizer, Inc.",
                                                    brand="Pfizer-BioNTech",
                                                    cursor=cursor)
                    # create a new AddDoses object
                    self.add_doses = self.vaccine.AddDoses(name="BNT162b2", lot_number="EW0167", quantity=3, cursor=cursor)
                    
                    # Create appointments to reserve vaccines from
                    sqlQuery = '''
                               INSERT INTO VaccineAppointments (PatientId)
                               VALUES (0);
                               INSERT INTO VaccineAppointments (PatientId)
                               VALUES (0);
                               '''
                    cursor.execute(sqlQuery)
                    
                    # Reserve doses for 1 person, should succeed
                    self.reserve_doses = self.vaccine.ReserveDoses(name="BNT162b2", patient_id=0, cursor=cursor)

                    # check if the vaccine is correctly reserved
                    sqlQuery = '''
                               SELECT *
                               FROM VaccineAppointments
                               WHERE VaccineName = 'BNT162b2'
                               '''
                    cursor.execute(sqlQuery)
                    rows = cursor.fetchall()
                    if len(rows) != 2:
                        self.fail("Reserving vaccine failed.")
                    # clear the tables after testing, just in-case
                    clear_tables(sqlClient)
                except Exception:
                    # clear the tables if an exception occurred
                    clear_tables(sqlClient)
                    self.fail("Adding vaccine doeses failed")


class TestVaccinePatient(unittest.TestCase):
    def test_init(self):
        with SqlConnectionManager(Server=os.getenv("Server"),
                                  DBname=os.getenv("DBName"),
                                  UserId=os.getenv("UserID"),
                                  Password=os.getenv("Password")) as sqlClient:
            with sqlClient.cursor(as_dict=True) as cursor:
                try:
                    # clear the tables before testing
                    clear_tables(sqlClient)
                    # create a new VaccinePatient object
                    self.patient = VaccinePatient(name="Albino Eeyore", 
                                                  cursor=cursor)
                    # check if the vaccine is correctly inserted into the database
                    sqlQuery = '''
                               SELECT *
                               FROM Patients
                               WHERE PatientName = 'Albino Eeyore'
                               '''
                    cursor.execute(sqlQuery)
                    rows = cursor.fetchall()
                    if len(rows) < 1:
                        self.fail("Creating patient failed.")
                    # clear the tables after testing, just in-case
                    clear_tables(sqlClient)
                except Exception:
                    # clear the tables if an exception occurred
                    clear_tables(sqlClient)
                    self.fail("Creating patient failed")
    
    def test_reserve_appointment(self):
        with SqlConnectionManager(Server=os.getenv("Server"),
                                  DBname=os.getenv("DBName"),
                                  UserId=os.getenv("UserID"),
                                  Password=os.getenv("Password")) as sqlClient:
            with sqlClient.cursor(as_dict=True) as cursor:
                try:
                    # clear the tables before testing
                    clear_tables(sqlClient)
                    # create a new VaccineCaregiver object
                    self.caregiver_a = VaccineCaregiver(name="Steve Ma",
                                                    cursor=cursor)
                    # Create new vaccines, and doses
                    sqlQuery = '''
                               INSERT INTO Vaccines (VaccineName, VaccineSupplier, VaccineBrand)
                               VALUES ('BNT162b2', 'Pfizer, Inc.', 'Pfizer-BioNTech');
                               INSERT INTO VaccineLineItems (VaccineName, VaccineLotNumber)
                               VALUES ('BNT162b2', '123456789');
                               '''
                    cursor.execute(sqlQuery)

                    # Create new patient
                    self.patient = VaccinePatient(name="Albino Eeyore", 
                                                  cursor=cursor)
                    cursor.execute("SELECT @@IDENTITY AS 'Identity'; ")
                    _identityRow = cursor.fetchone()
                    self.patientId = _identityRow['Identity']

                    # Create vaccine instance
                    class Vaccine:

                        def __init__(self, patient_id, vaccine_name):
                            self.patient_id = patient_id
                            self.vaccine_name = vaccine_name
                            self.intial_dose_date = None
                            self.slot_ids = []    # creates a new empty list for each slot
                            self.appointment_ids = []    # creates a new empty list for each appointment

                        def add_slot(self, slot_id):
                            self.slot_ids.append(slot_id)

                        def add_appointment(self, appointment_id):
                            self.appointment_ids.append(appointment_id)

                    self.vaccine = Vaccine(patient_id=self.patientId, vaccine_name="BNT162b2")
                    
                    # Make reservation
                    self.reservation = self.patient.ReserveAppointment(CaregiverSchedulingID=1, Vaccine=self.vaccine, cursor=cursor)
                    
                    # Check for the correct variables kept
                    self.assertEqual(self.reservation.slot_ids, [24, 1])
                    self.assertEqual(self.reservation.appointment_ids, [1, 2])
                    self.assertEqual(self.reservation.patient_id, self.patientId)

                    # clear the tables after testing, just in-case
                    clear_tables(sqlClient)
                except Exception:
                    # clear the tables if an exception occurred
                    clear_tables(sqlClient)
                    self.fail("Reserving appointment failed.")

    def test_schedule_appointment(self):
        with SqlConnectionManager(Server=os.getenv("Server"),
                                  DBname=os.getenv("DBName"),
                                  UserId=os.getenv("UserID"),
                                  Password=os.getenv("Password")) as sqlClient:
            with sqlClient.cursor(as_dict=True) as cursor:
                try:
                    # clear the tables before testing
                    clear_tables(sqlClient)
                    
                    # create two Vaccine Caregiver
                    self.caregiver_a = VaccineCaregiver(name="Steve Ma", cursor=cursor)
                    self.caregiver_a = VaccineCaregiver(name="Patrick Render", cursor=cursor)
                    
                    # Create new vaccines, and doses
                    sqlQuery = '''
                               INSERT INTO Vaccines (VaccineName, VaccineSupplier, VaccineBrand)
                               VALUES ('BNT162b2', 'Pfizer, Inc.', 'Pfizer-BioNTech');
                               INSERT INTO VaccineLineItems (VaccineName, VaccineLotNumber, Quantity)
                               VALUES ('BNT162b2', '123456789', 5);
                               '''
                    cursor.execute(sqlQuery)

                    # Create vaccine instance
                    class Vaccine:

                        def __init__(self, patient_id, vaccine_name):
                            self.patient_id = patient_id
                            self.vaccine_name = vaccine_name
                            self.intial_dose_date = None
                            self.slot_ids = []    # creates a new empty list for each slot
                            self.appointment_ids = []    # creates a new empty list for each appointment

                        def add_slot(self, slot_id):
                            self.slot_ids.append(slot_id)

                        def add_appointment(self, appointment_id):
                            self.appointment_ids.append(appointment_id)

                    # Attempt 5 new patients
                    self.patient_count = 0 # Patient counter
                    for self.patient_name in ["Winnie the Pooh", "Tigger", "Eeyore", "Piglet", "Rabbit"]:
                        self.patient_count += 1

                        # Create new patient
                        self.patient = VaccinePatient(name=self.patient_name, cursor=cursor)
                        cursor.execute("SELECT @@IDENTITY AS 'Identity'; ")
                        _identityRow = cursor.fetchone()
                        self.patientId = _identityRow['Identity']

                        # Create vaccine class instance for new patient
                        self.vaccine = Vaccine(patient_id=self.patientId, vaccine_name="BNT162b2")

                        # Search for avaiable slot
                        self.slot_id = SlotScheduler.PutHoldOnAppointmentSlot(self, cursor=cursor)
                        
                        # Make reservation
                        self.reservation = self.patient.ReserveAppointment(CaregiverSchedulingID=self.slot_id, Vaccine=self.vaccine, cursor=cursor)

                        if self.patient_count <= 2:
                            # Scheudle appointment
                            self.scheduling = self.patient.ScheduleAppointment(Vaccine=self.reservation, cursor=cursor)
                        else:
                            with self.assertRaises(Exception) as context:
                                self.patient.ScheduleAppointment(Vaccine=self.reservation, cursor=cursor)
                                self.assertTrue('This is broken' in context.exception)

                    # Query Caregiver Schedule updates
                    sqlQuery = ''' 
                               SELECT *
                               FROM CaregiverSchedule, VaccineAppointments
                               WHERE SlotStatus != 0
                               AND CaregiverSchedule.VaccineAppointmentId = VaccineAppointments.VaccineAppointmentId
                               '''
                    cursor.execute(sqlQuery)
                    _bookedRows = cursor.fetchall()

                    # Check number of slots scheduled
                    self.assertEqual(len(_bookedRows), 4)

                    # Check number of patients scheduled
                    self.patient_count = len(set([booking["PatientId"] for booking in _bookedRows]))
                    self.assertEqual(self.patient_count, 2)

                    print(str(len(_bookedRows)) + " slots scheduled for " + str(self.patient_count) + " patients.")

                    # clear the tables after testing, just in-case
                    clear_tables(sqlClient)
                except Exception:
                    # clear the tables if an exception occurred
                    clear_tables(sqlClient)
                    self.fail("Scheduling appointment failed.")


if __name__ == '__main__':
    unittest.main()
