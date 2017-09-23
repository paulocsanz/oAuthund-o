from flask import redirect, url_for, render_template
from json import dumps as json_dumps
from ..common.auth import login_required, CSRF_protection, get_csrf_token
from ..common.errors import (MissingRequiredFields, NotAuthenticated, MissingClientId,
                             NotAuthorized, InvalidGrantType, InvalidResponseType)
from ..common.utils import (add_args, get_form, get_param, optional_args)
from .. import api, app, session

@app.route('/oauth/token', methods=["POST"])
def token():
    grant_type = get_form("grant_type")
    code = get_form("code")
    client_id = get_form("client_id")
    client_secret = get_form("client_secret")

    if grant_type == "authorization_code":
        access_token, refresh_token = api.get_tokens(code, client_id, client_secret)
        username, password = api.get_username_password(refresh_token)
    elif grant_type == "refresh_token":
        refresh_token = code
        username, password = api.get_username_password(refresh_token)

        auth = api.authenticate(username, password)
        access_token, refresh_token = auth.access_token, auth.refresh_token
    else:
        raise InvalidGrantType()

    api.authenticate(username,
                     password,
                     access_token,
                     refresh_token)
    return json_dumps({"access_token": access_token,
                       "refresh_token": refresh_token,
                       "token_type": "bearer",
                       "expires": 3600})

@app.route('/oauth/authorize')
@login_required
def authorize(cookie):
    response_type = get_param("response_type")
    state = get_param("state")
    client_id = get_param("client_id")

    if response_type != "code":
        raise InvalidResponseType

    if client_id == "":
        raise MissingClientId()

    kwargs = {}
    optional_args(kwargs, state=state)

    try:
        api.get_authorization(client_id,
                              session["username"])
        return authorize_post()
    except NotAuthorized:
        pass

    try:
        kwargs["user"] = api.get_user(session["username"], cookie)
    except NotAuthenticated:
        kwargs["client_id"] = client_id
        return redirect(url_for('login', **kwargs))

    kwargs["app"] = api.get_application(client_id)
    kwargs["csrf_token"] = get_csrf_token()
    return render_template('authorize.html', **kwargs)

@app.route('/oauth/authorize', methods=["POST"])
@CSRF_protection
@login_required
def authorize_post(cookie):
    client_id = get_param("client_id")
    state = get_param("state")

    try:
        api.get_authorization(client_id,
                              session["username"])
    except NotAuthorized:
        api.set_authorization(client_id,
                              session["username"])

    application = api.get_application(client_id)
    access = api.set_tokens(client_id,
                            session["access_token"],
                            session["refresh_token"])
    kwargs = {"code": access.code}
    optional_args(kwargs, state=state)
    return redirect(add_args(application.redirect_uri, **kwargs))

@app.route('/delete/authorization', methods=["POST"])
@CSRF_protection
@login_required
def delete_authorization(cookie):
    client_id = get_form("client_id")

    if client_id == "":
        raise MissingRequiredFields()

    api.delete_authorization(session["username"], client_id)
    return redirect(url_for("home"))
