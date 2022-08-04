# ---------------- Exceptions for catching in process_request func from server.py ----------------
class ServerBaseException(Exception):
    """
    Base exception for convenient catching multiple exceptions
    in try-except block inside process_request func in server.py
    """
    pass


class UnknownControlServerResponseError(ServerBaseException):
    pass


class DBConnectionError(ServerBaseException):
    pass


class ReadTimeoutError(ServerBaseException):
    pass


class CommandExecTimeoutError(ServerBaseException):
    pass


# ---------------- Exceptions for catching in _check_request_data method of RKSOKProtocol instance ----------------
class RequestCheckBaseException(Exception):
    """
    Base exception for convenient catching multiple exceptions
    in _check_request_data method of RKSOKProtocol instance
    """
    pass


class UnknownRequestCommandError(RequestCheckBaseException):
    pass


class UnknownRequestProtocolError(RequestCheckBaseException):
    pass


class ExceededNameLengthError(RequestCheckBaseException):
    pass


# ---------------- Exceptions for checking raw request in _parse_request func in request_handler.py ----------------
class CanNotParseRequestError(Exception):
    pass
