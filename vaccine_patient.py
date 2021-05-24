from datetime import datetime
from datetime import timedelta
import pymssql
from vaccine_reservation_scheduler import VaccineReservationScheduler as SlotScheduler
from COVID19_vaccine import COVID19Vaccine


class VaccinePatient:
    ''' Adds the patient to the DB and updates vaccine appointments'''
    def __init__(self, name, cursor):
        self.sqltext = "INSERT INTO Patients (PatientName) VALUES ('" + name + "')"
        self.patientId = 0
        try: 
            cursor.execute(self.sqltext)
            # cursor.connection.commit()
            cursor.execute("SELECT @@IDENTITY AS 'Identity'; ")
            _identityRow = cursor.fetchone()
            self.patientId = _identityRow['Identity']
            # cursor.connection.commit()
            print('Query executed successfully. Patient : ' + name 
            +  ' added to the database using Patient ID = ' + str(self.patientId))
        except pymssql.Error as db_err:
            print("Database Programming Error in SQL Query processing for patients! ")
            print("Exception code: " + str(db_err.args[0]))
            if len(db_err.args) > 1:
                print("Exception message: " + db_err.args[1])
            print("SQL text that resulted in an Error: " + self.sqltext)

    def ReserveAppointment(self, CaregiverSchedulingID, Vaccine, cursor):
        try: 
            # Validate the CaregiverSchedule slot id parm
            sqlQuery = '''
                    SELECT *
                    FROM CaregiverSchedule
                    WHERE CaregiverSlotSchedulingId=
                    '''
            sqlQuery += str(CaregiverSchedulingID)
            cursor.execute(sqlQuery)
            _slotRow = cursor.fetchone()
            self.appointment_id = _slotRow['VaccineAppointmentId']
            self.slot_date = _slotRow['WorkDay']
            
            # Create an initial entry in the VaccineAppointments table
            sqlQuery = "INSERT INTO VaccineAppointments (PatientId) VALUES (" + str(Vaccine.patient_id) + ")"
            cursor.execute(sqlQuery)
            cursor.execute("SELECT @@IDENTITY AS 'Identity'; ")
            _identityRow = cursor.fetchone()
            self.appointment_id = _identityRow['Identity']
            Vaccine.add_appointment(self.appointment_id)
            
            # Appointment and patient info for 2 dose regiment
            sqlQuery = '''
                       SELECT *
                       FROM PatientStatus
                       WHERE PatientId=
                       '''
            sqlQuery += str(Vaccine.patient_id)
            cursor.execute(sqlQuery)
            _statusRow = cursor.fetchone()

            if _statusRow is None or _statusRow['VaccinationStatus'] == 0:
                # Flag the Patient as “Queued for 1st Dose”
                self.sqltext = '''
                               INSERT INTO PatientStatus (PatientId, VaccinationStatus)
                               VALUES (
                               '''
                self.sqltext += str(Vaccine.patient_id) + ", 1)"
                cursor.execute(self.sqltext)
                Vaccine.intial_dose_date = self.slot_date
                # create a second appointment
                self.slot_date += timedelta(days=21)
                self.new_slot_id = SlotScheduler.PutHoldOnAppointmentSlot(self,cursor=cursor,date=self.slot_date)
                self.ReserveAppointment(CaregiverSchedulingID=self.new_slot_id, Vaccine=Vaccine, cursor=cursor)

            # Validate 2nd 3-6 weeks after the 1st appointment
            if not Vaccine.slot_ids:
                Vaccine.add_slot(CaregiverSchedulingID)
                return Vaccine
            elif self.slot_date - Vaccine.intial_dose_date < timedelta(days=42):
                # Maintain the Vaccine inventory
                Vaccine.add_slot(CaregiverSchedulingID)
                return Vaccine
            else:
                cursor.connection.rollback()
                raise Exception('No availability for second dose.' )
        except pymssql.Error as db_err:
            cursor.connection.rollback()
            print("Database Programming Error in SQL Query processing for Appointments! ")
            print("Exception code: " + str(db_err.args[0]))
            if len(db_err.args) > 1:
                print("Exception message: " + db_err.args[1])
            print("SQL text that resulted in an Error: " + self.sqltext)

    def ScheduleAppointment(self, Vaccine, cursor):
        
        try:

            self.inventory = COVID19Vaccine.ReserveDoses(self, name=Vaccine.vaccine_name, patient_id=Vaccine.patient_id, cursor=cursor)

            # Query for current patient status
            sqlQuery = '''
                       SELECT TOP(1) *
                       FROM PatientStatus
                       WHERE PatientId =
                       '''
            sqlQuery += str(Vaccine.patient_id)
            sqlQuery += "ORDER BY StatusDate DESC"
            cursor.execute(sqlQuery)
            _statusRow = cursor.fetchone()
            self.vaccination_status = _statusRow['VaccinationStatus']

            # Update the Patient’s VaccineStatus field
            if self.vaccination_status < 2:
                self.sqltext = "INSERT INTO PatientStatus (PatientId, VaccinationStatus) VALUES (" + str(Vaccine.patient_id) + ", 2)"
            elif self.vaccination_status < 5:
                self.sqltext = "INSERT INTO PatientStatus (PatientId, VaccinationStatus) VALUES (" + str(Vaccine.patient_id) + ", 5)"
            else: 
                raise Exception("Both doses are already scheduled.")

            # Update CaregiverScheduler and VaccineAppointments Table
            for dose in range(len(Vaccine.slot_ids)):
                
                # Update the CaregiverScheduler Table
                self.sqltext = "UPDATE CaregiverSchedule "
                # Mark the slot as “Scheduled”
                self.sqltext += "SET SlotStatus = 2, "
                # Connect to slot to appointment
                self.sqltext += "VaccineAppointmentId = " + str(Vaccine.appointment_ids[dose])
                self.sqltext += " WHERE CaregiverSlotSchedulingId = " + str(Vaccine.slot_ids[dose])
                cursor.execute(self.sqltext)

        except pymssql.Error as db_err:
            cursor.connection.rollback()
            print("Database Programming Error in SQL Query processing for Appointments! ")
            print("Exception code: " + str(db_err.args[0]))
            if len(db_err.args) > 1:
                print("Exception message: " + db_err.args[1])
            print("SQL text that resulted in an Error: " + self.sqltext)
        finally:
            cursor.connection.commit()