import json
import trio

HOST = '0.0.0.0'
PORT = 12345
BUF_SIZE = 2048


async def parse_client_data(server_stream, data):
    new_dict = data.decode('utf-8')
    new = json.loads(new_dict)
    if new['id'] == 3:
        await server_stream.send_all(b'Server do the registration')
    elif new['name'] == 'abc':
        await server_stream.send_all(b'Login to the server')
    else:
        await server_stream.send_all(b'!EXIT!')


async def core_server(server_stream):
    print("echo_server : new connection started")
    try:
        while True:
            data = await server_stream.receive_some(BUF_SIZE)
            print("echo_server : received data {}".format(data))
            if not data:
                print("echo_server : connection closed")
                return
            await parse_client_data(server_stream, data)
    except Exception as exc:
        print("echo_server : crashed: {} ".format(exc))


async def main():
    try:
        await trio.serve_tcp(core_server, PORT, host=HOST)
    except KeyboardInterrupt:
        print('Server was stopped! CTRL + C')

trio.run(main)
