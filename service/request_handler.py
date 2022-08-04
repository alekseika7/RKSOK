import asyncio
from asyncio import StreamReader, TimeoutError
import re
from typing import Optional, Type

from config import CLIENT_REQUEST_TIMEOUT, COMMAND_EXEC_TIMEOUT, READ_BLOCK_SIZE, REQUEST_END
from exceptions import (
    CanNotParseRequestError,
    CommandExecTimeoutError,
    ReadTimeoutError,
    RequestCheckBaseException,
    UnknownControlServerResponseError,
)
from service.logger import logger
from models.models import RequestData, ControlServerConf
from service.db import RKSOKDatabaseClient
from service.protocols import RKSOKProtocol


async def _read_data(reader: StreamReader, block_size: int, separator: str) -> str:
    """Reads data from the stream until '\r\n\r\n' or eof"""
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
    """Reads data from the stream assuming timeout"""
    try:
        request = await asyncio.wait_for(
            _read_data(reader=reader, block_size=block_size, separator=separator), timeout=timeout
        )
    except TimeoutError:
        raise ReadTimeoutError(f'Timeout exceeded while reading! Current {timeout=}')

    return request


def _parse_request(request: str) -> RequestData:
    """
    Parses raw client request and returns request parts.
    If there is no option to parse data it will raise CanNotParseRequestError.
    """
    request_parts = request.rstrip(REQUEST_END).split('\r\n', 1)
    pattern = re.compile(r'(\S+) (.+) (\S+)')
    found_matches = re.findall(pattern, request_parts[0])

    is_valid_request = len(found_matches) > 0
    if is_valid_request:
        found_matches = found_matches[0]
        is_valid_request = len(found_matches) == 3

    if not is_valid_request:
        raise CanNotParseRequestError(
            r'Unknown request format! Server expects:\n<COMMAND> <name> <PROTOCOL>\r\n<value>\r\n\r\n'
        )
    value = None
    if len(request_parts) == 2:
        value = request_parts[1]

    return RequestData(
        command=found_matches[0],
        name=found_matches[1],
        protocol=found_matches[2],
        value=value,
    )


async def _get_control_server_permission(control_server: ControlServerConf, request: str) -> str:
    """Sends permission request to the control server, then reads response."""
    reader, writer = await asyncio.open_connection(host=control_server.host, port=control_server.port)
    writer.write(f'{control_server.ask_command} {control_server.protocol}\r\n{request}'.encode())
    await writer.drain()

    response = await read_data_with_timeout(reader=reader)

    writer.close()
    await writer.wait_closed()

    return response


async def process_client_request(
        request: str,
        db_client: RKSOKDatabaseClient,
        control_server_conf: ControlServerConf,
        rksok_type: Type[RKSOKProtocol],
) -> str:
    """
    Takes raw request and database client, parses request parts and checks their correctness,
    performs interactions with the control server, processes request with timeout and returns response to the client.
    """
    try:
        parsed_request = _parse_request(request=request)
        rksok = rksok_type(db_client=db_client, request_data=parsed_request)
    except (CanNotParseRequestError, RequestCheckBaseException) as parsing_error:
        logger.error(f'Exception happened: {parsing_error}')
        return f'{rksok_type.configuration.response_names.incorrect} {rksok_type.configuration.protocol}{REQUEST_END}'

    control_server_response = await _get_control_server_permission(control_server=control_server_conf, request=request)
    logger.info(f'Control server response: {control_server_response}')
    if control_server_response.startswith(control_server_conf.responses.no):
        return control_server_response
    elif not control_server_response.startswith(control_server_conf.responses.yes):
        raise UnknownControlServerResponseError(
            f'Unknown response! Available variants:\n{control_server_conf.responses.yes}, '
            f'{control_server_conf.responses.no}'
        )

    try:
        response = await asyncio.wait_for(rksok.process_request(), timeout=COMMAND_EXEC_TIMEOUT)
    except asyncio.TimeoutError:
        raise CommandExecTimeoutError(
            f'Exceeded timeout while reading! Current timeout: {COMMAND_EXEC_TIMEOUT} seconds.'
        )
    return response
