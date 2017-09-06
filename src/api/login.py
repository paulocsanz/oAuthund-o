from ..common.errors import NotAuthenticated
from ..models import User
from .siga_wrapper import login as _login, get_user as _get_user

def login(username, password):
    return _login(username, password)
    #auth = Authentication(username, password, client_id, cookie)
    #auth.save()
    #return auth.code

def grant(user_id):
    pass

def get_user(session):
    cpf = session["username"]
    try:
        name, photo_uri = _get_user(session["code"])
    except NotAuthenticated:
        session.pop("username")
        session.pop("expiration")
        raise
    user = User(cpf, name, photo_uri)
    return user
