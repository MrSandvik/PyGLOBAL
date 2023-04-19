#populate.py

import database
import sys
from config import mssql_db, mssql_schema, mysql_database, data_type_map, batch_size
from functions import validate_data, format_value, insert_rows, populate_progress, get_row_hash, update_existing_tables, check_existing

total_tables = 0

def populate_tables(mode, tables_to_process = None, force = False):

    mysql_conn = database.connect_to_mysql()
    mysql_cursor = mysql_conn.cursor()
    mysql_cursor.execute(f"USE {mysql_database};")

    mssql_conn = database.connect_to_mssql()
    mssql_cursor = mssql_conn.cursor()

    mssql_cursor.execute(f"SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE' AND TABLE_SCHEMA = '{mssql_schema}';")
    mssql_tables = [table[0] for table in mssql_cursor.fetchall()]
    mssql_tables.sort()

    if tables_to_process is not None:
        tables_to_populate = tables_to_process
    else:
        tables_to_populate = mssql_tables

    # Get total number of tables
    global total_tables
    total_tables = len(tables_to_populate)


    if mode == "repopulate":
        # Truncate all tables in mysql_db
        mysql_cursor.execute("SHOW TABLES")
        all_tables = [table[0] for table in mysql_cursor.fetchall()]

        for table in all_tables:
            mysql_cursor.execute(f"TRUNCATE TABLE {table};")
            mysql_conn.commit()

    if mode == "update":
        # Implement logic to update existing tables with new records
        update_existing_tables(mysql_cursor, mssql_cursor, tables_to_populate, columns)
        mysql_conn.commit()


    if mode == "diff":
        # Implement logic to compare contents of each table and output report of changes
        pass
    
    with open('log.txt', 'a') as f:
        for index, table in enumerate(tables_to_populate, start=1):

            f.write(f"Populating table: {table}...\n")

            # Fetching number of records in current table
            mssql_cursor.execute(f"SELECT COUNT(*) FROM {mssql_db}.{mssql_schema}.{table};")
            mssql_rowcount = mssql_cursor.fetchone()[0]
            
            # Start data type processing
            mssql_cursor.execute(f"SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table}' AND TABLE_SCHEMA = '{mssql_schema}';")
            
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
                    row_hash = get_row_hash(row)
                    validate_data(table, row_number, columns, mssql_data_types, row)
                except ValueError as e:
                    f.write(f"Validation error: {str(e)}\n")
                    continue

                if force == False:
                    # Check if the row already exists, and if so, skip it
                    populate_progress(table, progress_count, mssql_rowcount, tableIndex, batch_size, total_tables, "Checking table")            
                    if check_existing(mysql_cursor, table, row_hash, f):
                        continue

                values = []
                for idx, value in enumerate(row):
                    values.append(format_value(value, columns, mssql_cursor, idx))
                all_rows.append(f"({','.join(['DEFAULT', row_hash] + values)})")
                            
                # If we have reached max_records, insert the rows
                if len(all_rows) == batch_size:
                    insert_rows(mysql_cursor, table, columns, all_rows, f)
                    all_rows = []
                progress_count += 1
                            
                # Print/update progress bar
                populate_progress(table, progress_count, mssql_rowcount, tableIndex, batch_size, total_tables, "Populating table")
                            
            # After the loop ends, insert any remaining records in all_rows
            if len(all_rows) > 0:
                insert_rows(mysql_cursor, table, columns, all_rows, f)
                all_rows = []

            # Print a full progress bar once all rows are done
            populate_progress(table, mssql_rowcount, mssql_rowcount, tableIndex, batch_size, total_tables, "Completed")
            sys.stdout.write("\n")
            sys.stdout.flush()

            
    mysql_cursor.close()
    mysql_conn.close()
    mssql_cursor.close()
    mssql_conn.close()

    print("Tables populated successfully!")

