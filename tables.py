import database
import re
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

        mssql_cursor.execute(f"SELECT * FROM {mssql_db}.{mssql_schema}.{table};")
        for row in mssql_cursor.fetchall():
            values = []
            for value in row:
                #strings
                if isinstance(value, str): 
                    value = value.replace("'", "\\'")
                    value = value.replace('\r\n', '\\n').replace('\r', '\\n').replace('\n', '\\n')
                    # Split the text into 10,000 character chunks
                    chunks = [value[i:i+10000] for i in range(0, len(value), 10000)]
                    # Add each chunk to the list of values
                    for chunk in chunks:
                        values.append(f"'{chunk}'")
                
                #dates/datetimes
                elif re.match(r'\d{4}-\d{2}-\d{2}', str(value)):
                    values.append(f"'{str(value)}'")

                #bytes
                elif isinstance(value, bytes):
                    column_data_type = next((column[1] for column in mssql_cursor.description if column[0] == columns[i].split()[0]), None)
                    if column_data_type.lower() == 'binary' or column_data_type.lower() == 'varbinary':
                        value = "0x" + value.hex()

                #numbers
                else:
                    values.append(str(value))

            # Construct the insert query
            insert_query = f"INSERT INTO `{table}` ({','.join(['id'] + [column.split()[0] for column in columns])}) VALUES (DEFAULT,{','.join(values)})"
            print(f"Query: \n {insert_query}")
            #input()
            # Execute the insert query if all values in the row have been processed
            if len(values) == len(columns):
                mysql_cursor.execute(insert_query)
            
        mysql_conn.commit()


    mysql_cursor.close()
    mysql_conn.close()
    mssql_cursor.close()
    mssql_conn.close()

    print("Tables created successfully!")
    
