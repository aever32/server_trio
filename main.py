import json
import trio

HOST = '0.0.0.0'
PORT = 12345
BUF_SIZE = 2048


async def action(server_stream):
    await server_stream.send_all(b'Server do the action')


async def login(server_stream):
    await server_stream.send_all(b'Login to the server')


async def registration(server_stream):
    await server_stream.send_all(b'Registration on the server')


async def parse_client_data(server_stream, data):
    """ testing function to parse client data with JSON """

    client_data = json.loads(data)
    if client_data['main'] == 'action':
        await action(server_stream)
    elif client_data['main'] == 'login':
        await login(server_stream)
    elif client_data['main'] == 'registration':
        await registration(server_stream)
    # else:
    #     await server_stream.send_all(b'!EXIT!')


async def core_server(server_stream):
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
