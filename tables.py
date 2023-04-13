import database
from config import mysql_database, mssql_schema, data_type_map

def create_tables():
    mysql_conn = database.connect_to_mysql()
    mysql_cursor = mysql_conn.cursor()

    mssql_conn = database.connect_to_mssql()
    mssql_cursor = mssql_conn.cursor()

    # Drop the database if it exists
    mysql_cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    mysql_cursor.execute(f"DROP DATABASE IF EXISTS {mysql_database};")
    mysql_cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
    
    # Create the database
    mysql_cursor.execute(f"CREATE DATABASE {mysql_database};")
    mysql_cursor.execute(f"USE {mysql_database};")
    print(f"Created database {mysql_database}")

    mssql_cursor.execute(f"SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE' AND TABLE_SCHEMA = '{mssql_schema}';")
    mssql_tables = [table[0] for table in mssql_cursor.fetchall()]

    for table in mssql_tables:
        mssql_cursor.execute(f"SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, NUMERIC_PRECISION, NUMERIC_SCALE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table}';")
        columns = []
        for column in mssql_cursor.fetchall():
            # Map the MSSQL data type to a MySQL data type
            mysql_data_type = data_type_map.get(column[1].lower(), 'varchar')
            if mysql_data_type == 'varchar':
                if column[2]:
                    if column[2] == -1:  # This means MAX
                        mysql_data_type = 'text'
                    else:
                        mysql_data_type = f'varchar({column[2]})'
                else:
                    mysql_data_type = 'varchar'
            elif mysql_data_type == 'binary':
                mysql_data_type = f'binary({column[2]})' if column[2] else 'binary'
            elif mysql_data_type == 'varbinary':
                mysql_data_type = f'varbinary({column[2]})' if column[2] else 'varbinary'
            elif mysql_data_type == 'decimal':
                precision = column[3]
                scale = column[4]
                mysql_data_type = f'decimal({precision},{scale})'
            columns.append(f"`{column[0]}` {mysql_data_type}")

        create_query = f"CREATE TABLE IF NOT EXISTS `{table}` (`myPK` INT NOT NULL AUTO_INCREMENT,{','.join(columns)}, PRIMARY KEY (`myPK`))"
        print(f"Creating table {table} with query: {create_query}")
        mysql_cursor.execute(create_query)

    mysql_cursor.close()
    mysql_conn.close()
    mssql_cursor.close()
    mssql_conn.close()

    print("Tables created successfully!")
