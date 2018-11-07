import json
# import logging
import trio
import trio_mysql

HOST = '0.0.0.0'
PORT = 12345
BUF_SIZE = 2048

DB_LOGIN = 'root'
DB_PASSWORD = 'root'
DB_HOST = 'localhost'
DB_NAME = 'game'
DB_CHARSET = 'utf8mb4'

connection = trio_mysql.connect(host=DB_HOST,
                                user=DB_LOGIN,
                                password=DB_PASSWORD,
                                db=DB_NAME,
                                charset=DB_CHARSET,
                                cursorclass=trio_mysql.cursors.DictCursor)

# FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
# logging.basicConfig(format=FORMAT, filename='logs.log')


async def action(server_stream, data):
    # Вход: логин, пароль, объект взаимодействия и само действие
    # Выход: в случае успеха, отослать клиенту сообщение успешной операции
    await server_stream.send_all(b'Server do the action')


async def login(server_stream, data):
    # Вход: логин, пароль
    # Выход: в случае успеха отсылает клиенту данные из БД
    await server_stream.send_all(b'Login to the server')


async def registration(server_stream, data):
    # Вход: логин, пароль, ник, эмейл, номер тел.
    # Выход: ответ клиенту
    async with connection as conn:
        async with conn.cursor() as cursor:
            # Create a new record
            sql = "INSERT INTO 'Users' ('login', 'password, 'nickname', 'email') VALUES (%s, %s, %s, %s)"
            await cursor.execute(sql, (data['login'], data['password'], data['nickname'], data['email']))
        # connection is not autocommit by default. So you must commit to save
        # your changes.
        conn.commit()
        await server_stream.send_all(b'Registration is successful')


async def text_filter(text):
    """ text filter of client data for protection DB """
    pass


async def parse_client_data(server_stream, data):
    """ testing function to parse client data with JSON """
    client_data = json.loads(data)
    if client_data['main'] == 'action':
        await action(server_stream, client_data)
    elif client_data['main'] == 'login':
        await login(server_stream, client_data)
    elif client_data['main'] == 'registration':
        await registration(server_stream, client_data)


async def core_server(server_stream):
    # logging.info("server : new connection started")
    print("server : new connection started")
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
