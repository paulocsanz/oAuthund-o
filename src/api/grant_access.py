from ..common.errors import InvalidClientId, InvalidCodeOrClientSecret
from ..models import GrantAccess

def set_tokens(client_id, access_token, refresh_token):
    token = GrantAccess(client_id, access_token, refresh_token)
    token.save()
    return token

def get_tokens(code, client_id, client_secret):
    try:
        return GrantAccess.grant(code, client_id, client_secret)
    except NotFound:
        # Raises InvalidClientId if it doesn't exist
        get_application(client_id)
        raise InvalidCodeOrClientSecret()
