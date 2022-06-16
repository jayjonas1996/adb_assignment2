import os
from datetime import datetime, timedelta
import pymssql
import pandas as pd
import numpy as np

SERVER = 'jknadb.database.windows.net'
USER = 'user'
_DB = 'assignment1'

# Database interfac class to interact with the hosted sql database
# with resuable dynamic modular functinos
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

    def query_range(self, mi, ma, metric, offset=None):
        datetime.today() - timedelta(weeks=1)
        today = f"{datetime.now():%Y-%m-%d %H:%M:%S}"
        if offset:
            past = self.timed(metric, offset)
            rows = self._execute('SELECT * from test0 where mag BETWEEN %d AND %d AND time BETWEEN %s and %s', (mi, ma, past, today))
        elif mi and ma:
            rows = self._execute('SELECT * from test0 where mag BETWEEN %d AND %d', (mi, ma))
        elif mi:
            rows = self._execute('SELECT * from test0 where mag >= %d', (mi))
        elif ma:
            rows = self._execute('SELECT * from test0 where mag <= %d', (ma))
        return self.cols, rows

    def query_radius(self, lat, lon, radius):
        rows = self._execute("select * from test0 where ((geography::Point(%d, %d, 4326).STDistance(geography::Point(latitude, longitude, 4326))) / 1000)  < %d;", (lat, lon, radius))
        return self.cols, rows

    def query_cluster(self):
        rows = self._execute("SELECT * from test0")
        df = pd.DataFrame(rows, columns=self.columns)
        a = pd.cut(df["longitude"], np.arange(-180, 180 + 30, 30), labels=[str(x) for x in range(int(360 / 30))])
        b = pd.cut(df["latitude"],  np.arange(-90, 90 + 30, 30),   labels=[str(x) for x in range(int(180 / 30))])
        
        df['blocks'] = [f"{a}-{b}" for a, b in zip(a, b)]
        a = list(df[['blocks', 'time']].groupby(['blocks']).count().index)
        b = list(df[['blocks', 'time']].groupby(['blocks']).count().values)
        v = []
        print(list(zip(a, b)))
        for x, y in zip(a, b):
            v.append([x, y[0]])
        return ['blocks', 'count'], v

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
        

