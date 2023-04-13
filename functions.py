import re
from datetime import datetime
from decimal import Decimal

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


def validate_data(table_name, row_number, columns, mssql_data_types, row):
    for idx, value in enumerate(row):
        column_name = columns[idx].split()[0]
        mssql_data_type = mssql_data_types[idx]
        if not is_valid_value(value, mssql_data_type):
            raise ValueError(f"Invalid value '{value}' for column '{column_name}' with data type '{mssql_data_type}' in table '{table_name}', row {row_number}")


def format_value(value, columns, mssql_cursor, idx):
    # empty strings
    if value == '':
        return "''"

    # strings
    elif isinstance(value, str):
        value = value.replace("'", "\\'")
        value = value.replace('\r\n', '\\n').replace('\r', '\\n').replace('\n', '\\n')
        # Split the text into 10,000 character chunks
        chunks = [value[i:i + 10000] for i in range(0, len(value), 10000)]
        # Add each chunk to the list of values
        return ','.join([f"'{chunk}'" for chunk in chunks])

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
    insert_query = f"INSERT INTO `{table}` ({','.join(['myPK'] + [column.split()[0] for column in columns])}) VALUES {','.join(rows)}"
    try:
        # Execute the insert query
        mysql_cursor.execute(insert_query)
        mysql_cursor.connection.commit()
        f.write(f"Inserted {len(rows)} rows into {table}\n")
    except Exception as e:
        mysql_cursor.connection.rollback()
        f.write(f"Error inserting into {table}: {str(e)}\n")
        f.write(f"Query: \n {insert_query}\n\n")
        mysql_cursor.close()
        mysql_cursor.connection.close()
        print("Error inserting data into MySQL. Terminating execution.")
        exit(1)

