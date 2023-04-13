import database
import re
from config import mssql_db, mssql_schema, data_type_map
from functions import validate_data

def populate_tables():
    mysql_conn = database.connect_to_mysql()
    mysql_cursor = mysql_conn.cursor()

    mssql_conn = database.connect_to_mssql()
    mssql_cursor = mssql_conn.cursor()

    mssql_cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE';")
    mssql_tables = [table[0] for table in mssql_cursor.fetchall()]

    with open('log.txt', 'w') as f:
        for table in mssql_tables:
            mssql_cursor.execute(f"SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table}';")
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

            all_rows = []
            for row in mssql_cursor.fetchall():
                try:
                    validate_data(columns, mssql_data_types, row)
                except ValueError as e:
                    f.write(f"Validation error: {str(e)}\n")
                    continue

                values = []
                for idx, value in enumerate(row):
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
                        column_data_type = next((column[1] for column in mssql_cursor.description if column[0] == columns[idx].split()[0]), None)
                        if column_data_type and (column_data_type.lower() == 'binary' or column_data_type.lower() == 'varbinary'):
                            value = "0x" + value.hex()
                        else:
                            value = f"X'{value.hex()}'"
                        values.append(str(value))

                    #numbers
                    else:
                        values.append('NULL' if value is None else str(value))
                        
                all_rows.append(f"({','.join(['DEFAULT'] + values)})")

            # Check if all_rows is not empty
            if all_rows:
                # Construct the insert query
                insert_query = f"INSERT INTO `{table}` ({','.join(['myPK'] + [column.split()[0] for column in columns])}) VALUES {','.join(all_rows)}"
                f.write(f"Query: \n {insert_query}\n")
                try:
                    # Execute the insert query
                    mysql_cursor.execute(insert_query)
                    mysql_conn.commit()
                    f.write(f"Inserted {len(all_rows)} rows into {table}\n")
                except Exception as e:
                    f.write(f"Error inserting into {table}: {str(e)}\n")

        mysql_cursor.close()
        mysql_conn.close()
        mssql_cursor.close()
        mssql_conn.close()

    print("Tables populated successfully!")

if __name__ == "__main__":
    populate_tables()
