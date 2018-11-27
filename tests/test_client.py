import json
from socket import *

HOST = '127.0.0.1'
PORT = 12345
ADDR = (HOST, PORT)
BUFFER = 1024

TOKEN = {}

client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect(ADDR)

print('Connected to: ', ADDR)


def parse_token(json_data: dict):
    TOKEN['id'] = json_data['id']
    TOKEN['token'] = json_data['token']


def parse_data_from_server(server_data):
    try:
        json_data = json.loads(server_data)
        print(json_data)
        if json_data['server'] == 'login':
            parse_token(json_data)
    except ValueError:
        print(server_data)
    except KeyError:
        pass


def main():
    while True:
        print('reg - регистрация')
        print('log - вход')
        print('act - действие')
        print('exit - выход')
        msg = input('Введите требуемое значение:')

        if msg == 'exit':
            client_socket.close()
            print('Client is close!')
            break

        elif msg:
            if msg == 'reg':
                email = str(input('Введите ваш Email минимум 10 символов: '))
                password = str(input('Password от 6 до 30 символов: '))
                nickname = str(input('Nickname от 3 до 20 символов: '))
                json_data = json.dumps({'client': 'reg',
                                        'email': email,
                                        'password': password,
                                        'nickname': nickname,
                                        })
                client_socket.send(bytes(json_data.encode('utf-8')))

            elif msg == 'log':
                email = str(input('Email: '))
                password = str(input('Password: '))
                json_data = json.dumps({'client': 'log',
                                        'email': email,
                                        'password': password})
                client_socket.send(bytes(json_data.encode('utf-8')))

            elif msg == 'act':
                obj = str(input('Object: '))
                action = str(input('Action: '))
                id_token = TOKEN['id']
                token = TOKEN['token']
                json_data = json.dumps({'client': 'act',
                                        'id': id_token,
                                        'token': token,
                                        'object': obj,
                                        'action': action})
                client_socket.send(bytes(json_data.encode('utf-8')))

            else:
                client_socket.send(msg.encode('utf-8'))

        server_data = client_socket.recv(BUFFER)
        parse_data_from_server(server_data)


if __name__ == '__main__':
    main()
