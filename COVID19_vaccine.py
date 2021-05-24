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
        self.sqltext = "INSERT INTO VaccineLineItems (VaccineName, VaccineLotNumber, Quantity) VALUES ('" + name + "', '" + lot_number + "', '" + str(quantity) + "')"
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

    def ReserveDoses(self, name, patient_id, cursor):
        self.sqltext = "UPDATE TOP(2) VaccineAppointments " + "SET VaccineName = '" + name + "' WHERE PatientId = " + str(patient_id) + " AND VaccineName IS NULL"
        try: 
            # Query total doses
            sqltext_2 = "SELECT SUM(Quantity) as Total_Doses"
            sqltext_2 += " FROM VaccineLineItems"
            sqltext_2 += " WHERE VaccineName = '" + name + "'"
            cursor.execute(sqltext_2)
            _vaccineRow = cursor.fetchone()
            self.total_doses = _vaccineRow['Total_Doses']
            # Query reserved and used doses
            sqltext_3 = "SELECT COUNT(*) as Booked_Doses"
            sqltext_3 += " FROM VaccineAppointments"
            sqltext_3 += " WHERE VaccineName = '" + name + "'"
            cursor.execute(sqltext_3)
            _vaccineRow = cursor.fetchone()
            self.booked_doses = _vaccineRow['Booked_Doses']
            if int(self.total_doses) - int(self.booked_doses) >= 2:
                cursor.execute(self.sqltext)
                print('Query executed successfully. Reserved 2 of doses.')
            else:
                cursor.connection.rollback()
                raise Exception('Only ' + str(int(self.total_doses) - int(self.booked_doses)) + ' dose remaining.')
        except pymssql.Error as db_err:
            cursor.connection.rollback()
            print("Database Programming Error in SQL Query processing for Vaccines doses!")
            print("Exception code: " + str(db_err.args[0]))
            if len(db_err.args) > 1:
                print("Exception message: " + db_err.args[1])
            print("SQL text that resulted in an Error: " + self.sqltext)