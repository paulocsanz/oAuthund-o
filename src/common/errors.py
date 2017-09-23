class NotAuthenticated(Exception):
    def __str__(self):
        return "Por favor, se autentique com o sigalogado para continuar"

class MissingRequiredFields(Exception):
    pass

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

class CSRFDetected(Exception):
    pass

class OAuth2Error(Exception):
    pass

class MissingClientId(OAuth2Error):
    pass

class NoAccessToken(OAuth2Error):
    pass

class InvalidToken(OAuth2Error):
    pass

class InvalidClientId(OAuth2Error):
    pass

class InvalidCodeOrClientSecret(OAuth2Error):
    pass

class NotAuthorized(OAuth2Error):
    pass

class InvalidAccessToken(OAuth2Error):
    pass

class InvalidRefreshToken(OAuth2Error):
    pass

class InvalidGrantType(OAuth2Error):
    pass

class InvalidResponseType(OAuth2Error):
    pass
