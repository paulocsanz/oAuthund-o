from flask import request
from datetime import datetime
from ..common.errors import CRSFDetected
from ..common.utils import random_string, add_arg
from .. import api, app

@app.route('/login')
def authenticate():
    state = request.args.get("state")
    client_id = request.args.get("client_id")

    client = api.get_client(client_id)
    return render_template("login.html",
                           state=state,
                           client=client)

def authorize():
    state = request.args.get("state")
    client_id = request.args.get("client_id")

    username = session.get("username") or ""
    expiration = session.get("expiration") or datetime.now()+1000
    if username is "" or expiration > datetime.now():
        return authenticate()

    authorization = api.get_authorization(cliend_id, username)
    if authorization is not None:
        redirect_uri = add_arg(redirect_uri,
                               code=code,
                               state=state) 
        return redirect(redirect_uri)

@app.route('/authorize')
def handle_authorization():
    response_type = request.args.get("response_type")
    if response_type == "code":
        raise ProtocolError()

    if (request.args.get("code") or "") == "":
        return authenticate()
    else:
        return authorize()

@app.route('/authorize', methods=["POST"])
def login():
    state = request.form.get("state")
    username = request.form.get("username")
    password = request.form.get("password")

    code = api.login(username, password)
    session["username"] = username
    session["expire"] = app.config["SESSION_EXPIRATION"]
    
    return redirect(url_for("login", code=code))

@app.route('/grant', methods=["POST"])
def grant():
    grant_type = request.args.get("grant_type")
    client_id = request.args.get("client_id")
    client_secret = request.args.get("client_secret")
    code = request.args.get("code")

    #api.
    #session["auth_id"] = 
