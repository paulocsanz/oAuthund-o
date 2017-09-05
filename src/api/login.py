from .siga_wrapper import login as _login

def login(username, password, client_id):
    cookie = _login(username, password)
    auth = Authentication(username, password, client_id, cookie)
    auth.save()
    return auth.code

def grant(user_id):
    pass
