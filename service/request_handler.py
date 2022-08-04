import asyncio
from asyncio import StreamReader, TimeoutError
import re
from typing import Optional

from config import (
    CLIENT_REQUEST_TIMEOUT,
    COMMAND_EXEC_TIMEOUT,
    CONTROL_SERVER_HOST,
    CONTROL_SERVER_PORT,
    READ_BLOCK_SIZE,
    REQUEST_END,
)
from service.db import RKSOKDatabaseClient
from exceptions import (
    CanNotParseRequestError,
    CommandExecTimeoutError,
    ReadTimeoutError,
    RequestCheckBaseException,
    UnknownControlServerResponseError,
)
from models.models import RequestData, ControlServerConf, ControlServerResponse
from service.protocols import RKSOKProtocolFirstVersion


async def read_data(reader: StreamReader, block_size: int, separator: str) -> str:
    """"""
    request = b''
    separator_bytes = separator.encode()
    while True:
        next_block = await reader.read(block_size)
        request += next_block
        if not next_block or next_block.endswith(separator_bytes):
            return request.decode()


async def read_data_with_timeout(
    reader: StreamReader,
    block_size: Optional[int] = READ_BLOCK_SIZE,
    separator: Optional[str] = REQUEST_END,
    timeout: Optional[int] = CLIENT_REQUEST_TIMEOUT,
) -> str:
    """"""
    try:
        request = await asyncio.wait_for(
            read_data(reader=reader, block_size=block_size, separator=separator), timeout=timeout
        )
    except TimeoutError:
        raise ReadTimeoutError(f'Timeout exceeded while reading! Current {timeout=}')

    return request


def _parse_request(request: str) -> RequestData:
    """
    Parses client request and returns request parts.
    If there is no option to parse data it will raise the CanNotParseRequestError.
    """
    request_parts = request.rstrip(REQUEST_END).split('\r\n', 1)
    found_patterns = re.findall(r'(\S+) (.+) (\S+)', request_parts[0])
    is_valid_request = len(found_patterns) > 0
    if is_valid_request:
        found_patterns = found_patterns[0]
        is_valid_request = len(found_patterns) == 3

    if not is_valid_request:
        raise CanNotParseRequestError(
            r'Unknown request format! Server expects:\n<COMMAND> <name> <PROTOCOL>\r\n<value>\r\n\r\n'
        )

    value = None
    if len(request_parts) == 2:
        value = request_parts[1]

    return RequestData(
        command=found_patterns[0],
        name=found_patterns[1],
        protocol=found_patterns[2],
        value=value,
    )


async def _get_control_server_permission(control_server: ControlServerConf, request: str) -> str:
    """"""
    reader, writer = await asyncio.open_connection(host=control_server.host, port=control_server.port)
    writer.write(f'{control_server.ask_command} {control_server.protocol}\r\n{request}'.encode())
    await writer.drain()

    response = await read_data_with_timeout(reader=reader)

    writer.close()
    await writer.wait_closed()

    return response


async def process_client_request(request: str, db_client: RKSOKDatabaseClient) -> str:
    """"""
    rksok_type = RKSOKProtocolFirstVersion
    response_incorrect = (
        rksok_type.configuration.response_names.incorrect +
        ' ' +
        rksok_type.configuration.protocol +
        REQUEST_END
    )
    try:
        parsed_request = _parse_request(request=request)
        rksok = rksok_type(db_client=db_client, request_data=parsed_request)
    except (CanNotParseRequestError, RequestCheckBaseException) as parsing_error:
        return response_incorrect

    control_server = ControlServerConf(
        host=CONTROL_SERVER_HOST,
        port=CONTROL_SERVER_PORT,
        ask_command='АМОЖНА?',
        protocol=parsed_request.protocol,
        responses=ControlServerResponse(yes='МОЖНА', no='НИЛЬЗЯ')
    )
    control_server_response = await _get_control_server_permission(control_server=control_server, request=request)
    if control_server_response.startswith(control_server.responses.no):
        return control_server_response
    elif not control_server_response.startswith(control_server.responses.yes):
        raise UnknownControlServerResponseError(
            f'Unknown response! Available variants:\n{control_server.responses.yes}, {control_server.responses.no}')

    try:
        response = await asyncio.wait_for(
            rksok.process_request(), timeout=COMMAND_EXEC_TIMEOUT
        )
    except asyncio.TimeoutError:
        raise CommandExecTimeoutError(
            f'Exceeded timeout while reading! Current timeout: {COMMAND_EXEC_TIMEOUT} seconds.'
        )
    return response
