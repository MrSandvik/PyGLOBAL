# functions.py

import sys
import re
import hashlib
from datetime import datetime
from decimal import Decimal
from config import mssql_db, mssql_schema, mysql_database


def is_valid_value(value, mssql_data_type):
    if value is None:
        return True
    elif mssql_data_type == 'int' and not isinstance(value, int):
        return False
    elif mssql_data_type in ('varchar', 'nvarchar', 'text', 'ntext', 'char', 'nchar') and not isinstance(value, str):
        return False
    elif mssql_data_type in ('bigint', 'smallint', 'tinyint', 'numeric', 'float', 'real', 'money', 'smallmoney') and not isinstance(value, (int, float, Decimal)):
        return False
    elif mssql_data_type == 'decimal' and not isinstance(value, Decimal):
        return False
    elif mssql_data_type in ('bit') and not isinstance(value, bool):
        return False
    elif mssql_data_type in ('date', 'datetime', 'datetime2', 'smalldatetime') and not isinstance(value, datetime):
        return False
    elif mssql_data_type in ('binary', 'varbinary', 'image') and not isinstance(value, bytes):
        return False
    elif mssql_data_type == 'uniqueidentifier' and not (isinstance(value, str) and re.match(r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$', value)):
        return False
    elif mssql_data_type == 'time' and not (isinstance(value, str) and re.match(r'^\d{2}:\d{2}:\d{2}$', value)):
        return False
    else:
        return True


def check_existing(mysql_cursor, table, row_hashes, f):
    mysql_cursor.execute(f"SELECT `MyChecksum` FROM {table} WHERE `MyChecksum` IN ({','.join(map(lambda x: '%s', row_hashes))})", row_hashes)
    existing_hashes = {row[0] for row in mysql_cursor.fetchall()}
    return [hash_value in existing_hashes for hash_value in row_hashes]


def check_existing2(mysql_cursor, table, row_hash, f):
    mysql_cursor.execute(f"SELECT COUNT(*) FROM `{table}` WHERE `MyChecksum` = {row_hash};")
    count = mysql_cursor.fetchone()[0]
    return count > 0


def validate_data(table_name, row_number, columns, mssql_data_types, row):
    for idx, value in enumerate(row):
        column_name = columns[idx].split()[0]
        mssql_data_type = mssql_data_types[idx]
        if not is_valid_value(value, mssql_data_type):
            raise ValueError(f"Invalid value '{value}' for column '{column_name}' with data type '{mssql_data_type}' in table '{table_name}', row {row_number}")


def get_row_hash(row):
    return "'" + hashlib.md5("".join(str(value) for value in row).encode("utf-8")).hexdigest() + "'"


def format_value(value, columns, mssql_cursor, idx):
    # empty strings
    if value == '':
        return "''"

    # strings
    elif isinstance(value, str):
        value = value.replace("\\", "\\\\")
        value = value.replace("'", "\\'")
        value = value.replace('\r\n', '\\n').replace('\r', '\\n').replace('\n', '\\n')
        # Split the text into 10,000 character chunks
        chunks = [value[i:i + 10000] for i in range(0, len(value), 10000)]
        # Add each chunk to the list of values
        return f"'{''.join([chunk for chunk in chunks])}'"

    # dates/datetimes
    elif re.match(r'\d{4}-\d{2}-\d{2}', str(value)):
        return 'NULL' if value is None else f"'{str(value)}'"

    # bytes
    elif isinstance(value, bytes):
        column_data_type = next((column[1] for column in mssql_cursor.description if column[0] == columns[idx].split()[0]), None)
        if column_data_type and (column_data_type.lower() == 'binary' or column_data_type.lower() == 'varbinary'):
            value = "0x" + value.hex()
        else:
            value = f"X'{value.hex()}'"
        return str(value)

    # numbers
    else:
        column_name = columns[idx].split()[0]
        column_data_type = next((column[1] for column in mssql_cursor.description if column[0] == column_name), None)
        return 'NULL' if value is None else str(value)


def insert_rows(mysql_cursor, table, columns, rows, f):
    # Construct the insert query
    insert_query = f"INSERT INTO `{table}` ({','.join(['myPK', 'MyChecksum'] + [column.split()[0] for column in columns])}) VALUES {','.join(rows)}"
    f.write(f"L-1: Inserting batch of {len(rows)} rows into {table}\n")
    try:
        # Execute the insert query
        mysql_cursor.execute(insert_query)
        mysql_cursor.connection.commit()
    except Exception as e:
        mysql_cursor.connection.rollback()
        f.write(f"L-3: Error inserting into {table}: {str(e)}\n")
        f.write(f"     Query: \n     {insert_query}\n\n")
        mysql_cursor.close()
        mysql_cursor.connection.close()
        print("Error inserting data into MySQL. Terminating execution.")
        exit(1)


def update_existing_tables(mysql_cursor, mssql_cursor, tables_to_populate, columns):
    for index, table in enumerate(tables_to_populate, start=1):

        # Fetch all records in the current table from both databases
        mssql_cursor.execute(f"SELECT * FROM {mssql_db}.{mssql_schema}.{table};")
        mysql_cursor.execute(f"SELECT * FROM {mysql_database}.{table};")

        # Get row hashes for each record in both databases
        mssql_rows = {get_row_hash(row): row for row in mssql_cursor.fetchall()}
        mysql_rows = {get_row_hash(row[1:]): row for row in mysql_cursor.fetchall()}

        # Find rows that need to be updated
        rows_to_update = {row_hash: mssql_rows[row_hash] for row_hash in mssql_rows if row_hash not in mysql_rows}

        # Update rows in the MySQL database
        for row_hash, row in rows_to_update.items():
            row_data = [format_value(value, columns, mssql_cursor, idx) for idx, value in enumerate(row)]
            row_data_str = ', '.join([f"{columns[idx].split(' ')[0]} = {value}" for idx, value in enumerate(row_data)])
            mysql_cursor.execute(f"UPDATE {table} SET {row_data_str} WHERE `hash` = '{row_hash}';")


def populate_progress(table, current, total, tableIndex, batch_size, total_tables, title):
    progress_width = 50
    if int(total) == 0:
        current = 100
        total = 100
        percent = 100
    else:
        percent = int(current / total * 100)

    percent = int(current / total * 100)
    completed_width = int(progress_width * current / total)
    remaining_width = progress_width - completed_width
    progress_bar = '█' * completed_width + '░' * remaining_width
    batches = int(current / batch_size) + 1
    total_batches = int(total / batch_size) + 1
    progress_str = f"{title:.<16}: \x1b[1m{table:<40}\x1b[0m | \x1b[32m{progress_bar}\x1b[0m | {percent:>3}% | {batches}/{total_batches} batches | table {tableIndex} of {total_tables}"
    sys.stdout.write('\r' + ' ' * len(progress_str) + '\r')
    sys.stdout.write(progress_str)
    sys.stdout.flush()


## Tables.py functions

def drop_and_create_database(mysql_cursor):
    mysql_cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    mysql_cursor.execute(f"DROP DATABASE IF EXISTS {mysql_database};")
    mysql_cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
    
    # Create the database
    mysql_cursor.execute(f"CREATE DATABASE {mysql_database};")
    mysql_cursor.execute(f"USE {mysql_database};")
    print(f"Created database {mysql_database}")