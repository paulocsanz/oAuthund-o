from ..common.errors import NoResult, InvalidAccessToken, InvalidRefreshToken
from ..models import Authentication
from .siga_wrapper import login

def authenticate(username, password, access_token=None, refresh_token=None):
    cookie = login(username, password)
    auth = Authentication(username, password, cookie, None, access_token, refresh_token)
    auth.save()
    return auth

def get_cookie(access_token):
    try:
        return Authentication.retrieve_cookie(access_token)
    except NoResult:
        raise InvalidAccessToken()

def get_username_password(refresh_token):
    try:
        return Authentication.retrieve_username_password(refresh_token)
    except NoResult:
        raise InvalidRefreshToken()

def get_username(access_token):
    try:
        return Authentication.get_username(access_token)
    except NoResult:
        raise InvalidAccessToken()
