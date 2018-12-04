import trio_mysql.cursors

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "root",
    "database": "game",
    "charset": "utf8mb4",
    "cursorclass": trio_mysql.cursors.DictCursor,
}

connection = trio_mysql.connect(**DB_CONFIG)


async def execute(cursor, command, arguments):
    try:
        await cursor.execute(command, arguments)
        result = await cursor.fetchall()
    except trio_mysql.err.MySQLError as error:
        print('error in MYSQL execute: {}'.format(error))
        result = None
    return result


async def sql(command, arguments=None):
    async with connection as conn:
        async with conn.cursor() as cursor:
            result = await execute(cursor, command, arguments)
            # FIXME временная заплатка для записи в БД
            # Нужно добавить автокомит или разобраться с ТРАНЗАКЦИЯМИ!
            # Соединение не автокомитится по умолчанию.
            # Поэтому нужно сделать комит для сохранения данных в БД
            await conn.commit()
            return result
