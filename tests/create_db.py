import trio
import trio_mysql.cursors

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "root",
    "charset": "utf8mb4",
    "autocommit": "True",
}

connection = trio_mysql.connect(**DB_CONFIG)


async def main():
    async with connection as conn:
        async with conn.cursor() as cursor:
            try:
                sql_1 = """
                            CREATE DATABASE IF NOT EXISTS game;
                            """
                sql_2 = """
                            USE game;
                            """
                sql_3 = """ 
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
                await cursor.execute(sql_1)
                await cursor.execute(sql_2)
                await cursor.execute(sql_3)

            except trio_mysql.err.MySQLError as err:
                print("Failed: {}".format(err))
                exit(1)

trio.run(main)
