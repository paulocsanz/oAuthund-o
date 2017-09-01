class UserNotFound(Exception):
    pass

class ProtocolError(Exception):
    pass

class NoResult(Exception):
    pass

class UnexpectedError(Exception):
    pass

class InsertFailed(Exception):
    pass

class NoDBConfig(Exception):
    pass

class NoDateFormat(Exception):
    pass

class CRSFDetected(Exception):
    pass
