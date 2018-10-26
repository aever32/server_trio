import trio

HOST = '0.0.0.0'
PORT = 12345
BUF_SIZE = 2048


async def id_for_client(data):
    pass


async def echo_server(server_stream):
    print("echo_server : new connection started")
    try:
        while True:
            data = await server_stream.receive_some(BUF_SIZE)
            print("echo_server : received data {}".format(data))
            if not data:
                print("echo_server : connection closed")
                return
            await id_for_client(data)
            print("echo_server : sending data {}" . format(data))
            await server_stream.send_all(data)
    except Exception as exc:
        print("echo_server : crashed: {} ".format(exc))


async def main():
    await trio.serve_tcp(echo_server, PORT, host=HOST)

trio.run(main)
