# database.py
import pymysql
import pyodbc
import config


def connect_to_mssql():
        conn_str = 'DRIVER={FreeTDS};SERVER='+config.mssql_server+';PORT=1433;DATABASE='+config.mssql_db+';UID='+config.mssql_user+';PWD='+config.mssql_password+';TDS_Version=7.4'
        conn = pyodbc.connect(conn_str)
        return conn


def connect_to_mysql():
    return pymysql.connect(
        host=config.mysql_server,
        user=config.mysql_user,
        password=config.mysql_password,
        database=config.mysql_database
    )