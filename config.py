# config.py
mssql_server = "192.168.1.129"
mssql_db = "MarLogASGLOBALData"
mssql_schema = "MarLogAS"
mssql_user = "sa"
mssql_password = "Syndicate4!"

mysql_server = "localhost"
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