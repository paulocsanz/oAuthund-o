from ..common.errors import NotAuthenticated
from ..common.auth import logout_session
from ..models import User, Authentication
from .siga_wrapper import login as _login, get_user as _get_user

def login(username, password):
    cookie = _login(username, password)
    auth = Authentication(username, password, cookie)
    auth.save()
    return auth

def grant(user_id):
    pass

def get_user(session):
    username = session["username"]
    code = session["code"]
    cookie = Authentication.retrieve_cookie(username, code)
    try:
        name, photo_uri = _get_user(cookie)
    except NotAuthenticated:
        logout_session()
        raise
    user = User(username, name, photo_uri)
    return user
