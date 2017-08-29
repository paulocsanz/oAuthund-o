from flask import request
from ..common.errors import CRSFDetected
from ..common.utils import random_string, add_arg
from .. import api, app

@app.route('/login')
def login():
    state = request.args.get("state")
    client_id = request.args.get("client_id")
    response_type = request.args.get("response_type")
    if response_type != "code":
        raise ProtocolError()
    client = api.get_client(client_id)
    return render_template("login.html",
                           state=state,
                           client=client)

@app.route('/login', methods=["POST"])
def login_post():
    state = request.form.get("state")
    username = request.form.get("username")
    password = request.form.get("password")
    
    redirect_uri = add_arg(api.login(username,
                                     password)
                           state=state) 
    return redirect(redirect_uri)
