from flask import request, redirect, url_for
from .. import app, session
from ..common.utils import get_arg, optional_args, add_args
from ..common.errors import NotAuthenticated, DisplayError, RedirectError

@app.errorhandler(NotAuthenticated)
def authenticate(err):
    state = get_arg("state")
    client_id = get_arg("client_id")

    kwargs = {}
    optional_args(kwargs,
                  state=state,
                  client_id=client_id,
                  e=str(err))
    session["next"] = request.script_root + request.path
    return redirect(url_for("login", **kwargs))

@app.errorhandler(DisplayError)
def display_error(err):
    return err.error_description, err.code

@app.errorhandler(RedirectError)
def redirect_error(err):
    if err.redirect_uri not in ["", None]:
        return redirect(add_args(err.redirect_uri,
                                 error=err.error,
                                 error_description=err.error_description))
    return display_error(err)
