import json
from socket import *

HOST = '127.0.0.1'
PORT = 12345
ADDR = (HOST, PORT)

client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect(ADDR)

print('Connected to: ', ADDR)

while True:
    msg = input('Send data to server: ')

    if msg == 'exit':
        client_socket.close()
        print('Client is close!')
        break

    elif msg:
        if msg == 'reg':
            login = str(input('Login: '))
            password = str(input('Password: '))
            nickname = str(input('Nickname: '))
            email = str(input('Email: '))
            json_data = json.dumps({'main': 'reg',
                                    'login': login,
                                    'password': password,
                                    'nickname': nickname,
                                    'email': email})
            client_socket.send(bytes(json_data.encode('utf-8')))

        elif msg == 'log':
            login = str(input('Login: '))
            password = str(input('Password: '))
            json_data = json.dumps({'main': 'log',
                                    'login': login,
                                    'password': password})
            client_socket.send(bytes(json_data.encode('utf-8')))

        elif msg == 'act':
            json_data = json.dumps({'main': 'act'})
            client_socket.send(bytes(json_data.encode('utf-8')))

        else:
            client_socket.send(msg.encode('utf-8'))

        print(client_socket.recv(1024).decode('utf-8'))
