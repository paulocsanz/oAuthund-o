from ..models import GrantAccess

def set_tokens(client_id, access_token, refresh_token):
    token = GrantAccess(client_id, access_token, refresh_token)
    token.save()
    return token

def get_tokens(code, client_id, client_secret):
    return GrantAccess.grant(code, client_id, client_secret)
