import database
import sys
from config import mssql_db, mssql_schema, data_type_map, batch_size
from functions import validate_data, format_value, insert_rows

batches = 0
total_batches = 0
total_tables = 0

def print_progress(table, current, total, tableIndex):
    progress_width = 50
    if int(total) == 0:
        current = 100
        total = 100
        percent = 100
    else:
        percent = int(current / total * 100)
    completed_width = int(progress_width * current / total)
    remaining_width = progress_width - completed_width
    progress_bar = '█' * completed_width + '░' * remaining_width
    batches = int(current / batch_size) + 1
    total_batches = int(total / batch_size) + 1
    progress_str = f"Populating table: \x1b[1m{table:<40}\x1b[0m | \x1b[32m{progress_bar}\x1b[0m | {percent:>3}% | {batches}/{total_batches} batches | table {tableIndex} of {total_tables}"
    sys.stdout.write('\r' + ' ' * len(progress_str) + '\r')
    sys.stdout.write(progress_str)
    sys.stdout.flush()

def populate_tables():
    mysql_conn = database.connect_to_mysql()
    mysql_cursor = mysql_conn.cursor()

    mssql_conn = database.connect_to_mssql()
    mssql_cursor = mssql_conn.cursor()

    mssql_cursor.execute(f"SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE' AND TABLE_SCHEMA = '{mssql_schema}';")
    mssql_tables = [table[0] for table in mssql_cursor.fetchall()]
    mssql_tables.sort()
    global total_tables
    total_tables = len(mssql_tables)

    with open('log.txt', 'a') as f:
        for index, table in enumerate(mssql_tables, start=1):
            mssql_cursor.execute(f"SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table}';")
            f.write(f"Populating table: {table}...\n")
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
            global tableIndex
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
                print_progress(table, progress_count, mssql_cursor.rowcount, tableIndex)
                
            # print a full progress bar once all rows are done
            print_progress(table, mssql_cursor.rowcount, mssql_cursor.rowcount, tableIndex)
            sys.stdout.write("\n")
            sys.stdout.flush()

    mysql_cursor.close()
    mysql_conn.close()
    mssql_cursor.close()
    mssql_conn.close()

    print("Tables populated successfully!")


