from bs4 import BeautifulSoup
from werkzeug.exceptions import InternalServerError
from io import BytesIO
from ..common.errors import UserNotFound, NotAuthenticated
from ..common.utils import format_title, http_get, http_post
from flask import session

def login(username, password):
    global session
    uri = "https://portalaluno.ufrj.br/Portal/acesso"
    req_get = http_get(uri)
    if req_get.status_code != 200:
        raise InternalServerError(req_get.status_code)

    JSESSIONID = req_get.cookies["JSESSIONID"]
    req_post = http_post(
        uri,
        data={
            "gnosys-login-form": "gnosys-login-form", 
            "btnEntrar": "Entrar",
            "javax.faces.ViewState": "j_id1",
            "inputUsername": username,
            "inputPassword": password
        }, cookies = {
            "cookie-portalaluno": req_get.cookies["cookie-portalaluno"],
            "JSESSIONID": req_get.cookies["JSESSIONID"]
        }
    )
    try:
        return req_post.cookies["gnosys-token"]
    except KeyError:
        print(req_post.cookies, req_post.content.decode('utf-8'), req_post.status_code, req_post.headers)
        raise UserNotFound()

def get_user(cookie):
    uri = "https://portalaluno.ufrj.br/Portal/inicial"
    req = http_get(uri,cookies={"gnosys-token": cookie})
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

    return name, avatar_id_list[0]["value"]

def get_user_photo(cookie, photo_id):
    uri = "https://portalaluno.ufrj.br/Portal/inicial"
    req = http_get(uri,cookies={"gnosys-token": cookie})
    if req.status_code != 200:
        raise InternalServerError(req.status_code)

    soup = BeautifulSoup(req.content.decode('utf-8'), "html.parser")
    avatar_id_list = soup.select("#avatarId")
    if len(avatar_id_list) < 1:
        raise NotAuthenticated()

    req = http_get("https://sigadocker.ufrj.br/fotos/" + avatar_id_list[0]["value"])
    if req.status_code != 200:
        raise InternalServerError(req.status_code)
    return BytesIO(req.content)
