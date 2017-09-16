from ..common.errors import NoResult, MissingRequiredFields
from ..common.auth import login_required, OAuth_authentication
from ..common.utils import object_json, random_string
from .. import api, app, session

@app.route('/')
@login_required
def home(cookie):
    user = api.get_user(cookie)

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
    
@app.route('/user', methods=["POST"])
@OAuth_authentication
def user(access_token):
    cookie = api.get_cookie(access_token)
    return object_json(api.get_user(cookie))
