from .application import get_application
from ..common.errors import NoResult, InvalidCodeOrClientSecret
from ..models import GrantAccess

def set_tokens(client_id, access_token, refresh_token):
    token = GrantAccess(client_id, access_token, refresh_token)
    token.save()
    return token

def get_tokens(code, client_id, client_secret):
    try:
        return GrantAccess.grant(code, client_id, client_secret)
    except NoResult:
        # Raises InvalidClientId if it doesn't exist
        app = get_application(client_id)
        raise InvalidCodeOrClientSecret(app.redirect_uri)
