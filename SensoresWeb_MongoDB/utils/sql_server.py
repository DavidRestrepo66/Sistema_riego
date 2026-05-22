import pyodbc


def get_sql_server_connection():

    conn = pyodbc.connect(

        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=FelipeSalda\\SQLEXPRESS;"
        "DATABASE=sensores_sql;"
        "Trusted_Connection=yes;"
    )

    return conn