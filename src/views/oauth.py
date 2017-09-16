from flask import request, redirect, url_for, render_template
from json import loads as json_loads, dumps as json_dumps
from ..common.auth import login_required, CSRF_protection
from ..common.errors import NoResult, MissingRequiredFields, NotAuthenticated, MissingClientId
from ..common.utils import random_string, add_arg, object_json, hash
from .. import api, app, session

@app.route('/oauth/token', methods=["POST"])
def tokens():
    # Ignores grant_type, since endpoint only does this
    code = request.form.get("code") or ""
    client_id = request.form.get("client_id") or ""
    client_secret = request.form.get("client_secret") or ""
    access_token, refresh_token = api.get_tokens(code, client_id, client_secret)

    username = api.get_username(access_token)
    password = api.get_password(refresh_token)
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
    # Ignores response_type, since this endpoint only does this
    state = request.args.get("state") or request.form.get("state") or ""
    client_id = request.args.get("client_id") or request.form.get("client_id") or ""

    kwargs = {}
    if state != "":
        kwargs["state"] = state

    if client_id != "":
        kwargs["app"] = api.get_application(client_id)
    else:
        raise MissingClientId()

    try:
        authorization = api.get_authorization(client_id,
                                              session["username"])
        return authorize_post()
    except NoResult:
        pass

    try:
        kwargs["user"] = api.get_user(session["username"], cookie)
    except NoResult:
        kwargs["client_id"] = client_id
        return redirect(url_for('login', **kwargs))

    kwargs["csrf_token"] = session["csrf_token"] = (session.get("csrf_token")
                                                    or random_string(app.config["CODE_SIZE"]))
    return render_template('authorize.html', **kwargs)

@app.route('/oauth/authorize', methods=["POST"])
@CSRF_protection
@login_required
def authorize_post(cookie):
    client_id = request.form.get("client_id") or request.args.get("client_id") or ""
    state = request.form.get("state") or request.args.get("state") or ""

    try:
        authorization = api.get_authorization(client_id,
                                              session["username"])
    except NoResult:
        authorization = api.set_authorization(client_id,
                                              session["username"])

    application = api.get_application(client_id)
    access = api.set_tokens(client_id,
                            session["access_token"],
                            session["refresh_token"])
    kwargs = {"code": access.code}

    if state != "":
        kwargs["state"] = state
    return redirect(add_arg(application.redirect_uri, **kwargs))

@app.route('/delete/authorization', methods=["POST"])
@CSRF_protection
@login_required
def delete_authorization(cookie):
    client_id = request.form.get("client_id") or ""
    if client_id == "":
        raise MissingRequiredFields()
    api.delete_authorization(session["username"], client_id)
    return redirect(url_for("home"))
