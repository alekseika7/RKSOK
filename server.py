import asyncio
from asyncio import StreamReader, StreamWriter

from config import SERVER_HOST, SERVER_PORT
from exceptions import ServerBaseException
from service.db import RKSOKMongoClient
from service.request_handler import process_client_request, read_data_with_timeout


async def process_request(reader: StreamReader, writer: StreamWriter) -> None:
    """Callback for asyncio streams server."""
    try:
        client_address = writer.get_extra_info('peername')
        request = await read_data_with_timeout(reader=reader)
        print(f"Received {request!r} from {client_address!r}")

        db_client = RKSOKMongoClient()
        await db_client.connect_to_db(user_id=client_address[0])
        response = await process_client_request(request=request, db_client=db_client)
        print(f"Send: {response!r}")
    except ServerBaseException as server_exception:
        print(server_exception)
    else:
        writer.write(response.encode())
        await writer.drain()
    finally:
        print("Close the connection")
        writer.close()


async def main() -> None:
    server = await asyncio.start_server(client_connected_cb=process_request, host=SERVER_HOST, port=SERVER_PORT)
    print(f'Serving on {SERVER_HOST}:{SERVER_PORT}')
    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    asyncio.run(main())
