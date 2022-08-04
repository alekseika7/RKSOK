import asyncio
from asyncio import StreamReader, StreamWriter

from config import SERVER_HOST, SERVER_PORT, CONTROL_SERVER_PORT, CONTROL_SERVER_HOST
from exceptions import ServerBaseException
from models.models import ControlServerConf, ControlServerResponse
from service.db import RKSOKMongoClient
from service.logger import logger
from service.protocols import RKSOKProtocolFirstVersion
from service.request_handler import process_client_request, read_data_with_timeout

mongo_client = RKSOKMongoClient()
control_server_conf = ControlServerConf(
    host=CONTROL_SERVER_HOST,
    port=CONTROL_SERVER_PORT,
    ask_command='АМОЖНА?',
    protocol='РКСОК/1.0',
    responses=ControlServerResponse(yes='МОЖНА', no='НИЛЬЗЯ')
)
RKSOK_type = RKSOKProtocolFirstVersion


async def process_request(reader: StreamReader, writer: StreamWriter) -> None:
    """Callback for asyncio streams server."""
    try:
        client_address = writer.get_extra_info('peername')
        logger.debug(f'New connection from {client_address!r}')
        request = await read_data_with_timeout(reader=reader)
        logger.info(f'Received {request!r} from {client_address!r}')

        await mongo_client.connect_to_db(user_id=client_address[0])
        logger.debug('Starting request processing...')
        response = await process_client_request(
            request=request,
            db_client=mongo_client,
            control_server_conf=control_server_conf,
            rksok_type=RKSOK_type,
        )
        logger.info(f'Send {response!r} to {client_address!r}')
    except ServerBaseException as server_exception:
        logger.error(f'Exception happened: {server_exception}')
    else:
        writer.write(response.encode())
        await writer.drain()
    finally:
        logger.debug(f'Close the connection to {client_address!r}')
        writer.close()


async def main() -> None:
    server = await asyncio.start_server(client_connected_cb=process_request, host=SERVER_HOST, port=SERVER_PORT)
    logger.debug(f'Started RKSOK server on {SERVER_HOST}:{SERVER_PORT}')
    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    asyncio.run(main())
