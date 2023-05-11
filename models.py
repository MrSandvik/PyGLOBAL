import json
import re
import pymysql
import config

# MySQL connection details
host = config.mysql_server
user = config.mysql_user
password = config.mysql_password
database = "mymodels"

# JSON file to read data from
json_file = "ux/global.json"

# Model details
model_id = 1
model_name = "vg"

# Connect to MySQL server
conn = pymysql.connect(
    host=host,
    user=user,
    password=password,
    database=database
)

# Create database if it does not exist
cursor = conn.cursor()
cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database.lower()};")
cursor.close()

# Read JSON data
with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# Get table name from first branch in JSON data
table_name = list(data.keys())[0]
table_name = table_name.replace("BC_", "")
table_name = table_name.split(" ")[0]

# Create table if it does not exist
cursor = conn.cursor()
cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {model_name} (
        myPK INT AUTO_INCREMENT PRIMARY KEY,
        ModelID INT,
        ModelName VARCHAR(255),
        TableName VARCHAR(255),
        FieldName VARCHAR(255),
        Description VARCHAR(255)
    )
""")

# Insert data into table
with open('log.txt', 'w', encoding='utf-8') as f:
    for table_name, table_data in data.items():
        for item in table_data:
            table_name = re.sub("^BC_", "", table_name)
            table_name = re.sub(" \(.*\)$", "", table_name)
            if item['ObjectName'].startswith('ID'):
                continue
            field_name = re.sub(r'^\w+_', '', item['ObjectName'])
            description = item["Description"].replace("'", "\\'")
            f.write(f"INSERT INTO {model_name} (ModelID, ModelName, TableName, FieldName, Description) VALUES ({model_id}, '{model_name}', '{table_name}', '{field_name}', '{description}')\n")
            cursor.execute(f"INSERT INTO {model_name} (ModelID, ModelName, TableName, FieldName, Description) VALUES ({model_id}, '{model_name}', '{table_name}', '{field_name}', '{description}')")

conn.commit()
cursor.close()
conn.close()
