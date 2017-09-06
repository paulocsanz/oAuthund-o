from bs4 import BeautifulSoup
from werkzeug.exceptions import InternalServerError
from requests import get, post
from ..common.errors import UserNotFound, NotAuthenticated
from ..common.utils import format_title

def login(username, password):
    uri = "https://portalaluno.ufrj.br/Portal/acesso"
    req_get = get(uri)
    if req_get.status_code != 200:
        raise InternalServerError(req_get.status_code)

    JSESSIONID = req_get.cookies["JSESSIONID"]
    req_post = post(
        uri,
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

def get_user(cookie):
    uri = "https://portalaluno.ufrj.br/Portal/inicial"
    photo_base_uri = "https://sigadocker.ufrj.br:8090/{}"
    req = get(uri,cookies={"gnosys-token": cookie})
    if req.status_code != 200:
        raise InternalServerError(req.status_code)

    soup = BeautifulSoup(req.content.decode('utf-8'), "html.parser")
    name_div_list = soup.find_all("div", class_="gnosys-login-nome")
    if len(name_div_list) < 1:
        raise NotAuthenticated()

    name = format_title(name_div_list[0].get_text())

    avatar_id_list = soup.select("#avatarId")
    if len(avatar_id_list) < 1:
        raise NotAuthenticated()
    photo_uri = photo_base_uri.format(avatar_id_list[0]["value"])

    return name, photo_uri
