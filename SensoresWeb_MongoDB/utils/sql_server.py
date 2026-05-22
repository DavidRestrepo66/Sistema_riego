import pyodbc
from config import Config

def get_sql_server_connection():
    conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={Config.SQL_SERVER};"
        f"DATABASE={Config.SQL_DATABASE};"
        "Trusted_Connection=yes;"
    )
    return conn
