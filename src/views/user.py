from flask import render_template, send_file
from ..common.errors import NoResult, MissingRequiredFields
from ..common.auth import login_required, OAuth_authentication, get_access_token
from ..common.utils import object_json, random_string
from .. import api, app, session

@app.route('/')
@login_required
def home(cookie):
    user = api.get_user(session["username"], cookie)

    try:
        authorizations = api.get_authorizations(user.username)
    except NoResult:
        authorizations = None

    try:
        apps = api.get_apps(user.username)
    except NoResult:
        apps = None
    return render_template('profile.html',
                           csrf_token=session.get("csrf_token") or random_string(app.config["CODE_SIZE"]),
                           user=user,
                           apps=apps,
                           authorizations=authorizations)

@app.route('/user.json', methods=["POST"])
@OAuth_authentication
def user(cookie):
    username = api.get_username(get_access_token())
    return object_json(api.get_user(username, cookie))

@app.route('/user/profile.png', methods=["GET", "POST"])
@OAuth_authentication
def photo_profile(cookie):
    user = api.get_user(None, cookie)
    return photo(user.photo_id)

@app.route('/user/photo/<id>.png', methods=["GET", "POST"])
@OAuth_authentication
def photo(cookie, id):
    return send_file(api.get_user_photo(cookie, id),
                     mimetype="image/png")
