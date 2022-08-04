from config import REQUEST_END
from service.db import RKSOKDatabaseClient
from exceptions import (
    ExceededNameLengthError,
    UnknownRequestCommandError,
    UnknownRequestProtocolError,
)
from models.models import (
    RequestData,
    RKSOKServerCommands,
    RKSOKServerConf,
    RKSOKServerResponses,
    TaskStatus,
    TaskResult,
)


class RKSOKProtocol:
    """"""
    configuration: RKSOKServerConf

    def __init__(self, db_client: RKSOKDatabaseClient, request_data: RequestData) -> None:
        self._db_client = db_client
        self._request = request_data
        self._check_request_data()

    def _check_request_data(self) -> None:
        """"""
        available_commands = [command for command in self.configuration.command_names]
        if self._request.command not in available_commands:
            raise UnknownRequestCommandError(
                f'Unknown command {self._request.command}! Available commands:\n{available_commands}'
            )
        if len(self._request.name) > self.configuration.max_name_length:
            raise ExceededNameLengthError(
                f'Name {self._request.name} length is too long! Max name length is {self.configuration.max_name_length}'
            )
        if self._request.protocol != self.configuration.protocol:
            raise UnknownRequestProtocolError(
                f'Unknown protocol {self._request.protocol}! Protocol must be {self.configuration.protocol}'
            )

    async def _get(self) -> TaskResult:
        """"""
        raise NotImplementedError('Abstract method!')

    async def _put(self) -> TaskResult:
        """"""
        raise NotImplementedError('Abstract method!')

    async def _delete(self) -> TaskResult:
        """"""
        raise NotImplementedError('Abstract method!')

    def _format_response(self, response_header: str, value: str | None) -> str:
        """"""
        first_row = f'{response_header} {self.configuration.protocol}'
        optional_fields = '\r\n' + value if value else ''
        return first_row + optional_fields + REQUEST_END

    async def process_request(self) -> str:
        """"""
        response = None
        match self._request.command:
            case self.configuration.command_names.get:
                response = await self._get()
            case self.configuration.command_names.put:
                response = await self._put()
            case self.configuration.command_names.delete:
                response = await self._delete()

        if response.status == TaskStatus.NOT_OK:
            return self._format_response(
                response_header=self.configuration.response_names.not_found, value=response.result)

        return self._format_response(response_header=self.configuration.response_names.ok, value=response.result)


class RKSOKProtocolFirstVersion(RKSOKProtocol):
    """"""
    configuration = RKSOKServerConf(
        protocol='РКСОК/1.0',
        max_name_length=30,
        command_names=RKSOKServerCommands(get='ОТДОВАЙ', put='ЗОПИШИ', delete='УДОЛИ'),
        response_names=RKSOKServerResponses(ok='НОРМАЛДЫКС', not_found='НИНАШОЛ', incorrect='НИПОНЯЛ')
    )

    def __init__(self, db_client: RKSOKDatabaseClient, request_data: RequestData) -> None:
        super().__init__(db_client=db_client, request_data=request_data)

    async def _get(self) -> TaskResult:
        """"""
        return await self._db_client.get(name=self._request.name)

    async def _put(self) -> TaskResult:
        """"""
        return await self._db_client.update(name=self._request.name, value=self._request.value)

    async def _delete(self) -> TaskResult:
        """"""
        return await self._db_client.delete(name=self._request.name)
