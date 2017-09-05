from werkzeug.errors import ServerError
from ..common.errors import UserNotFound
from requests import get, post

def login(username, password):
    url = "https://portalaluno.ufrj.br/Portal/acesso"
    req_get = get(url)
    if req_get.status_code != 200:
        raise ServerError(req.status_code)

    JSESSIONID = req_get.cookies["JSESSIONID"]
    req_post = post(
        url,
        data={
            "gnosys-login-form": "gnosys-login-form", 
            "btnEntrar": "Entrar",
            "javax.faces.ViewState": "j_id1",
            "inputUsername": username,
            "inputPassword": password
        }, cookies = {
            "JSESSIONID": JSESSIONID
        }
    )
    try:
        return req_post.cookies["gnosys-token"]
    except KeyError:
        raise UserNotFound()
