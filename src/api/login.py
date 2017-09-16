from ..common.errors import NotAuthenticated
from ..common.auth import logout_session
from ..models import User, Authentication
from .siga_wrapper import login as _login, get_user as _get_user

def login(username, password, access_token=None, refresh_token=None):
    cookie = _login(username, password)
    auth = Authentication(username, password, cookie, None, access_token, refresh_token)
    auth.save()
    return auth

def get_user(cookie):
    try:
        name, photo_uri = _get_user(cookie)
    except NotAuthenticated:
        logout_session()
        raise
    user = User(username, name, photo_uri)
    return user

def get_cookie(access_token):
    return Authentication.retrieve_cookie(access_token)

def get_password(refresh_token):
    return Authentication.retrieve_password(refresh_token)

def get_username(access_token):
    return Authentication.get_username(access_token)
