class CWException(Exception):
    pass


class FailedSocketHandshakeException(CWException):
    pass


class ExecuteCommandException(CWException):
    pass


class ActionException(CWException):
    pass


class TooFarAwayException(CWException):
    pass