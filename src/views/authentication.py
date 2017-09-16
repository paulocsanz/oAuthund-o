from flask import request, render_template, redirect, url_for
from ..common.utils import random_string, add_arg
from ..common.auth import is_auth, login_required, login_session, CSRF_protection
from ..common.errors import NoResult, MissingRequiredFields, NotAuthenticated
from .. import api, app, session

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

    kwargs["crsf_token"] = session["csrf_token"] = (session.get("csrf_token")
                                                    or random_string(app.config["CODE_SIZE"]))
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

    auth = api.authenticate(username, password)
    login_session(auth, username)

    kwargs = {}
    if client_id != "":
        kwargs["client_id"] = client_id
    if state != "":
        kwargs["state"] = state

    if session.get("next") is not None:
        url = add_arg(session.pop("next"), **kwargs)
    elif client_id == "":
        url = url_for("home")
    else:
        url = url_for('authorize', **kwargs)
    return redirect(url)
