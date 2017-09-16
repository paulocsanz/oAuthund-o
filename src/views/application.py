from ..common.utils import random_string
from ..common.auth import login_required, CSRF_protection
from .. import api, app, session

@app.route('/register/app')
@login_required
def register_app(cookie):
    session["csrf_token"] = session.get("csrf_token") or random_string(app.config["CODE_SIZE"])
    return render_template("register_app.html",
                           csrf_token=session["csrf_token"])

@app.route('/register/app', methods=["POST"])
@CSRF_protection
@login_required
def register_app_post(cookie):
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

@app.route('/application')
@login_required
def application(cookie):
    client_id = request.args.get("client_id") or ""
    app = api.get_application(client_id)
    return render_template("application.html",
                           app=app,
                           csrf_token=session.get("csrf_token") or random_string(app.config["CODE_SIZE"]))

@app.route('/delete/app', methods=["POST"])
@CSRF_protection
@login_required
def delete_application(cookie):
    client_id = request.form.get("client_id") or ""
    if client_id == "":
        raise MissingRequiredFields()
    api.delete_app(session["username"], client_id)
    return redirect(url_for("home"))
