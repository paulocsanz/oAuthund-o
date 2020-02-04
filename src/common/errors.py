class InsertFailed(Exception):
    pass

class NoDBConfig(Exception):
    pass

class NoDateFormat(Exception):
    pass


class InvalidToken(Exception):
    code = 400

class NotAuthenticated(Exception):
    code = 403
    error_description = "Please sign-in first"

class MissingRequiredFields(Exception):
    code = 400

class NoResult(Exception):
    code = 404

class UserNotFound(NoResult):
    pass

class UnexpectedError(Exception):
    code = 500

class CSRFDetected(Exception):
    code = 403

class OAuth2Error(Exception):
    error = "server_error"
    error_description = "OAuth2 Protocol Error"

class DisplayError(OAuth2Error):
    pass

class RedirectError(OAuth2Error):
    def __init__(self, redirect_uri):
        self.redirect_uri = redirect_uri

class MissingParameter(DisplayError):
    error = "invalid_request"
    error_description = "Missing Parameter"

class MissingClientId(DisplayError):
    error_description = "Missing Client Id"

class MissingAccessToken(DisplayError):
    error_description = "Missing Access Token"

class InvalidParameter(RedirectError):
    error = "invalid_request"
    error_description = "Invalid Parameter"

class InvalidClientId(DisplayError):
    # We don't have the redirect_uri, so we have to display it
    error_description = "Invalid Client Id"

class InvalidCodeOrClientSecret(InvalidParameter):
    error_description = "Invalid Code or Client Secret"

class InvalidAccessToken(InvalidParameter):
    error_description = "Invalid Access Token"

class InvalidRefreshToken(InvalidParameter):
    error_description = "Invalid Refresh Token"

class InvalidGrantType(InvalidParameter):
    error_description = "Invalid Grant Type"

class InvalidResponseType(InvalidParameter):
    error = "unsupported_response_type"
    error_description = "Only 'code' is allowed as 'response_type'"

class NotAuthorized(OAuth2Error):
    error = "unauthorized_client"
    error_description = "The application was not authorized to access user's data"

class CspReport(Exception):
    error = "csp_report"
    error_description = "Violated rules in 'Content-Security-Policy' header set in `src/common/headers.py`"

    def __init__(self, body):
        self.body = body
