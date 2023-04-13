import re
from datetime import datetime

def is_valid_value(value, mssql_data_type):
    if mssql_data_type == 'int' and not isinstance(value, int):
        return False
    elif mssql_data_type in ('varchar', 'nvarchar', 'text', 'ntext', 'char', 'nchar') and not isinstance(value, str):
        return False
    elif mssql_data_type in ('bigint', 'smallint', 'tinyint', 'decimal', 'numeric', 'float', 'real', 'money', 'smallmoney') and not isinstance(value, (int, float)):
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

def validate_data(columns, mssql_data_types, row):
    for idx, value in enumerate(row):
        column_name = columns[idx].split()[0]
        mssql_data_type = mssql_data_types[idx]
        if not is_valid_value(value, mssql_data_type):
            raise ValueError(f"Invalid value '{value}' for column '{column_name}' with data type '{mssql_data_type}'")
