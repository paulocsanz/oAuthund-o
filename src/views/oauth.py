from flask import request, render_template, redirect, url_for
from datetime import datetime
from ..common.auth import is_auth, login_required
from ..common.errors import CRSFDetected, NoResult, MissingRequiredFields, NotAuthenticated
from ..common.utils import random_string, add_arg
from .. import api, app, session

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login')
def authenticate():
    state = request.args.get("state") or ""
    client_id = request.args.get("client_id") or ""

    if client_id == "":
        raise MissingRequiredFields()

    try:
        is_auth()
        kwrags = {"client_id": client_id}
        if state != "":
            kwargs["state"] = state
        return redirect(url_for("authorize", **kwargs))
    except NotAuthenticated:
        pass

    try:
        if client_id is None:
            raise NoResult

        client = api.get_client(client_id)
    except NoResult:
        client = None

    kwrags = {"client": client}
    if state != "":
        kwargs["state"] = state
    return render_template("login.html", **kwargs)

@app.route('/login', methods=["POST"])
def login():
    state = request.form.get("state")
    username = request.form.get("username")
    password = request.form.get("password")

    code = api.login(username, password)
    session["code"] = code
    session["username"] = username
    session["expire"] = app.config["SESSION_EXPIRATION"]
    
    kwargs = {"code": code}
    if state is not None:
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

    user = api.get_user(session['username'])
    return render_template('authorize.html',
                           code=code,
                           client=client,
                           user=user)

@app.route('/authorize', methods=["POST"])
def authorize_post():
    return redirect(url_for("login"))

@app.route('/register/app')
def register_app():
    return render_template("register_app.html")

@app.route('/register/app', methods=["POST"])
def register_app_post():
    name = request.form.get("name") or ""
    description = request.form.get("description") or ""
    redirect_uri = request.form.get("redirect_uri") or ""
    if "" in [name, redirect_uri]:
        raise MissingRequiredFields()
    client_id = api.register_app(name, description, redirect_uri)
    return redirect(url_for('application', client_id=client_id))

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
