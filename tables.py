import database
from config import mysql_database, mssql_db, mssql_schema, data_type_map

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

    mssql_cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE';")
    mssql_tables = [table[0] for table in mssql_cursor.fetchall()]

    for table in mssql_tables:
        mssql_cursor.execute(f"SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table}';")
        columns = []
        for column in mssql_cursor.fetchall():
            # Map the MSSQL data type to a MySQL data type
            mysql_data_type = data_type_map.get(column[1].lower(), 'varchar')
            if column[0] == 'Name':
                mysql_data_type = 'varchar(255)'
            columns.append(f"`{column[0]}` {mysql_data_type}")

        create_query = f"CREATE TABLE IF NOT EXISTS `{table}` (`id` INT NOT NULL AUTO_INCREMENT,{','.join(columns)}, PRIMARY KEY (`id`))"
        print(f"Creating table {table} with query: {create_query}")
        mysql_cursor.execute(create_query)

    mysql_cursor.close()
    mysql_conn.close()
    mssql_cursor.close()
    mssql_conn.close()

    print("Tables created successfully!")

