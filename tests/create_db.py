import mysql.connector

connection = mysql.connector.connect(user='root',
                                     password='root',
                                     host='127.0.0.1',
                                     charset='utf8mb4')
cursor = connection.cursor()

try:
    sql_1 = """
                CREATE DATABASE IF NOT EXISTS game;
                """
    sql_2 = """
                USE game;
                CREATE TABLE IF NOT EXISTS users (
                id int unsigned PRIMARY KEY AUTO_INCREMENT,
                email varchar(128) NOT NULL UNIQUE KEY,
                password char(64) NOT NULL,
                nickname varchar(30) NOT NULL UNIQUE KEY,
                phone_num varchar(15) NULL UNIQUE KEY,
                created TIMESTAMP NOT NULL Default CURRENT_TIMESTAMP,
                updated TIMESTAMP NOT NULL Default CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                );
                """
    cursor.execute(sql_1)
    cursor.execute(sql_2)

except mysql.connector.Error as err:
    print("Failed: {}".format(err))
    exit(1)

cursor.close()
connection.close()
