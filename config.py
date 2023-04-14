# config.py
# Microsoft SQL Server connection settings
odbc_driver = {
    1: '{FreeTDS}',
    2: '{ODBC Driver 17 for SQL Server}',
    3: '{SQL Server Native Client 11.0}'
}

mssql_driver = odbc_driver[2]
mssql_server = "192.168.1.165"
mssql_db = "protel"
mssql_schema = "proteluser"
mssql_user = "sa"
mssql_password = "Syndicate4!"


# mySQL Server connection settings
mysql_server = "orion"
mysql_user = "root"
mysql_password = "(Volvo90V)"
mysql_database = mssql_db

# Maximum number of records per INSERT statement
batch_size = 1000

# Maximum varchar size before converting to text data type
maxVarchar = 1000

# Define a dictionary to map data types between MSSQL and MySQL
data_type_map = {
    'bigint': 'bigint',
    'binary': 'binary',
    'bit': 'bit',
    'char': 'char',
    'date': 'date',
    'datetime': 'datetime',
    'datetime2': 'datetime',
    'decimal': 'decimal',
    'float': 'float',
    'int': 'int',
    'image': 'longblob',
    'money': 'decimal',
    'nchar': 'char',
    'ntext': 'text',
    'numeric': 'decimal',
    'nvarchar': 'varchar',
    'real': 'float',
    'smalldatetime': 'datetime',
    'smallint': 'smallint',
    'smallmoney': 'decimal',
    'text': 'text',
    'time': 'time',
    'tinyint': 'tinyint',
    'uniqueidentifier': 'char(36)',
    'varbinary': 'varbinary',
    'varchar': 'varchar',
}