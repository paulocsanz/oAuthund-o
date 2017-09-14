from flask import request
from .oauth import *
from ..common.errors import NotAuthenticated

@app.errorhandler(NotAuthenticated)
def authenticate(err):
    state = request.args.get("state")
    client_id = request.args.get("client_id")
    kwargs = {key: value
                for key, value in [("state", state),
                            ("client_id", client_id),
                            ("e", err)]
                    if value is not None}
    kwargs["e"] = str(err)
    session["next"] = request.script_root + request.path
    return redirect(url_for("login", **kwargs))
