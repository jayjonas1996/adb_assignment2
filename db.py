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
    columns3 = ['year', 'state', 'votes', 'party']
    columns4 = ['col1', 'col2', 'col3', 'fruits']

    cols = []
    conn = None
    auto_close = True
    
    def __init__(self, auto_close=True):
        self.auto_close = auto_close
        self.conn = pymssql.connect(server=SERVER, user=USER, password=os.environ.get('DB_PASS'), database=_DB)
        cursor = self.conn.cursor()
        cursor.execute("select COLUMN_NAME from INFORMATION_SCHEMA.columns where TABLE_NAME = 'test0';")
        self.cols = [x[0] for x in cursor.fetchall()]
    
    def short_query(self, text, param=None):
        if param:
           return self._execute(text, param) 
        return self._execute(text)

    def query_range(self, mi, ma, metric=None, offset=None):
        rows = []
        datetime.today() - timedelta(weeks=1)
        today = f"{datetime.now():%Y-%m-%d %H:%M:%S}"
        if offset and metric:
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
        rows = self._execute("""select * from quiz2 where net = %s""", (net1))
        self._execute("""update quiz2 set net = %s where net = %s""", (net2, net1), fetch=False)
        self.conn.commit()
        row_count = len(rows)
        print(row_count)
        self.close()
        return ['affected rows'], [[row_count]]
    
    def query_votes(self, year_from, year_to, votes_from=None, votes_to=None):
        cols = self.columns3
        if votes_from is not None and votes_to is not None:
            rows = self._execute('select * from pvotes where year between %d and %d and votes between %d and %d order by votes desc', (year_from, year_to, votes_from, votes_to))
            rows_max = self._execute('select top 1 * from pvotes where year between %d and %d and votes between %d and %d order by votes desc', (year_from, year_to, votes_from, votes_to))
            rows_min = self._execute('select top 1 * from pvotes where year between %d and %d and votes between %d and %d order by votes', (year_from, year_to, votes_from, votes_to))
        else:
            rows = self._execute('select state, sum(votes), party from pvotes where year between %d and %d group by state, party order by state', (year_from, year_to))
            rows_max = self._execute('select top 1 state, party, max(votes) as count from pvotes where year between %d and %d group by state, party order by count desc', (year_from, year_to))
            rows_min = self._execute('select top 1 state, party, max(votes) as count from pvotes where year between %d and %d group by state, party order by count',  (year_from, year_to))
            cols = ['state', 'votes', 'party']
        return cols, rows, rows_max + rows_min
    
    def query_n_fruits(self, fruits):
        cols = self.columns4
        fruits = "', '".join(fruits)
        fruits = "'" + fruits + "'"
        rows = self._execute(f'select count(*) from quiz4 where name in ({fruits}) group by name;')
        return cols, rows
    
    def query_bar_fruits(self, n):
        cols = self.columns4
        rows = self._execute("select top %d name, count(*) as 'count' from quiz4 group by name order by 'count' desc", (n))
        return cols, rows
    
    def query_range_fruit(self, low, high):
        cols = ['col1', 'col3']
        rows = self._execute('select col1, col3 from quiz4 where col1 between %d and %d', (low, high))
        return cols, rows
    
    def query_student_id(self, id):
        cols = ['id', 'Fname', 'Lname', 'Age', 'Credit']
        rows = self._execute('select * from students where id = %d', (id))
        return cols, rows
    
    def query_register(self, student_id, course_id, section_id, r):
        cols = ['Student id', 'Course id', 'Section id']

        is_registered = self._execute('select count(*) from registration where student_id = %d and course_id = %d and section_id = %d', (student_id, course_id, section_id))[0][0]
        print(is_registered)
        if is_registered > 0:
            return [], [], f'Student {student_id} is already registered for course {course_id} and section {section_id}'

        age_limit = int(r.get('age'))
        age = int(self._execute('select age from students where id = %d', (student_id))[0][0])
        if age < age_limit and course_id > 5000:
            return [], [], f"Age {age} is less than allowed limit of {age_limit}"

        course = self._execute('select * from class where Course = %d and Section = %d', (course_id, section_id))
        course_limit = int(course[0][3])
        students = self._execute('select count(*) from registration where course_id = %d and section_id = %d', (course_id, section_id))
        if int(students[0][0]) >= course_limit:
            return [], [], f"Class is full"

        courses = self._execute('select course_id, section_id from registration where student_id = %d', (student_id))
        print(courses)

        rows = self._execute('select course_id, section_id from registration where student_id = %d', (student_id))
        rows = self._execute('select * from class where Course = %d and Section = %d', (course_id, section_id))
        m = 0
        w = 0
        f = 0
        t = 0
        tr = 0
        for row in rows:
            print(row)
            m += row[2].count('M')
            w += row[2].count('W')
            f += row[2].count('F')
            tr += row[2].count('TR')
            t += (row[2].count('TR') - row[2].count('T'))
        if (course[0][2].count('M') > 0 and m == 2) and (course[0][2].count('W') > 0 and w == 2) and \
            (course[0][2].count('F') > 0 and f == 2) and (course[0][2].count('T') > 0 and T == 2) and (course[0][2].count('TR') > 0 and tr == 2):
            return [], [], f"Per day class limit exceeded"

        self._execute('insert into registration values (%d, %d, %d)', (student_id, course_id, section_id))
        self.conn.commit()
        rows = self._execute('select * from registration where student_id = %d', (student_id))

        return cols, rows, ''
    
    def query_registeration(self, course_id, section_id):
        cols = ['student id', 'course id', 'section id']
        rows = self._execute('select * from registration where course_id = %d and section_id = %d', (course_id, section_id))
        return cols, rows

    def _execute(self, query, data=(), fetch=True):
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
            if self.auto_close:
                self.close()

        return rows

    def close(self):
        self.conn.close()
    
    def timed(self, metric, offset):
        return f"""{datetime.today() - timedelta(weeks=offset if metric == 'weeks' else 0, 
                    days=offset if metric == 'days' else 0):%Y-%m-%d %H:%M:%S}"""
        

