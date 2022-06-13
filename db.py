import os
import pyodbc



class DB:
    
    def __init__(self):
        conn = pyodbc.connect(os.environ('CONNECTION_STRING'))
        cursor = conn.cursor()
    

