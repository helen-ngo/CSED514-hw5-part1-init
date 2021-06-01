def clear_tables(client):
    sqlQuery = '''
               Truncate Table CaregiverSchedule
               DBCC CHECKIDENT ('CaregiverSchedule', RESEED, 0)
               DELETE FROM VaccineAppointments
               DBCC CHECKIDENT ('VaccineAppointments', RESEED, 0)
               Truncate Table PatientStatus
               Delete FROM VaccineBatches
               DELETE FROM Caregivers
               DBCC CHECKIDENT ('Caregivers', RESEED, 0)
               Delete From Patients WHERE PatientId > 0
               DBCC CHECKIDENT ('Patients', RESEED, 0)
               DELETE FROM Vaccines
               '''
    client.cursor().execute(sqlQuery)
    client.commit()
