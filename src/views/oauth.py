from flask import request, render_template, redirect, url_for
from json import loads as json_loads, dumps as json_dumps
from datetime import datetime
from ..common.auth import is_auth, login_required, login_session, CSRF_protection
from ..common.errors import NoResult, MissingRequiredFields, NotAuthenticated, MissingClientId
from ..common.utils import random_string, add_arg
from .. import api, app, session

@app.route('/')
@login_required
def home():
    user = api.get_user(session)

    try:
        authorizations = api.get_authorizations(user.username)
    except NoResult:
        authorizations = None

    try:
        apps = api.get_apps(user.username)
    except NoResult:
        apps = None
    return render_template('profile.html',
                           csrf_token=session.get("csrf_token") or random_string(app.config["CODE_SIZE"]),
                           user=user,
                           apps=apps,
                           authorizations=authorizations)

@app.route('/login')
def login():
    state = request.args.get("state") or ""
    client_id = request.args.get("client_id") or ""
    kwargs = {}

    if state != "":
        kwargs["state"] = state

    try:
        is_auth()
        if client_id != "":
            kwargs["client_id"] = client_id
            return redirect(url_for("authorize", **kwargs))
        else:
            return redirect(url_for("home"))
    except NotAuthenticated:
        pass

    try:
        if client_id == "":
            raise NoResult()

        application = api.get_application(client_id)
    except NoResult:
        application = None

    session["csrf_token"] = session.get("csrf_token") or random_string(app.config["CODE_SIZE"])
    kwargs["app"] = application
    return render_template("login.html", **kwargs)

@app.route('/login', methods=["POST"])
@CSRF_protection
def login_post():
    state = request.form.get("state") or ""
    client_id = request.form.get("client_id") or ""
    username = request.form.get("username") or ""
    password = request.form.get("password") or ""

    if "" in [username, password]:
        raise MissingRequiredFields()

    auth = api.login(username, password)
    login_session(auth, username)

    if session.get("next") is not None:
        return redirect(session.pop("next", None))
    
    if client_id == "":
        return redirect(url_for("home"))

    kwargs = {"client_id": client_id}

    if state != "":
        kwargs["state"] = state
    return redirect(url_for("authorize", **kwargs))

@app.route('/oauth/token', methods=["POST"])
def tokens():
    # Also ignores grant_type, since endpoint only does this
    code = request.form.get("code") or ""
    client_id = request.form.get("client_id") or ""
    client_secret = request.form.get("client_secret") or ""
    access_token, refresh_token = api.get_tokens(code, client_id, client_secret)
    return json_dumps({"access_token": access_token,
                       "refresh_token": refresh_token,
                       "token_type": "bearer",
                       "expires": 3600})

@app.route('/oauth/authorize')
@login_required
def authorize():
    # Let's ignore response_type, since this endpoint only does this
    state = request.args.get("state") or ""
    client_id = request.args.get("client_id") or ""

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
        kwargs["user"] = api.get_user(session)
    except NoResult:
        kwargs["client_id"] = client_id
        return redirect(url_for('login', **kwargs))

    session["csrf_token"] = session.get("csrf_token") or random_string(app.config["CODE_SIZE"])
    return render_template('authorize.html', **kwargs)

@app.route('/oauth/authorize', methods=["POST"])
@CSRF_protection
@login_required
def authorize_post():
    client_id = request.form.get("client_id") or request.args.get("client_id") or ""
    state = request.form.get("state") or ""

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

@app.route('/register/app')
@login_required
def register_app():
    session["csrf_token"] = session.get("csrf_token") or random_string(app.config["CODE_SIZE"])
    return render_template("register_app.html",
                           csrf_token=session["csrf_token"])

@app.route('/register/app', methods=["POST"])
@CSRF_protection
@login_required
def register_app_post():
    name = request.form.get("name") or ""
    description = request.form.get("description") or ""
    redirect_uri = request.form.get("redirect_uri") or ""
    if "" in [name, redirect_uri]:
        raise MissingRequiredFields()

    client_id = api.register_app(session["username"],
                                 name,
                                 description,
                                 redirect_uri)
    return redirect(url_for('application', client_id=client_id))

@app.route('/application')
@login_required
def application():
    client_id = request.args.get("client_id") or ""
    app = api.get_application(client_id)
    return render_template("application.html",
                           app=app,
                           csrf_token=session.get("csrf_token") or random_string(app.config["CODE_SIZE"]))

@app.route('/delete/authorization', methods=["POST"])
@CSRF_protection
@login_required
def delete_authorization():
    client_id = request.form.get("client_id") or ""
    if client_id == "":
        raise MissingRequiredFields()
    api.delete_authorization(session["username"], client_id)
    return redirect(url_for("home"))

@app.route('/delete/app', methods=["POST"])
@CSRF_protection
@login_required
def delete_app():
    client_id = request.form.get("client_id") or ""
    if client_id == "":
        raise MissingRequiredFields()
    api.delete_app(session["username"], client_id)
    return redirect(url_for("home"))
