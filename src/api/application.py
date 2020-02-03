from ..common.errors import NoResult, InvalidClientId
from ..models import Application

def get_apps(username):
    return Application.find_by_user(username)

def get_application(client_id):
    try:
        return Application.find_by_client(client_id)
    except NoResult:
        raise InvalidClientId()

def edit_app(username, name, description, redirect_uri, client_id):
    app = Application.find_by_client(client_id)

    if app.creator_username != username:
        raise NotAuthorized()

    app.name = name
    app.description = description
    app.redirect_uri = redirect_uri
    app.save()
    return app.client_id

def register_app(username, name, description, redirect_uri):
    app = Application(username, name, description, redirect_uri)
    app.save()
    return app.client_id

def delete_app(username, client_id):
    Application.delete(username, client_id)
