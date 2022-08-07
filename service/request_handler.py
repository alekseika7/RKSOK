import asyncio
import re
from typing import Optional, Type

from config import (DB_QUERY_EXEC_TIMEOUT, REQUEST_END)
from exceptions import (
    CanNotParseRequestError,
    CommandExecTimeoutError,
    RequestCheckBaseException,
    UnknownControlServerResponseError,
)
from models.models import ControlServerConf, RequestData
from service.control_server import get_control_server_response, CONTROL_SERVER_CONF
from service.db import RKSOKDatabaseClient
from service.logger import logger
from service.protocols import RKSOKProtocol, RKSOKProtocolFirstVersion


def _parse_request(request: str) -> RequestData:
    """
    Parses raw client request and returns request parts.
    If there is no option to parse data it will raise CanNotParseRequestError.
    """
    request_parts = request.rstrip(REQUEST_END).split('\r\n', 1)
    pattern = re.compile(r'(\S+) (.+) (\S+)')  # todo: вынести в константу?
    found_matches = re.findall(pattern, request_parts[0])

    is_valid_request = len(found_matches) > 0
    if is_valid_request:
        found_matches = found_matches[0]
        is_valid_request = len(found_matches) == 3

    if not is_valid_request:
        raise CanNotParseRequestError(
            r'Unknown request format! Server expects:<COMMAND> <name> <PROTOCOL>\r\n<value>\r\n\r\n'
        )
    value = None
    if len(request_parts) == 2:
        value = request_parts[1]

    return RequestData(command=found_matches[0], name=found_matches[1], protocol=found_matches[2], value=value)


async def process_client_request(
    request: str,
    db_client: RKSOKDatabaseClient,
    rksok_type: Optional[Type[RKSOKProtocol]] = RKSOKProtocolFirstVersion,
    control_server_conf: Optional[ControlServerConf] = CONTROL_SERVER_CONF,
) -> str:
    """
    Takes raw request and database client, parses request parts and checks their correctness,
    performs interactions with the control server, processes request with timeout and returns response to the client.
    """
    rksok = rksok_type(db_client=db_client)
    try:
        parsed_request = _parse_request(request=request)
        rksok.check_request_data(request_data=parsed_request)
    except (CanNotParseRequestError, RequestCheckBaseException) as parsing_error:
        logger.error(f'Exception happened: {parsing_error}')
        return f'{rksok.configuration.response_names.incorrect} {rksok.configuration.protocol}{REQUEST_END}'

    control_server_response = await get_control_server_response(request=request, server_conf=control_server_conf)
    if control_server_response.startswith(control_server_conf.responses.no):
        return control_server_response
    elif not control_server_response.startswith(control_server_conf.responses.yes):
        raise UnknownControlServerResponseError(
            f'Unknown response! Available variants:\n{control_server_conf.responses.yes}, '
            f'{control_server_conf.responses.no}'
        )

    try:
        response = await asyncio.wait_for(rksok.process_request(), timeout=DB_QUERY_EXEC_TIMEOUT)
    except asyncio.TimeoutError:
        raise CommandExecTimeoutError(
            f'Exceeded timeout while reading! Current timeout: {DB_QUERY_EXEC_TIMEOUT} seconds.'
        )
    return response
