from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True, slots=True)
class RequestData:
    command: str
    name: str
    protocol: str
    value: str | None


@dataclass(frozen=True, slots=True)
class ControlServerResponse:
    yes: str
    no: str


@dataclass(frozen=True, slots=True)
class ControlServerConf:
    host: str
    port: int
    ask_command: str
    protocol: str
    responses: ControlServerResponse


@dataclass(frozen=True, slots=True)
class RKSOKServerResponses:
    ok: str
    not_found: str
    incorrect: str


@dataclass(frozen=True, slots=True)
class RKSOKServerCommands:
    get: str
    put: str
    delete: str


@dataclass(frozen=True, slots=True)
class RKSOKServerConf:
    protocol: str
    max_name_length: int
    command_names: RKSOKServerCommands
    response_names: RKSOKServerResponses


class TaskStatus(Enum):
    OK = 'ok'
    NOT_OK = 'not ok'


@dataclass(frozen=True, slots=True)
class TaskResult:
    status: TaskStatus
    result: str | None
