import json
# import logging
import re
import secrets
import trio
import trio_mysql.cursors

HOST = '0.0.0.0'
PORT = 12345
BUF_SIZE = 2048

TOKENS = {}

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

# FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
# logging.basicConfig(format=FORMAT, filename='logs.log')


async def action(server_stream, data, token):
    # Вход: токен, объект взаимодействия и само действие
    # Выход: в случае успеха, отослать клиенту сообщение успешной операции
    async with connection as conn:
        async with conn.cursor() as cursor:
            # Create a new record
            sql = "UPDATE users SET updated=now() WHERE email = %s"
            await cursor.execute(sql, (data['email']))
            # connection is not autocommit by default. So you must commit to save
            # your changes.
            await conn.commit()
        await server_stream.send_all(b'Server do the action')


async def get_token():
    pass


async def generate_token(key):
    id_key = key['id']
    TOKENS[id_key] = secrets.token_urlsafe(16)
    print(TOKENS[id_key])
    return TOKENS[id_key]


async def login(server_stream, data):
    # Вход: логин, пароль
    # Выход: в случае успеха отсылает клиенту данные из БД и выдает временный токен.
    async with connection as conn:
        async with conn.cursor() as cursor:
            # Read a single record
            sql = "SELECT id FROM users WHERE email = %s and password = %s"
            await cursor.execute(sql, (data['email'], data['password']))
            result = await cursor.fetchone()
            if result is None:
                await server_stream.send_all(None)
            else:
                token = await generate_token(result)
                await server_stream.send_all(bytes(token.encode('utf-8')))


async def registration(server_stream, data):
    # Вход: логин, пароль, ник, эмейл, номер тел.
    # Выход: ответ клиенту
    async with connection as conn:
        async with conn.cursor() as cursor:
            # Create a new record
            sql = "INSERT INTO users (email, password, nickname) VALUES (%s, %s, %s)"
            await cursor.execute(sql, (data['email'], data['password'], data['nickname']))
            # connection is not autocommit by default. So you must commit to save
            # your changes.
            await conn.commit()
        await server_stream.send_all(b'Registration is successful')


async def parse_client_data(server_stream, data):
    """ testing function to parse client data with JSON """
    client_data = json.loads(data)
    if client_data['main'] == 'act':
        await action(server_stream, client_data)
    elif client_data['main'] == 'log':
        await login(server_stream, client_data)
    elif client_data['main'] == 'reg':
        await registration(server_stream, client_data)
    else:
        await server_stream.send_all(b'Wrong request!')


async def core_server(server_stream):
    # logging.info("server : new connection started")
    print("server : new connection started")
    print(TOKENS)
    try:
        while True:
            data = await server_stream.receive_some(BUF_SIZE)
            print("server : received data {}".format(data))
            if not data:
                print("server : connection closed")
                return
            await parse_client_data(server_stream, data)
    except Exception as exc:
        print("server : crashed: {} ".format(exc))


async def main():
    try:
        await trio.serve_tcp(core_server, PORT, host=HOST)
    except KeyboardInterrupt:
        print('Server was stopped! CTRL + C')

trio.run(main)
