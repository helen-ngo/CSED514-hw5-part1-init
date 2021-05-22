from datetime import datetime
from datetime import timedelta
import pymssql


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

    def ReserveAppointment(CaregiverSchedulingID, Vaccine, cursor)
        # validating the CaregiverSchedule slot id parm
        # create an initial entry in the VaccineAppointment Table
        # flag the Patient as “Queued for 1st Dose”
        # while
        return True

    def ScheduleAppointment()
        # Connect VaccineAppointment to CaregiverScheduler
        # update the Patient’s VaccineStatus field
        # maintain the Vaccine inventory
        # update the CaregiverScheduler Table
        return True

        cursor.connection.commit()