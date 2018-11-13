import json
from socket import *

HOST = '127.0.0.1'
PORT = 12345
ADDR = (HOST, PORT)
BUFFER = 1024

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
            email = str(input('Email: '))
            password = str(input('Password: '))
            nickname = str(input('Nickname: '))
            json_data = json.dumps({'main': 'reg',
                                    'email': email,
                                    'password': password,
                                    'nickname': nickname,
                                    })
            client_socket.send(bytes(json_data.encode('utf-8')))

        elif msg == 'log':
            email = str(input('Email: '))
            password = str(input('Password: '))
            json_data = json.dumps({'main': 'log',
                                    'email': email,
                                    'password': password})
            client_socket.send(bytes(json_data.encode('utf-8')))

        elif msg == 'act':
            token = str(input('Token: '))
            json_data = json.dumps({'mail': 'act',
                                    'token': token})
            client_socket.send(bytes(json_data.encode('utf-8')))

        else:
            client_socket.send(msg.encode('utf-8'))

        print(client_socket.recv(BUFFER).decode('utf-8'))
