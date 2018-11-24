import hashlib
import json
# import logging
# import re
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


async def clean_registration(data: dict) -> bool:
    email_len = len(data['email'])
    print(email_len)
    password_len = len(data['password'])
    nickname_len = len(data['nickname'])
    if (10 <= email_len <= 50) and (6 <= password_len <= 30) and (3 <= nickname_len <= 20):
        return True
    else:
        return False


async def clean_login(data: dict) -> bool:
    pass


async def clean_action(data: dict) -> bool:
    pass


async def filter_client_data(data: dict):
    if data['client'] == 'act':
        print('test ACT')
        return True
    elif data['client'] == 'reg':
        print('test REG')
        return await clean_registration(data)
    elif data['client'] == 'log':
        print('test LOG')
        return True
    else:
        return False


async def get_hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


async def compare_password(hashed_password: str, user_password: str) -> bool:
    return hashed_password == hashlib.sha256(user_password.encode('utf-8')).hexdigest()


async def generate_token(db_user_id: dict) -> dict:
    id_key = db_user_id['id']
    TOKENS[id_key] = secrets.token_urlsafe(16)
    token = {'server': 'login', 'id': id_key, 'token': TOKENS[id_key]}
    return token


async def send_json_to_client(server_stream, data: dict):
    json_data = json.dumps(data)
    await server_stream.send_all(bytes(json_data.encode('utf-8')))


async def action(server_stream, data: dict):
    async with connection as conn:
        async with conn.cursor() as cursor:
            sql = "UPDATE users SET updated=now() WHERE email = %s"
            await cursor.execute(sql, (data['email']))
            await conn.commit()
            await server_stream.send_all(b'Server do the action')


async def login(server_stream, data: dict):
    async with connection as conn:
        async with conn.cursor() as cursor:
            sql = "SELECT id FROM users WHERE email = %s and password = %s"
            await cursor.execute(sql, (data['email'], await get_hash_password(data['password'])))
            user_id = await cursor.fetchone()
            if user_id is None:
                await server_stream.send_all(b'LOGIN ERROR')
            else:
                token = await generate_token(user_id)
                await send_json_to_client(server_stream, token)


async def registration(server_stream, data: dict):
    async with connection as conn:
        async with conn.cursor() as cursor:
            sql = "INSERT IGNORE INTO users (email, password, nickname) VALUES (%s, %s, %s)"
            await cursor.execute(sql, (data['email'], await get_hash_password(data['password']), data['nickname']))
            # connection is not autocommit by default. So you must commit to save
            # your changes.
            await conn.commit()
            sql2 = "show warnings"
            if await cursor.execute(sql2):
                result = {'result': 'failed'}
                await send_json_to_client(server_stream, result)
            else:
                result = {'result': 'success'}
                await send_json_to_client(server_stream, result)


async def parse_client_data(server_stream, data: bytes):
    client_data = json.loads(data)
    clean_data = await filter_client_data(client_data)
    if clean_data:
        if client_data['client'] == 'act':
            await action(server_stream, client_data)
        elif client_data['client'] == 'log':
            await login(server_stream, client_data)
        elif client_data['client'] == 'reg':
            await registration(server_stream, client_data)
        else:
            await server_stream.send_all(b'Wrong client request!')
    else:
        await server_stream.send_all(b'Not clean data!')


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
