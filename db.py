import os
import pandas as pd
import pymssql

SERVER = 'jknadb.database.windows.net'
USER = 'user'
_DB = 'assignment1'

class DB:

    columns = ['time', 'latitude', 'longitude', 'depth', 'mag', 'magtype', 'nst', 'gap', 'dmin', 
               'rms', 'net', 'id', 'updated', 'place', 'type', 'horizontalerror', 'deptherror', 
               'magerror', 'magnst', 'status', 'localsource', 'magsource']
    lat = 32.7305688
    lon = -97.11319
    conn = None
    
    def __init__(self):
        self.conn = pymssql.connect(server=SERVER, user=USER, password=os.environ.get('DB_PASS'), database=_DB)
        

        # df = pd.DataFrame(row, columns=DB.columns)
        # print(df)
        # print(df.dtypes)
        # while row:  
        #     print(row)     
        #     row = cursor.fetch()
    def get(self):
        cursor = self.conn.cursor()

        cursor.execute("select COLUMN_NAME from INFORMATION_SCHEMA.columns where TABLE_NAME = 'test0';")
        columns = [x[0] for x in cursor.fetchall()]
        
        cursor.execute(f"""Declare @source geography = geography::Point({DB.lat}, {DB.lon}, 4326);
                           select * from test0 where ((@source.STDistance(geography::Point(latitude, longitude, 4326))) / 1000)  < {300};""")
        rows = cursor.fetchall()
        print(rows)
        return columns, rows

    def close(self):
        self.conn.close()
