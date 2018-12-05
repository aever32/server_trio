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
    await cursor.execute(command, arguments)
    try:
        result = await cursor.fetchall()
    except trio_mysql.err.ProgrammingError as error:
        print('error in MYSQL execute: {}'.format(error))
        result = None
    return result


async def sql(command, arguments=None):
    async with connection() as conn:
        async with conn.cursor() as cursor:
            result = await execute(cursor, command, arguments)
            # FIXME временная заплатка для записи в БД
            # Нужно добавить автокомит или разобраться с ТРАНЗАКЦИЯМИ!
            # Соединение не автокомитится по умолчанию.
            # Поэтому нужно использовать комит для сохранения данных в БД
            await conn.commit()
            return result


async def transaction(callback, arguments):
    async with connection as conn:
        async with conn.cursor() as cursor:

            await cursor.execute('BEGIN')

            try:
                result = await callback(arguments=arguments,
                                        execute=lambda command, arguments=None: execute(cursor, command, arguments))
            except BaseException:
                await cursor.execute('ROLLBACK')
                raise
            else:
                await cursor.execute('COMMIT')
            return result
