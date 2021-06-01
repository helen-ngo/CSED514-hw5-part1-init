from datetime import datetime
from datetime import timedelta
import pymssql


class COVID19Vaccine:
    ''' Adds the Vaccine to the DB and maintains its inventory'''
    def __init__(self, name, supplier, brand, cursor):
        self.sqltext = "INSERT INTO Vaccines (VaccineName, VaccineSupplier, VaccineBrand) VALUES ('" + name + "', '" + supplier + "', '" + brand + "')"
        try: 
            cursor.execute(self.sqltext)
            cursor.connection.commit()
            cursor.execute("SELECT @@IDENTITY AS 'Identity'; ")
            _identityRow = cursor.fetchone()
            self.vaccineId = _identityRow['Identity']
            cursor.connection.commit()
            print('Query executed successfully. ' + brand + 'vaccine added as '
            + name)
        except pymssql.Error as db_err:
            print("Database Programming Error in SQL Query processing for Vacines! ")
            print("Exception code: " + str(db_err.args[0]))
            if len(db_err.args) > 1:
                print("Exception message: " + db_err.args[1])
            print("SQL text that resulted in an Error: " + self.sqltext)

    def AddDoses(self, name, lot_number, quantity, cursor):
        self.sqltext = "INSERT INTO VaccineBatches (VaccineName, VaccineLotNumber, OwnedDoses) VALUES ('" + name + "', '" + lot_number + "', '" + str(quantity) + "')"
        try: 
            cursor.execute(self.sqltext)
            cursor.connection.commit()
            print('Query executed successfully. Added ' + str(quantity)
            +  ' doses of Vaccine Name = ' + name)
        except pymssql.Error as db_err:
            print("Database Programming Error in SQL Query processing for Vaccines doses!")
            print("Exception code: " + str(db_err.args[0]))
            if len(db_err.args) > 1:
                print("Exception message: " + db_err.args[1])
            print("SQL text that resulted in an Error: " + self.sqltext)

    def ReserveDoses(self, name, patient_id, date, cursor):
        self.sqltext = "UPDATE TOP(2) VaccineAppointments " + "SET VaccineName = '" + name + "' WHERE PatientId = " + str(patient_id) + " AND VaccineName IS NULL"
        try: 
            
            # Set first dose date
            self.dose_date = date
            
            # Query available doses for first dose date
            self.sqltext_2 = "SELECT SUM(OwnedDoses) AS Total_Doses, SUM(ReservedDoses) AS Booked_Doses, Total_Doses - Booked_Doses AS Available_Doses"
            self.sqltext_2 += " FROM VaccineBatches"
            self.sqltext_2 += " WHERE VaccineName = '" + name + "'"
            self.sqltext_2 += " AND ExpirationDate > '" + self.dose_date + "'"
            cursor.execute(self.sqltext_2)
            _vaccineRow = cursor.fetchone()
            self.first_doses_available = _vaccineRow['Available_Doses']

            # Reserved first dose
            if self.first_doses_available >= 2:
                self.sqltext_3 = "UPDATE TOP(2) VaccineBatches"
                # Mark the slot as “Scheduled”
                self.sqltext_3 += " SET ReservedDoses = ReservedDoses + 1 ,"
                self.sqltext_3 += " WHERE VaccineName = '" + name + "'"
                self.sqltext_3 += " AND ExpirationDate > '" + self.dose_date + "'"
                self.sqltext_3 += " ORDER BY ExpirationDate"
                cursor.execute(self.sqltext)
            else:
                cursor.connection.rollback()
                raise Exception('Only ' + self.first_doses_available + ' valid dose remaining.')

            # Set max second dose date and find avaiable second doses
            self.dose_date += timedelta(days=42)
            cursor.execute(self.sqltext_2)
            _vaccineRow = cursor.fetchone()
            self.second_doses_available = _vaccineRow['Available_Doses']

            # Reserve second dose
            if self.second_doses_available >= 1:
                cursor.execute(self.sqltext)
            else:
                cursor.connection.rollback()
                raise Exception('Only ' + self.first_doses_available + ' valid dose remaining.')

            # Update appointment table with vaccine to be used
            cursor.execute(self.sqltext)
            print('Query executed successfully. Reserved 2 of doses.')

        except pymssql.Error as db_err:
            cursor.connection.rollback()
            print("Database Programming Error in SQL Query processing for Vaccines doses!")
            print("Exception code: " + str(db_err.args[0]))
            if len(db_err.args) > 1:
                print("Exception message: " + db_err.args[1])
            print("SQL text that resulted in an Error: " + self.sqltext)