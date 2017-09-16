from ..models import Authentication
from .siga_wrapper import login

def authenticate(username, password, access_token=None, refresh_token=None):
    cookie = login(username, password)
    auth = Authentication(username, password, cookie, None, access_token, refresh_token)
    auth.save()
    return auth

def get_cookie(access_token):
    return Authentication.retrieve_cookie(access_token)

def get_password(refresh_token):
    return Authentication.retrieve_password(refresh_token)

def get_username(access_token):
    return Authentication.get_username(access_token)
