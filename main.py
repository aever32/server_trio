import hashlib
import json
# import logging
import secrets
import trio
from mysql_db import (sql, transaction)
from check_client_data import (clean_registration, clean_login, clean_action)

HOST = '0.0.0.0'
PORT = 12345
BUF_SIZE = 2048

# Глобальный словарь {id пользователя: токен}
TOKENS = dict()

# FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
# logging.basicConfig(format=FORMAT, filename='logs.log')


# Генерация хэш пароля
async def get_hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


# Сравнение хэш пароля
# Пока нигде не используется, нужна ли она вообще?!
async def compare_password(hashed_password: str, user_password: str) -> bool:
    return hashed_password == hashlib.sha256(user_password.encode('utf-8')).hexdigest()


# Генерация токена
async def generate_token(db_user_id: list) -> dict:
    id_key = db_user_id[0]['id']
    TOKENS[id_key] = secrets.token_urlsafe(16)
    token = {'server': 'login', 'id': id_key, 'token': TOKENS[id_key]}
    return token


# Интерфейс для отправки json клиенту
async def send_json_to_client(server_stream, data: dict):
    json_data = json.dumps(data)
    await server_stream.send_all(bytes(json_data.encode('utf-8')))


# Основное действие клиента
async def action(server_stream, data: dict):
    # Проверка данных на чистоту, если всё в порядке продолжаем пользовательское действие
    result = await clean_action(data)
    if result['result'] == 'true':
        # временная вставка if, просто для теста
        if not data.get('email'):
            result = {'result': 'it`s alive!'}
            await send_json_to_client(server_stream, result)
        else:
            query = "UPDATE users SET updated=now() WHERE email = %s"
            # Делаем запрос в БД
            await sql(query, (data['email']))
            result = {'result': 'server do the action'}
            await send_json_to_client(server_stream, result)
    else:
        # Иначе отправляются данные с объяснениями клиенту об ошибке.
        await send_json_to_client(server_stream, result)


# Пример функции с нужными запросами внутри транзакции
async def do_in_transaction(execute, arguments):
    my_arg0 = arguments[0]
    my_arg1 = arguments[1]
    my_arg2 = arguments[2]
    try:
        result = await execute("INSERT INTO users (email, password, nickname) VALUES (%s, %s, %s)",
                               (my_arg0, my_arg1, my_arg2))
        print('Result 1 inside do_in_transaction() ->', result)
        result = await execute("SELECT nickname FROM users")
        print('Result 2 inside do_in_transaction() ->', result)
        result = await execute("INSERT INTO users (email, password, nickname) VALUES ('a@q.ru', 'pas12345', 'name0')")
        print('Result 3 inside do_in_transaction() ->', result)
    except BaseException as err:
        print('INSIDE do_in_trans -> ', err)


# Аутентификация пользователя и генерация токена
async def login(server_stream, data: dict):
    # Проверка данных на чистоту, если всё в порядке продолжаем аутентификацию
    result = await clean_login(data)
    if result['result'] == 'true':
        arguments = ('www@mail.com', 'data123', 'test345')
        # FIXME Пример использования функции транзакции, удалю при следующем коммите.
        # Для запуска этого примера, просто введи на клиенте команду: log с любым email и password
        result = await transaction(do_in_transaction, arguments)
        print('РЕЗУЛЬТАТ ПОСЛЕ transaction()! ->', result)
        query = "SELECT id FROM users WHERE email = %s and password = %s"
        # Делаем запрос в БД и получаем результат
        user_id = await sql(query,
                            (data['email'], await get_hash_password(data['password'])))
        if user_id:
            token = await generate_token(user_id)
            await send_json_to_client(server_stream, token)
        else:
            result = {'result': 'login error'}
            await send_json_to_client(server_stream, result)
    else:
        # Иначе отправляются данные с объяснениями клиенту об ошибке.
        await send_json_to_client(server_stream, result)


# Регистрация нового пользователя
async def registration(server_stream, data: dict):
    # Проверка данных на чистоту, если всё в порядке продолжаем регистрацию
    result = await clean_registration(data)
    if result['result'] == 'true':
        query = "SELECT id FROM users WHERE email = %s or nickname = %s"
        # Делаем запрос в БД и получаем результат
        user_exist = await sql(query,
                               (data['email'], data['nickname']))
        if user_exist:
            result = {'result': 'user already exist'}
            await send_json_to_client(server_stream, result)
        else:
            query = "INSERT INTO users (email, password, nickname) VALUES (%s, %s, %s)"
            result = await sql(query,
                               (data['email'], await get_hash_password(data['password']), data['nickname']))
            if not result:
                result = {'result': 'registration is successful'}
                await send_json_to_client(server_stream, result)
    else:
        # Иначе отправляются данные с объяснениями клиенту об ошибке.
        await send_json_to_client(server_stream, result)


# Интерфейс для обработки данных от клиента
async def parse_client_data(server_stream, data: bytes):
    try:
        client_data = json.loads(data)
        if client_data['client'] == 'act':
            await action(server_stream, client_data)
        elif client_data['client'] == 'log':
            await login(server_stream, client_data)
        elif client_data['client'] == 'reg':
            await registration(server_stream, client_data)
        else:
            result = {'result': 'wrong data in main field'}
            await send_json_to_client(server_stream, result)
    except ValueError as e:
        print(e)
        await send_json_to_client(server_stream, {'result': 'error input data'})


# Получение данных от клиента
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


# Ожидание подключения новых клиентов.
async def main():
    try:
        await trio.serve_tcp(core_server, PORT, host=HOST)
    except KeyboardInterrupt:
        print('Server was stopped! CTRL + C')

# Запуск главного цикла программы
trio.run(main)
