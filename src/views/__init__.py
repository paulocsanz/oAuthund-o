from .oauth import *
from ..common.errors import NotAuthenticated

@app.errorhandler(NotAuthenticated)
def authenticate(err):
    state = request.args.get("state")
    client_id = request.args.get("client_id")
    kwargs = {arg[0]: arg[1] for arg in [("state", state), ("client_id", client_id), ("e", err)] if arg[1] is not None}
    kwargs["e"] = str(err)
    return redirect(url_for("login", **kwargs))
