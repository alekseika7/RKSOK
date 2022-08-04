# ---------------- Exceptions for catching in process_request func from server.py ----------------
class ServerBaseException(Exception):
    """"""
    pass


class CanNotParseRequestError(ServerBaseException):
    """"""
    pass


class UnknownControlServerResponseError(ServerBaseException):
    """"""
    pass


class WrongFileExtensionError(ServerBaseException):
    """"""
    pass


class DBConnectionError(ServerBaseException):
    """"""
    pass


class ReadTimeoutError(ServerBaseException):
    """"""
    pass


class DidNotReachRequestEndError(ServerBaseException):
    """"""
    pass


class CommandExecTimeoutError(ServerBaseException):
    """"""
    pass


# ---------------- Exceptions for catching in _check_request_data method of RKSOKProtocol instance ----------------
class RequestCheckBaseException(Exception):
    """"""
    pass


class UnknownRequestCommandError(RequestCheckBaseException):
    """"""
    pass


class UnknownRequestProtocolError(RequestCheckBaseException):
    """"""
    pass


class ExceededNameLengthError(RequestCheckBaseException):
    """"""
    pass


class MissingRequestValueError(RequestCheckBaseException):
    """"""
    pass