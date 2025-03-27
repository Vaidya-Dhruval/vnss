# db_helper.py
import mysql.connector
import pandas as pd
from sqlalchemy import create_engine
from datetime import date, timedelta

class DBHelper:
    def __init__(self, host, username, password, database):
        self.host = host
        self.username = username
        self.password = password
        self.database = database
        self.conn = None
        self.cursor = None
        self.engine = None
        
    def connect(self):
        try:
            self.conn = mysql.connector.connect(
                host=self.host,
                user=self.username,
                password=self.password,
                database=self.database
            )
            self.cursor = self.conn.cursor()
            self.engine = create_engine(f"mysql+pymysql://{self.username}:{self.password}@{self.host}/{self.database}")
            return True
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return False
            
    def disconnect(self):
        if self.conn:
            self.conn.close()
        if self.cursor:
            self.cursor.close()
            
    def get_latest_date(self, table, column="Date", condition=""):
        query = f"SELECT MAX({column}) FROM {table} {condition}"
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        return result[0] if result and result[0] else None
        
    def insert_dataframe(self, df, table_name, if_exists="append"):
        """Insert a pandas DataFrame into a MySQL table"""
        try:
            df.to_sql(
                table_name, 
                con=self.engine, 
                index=False, 
                if_exists=if_exists, 
                chunksize=10000
            )
            return True
        except Exception as e:
            print(f"Error inserting data: {e}")
            return False
            
    def execute_query(self, query, params=None):
        """Execute a query and return results"""
        try:
            self.cursor.execute(query, params or ())
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Query error: {err}")
            return []
            
    def execute_and_fetch_df(self, query, params=None):
        """Execute a query and return results as pandas DataFrame"""
        try:
            return pd.read_sql(query, self.conn, params=params)
        except Exception as e:
            print(f"Query error: {e}")
            return pd.DataFrame()