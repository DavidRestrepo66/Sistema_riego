from utils.sql_server import (
    get_sql_server_connection
)

try:

    conn = get_sql_server_connection()

    print(
        "SQL Server conectado correctamente"
    )

    conn.close()

except Exception as e:

    print(
        "Error:",
        e
    )