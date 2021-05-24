import datetime
from enum import IntEnum
import os
import pymssql
import traceback

from sql_connection_manager import SqlConnectionManager
from vaccine_caregiver import VaccineCaregiver
from enums import *
from utils import *
# from covid19_vaccine import COVID19Vaccine as covid
# from vaccine_patient import VaccinePatient as patient


class VaccineReservationScheduler:

    def __init__(self):
        return

    def PutHoldOnAppointmentSlot(self, cursor, date=None):
        ''' Method that reserves a CareGiver appointment slot &
        returns the unique scheduling slotid
        Should return 0 if no slot is available  or -1 if there is a database error'''
        if date is None:
            self.date = datetime.date.today()
        else:
            self.date = date
        self.slotSchedulingId = 0
        self.getAppointmentSQL = '''
                                 SELECT TOP(1) CaregiverSlotSchedulingId
                                 FROM CaregiverSchedule
                                 WHERE VaccineAppointmentId IS NULL
                                 AND SlotStatus = 0
                                 '''
        self.getAppointmentSQL += "AND WorkDay >= '" + str(self.date) + "'"
        try:
            cursor.execute(self.getAppointmentSQL)
            _slotRow = cursor.fetchone()
            if _slotRow is not None:
                self.slotSchedulingId = _slotRow['CaregiverSlotSchedulingId']
                self.holdAppointmentSQL = '''
                                          UPDATE CaregiverSchedule 
                                          SET SlotStatus = 1 
                                          WHERE CaregiverSlotSchedulingId =
                                          '''
                self.holdAppointmentSQL += str(self.slotSchedulingId)
                cursor.execute(self.holdAppointmentSQL)
            return self.slotSchedulingId
        
        except pymssql.Error as db_err:
            print("Database Programming Error in SQL Query processing! ")
            print("Exception code: " + str(db_err.args[0]))
            if len(db_err.args) > 1:
                print("Exception message: " + db_err.args[1])           
            print("SQL text that resulted in an Error: " + self.getAppointmentSQL)
            cursor.connection.rollback()
            return -1

    def ScheduleAppointmentSlot(self, slotid, cursor):
        '''method that marks a slot on Hold with a definite reservation  
        slotid is the slot that is currently on Hold and whose status will be updated 
        returns the same slotid when the database update succeeds 
        returns 0 is there if the database update fails 
        returns -1 the same slotid when the database command fails
        returns -2 if the slotid parm is invalid '''
        if slotid < 1:
            return -2
        self.slotSchedulingId = slotid
        self.getAppointmentSQL = '''
                                 SELECT *
                                 FROM CaregiverSchedule
                                 WHERE CaregiverSlotSchedulingId =
                                 '''
        self.scheduleAppointmentSQL += str(self.slotSchedulingId)
        try:
            cursor.execute(self.getAppointmentSQL)
            _slotRow = cursor.fetchone()
            if len(_slotRow) < 1:
                self.slotSchedulingId = 0
            else:
                self.scheduleAppointmentSQL = '''
                                              UPDATE CaregiverSchedule 
                                              SET SlotStatus = 2 
                                              WHERE CaregiverSlotSchedulingId =
                                              '''
                self.scheduleAppointmentSQL += str(self.slotSchedulingId) 
            return self.slotSchedulingId
        except pymssql.Error as db_err:    
            print("Database Programming Error in SQL Query processing! ")
            print("Exception code: " + db_err.args[0])
            if len(db_err.args) > 1:
                print("Exception message: " + str(db_err.args[1]))  
            print("SQL text that resulted in an Error: " + self.getAppointmentSQL)
            return -1

if __name__ == '__main__':
        with SqlConnectionManager(Server=os.getenv("Server"),
                                  DBname=os.getenv("DBName"),
                                  UserId=os.getenv("UserID"),
                                  Password=os.getenv("Password")) as sqlClient:
            clear_tables(sqlClient)
            vrs = VaccineReservationScheduler()

            # get a cursor from the SQL connection
            dbcursor = sqlClient.cursor(as_dict=True)

            # Inialize the caregivers, patients & vaccine supply
            caregiversList = []
            caregiversList.append(VaccineCaregiver('Carrie Nation', dbcursor))
            caregiversList.append(VaccineCaregiver('Clara Barton', dbcursor))
            caregivers = {}
            for cg in caregiversList:
                cgid = cg.caregiverId
                caregivers[cgid] = cg

            # Add a vaccine and Add doses to inventory of the vaccine
            # Ass patients
            # Schedule the patients
            
            # Test cases done!
            clear_tables(sqlClient)
