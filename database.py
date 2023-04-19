# database.py
import pymysql
import pyodbc
from config import mssql_driver, mssql_server, mssql_port, mssql_db, mssql_user, mssql_password, mssql_encrypt, mssql_trust_cert, mysql_server, mysql_user, mysql_password, mysql_database


def connect_to_mssql():
        conn_str = f'DRIVER={mssql_driver};SERVER={mssql_server};PORT={mssql_port};DATABASE={mssql_db};UID={mssql_user};PWD={mssql_password};Encrypt={mssql_encrypt};TrustServerCertificate={mssql_trust_cert};TDS_Version=7.4'
        conn = pyodbc.connect(conn_str)
        return conn


def connect_to_mysql():
    return pymysql.connect(
        host=mysql_server,
        user=mysql_user,
        password=mysql_password
    )