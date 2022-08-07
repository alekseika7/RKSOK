import asyncio

from config import CONTROL_SERVER_HOST, CONTROL_SERVER_PORT, ENCODING
from exceptions import IncorrectHostError, IncorrectPortError
from models.models import ControlServerConf, ControlServerResponse
from service.data_reader import read_data_with_timeout
from service.logger import logger
from utils import check_host_port

CONTROL_SERVER_CONF = ControlServerConf(
    host=CONTROL_SERVER_HOST,
    port=CONTROL_SERVER_PORT,
    ask_command='АМОЖНА?',
    protocol='РКСОК/1.0',
    responses=ControlServerResponse(yes='МОЖНА', no='НИЛЬЗЯ')
)


async def get_control_server_response(server_conf: ControlServerConf, request: str) -> str:
    """
    Sends permission request to the control server, then reads response.
    If host and port of the control server are incorrect function will return empty string.
    """
    try:
        check_host_port(host=server_conf.host, port=server_conf.port)
    except (IncorrectHostError, IncorrectPortError) as connection_data_error:
        logger.error(f'Exception during checking host and port of the control server: {connection_data_error}')
        return ""
    reader, writer = await asyncio.open_connection(host=server_conf.host, port=server_conf.port)
    writer.write(f'{server_conf.ask_command} {server_conf.protocol}\r\n{request}'.encode(encoding=ENCODING))
    await writer.drain()

    response = await read_data_with_timeout(reader=reader)

    writer.close()
    await writer.wait_closed()

    logger.info(f'Control server response: {response}')
    return response
