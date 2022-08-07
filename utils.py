from typing import Any
from exceptions import IncorrectHostError, IncorrectPortError


def _check_host(host: Any) -> None:
    """Checks host correctness."""
    if not isinstance(host, str):
        raise IncorrectHostError('Host is not str!')


def _check_port(port: Any) -> None:
    """Checks port correctness."""
    try:
        int(port)
    except ValueError:
        raise IncorrectPortError('Port can not be converted to int!')


def check_host_port(host: Any, port: Any) -> None:
    _check_host(host=host)
    _check_port(port=port)


