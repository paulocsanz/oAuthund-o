from ..common.errors import NotAuthenticated
from ..common.auth import logout_session
from ..models import User
from .siga_wrapper import get_user as _get_user

def get_user(cookie):
    try:
        name, photo_uri = _get_user(cookie)
    except NotAuthenticated:
        logout_session()
        raise
    user = User(username, name, photo_uri)
    return user
