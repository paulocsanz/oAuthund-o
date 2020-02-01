from flask import request
from functools import wraps
from datetime import datetime
from .utils import random_string
from .errors import NotAuthenticated, NoResult, CSRFDetected, MissingAccessToken, InvalidAccessToken
from ..models import Authentication

CSRF_TOKEN_EXPIRATION = None
SESSION_EXPIRATION = None
TOKEN_SIZE = None
session = None
def ConfigAuth(app, _session):
    global session, SESSION_EXPIRATION, TOKEN_SIZE, CSRF_TOKEN_EXPIRATION
    session = _session
    CSRF_TOKEN_EXPIRATION = app.config["CSRF_TOKEN_EXPIRATION"]
    SESSION_EXPIRATION = app.config["SESSION_EXPIRATION"]
    TOKEN_SIZE = app.config["TOKEN_SIZE"]

def get_csrf_token():
    global session, CSRF_TOKEN_EXPIRATION
    if session.get("csrf_token") is None:
        set_csrf_token()

    if datetime.now().timestamp() - session["csrf_token"]["time"] > CSRF_TOKEN_EXPIRATION:
        set_csrf_token()

    return session["csrf_token"]["value"]

def set_csrf_token():
    global session
    session["csrf_token"] = { "value": random_string(20), "time": datetime.now().timestamp() }

def login_session(auth, username):
    global session
    session["access_token"] = auth.access_token
    session["refresh_token"] = auth.refresh_token
    session["username"] = username
    session["expiration"] = SESSION_EXPIRATION
    session["client_id"] = "self"

def logout_session():
    global session
    session.pop("access_token", None)
    session.pop("refresh_token", None)
    session.pop("username", None)
    session.pop("expiration", None)
    session.pop("client_id", None)

def is_auth():
    global session
    username = session.get("username")
    expiration = session.get("expiration")
    access_token = session.get("access_token")

    if None in [username, expiration, access_token]:
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
        session_token = get_csrf_token()
        form_token = _dict.get("csrf_token") 
        if session_token != form_token:
            raise CSRFDetected()
        return f(*args, **kwargs)
    return wrap

def get_access_token():
    return (request.form.get("access_token")
            or ((request.headers.get("Authorization") or "")
                               .split("Bearer")[-1]
                               .strip())
            or session.get("access_token")
            or "")


def OAuth_authentication(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        access_token = get_access_token()
        if access_token == "":
            raise MissingAccessToken()
        try:
            cookie = Authentication.retrieve_cookie(access_token)
        except NoResult:
            raise InvalidAccessToken()
        return f(cookie, *args, **kwargs)
    return wrap
