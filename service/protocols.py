from dataclasses import astuple

from config import REQUEST_END
from service.db import RKSOKDatabaseClient
from exceptions import (
    ExceededNameLengthError,
    MissingRKSOKConfigurationError,
    UncheckedRequestError,
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
    """Base class for RKSOK server protocols."""
    configuration: RKSOKServerConf

    def __init__(self, db_client: RKSOKDatabaseClient) -> None:
        try:
            self.configuration
        except AttributeError:
            raise MissingRKSOKConfigurationError('Define configuration class attribute!')

        self._db_client = db_client
        self._request = None
        self._is_checked = False

    def check_request_data(self, request_data: RequestData) -> None:
        self._request = request_data
        """Checks command, name and protocol correctness."""
        available_commands = [command for command in astuple(self.configuration.command_names)]
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
        self._is_checked = True

    async def _get(self) -> TaskResult:
        """Abstract method for getting phone by name."""
        raise NotImplementedError()

    async def _put(self) -> TaskResult:
        """Abstract method for writing new data."""
        raise NotImplementedError()

    async def _delete(self) -> TaskResult:
        """Abstract method for deleting phone from db."""
        raise NotImplementedError()

    def _format_response(self, response_header: str, value: str | None) -> str:
        """Formats proper output."""
        first_row = f'{response_header} {self.configuration.protocol}'
        optional_fields = '\r\n' + value if value else ''
        return first_row + optional_fields + REQUEST_END

    async def process_request(self) -> str:
        """Processes client request in form of RequestData, returns corresponding result."""
        if not self._is_checked:
            raise UncheckedRequestError('Run check_request_data() first!')
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
    """Realisation of the РКСОК/1.0 protocol."""
    configuration = RKSOKServerConf(
        protocol='РКСОК/1.0',
        max_name_length=30,
        command_names=RKSOKServerCommands(get='ОТДОВАЙ', put='ЗОПИШИ', delete='УДОЛИ'),
        response_names=RKSOKServerResponses(ok='НОРМАЛДЫКС', not_found='НИНАШОЛ', incorrect='НИПОНЯЛ')
    )

    def __init__(self, db_client: RKSOKDatabaseClient) -> None:
        super().__init__(db_client=db_client)

    async def _get(self) -> TaskResult:
        """Sends request to db to get phone by name."""
        return await self._db_client.get(name=self._request.name)

    async def _put(self) -> TaskResult:
        """Sends request to db to create (update) new record."""
        return await self._db_client.update(name=self._request.name, value=self._request.value)

    async def _delete(self) -> TaskResult:
        """Sends request to db to delete record with specified name."""
        return await self._db_client.delete(name=self._request.name)
