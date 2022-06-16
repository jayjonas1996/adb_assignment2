import os
# import pandas as pd
import pymssql

SERVER = 'jknadb.database.windows.net'
USER = 'user'
_DB = 'assignment1'

class DB:

    columns = ['time', 'latitude', 'longitude', 'depth', 'mag', 'magtype', 'nst', 'gap', 'dmin', 
               'rms', 'net', 'id', 'updated', 'place', 'type', 'horizontalerror', 'deptherror', 
               'magerror', 'magnst', 'status', 'localsource', 'magsource']

    cols = []
    conn = None
    
    def __init__(self):
        self.conn = pymssql.connect(server=SERVER, user=USER, password=os.environ.get('DB_PASS'), database=_DB)
        cursor = self.conn.cursor()
        cursor.execute("select COLUMN_NAME from INFORMATION_SCHEMA.columns where TABLE_NAME = 'test0';")
        self.cols = [x[0] for x in cursor.fetchall()]
        
    def get(self):
        cursor = self.conn.cursor()
        cursor.execute(f"""Declare @source geography = geography::Point(%d, %d, 4326);
                           select * from test0 where ((@source.STDistance(geography::Point(latitude, longitude, 4326))) / 1000)  < %d;""", (DB.lat, DB.lon, 300))
        rows = cursor.fetchall()
        return columns, rows

    def query_range(self, mi, ma):
        rows = self._execute('SELECT * from [dbo].[test0] where mag BETWEEN %d AND %d', mi, ma)
        return rows

    def query_radius(self, lat, lon, radius):
        rows = self._execute("select * from test0 where ((geography::Point(%d, %d, 4326).STDistance(geography::Point(latitude, longitude, 4326))) / 1000)  < %d;", (lat, lon, radius))
        return rows
    
    def _execute(self, query, data=()):
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, data)
            rows = cursor.fetchall()
        except e as Exception:
            print(e)
            rows = []
        finally:
            self.close()

        return rows

    def close(self):
        self.conn.close()
