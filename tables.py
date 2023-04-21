# tables.py

import sys
import database
from config import mssql_schema, mysql_database, data_type_map, maxVarchar


def start(force=False, tables_to_process=None):
    mysql_conn = database.connect_to_mysql()
    mysql_cursor = mysql_conn.cursor()
    mysql_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {mysql_database};")
    mysql_cursor.execute(f"USE {mysql_database};")

    mssql_conn = database.connect_to_mssql()
    mssql_cursor = mssql_conn.cursor()

    if force:
        mysql_cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        mysql_cursor.execute(f"DROP DATABASE IF EXISTS {mysql_database};")
        mysql_cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

        # Create the database
        mysql_cursor.execute(f"CREATE DATABASE {mysql_database};")
        mysql_cursor.execute(f"USE {mysql_database};")
        print(f"Created database {mysql_database}")

        # Set tables_to_create to all tables
        tables_to_create = [table[0] for table in mssql_cursor.execute(f"SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE' AND TABLE_SCHEMA = '{mssql_schema}' ORDER BY TABLE_NAME;")]
    else:
        if tables_to_process is None:
            tables_to_create, tables_to_drop = run_consistency_check(mssql_cursor, mysql_cursor)
            tables_to_create.sort()
            tables_to_drop.sort()

            for table in tables_to_drop:
                mysql_cursor.execute(f"DROP TABLE IF EXISTS `{table}`;")
        else:
            tables_to_create, tables_to_drop = run_consistency_check(mssql_cursor, mysql_cursor, tables_to_process=tables_to_process)
            tables_to_create.sort()
            tables_to_drop.sort()

            for table in tables_to_drop:
                mysql_cursor.execute(f"DROP TABLE IF EXISTS `{table}`;")

    if tables_to_create is not None:
        create_tables(mysql_cursor, mssql_cursor, tables_to_create)

    mysql_cursor.close()
    mysql_conn.close()

    return tables_to_create


def drop_and_create_database(mysql_cursor):
    mysql_cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    mysql_cursor.execute(f"DROP DATABASE IF EXISTS {mysql_database};")
    mysql_cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
    
    # Create the database
    mysql_cursor.execute(f"CREATE DATABASE {mysql_database};")
    mysql_cursor.execute(f"USE {mysql_database};")
    print(f"Created database {mysql_database}")


def run_consistency_check(mssql_cursor, mysql_cursor, tables_to_process=None):
    # Get the list of tables in the source MSSQL database
    mssql_cursor.execute(f"SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE' AND TABLE_SCHEMA = '{mssql_schema}' ORDER BY TABLE_NAME;")
    mssql_tables = [table[0] for table in mssql_cursor.fetchall()]

    # Get the list of tables in the target MySQL database
    mysql_cursor.execute(f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{mysql_database.lower()}' ORDER BY table_name")
    mysql_tables = [table[0].lower() for table in mysql_cursor.fetchall()]  # convert to lowercase

    # Prepare arrays
    tables_to_drop = []
    if tables_to_process is None:
        tables_to_create = [table for table in mssql_tables if table not in mysql_tables]
    else:
        tables_to_create = [table for table in tables_to_process if table in mssql_tables and table not in mysql_tables]

    with open("check.txt", "w") as f:
        for i, table in enumerate(mssql_tables):
            if tables_to_process is not None and table not in tables_to_process:
                continue  # Skip table if it's not in the list of tables to process
            
            # Get column names and data types for the MSSQL table
            mssql_cursor.execute(f"SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table}' AND TABLE_SCHEMA = '{mssql_schema}';")
            mssql_columns = [(column[0], data_type_map.get(column[1], column[1])) for column in mssql_cursor.fetchall()]
            
            if table.lower() in mysql_tables:  # use lowercase comparison
                # Get column names and data types for the MySQL table
                mysql_cursor.execute(f"SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table.lower()}' AND TABLE_SCHEMA = '{mysql_database.lower()}' AND COLUMN_NAME NOT IN ('myPK', 'myChecksum');")
                mysql_columns = [(column[0], column[1]) for column in mysql_cursor.fetchall()]
                
                if set(mssql_columns) != set(mysql_columns):
                    #input(f"\n\n---\n{mssql_columns}\n---\n>")
                    tables_to_drop.append(table)
                    tables_to_create.append(table)
                    f.write(f"L-2: Table {table} has mismatched columns and will be recreated.\n")
                    f.write("      " + "MSSQL".ljust(25) + "MYSQL\n")
                    for (mssql_col, mssql_dtype), (mysql_col, mysql_dtype) in zip(mssql_columns, mysql_columns):
                        f.write("      " + f"{mssql_col} ({mssql_dtype})".ljust(25) + f"{mysql_col} ({mysql_dtype})\n")

                else:
                    f.write(f"L-0: Table {table} has matching columns and will not be recreated.\n")
            else:
                f.write(f"L-1: Table {table} does not exist in target database and will be created.\n")

            print_progress(i + 1, len(mssql_tables), table, "Consistency check:")


    with open("check.txt", "a") as f:
        f.write("Tables to drop: " + str(tables_to_drop) + "\n")
        f.write("Tables to create: " + str(tables_to_create) + "\n")
    return tables_to_create, tables_to_drop

def print_progress(current, total, tables, title):
    progress_width = 50
    percent = int(current / total * 100)
    completed_width = int(progress_width * current / total)
    remaining_width = progress_width - completed_width
    progress_bar = '█' * completed_width + '░' * remaining_width
    sys.stdout.write(f"\r\x1b[2K{title:<58} | \x1b[33m{progress_bar}\x1b[0m | {percent:>3}% | {tables} tables")
    sys.stdout.flush()


def create_tables(mysql_cursor, mssql_cursor, tables_to_create):
    table_count = len(tables_to_create)
    table_index = 0

    with open('log.txt', 'w') as f:
        for table in tables_to_create:
            f.write(f"L-0: Processing table {table}\n")
            mssql_cursor.execute(f"SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, NUMERIC_PRECISION, NUMERIC_SCALE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table}' AND TABLE_SCHEMA = '{mssql_schema}';")
            columns = []
            for column in mssql_cursor.fetchall():
                # Map the MSSQL data type to a MySQL data type
                mysql_data_type = data_type_map.get(column[1].lower(), 'varchar')
                if mysql_data_type == 'varchar':
                    if column[2]:
                        if column[2] == -1:  # This means MAX
                            mysql_data_type = 'text'
                        elif column[2] > maxVarchar:
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

            # Create table in MySQL
            create_query = f"CREATE TABLE IF NOT EXISTS `{table.lower()}` (myPK INT NOT NULL AUTO_INCREMENT, myChecksum VARCHAR(32), {','.join(columns)}, PRIMARY KEY (myPK))"
            f.write(f"L-1: Creating table {table} with query: {create_query}\n")
            mysql_cursor.execute(create_query)

            # Fetch existing indices from MSSQL
            mssql_cursor.execute(f"SELECT i.name as index_name, c.name as column_name FROM sys.indexes i JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id JOIN sys.objects o ON i.object_id = o.object_id WHERE i.is_primary_key = 0 AND i.is_unique_constraint = 0 AND OBJECT_NAME(i.object_id) = '{table}' AND SCHEMA_NAME(o.schema_id) = '{mssql_schema}' ORDER BY i.name, ic.key_ordinal;")
            indices = {}
            for index in mssql_cursor.fetchall():
                f.write(f"L-0: Index {index[0]} on {index[1]} found in table {table}\n")
                index_name, column_name = index
                truncated_index_name = index_name[:64]
                if truncated_index_name not in indices:
                    indices[truncated_index_name] = []
                indices[truncated_index_name].append(column_name)

            # Add myPK and myChecksum indices
            indices[f"idx_{table.lower()}_myPK"] = ["myPK"]
            indices[f"idx_{table.lower()}_myChecksum"] = ["myChecksum"]

            # Drop and create indices in MySQL
            for index_name, index_columns in indices.items():
                # Check if the index exists
                mysql_cursor.execute(f"SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS WHERE table_name = '{table.lower()}' AND index_name = '{index_name[:64]}'")
                index_exists = mysql_cursor.fetchone()[0] > 0

                # Drop the index if it exists
                if index_exists:
                    drop_index_query = f"DROP INDEX `{index_name[:64]}` ON `{table.lower()}`"
                    f.write(f"L-2: Dropping existing index {index_name[:64]} with query: {drop_index_query}\n")
                    mysql_cursor.execute(drop_index_query)

                # Create the index
                index_column_str = ', '.join(f"`{c}`" for c in index_columns)
                index_query = f"CREATE INDEX `{index_name[:64]}` ON `{table.lower()}` ({index_column_str});"
                f.write(f"L-1: Creating index {index_name[:64]} with query: {index_query}\n")
                try:
                    mysql_cursor.execute(index_query)
                except:
                    continue

            table_index += 1
            print_progress(table_index, table_count, f"{table_index}/{table_count}", f"Creating table: {table}")

        print_progress(100, 100, f"{table_index}/{table_count}", f"Tables and indices created.")
        print()
        f.write("Tables cloned successfully!\n")
        f.close()

    return tables_to_create

