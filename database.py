import pymssql
import pymysql
import config


def connect_to_mssql():
    return pymssql.connect(
        server=config.mssql_server,
        database=config.mssql_db,
        user=config.mssql_user,
        password=config.mssql_password,
        port=1433
    )


def connect_to_mysql():
    return pymysql.connect(
        host=config.mysql_server,
        user=config.mysql_user,
        password=config.mysql_password,
        database=config.mysql_database
    )

