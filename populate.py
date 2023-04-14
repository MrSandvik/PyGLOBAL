import database
import sys
from config import mssql_db, mssql_schema, data_type_map, batch_size
from functions import validate_data, format_value, insert_rows, populate_progress

total_tables = 0

def populate_tables():
    mysql_conn = database.connect_to_mysql()
    mysql_cursor = mysql_conn.cursor()

    mssql_conn = database.connect_to_mssql()
    mssql_cursor = mssql_conn.cursor()

    mssql_cursor.execute(f"SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE' AND TABLE_SCHEMA = '{mssql_schema}';")
    mssql_tables = [table[0] for table in mssql_cursor.fetchall()]
    mssql_tables.sort()

    # Get total number of tables
    global total_tables
    total_tables = len(mssql_tables)
    
    with open('log.txt', 'a') as f:
        for index, table in enumerate(mssql_tables, start=1):
            f.write(f"Populating table: {table}...\n")

            # Fetching number of records in current table
            mssql_cursor.execute(f"SELECT COUNT(*) FROM {mssql_db}.{mssql_schema}.{table};")
            mssql_rowcount = mssql_cursor.fetchone()[0]
            
            # Start data type processing
            mssql_cursor.execute(f"SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table}';")
            
            columns = []
            mssql_data_types = []
            for column in mssql_cursor.fetchall():
                # Map the MSSQL data type to a MySQL data type
                mysql_data_type = data_type_map.get(column[1].lower(), 'varchar')
                if column[0] == 'Name':
                    mysql_data_type = 'varchar(255)'
                columns.append(f"`{column[0]}` {mysql_data_type}")
                mssql_data_types.append(column[1])

            # Fetch all records in current table
            mssql_cursor.execute(f"SELECT * FROM {mssql_db}.{mssql_schema}.{table};")

            tableIndex = index
            all_rows = []
            progress_count = 0
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
                if len(all_rows) == batch_size or row_number == mssql_cursor.rowcount - 1:
                    insert_rows(mysql_cursor, table, columns, all_rows, f)
                    all_rows = []
                progress_count += 1
                
                # Print/update progress bar
                populate_progress(table, progress_count, mssql_rowcount, tableIndex, batch_size, total_tables)
                
            # print a full progress bar once all rows are done
            populate_progress(table, mssql_rowcount, mssql_rowcount, tableIndex, batch_size, total_tables)
            sys.stdout.write("\n")
            sys.stdout.flush()

    mysql_cursor.close()
    mysql_conn.close()
    mssql_cursor.close()
    mssql_conn.close()

    print("Tables populated successfully!")