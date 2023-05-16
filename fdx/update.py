import os
import requests
import json
import pymysql.cursors
import config
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Freshdesk credentials
credentials = (config.fdx_api_key, config.fdx_password)

# Connect to MySQL server
conn = pymysql.connect(
    host=config.mysql_server,
    user=config.mysql_user,
    password=config.mysql_password,
    db=config.mysql_database,
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

# Function to fetch data from the Freshdesk API with pagination
def fetch_data(endpoint):
    page = 1
    while True:
            
        # Build the URL for the current page
        url = f'{config.fdx_base_url}/{endpoint}?page={page}'

        if endpoint == 'tickets':
            today = datetime.today()
            from_date = today - relativedelta(months=6)
            from_date = from_date.strftime('%Y-%m-%d')
            url += f'&updated_since={from_date}'
            
        # Make the API request and handle errors
        response = requests.get(url, auth=credentials)
        response.raise_for_status()

        # Write the HTTP response to the log file
        with open('log.txt', 'a', encoding='utf-8') as log_file:
            log_file.write(f'URL: {url}\n')
            log_file.write(f'Header: {response.headers}\n')
            log_file.write(f'Response: {response.text}\n')

        # Parse the JSON response
        data = response.json()

        # If there's no data, we've reached the end of the pagination
        if not data:
            break

        # Yield each item in the current page of data
        for item in data:
            yield item

        # Move on to the next page
        page += 1

# Function to check if a column exists, and if not, create it
def ensure_columns_exist(table, data):
    with conn.cursor() as cursor:
        # Get existing columns in the table
        cursor.execute(f'''
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = '{table}'
        ''')
        existing_columns = {row['COLUMN_NAME']: row['DATA_TYPE'] for row in cursor.fetchall()}

        # Check each key in the data
        for column in data.keys():
            # If the column does not exist in the table, create it
            if column not in existing_columns:
                cursor.execute(f'ALTER TABLE {table} ADD COLUMN {column} TEXT')
                print(f'Column {column} added to table {table}.', file=open('log.txt', 'a'))
    conn.commit()

# Function to insert or update data in the database
def insert_update_data(table, data):
    # Ensure the necessary columns exist in the table
    ensure_columns_exist(table, data)
    
    with conn.cursor() as cursor:
        # Ensure the data is flat
        flat_data = {k: json.dumps(v) if isinstance(v, (dict, list)) else v for k, v in data.items()}
        columns = ', '.join('`' + str(column).replace('/', '_') + '`' for column in flat_data.keys())
        values = ', '.join('%s' for _ in flat_data.values())
        placeholders = ', '.join('`' + str(column).replace('/', '_') + '`=%s' for column in flat_data.keys())
        sql = f'INSERT INTO {table} ({columns}) VALUES ({values}) ON DUPLICATE KEY UPDATE {placeholders}'
        cursor.execute(sql, list(flat_data.values())*2)
        with open('log.txt', 'a', encoding='utf-8') as log_file:
            log_file.write(f"Executed SQL: {sql}\nWith values: {list(flat_data.values())*2}\n")

    conn.commit()

# Check if the file exists before attempting to delete it
if os.path.exists("log.txt"):
    os.remove("log.txt")

# Fetch data from the API and insert/update it in the database
#for endpoint in ['contacts', 'companies', 'tickets', 'time_entries']:  #'conversations', 
for endpoint in ['tickets']:  #'conversations', 
    for item in fetch_data(endpoint):
        insert_update_data(endpoint, item)

conn.close()
