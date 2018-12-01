import hashlib
import json
# import logging
import re
import secrets
import trio
import trio_mysql.cursors

HOST = '0.0.0.0'
PORT = 12345
BUF_SIZE = 2048

# Глобальный словарь {id пользователя: токен}
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


# Проверка блока регистрации
# FIXME Нужно доделать проверку блока регистрации
async def clean_registration(data: dict) -> dict:
    # проверка email по шаблону
    # шаблон Email
    pattern = re.compile('(^|\s)[-a-z0-9_.]+@([-a-z0-9]+\.)+[a-z]{2,6}(\s|$)')
    # Полученное с клиента значение
    address = data['email']
    # результат проверки
    is_valid = pattern.match(address)
    # email_len = len(data['email'])
    password_len = len(data['password'])
    nickname_len = len(data['nickname'])
    # Проверка длины данных пользователя
    if is_valid and (6 <= password_len <= 30) and (3 <= nickname_len <= 20):
        return {'flag': 'true'}
    else:
        return {'flag': 'false', 'result': 'email failed'}


# Проверка блока аутентификации
async def clean_login(data: dict) -> dict:
    # FIXME Нужно добавить проверку данных при аутентификации пользователя
    return {'flag': 'true'}


# Проверка блока действий
async def clean_action(data: dict) -> dict:
    # Сверка данных токена от пользователя с глобальным словарем токенов сервера
    if data['token'] == TOKENS.get(data['id']):
        return {'flag': 'true'}
    else:
        return {'flag': 'false'}


# Генерация хэш пароля
async def get_hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


# Сравнение хэш пароля
# Пока нигде не используется, нужна ли она вообще?!
async def compare_password(hashed_password: str, user_password: str) -> bool:
    return hashed_password == hashlib.sha256(user_password.encode('utf-8')).hexdigest()


# Генерация токена
async def generate_token(db_user_id: dict) -> dict:
    id_key = db_user_id['id']
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
    if result['flag'] == 'true':
        # временная вставка if, просто для теста
        if not data.get('email'):
            result = {'result': 'it`s alive!'}
            await send_json_to_client(server_stream, result)
        else:
            async with connection as conn:
                async with conn.cursor() as cursor:
                    sql = "UPDATE users SET updated=now() WHERE email = %s"
                    # Делаем запрос в БД
                    await cursor.execute(sql, (data['email']))
                    # Соединение не автокомитится по умолчанию.
                    # Поэтому нужно сделать комит для сохранения данных в БД
                    await conn.commit()
                    result = {'result': 'server do the action'}
                    await send_json_to_client(server_stream, result)
    else:
        # Иначе отправляются данные с объяснениями клиенту об ошибке.
        await send_json_to_client(server_stream, result)


# Аутентификация пользователя и генерация токена
async def login(server_stream, data: dict):
    # Проверка данных на чистоту, если всё в порядке продолжаем аутентификацию
    result = await clean_login(data)
    if result['flag'] == 'true':
        async with connection as conn:
            async with conn.cursor() as cursor:
                sql = "SELECT id FROM users WHERE email = %s and password = %s"
                # Делаем запрос в БД
                await cursor.execute(sql, (data['email'], await get_hash_password(data['password'])))
                # Получаем результат сделаного запроса
                user_id = await cursor.fetchone()
                if user_id is None:
                    await server_stream.send_all(b'LOGIN ERROR')
                else:
                    token = await generate_token(user_id)
                    await send_json_to_client(server_stream, token)
    else:
        # Иначе отправляются данные с объяснениями клиенту об ошибке.
        await send_json_to_client(server_stream, result)


# Регистрация нового пользователя
async def registration(server_stream, data: dict):
    # Проверка данных на чистоту, если всё в порядке продолжаем регистрацию
    result = await clean_registration(data)
    if result['flag'] == 'true':
        async with connection as conn:
            async with conn.cursor() as cursor:
                sql_check = "SELECT id FROM users WHERE email = %s or nickname = %s"
                # Делаем запрос в БД
                await cursor.execute(sql_check,
                                     (data['email'], data['nickname']))
                # Получаем результат сделаного запроса
                user_exist = await cursor.fetchone()
                if user_exist:
                    result = {'result': 'user exist'}
                    await send_json_to_client(server_stream, result)
                else:
                    sql_insert = "INSERT INTO users (email, password, nickname) VALUES (%s, %s, %s)"
                    # Делаем запрос в БД
                    await cursor.execute(sql_insert,
                                         (data['email'], await get_hash_password(data['password']), data['nickname']))
                    # Соединение не автокомитится по умолчанию.
                    # Поэтому нужно сделать комит для сохранения данных в БД
                    await conn.commit()
                    result = {'result': 'user is registered'}
                    await send_json_to_client(server_stream, result)
    else:
        # Иначе отправляются данные с объяснениями клиенту об ошибке.
        await send_json_to_client(server_stream, result)


# Интерфейс для обработки данных от клиента
async def parse_client_data(server_stream, data: bytes):
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
