# config.py

# Microsoft SQL Server connection parameters
odbc_driver = {
    1: '{FreeTDS}',
    2: '{ODBC Driver 17 for SQL Server}',
    3: '{SQL Server Native Client 11.0}'
}

mssql_driver = odbc_driver[2]
mssql_server = "Orion"
mssql_port = 1433
mssql_encrypt = "yes"
mssql_trust_cert = "yes"
mssql_db = "MarLogASGLOBALData"
mssql_schema = "MarLogAS"
mssql_user = "sa"
mssql_password = "Syndicate4!"


# mySQL Server connection parameters
mysql_server = "127.0.0.1"
mysql_user = "root"
mysql_password = "(Volvo90V)"
mysql_database = mssql_db


# Operating parameters
# Processing batch size
batch_size = 300

# Maximum varchar size before converting to text data type
maxVarchar = 1000

# Data type mapping between MSSQL and MySQL (mssql = mysql)
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