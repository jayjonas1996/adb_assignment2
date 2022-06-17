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
    columns2 = ['time', 'latitude', 'longitude', 'id', 'place'] #['time', 'latitude', 'longitude', 'depth', 'mag', 'magType', 'net', 'id', 'place', 'horizontalerror', 'magerror', 'magnst', 'locationsource']

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

    def query_nearest_mag(self, lat, lon, mi, ma):
        if mi and ma:
            rows = self._execute("""select time, place, mag, ((geography::Point(%d, %d, 4326).STDistance(geography::Point(latitude, longitude, 4326))) / 1000) 
                            as 'dist' from test0 where mag >= %d order by 'dist'""", (lat, lon, mi, ma))
        elif mi:
            rows = self._execute("""select time, place, mag, ((geography::Point(%d, %d, 4326).STDistance(geography::Point(latitude, longitude, 4326))) / 1000) 
                            as 'dist' from test0 where mag >= %d order by 'dist'""", (lat, lon, mi))
        elif ma:
            rows = self._execute("""select time, place, mag, ((geography::Point(%d, %d, 4326).STDistance(geography::Point(latitude, longitude, 4326))) / 1000) 
                            as 'dist' from test0 where mag <= %d order by 'dist'""", (lat, lon, ma))
    
        return ['Time', 'Place', 'Magnitude', 'distance in KM'], rows

    def query_cluster(self, lat_from, lat_to, lon_from, lon_to, interval):
        rows = self._execute("SELECT * from test0")
        df = pd.DataFrame(rows, columns=self.columns)
        a = pd.cut(df["longitude"], np.arange(lon_from, lon_to + interval, interval), labels=[str(x) for x in range(int((lon_to - lon_from) / interval))])
        b = pd.cut(df["latitude"],  np.arange(lat_from, lat_to + interval, interval),   labels=[str(x) for x in range(int((lat_to - lat_from) / interval))])
        
        df['blocks'] = [f"{a}-{b}" for a, b in zip(a, b)]
        a = list(df[['blocks', 'time']].groupby(['blocks']).count().index)
        b = list(df[['blocks', 'time']].groupby(['blocks']).count().values)
        v = []
        
        for x, y in zip(a, b):
            v.append([x, y[0]])

        return ['blocks', 'count'], v
    
    def query_bound(self, lat_from, lat_to, lon_from, lon_to):
        rows = self._execute("""select time, latitude, longitude, id, place from quiz2 where latitude between %d and %d and longitude between %d and %d""", (lat_from, lat_to, lon_from, lon_to))
        return self.columns2, rows

    def query_net(self, net, mi, ma):
        rows = self._execute("""select top 5 time, latitude, longitude, id, place from quiz2 where net = %s and mag between %d and %d""", (net, mi, ma))
        return self.columns2, rows
    
    def query_date(self, date):
        rows = self._execute("""select top 1 net, count(*) as 'occurance' from quiz2 
                                where time between DATETIMEFROMPARTS(%d, %d, %d, 0, 0, 0, 0) 
                                and DATETIMEFROMPARTS(%d, %d, %d, 23, 59, 59, 999) group by net order by 'occurance' desc""",(date.year, date.month, date.day, date.year, date.month, date.day), close=False)
        print(rows)
        
        rows2 = self._execute("""select top 1 net, count(*) as 'occurance' from quiz2 
                                where time between DATETIMEFROMPARTS(%d, %d, %d, 0, 0, 0, 0) 
                                and DATETIMEFROMPARTS(%d, %d, %d, 23, 59, 59, 999) group by net order by 'occurance'""",(date.year, date.month, date.day, date.year, date.month, date.day))
        if len(rows2):
            rows.append(rows2[0])
        return ['net', 'frequency'], rows
    
    def query_modify_net(self, net1, net2):
        rows = self._execute("""select * from quiz2 where net = %s""", (net1), close=False)
        self._execute("""update quiz2 set net = %s where net = %s""", (net2, net1), close=False, fetch=False)
        self.conn.commit()
        row_count = len(rows)
        print(row_count)
        self.close()
        return ['affected rows'], [[row_count]]

    def _execute(self, query, data=(), close=True, fetch=True):
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, data)
            rows = []
            if fetch:
                rows = cursor.fetchall()
        except Exception as e:
            print(e)
            rows = []
        finally:
            if close:
                self.close()

        return rows

    def close(self):
        self.conn.close()
    
    def timed(self, metric, offset):
        return f"""{datetime.today() - timedelta(weeks=offset if metric == 'weeks' else 0, 
                    days=offset if metric == 'days' else 0):%Y-%m-%d %H:%M:%S}"""
        

