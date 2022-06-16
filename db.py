import os
from datetime import datetime, timedelta
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

    def query_range(self, mi, ma, metric, offset):
        datetime.today() - timedelta(weeks=1)
        today = f"{datetime.now():%Y-%m-%d %H:%M:%S}"
        past = self.timed(metric, offset)
        rows = self._execute('SELECT * from test0 where mag BETWEEN %d AND %d AND time BETWEEN %s and %s', (mi, ma, past, today))
        return rows

    def query_radius(self, lat, lon, radius):
        rows = self._execute("select * from test0 where ((geography::Point(%d, %d, 4326).STDistance(geography::Point(latitude, longitude, 4326))) / 1000)  < %d;", (lat, lon, radius))
        return rows

    def _execute(self, query, data=()):
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, data)
            rows = cursor.fetchall()
        except Exception as e:
            print(e)
            rows = []
        finally:
            self.close()

        return rows

    def close(self):
        self.conn.close()
    
    def timed(self, metric, offset):
        return f"""{datetime.today() - timedelta(weeks=offset if metric == 'weeks' else 0, 
                    days=offset if metric == 'days' else 0):%Y-%m-%d %H:%M:%S}"""
        

