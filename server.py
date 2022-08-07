import asyncio

from config import SERVER_HOST, SERVER_PORT, ENCODING
from exceptions import IncorrectHostError, IncorrectPortError, ServerBaseException
from service.data_reader import read_data_with_timeout
from service.db import RKSOKMongoClient
from service.logger import logger
from service.request_handler import process_client_request
from utils import check_host_port


async def process_request(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    """Callback for asyncio streams server."""
    mongo_client = RKSOKMongoClient()
    try:
        client_address = writer.get_extra_info('peername')
        logger.debug(f'New connection from {client_address!r}')
        request = await read_data_with_timeout(reader=reader)
        logger.info(f'Received {request!r} from {client_address!r}')

        await mongo_client.connect_to_db(user_id=client_address[0])
        logger.debug('Starting request processing...')
        response = await process_client_request(request=request, db_client=mongo_client)
        logger.info(f'Send {response!r} to {client_address!r}')
    except ServerBaseException as server_exception:
        logger.error(f'Exception happened: {server_exception}')
    else:
        writer.write(response.encode(encoding=ENCODING))
        await writer.drain()
    finally:
        logger.debug(f'Close the connection to {client_address!r}')
        writer.close()


async def main() -> None:
    try:
        check_host_port(host=SERVER_HOST, port=SERVER_PORT)
    except (IncorrectHostError, IncorrectPortError) as connection_data_error:
        logger.error(f'Exception during checking host and port of the server: {connection_data_error}')
        raise KeyboardInterrupt
    server = await asyncio.start_server(client_connected_cb=process_request, host=SERVER_HOST, port=int(SERVER_PORT))
    logger.debug(f'Started RKSOK server on {SERVER_HOST}:{SERVER_PORT}')
    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('Interrupting server...')
        logger.debug('RKSOK server stopped working.')
