from flask import render_template, redirect, url_for
from ..common.utils import add_args, get_arg, get_form, optional_args
from ..common.auth import is_auth, login_session, CSRF_protection, get_csrf_token
from ..common.errors import MissingRequiredFields, NotAuthenticated, InvalidClientId
from .. import api, app, session

@app.route('/login')
def login():
    state = get_arg("state")
    client_id = get_arg("client_id")

    kwargs = {}
    optional_args(kwargs, state=state)

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
            raise InvalidClientId()

        application = api.get_application(client_id)
    except InvalidClientId:
        application = None

    kwargs["crsf_token"] =  get_csrf_token()
    kwargs["app"] = application
    return render_template("login.html", **kwargs)

@app.route('/login', methods=["POST"])
@CSRF_protection
def login_post():
    state = get_form("state")
    client_id = get_form("client_id")
    username = get_form("username")
    password = get_form("password")

    if "" in [username, password]:
        raise MissingRequiredFields()

    auth = api.authenticate(username, password)
    login_session(auth, username)

    kwargs = {}
    optional_args(kwargs,
                  client_id=client_id,
                  state=state)

    if session.get("next") is not None:
        url = add_args(session.pop("next"), **kwargs)
    elif client_id == "":
        url = url_for("home")
    else:
        url = url_for('authorize', **kwargs)
    return redirect(url)
