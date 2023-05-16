import argparse
import json
import pymysql.cursors
import config

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--rebuild", help="rebuild the database", action="store_true")
args = parser.parse_args()

# Load the model from the JSON file
with open('model.json', 'r') as f:
    original_model = json.load(f)
    model = {key.lower(): {k.lower(): v.lower() for k, v in value.items()} for key, value in original_model.items()}

# Connect to MySQL server
conn = pymysql.connect(
    host=config.mysql_server,
    user=config.mysql_user,
    password=config.mysql_password,
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

def table_exists(cursor, table_name):
    cursor.execute(f'''
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_name = '{table_name}'
    ''')
    result = cursor.fetchone()
    return result['COUNT(*)'] == 1

def alter_table(cursor, table_name, table_model):
    cursor.execute(f'''
        SELECT column_name, data_type, column_key
        FROM information_schema.columns
        WHERE table_name = '{table_name}'
    ''')
    existing_columns = {row['COLUMN_NAME']: {'type': row['DATA_TYPE'], 'key': row['COLUMN_KEY']} for row in cursor.fetchall()}

    for column_name, column_type in table_model.items():
        if column_type == 'boolean':
            column_type = 'tinyint(1)'

        if column_name not in existing_columns:
            cursor.execute(f'ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}')
            print(f"Adding column '{column_name}' ({column_type}) to table '{table_name}'")
        elif existing_columns[column_name]['type'] != column_type and existing_columns[column_name]['key'] != 'PRI':
            cursor.execute(f'ALTER TABLE {table_name} MODIFY COLUMN {column_name} {column_type}')
            print(f"Altering column '{column_name}' ({existing_columns[column_name]['type']} >> {column_type}) in table '{table_name}'")
        else:
            print(f"No changes to column '{column_name}' ({column_type}) in table '{table_name}'")


try:
    with conn.cursor() as cursor:
        if args.rebuild:
            # Drop the database if it exists
            print("Dropping and recreating freshdesk database..")
            cursor.execute("DROP DATABASE IF EXISTS freshdesk")
            cursor.execute("CREATE DATABASE freshdesk")
        else:
            print("Database freshdesk was not found. Creating..")
            cursor.execute("CREATE DATABASE IF NOT EXISTS freshdesk")
        
        # Use the database
        cursor.execute("USE freshdesk")

        # Create the tables based on the model
        for table_name, table_model in model.items():
            if not table_exists(cursor, table_name):
                fields = ', '.join(f'{name} {type}' for name, type in table_model.items())
                cursor.execute(f'CREATE TABLE IF NOT EXISTS {table_name} ({fields})')
                print(f"Created table '{table_name}'")
            else:
                alter_table(cursor, table_name, table_model)

finally:
    conn.close()
