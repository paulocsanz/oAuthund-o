from .errors import NotAuthenticated
from datetime import datetime
from functools import wraps
from . import session

def is_auth():
    username = session.get("username") or ""
    expiration = session.get("expiration") or ""
    code = session.get("code") or ""
    if "" in [username, expiration, code] or expiration > datetime.now().timestamp():
        raise NotAuthenticated()

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        is_auth()
        return f(*args, **kwargs)
    return wrap
