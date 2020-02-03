from ..common.errors import NotAuthenticated
from ..common.auth import logout_session
from ..models import User
from .siga_wrapper import get_user as _get_user, get_user_photo as _get_user_photo

def get_user(username, cookie):
    try:
        name, photo_uri = _get_user(cookie)
    except NotAuthenticated:
        logout_session()
        raise
    return User(name, photo_uri)

def get_user_photo(cookie, id):
    return _get_user_photo(cookie, id)
