import mysql.connector

connection = mysql.connector.connect(user='root',
                                     password='root',
                                     host='127.0.0.1')
cursor = connection.cursor()

try:
    create_db = """
                CREATE DATABASE IF NOT EXISTS game;
                USE game;
                CREATE TABLE IF NOT EXISTS users (
                id int(11) unsigned PRIMARY KEY AUTO_INCREMENT,
                email varchar(255) NOT NULL UNIQUE KEY,
                password char(64) NOT NULL,
                nickname varchar(30) NOT NULL UNIQUE KEY,
                phone_num varchar(15) UNIQUE KEY,
                created TIMESTAMP NOT NULL Default CURRENT_TIMESTAMP,
                updated TIMESTAMP NOT NULL Default CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                );"""
    cursor.execute(create_db)

except mysql.connector.Error as err:
    print("Failed: {}".format(err))
    exit(1)

cursor.close()
connection.close()
