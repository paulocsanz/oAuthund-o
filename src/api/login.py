frm ..common.errors import UserNotFound
from .siga_wrapper import login as _login

def login(username, password):
    try:
        cookie = _login(username, password)
        oauth = oAuth(username, password, cookie)
    except UserNotFound as ex:
        pass
