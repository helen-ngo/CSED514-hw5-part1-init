from datetime import datetime
from datetime import timedelta
import pymssql
from vaccine_reservation_scheduler import VaccineReservationScheduler as SlotScheduler


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
            sqlQuery = "INSERT INTO VaccineAppointments (PatientId, VaccineName) VALUES (" + str(Vaccine.patient_id) + ", '" + Vaccine.vaccine_name + "')"
            cursor.execute(sqlQuery)
            
            # Appointment and patient info for 2 dose regiment
            sqlQuery = '''
                    SELECT *
                    FROM PatientStatus
                    WHERE PatientId=
                    '''
            sqlQuery += str(Vaccine.patient_id)
            cursor.execute(sqlQuery)
            _statusRow = cursor.fetchone()

            if _statusRow == None or _statusRow['VaccinationStatus'] == 0:
                # Flag the Patient as “Queued for 1st Dose”
                sqlQuery = '''
                        INSERT INTO PatientStatus (PatientId, VaccinationStatus)
                        VALUES (
                        '''
                sqlQuery += str(Vaccine.patient_id) + ", 1)"
                cursor.execute(sqlQuery)
                Vaccine.intial_dose_date = self.slot_date
                # create a second appointment
                self.slot_date += timedelta(days=21)
                self.new_slot_id = SlotScheduler.PutHoldOnAppointmentSlot(self,date=self.slot_date, cursor=cursor)
                self.ReserveAppointment(CaregiverSchedulingID=self.new_slot_id, Vaccine=Vaccine, cursor=cursor)

            # Validate 2nd 3-6 weeks after the 1st appointment
            if not Vaccine.slot_ids:
                Vaccine.add_slot(CaregiverSchedulingID)
                cursor.connection.commit()
                return Vaccine
            elif self.slot_date - Vaccine.intial_dose_date < timedelta(days=42):
                Vaccine.add_slot(CaregiverSchedulingID)
                cursor.connection.commit()
                return Vaccine
            else:
                cursor.connection.rollback()
                self.fail("No availability for second dose.")
        except pymssql.Error as db_err:
            cursor.connection.rollback()
            print("Database Programming Error in SQL Query processing for Appointments! ")
            print("Exception code: " + str(db_err.args[0]))
            if len(db_err.args) > 1:
                print("Exception message: " + db_err.args[1])
            print("SQL text that resulted in an Error: " + self.sqltext)

    def ScheduleAppointment(self, Vaccine, cursor):
        # Connect VaccineAppointment to CaregiverScheduler
        # Update the Patient’s VaccineStatus field
        # Maintain the Vaccine inventory
        # Update the CaregiverScheduler Table
        return True

        cursor.connection.commit()