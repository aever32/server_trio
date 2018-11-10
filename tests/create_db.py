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
                id int(10) unsigned PRIMARY KEY AUTO_INCREMENT,
                login char(20) NOT NULL UNIQUE KEY,
                password char(30) NOT NULL,
                nickname char(20) NOT NULL,
                email char(40) NOT NULL,
                updated TIMESTAMP NOT NULL,
                created TIMESTAMP NOT NULL 
                );"""
    cursor.execute(create_db)

except mysql.connector.Error as err:
    print("Failed: {}".format(err))
    exit(1)

cursor.close()
connection.close()
