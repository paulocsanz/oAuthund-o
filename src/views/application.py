from flask import render_template, redirect, url_for
from ..common.errors import MissingRequiredFields
from ..common.utils import get_form, get_arg
from ..common.auth import login_required, CSRF_protection, get_csrf_token
from .. import api, app, session

@app.route('/app/register')
@login_required
def register_app(cookie):
    return render_template("register_app.html",
                           csrf_token=get_csrf_token())

@app.route('/app/register', methods=["POST"])
@CSRF_protection
@login_required
def register_app_post(cookie):
    name = get_form("name")
    description = get_form("description")
    redirect_uri = get_form("redirect_uri")

    if "" in [name, redirect_uri]:
        raise MissingRequiredFields()

    client_id = api.register_app(session["username"],
                                 name,
                                 description,
                                 redirect_uri)
    return redirect(url_for('application', client_id=client_id))

@app.route('/app/edit')
@login_required
def edit_app(cookie):
    client_id = get_arg("client_id")
    
    if client_id == "":
        raise MissingRequiredFields()

    return render_template("edit_app.html",
                           client_id=client_id,
                           csrf_token=get_csrf_token())

@app.route('/app/edit', methods=["POST"])
@CSRF_protection
@login_required
def edit_app_post(cookie):
    name = get_form("name")
    description = get_form("description")
    redirect_uri = get_form("redirect_uri")
    client_id = get_form("client_id")

    if "" in [name, redirect_uri, client_id]:
        raise MissingRequiredFields()

    client_id = api.edit_app(session["username"],
                             name,
                             description,
                             redirect_uri,
                             client_id)
    return redirect(url_for('application', client_id=client_id))

@app.route('/application')
@login_required
def application(cookie):
    client_id = get_arg("client_id")
    app = api.get_application(client_id)
    return render_template("application.html",
                           app=app,
                           csrf_token=get_csrf_token())

@app.route('/app/delete', methods=["POST"])
@CSRF_protection
@login_required
def delete_application(cookie):
    client_id = get_form("client_id")

    if client_id == "":
        raise MissingRequiredFields("client_id")

    api.delete_app(session["username"],
                   client_id)
    return redirect(url_for("home"))
