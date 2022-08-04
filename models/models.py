from enum import Enum
from typing import NamedTuple


class RequestData(NamedTuple):
    command: str
    name: str
    protocol: str
    value: str | None


class ControlServerResponse(NamedTuple):
    yes: str
    no: str


class ControlServerConf(NamedTuple):
    host: str
    port: int
    ask_command: str
    protocol: str
    responses: ControlServerResponse


class RKSOKServerResponses(NamedTuple):
    ok: str
    not_found: str
    incorrect: str


class RKSOKServerCommands(NamedTuple):
    get: str
    put: str
    delete: str


class RKSOKServerConf(NamedTuple):
    protocol: str
    max_name_length: int
    command_names: RKSOKServerCommands
    response_names: RKSOKServerResponses


class TaskStatus(Enum):
    OK = 'ok'
    NOT_OK = 'not ok'


class TaskResult(NamedTuple):
    status: TaskStatus
    result: str | None
