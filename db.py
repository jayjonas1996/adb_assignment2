import os
# import pyodbc
import pymssql

SERVER = 'jknadb.database.windows.net'
USER = 'user'
_DB = 'assignment1'

class DB:
    
    def __init__(self):
        conn = pymssql.connect(server=SERVER, user=USER, password=os.environ.get('DB_PASS'), database=_DB)
        cursor = conn.cursor()
        cursor.execute('select convert(varchar(10), GETDATE(), 108)')
        print(cursor.fetchone())

