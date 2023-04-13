import database
import re
from config import mssql_db, mssql_schema, data_type_map
from functions import validate_data, format_value, insert_rows


def populate_tables():
    mysql_conn = database.connect_to_mysql()
    mysql_cursor = mysql_conn.cursor()

    mssql_conn = database.connect_to_mssql()
    mssql_cursor = mssql_conn.cursor()

    mssql_cursor.execute(f"SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE' AND TABLE_SCHEMA = '{mssql_schema}';")
    mssql_tables = [table[0] for table in mssql_cursor.fetchall()]

    with open('log.txt', 'w') as f:
        for table in mssql_tables:
            mssql_cursor.execute(f"SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table}';")
            f.write(f"Populating table: {table}...\n")
            print(f"Populating table: {table}...")
            columns = []
            mssql_data_types = []
            for column in mssql_cursor.fetchall():
                # Map the MSSQL data type to a MySQL data type
                mysql_data_type = data_type_map.get(column[1].lower(), 'varchar')
                if column[0] == 'Name':
                    mysql_data_type = 'varchar(255)'
                columns.append(f"`{column[0]}` {mysql_data_type}")
                mssql_data_types.append(column[1])

            mssql_cursor.execute(f"SELECT * FROM {mssql_db}.{mssql_schema}.{table};")

            all_rows = []
            for row_number, row in enumerate(mssql_cursor.fetchall()):
                try:
                    validate_data(table, row_number, columns, mssql_data_types, row)
                except ValueError as e:
                    f.write(f"Validation error: {str(e)}\n")
                    continue

                values = []
                for idx, value in enumerate(row):
                    values.append(format_value(value, columns, mssql_cursor, idx))

                all_rows.append(f"({','.join(['DEFAULT'] + values)})")

                # If we have reached max_records or the last row, insert the rows
                if len(all_rows) == 1000 or row_number == mssql_cursor.rowcount - 1:
                    insert_rows(mysql_cursor, table, columns, all_rows, f)
                    all_rows = []

    mysql_cursor.close()
    mysql_conn.close()
    mssql_cursor.close()
    mssql_conn.close()

    print("Tables populated successfully!")


