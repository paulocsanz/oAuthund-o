from flask import request
from functools import wraps
from datetime import datetime
from .utils import random_string
from .errors import NotAuthenticated, NoResult, CSRFDetected, NoAccessToken, InvalidToken
from ..models import Authentication

SESSION_EXPIRATION = None
session = None
def ConfigAuth(app, _session):
    global session, SESSION_EXPIRATION
    session = _session
    SESSION_EXPIRATION =  app.config["SESSION_EXPIRATION"]

def login_session(auth, username):
    global session
    session["access_token"] = auth.access_token
    session["refresh_token"] = auth.refresh_token
    session["username"] = username
    session["expiration"] = SESSION_EXPIRATION

def logout_session():
    global session
    session.pop("access_token", None)
    session.pop("refresh_token", None)
    session.pop("username", None)
    session.pop("expiration", None)

def is_auth():
    global session
    username = session.get("username") or ""
    expiration = session.get("expiration") or ""
    access_token = session.get("access_token") or ""

    if "" in [username, expiration, access_token]:
        raise NotAuthenticated()

    try:
        cookie = Authentication.retrieve_cookie(access_token)
    except NoResult:
        raise NotAuthenticated()

    if expiration > datetime.now().timestamp():
        raise NotAuthenticated()
    return cookie

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        cookie = is_auth()
        return f(cookie, *args, **kwargs)
    return wrap

def CSRF_protection(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        _dict = request.form if request.method == "POST" else request.args
        csrf = session.get("crsf_token") is not None
        csrf = csrf and _dict.get("csrf_token") != session.get("csrf_token")
        session["csrf_token"] = random_string(20)
        if csrf:
            raise CSRFDetected()
        return f(*args, **kwargs)
    return wrap

def get_access_token():
    return (request.form.get("access_token")
            or (request.headers.get("Authorization")
                               .split("Bearer")
                               .strip())
            or "")


def OAuth_authentication(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        access_token = get_access_token()
        if access_token == "":
            raise NoAccessToken()
        try:
            cookie = Authentication.retrieve_cookie(access_token)
        except NoResult:
            raise InvalidToken()
        return f(cookie, *args, **kwargs)
    return wrap
