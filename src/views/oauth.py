from flask import request, render_template, redirect, url_for
from datetime import datetime
from ..common.auth import is_auth, login_required, login_session, CSRF_protection
from ..common.errors import NoResult, MissingRequiredFields, NotAuthenticated
from ..common.utils import random_string, add_arg
from .. import api, app, session

@app.route('/')
@login_required
def home():
    user = api.get_user(session)
    try:
        apps = api.get_apps(user.username)
    except NoResult:
        apps = None
    return render_template('profile.html',
                           user=user,
                           apps=apps)

@app.route('/login')
def authenticate():
    state = request.args.get("state") or ""
    client_id = request.args.get("client_id") or ""

    try:
        is_auth()
        if client_id != "":
            kwargs = {"client_id": client_id}
            if state != "":
                kwargs["state"] = state
            return redirect(url_for("authorize", **kwargs))
        else:
            return redirect(url_for("home"))
    except NotAuthenticated:
        pass

    try:
        if client_id == "":
            raise NoResult()

        client = api.get_client(client_id)
    except NoResult:
        client = None

    session["csrf_token"] = random_string(app.config["CODE_SIZE"])
    kwargs = {"client": client,
              "csrf_token": session["csrf_token"]}
    if state != "":
        kwargs["state"] = state
    return render_template("login.html", **kwargs)

@app.route('/login', methods=["POST"])
@CSRF_protection
def login():
    state = request.form.get("state") or ""
    client_id = request.form.get("client_id") or ""
    username = request.form.get("username") or ""
    password = request.form.get("password") or ""

    if "" in [username, password]:
        raise MissingRequiredFields()

    auth = api.login(username, password)
    login_session(auth, username)
    
    if client_id == "":
        return redirect(url_for("home"))

    kwargs = {"code": auth.code,
              "client_id": client_id}
    if state != "":
        kwargs["state"] = state
    return redirect(url_for("authorize", **kwargs))

@app.route('/authorize')
@login_required
def authorize():
    # Let's ignore response_type, since this endpoint only does this
    state = request.args.get("state") or ""
    client_id = request.args.get("client_id") or ""
    code = session.get("code") or ""

    if client_id != "":
        client = api.get_client(client_id)
    else:
        raise MissingRequiredFields()

    try:
        authorization = api.get_authorization(client_id, username)
        kwargs = {"code": authorization.code}
        if state != "":
            kwargs["state"] = state
        return redirect(add_arg(client.redirect_uri, **kwargs))
    except NoResult:
        pass

    try:
        user = api.get_user(session)
    except NoResult:
        return redirect(url_for('login'))

    session["csrf_token"] = random_string(app.config["CODE_SIZE"])
    return render_template('authorize.html',
                           code=code,
                           client=client,
                           user=user,
                           csrf_token=session["csrf_token"])

@app.route('/authorize', methods=["POST"])
def authorize_post():
    return redirect(url_for("login"))

@app.route('/register/app')
@login_required
def register_app():
    session["csrf_token"] = random_string(app.config["CODE_SIZE"])
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

@app.route('/delete/app', methods=["POST"])
@CSRF_protection
@login_required
def delete_app():
    client_id = request.args.get("client_id")
    if client_id == "":
        raise MissingRequiredFields()
    api.delete_app(session["username"], client_id)
    return redirect(url_for("home"))

@app.route('/app/<client_id>')
def application(client_id):
    # TODO
    return redirect(url_for("login"))

@app.route('/grant', methods=["POST"])
def grant():
    grant_type = request.args.get("grant_type")
    client_id = request.args.get("client_id")
    client_secret = request.args.get("client_secret")
    code = request.args.get("code")

    #api.
    #session["auth_id"] = 
